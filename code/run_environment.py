"""Step 10 - environment-aware weighting with the real survey covariates.

The radiometric CSV carries per-sample temperature and humidity.  They are
gridded to the 50 m survey grid and turned into per-pixel modality quality
factors (see common.quality_field).  This is the only experiment where the
"environment-aware" part of the framework uses measured covariates rather than
simulated degradation.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from osgeo import gdal

import common as C

gdal.UseExceptions()

CSV = C.ROOT / "Radiometric_Data.csv"


def build_env_fields():
    ds = gdal.Open(str(C.RAW / "K.gxf"), gdal.GA_ReadOnly)
    gt = ds.GetGeoTransform()
    w, h = ds.RasterXSize, ds.RasterYSize
    x0, dx, y0, dy = gt[0], gt[1], gt[3], gt[5]
    ds = None

    df = pd.read_csv(CSV, usecols=["x", "y", "temperature", "humidity"])
    col = np.floor((df["x"].to_numpy() - x0) / dx).astype(np.int64)
    row = np.floor((df["y"].to_numpy() - y0) / dy).astype(np.int64)
    ok = (col >= 0) & (col < w) & (row >= 0) & (row < h)
    col, row = col[ok], row[ok]

    sum_t = np.zeros((h, w), dtype=np.float64)
    sum_h = np.zeros((h, w), dtype=np.float64)
    cnt = np.zeros((h, w), dtype=np.int32)
    np.add.at(sum_t, (row, col), df["temperature"].to_numpy()[ok])
    np.add.at(sum_h, (row, col), df["humidity"].to_numpy()[ok])
    np.add.at(cnt, (row, col), 1)

    temp = np.full((h, w), np.nan)
    hum = np.full((h, w), np.nan)
    filled = cnt > 0
    temp[filled] = sum_t[filled] / cnt[filled]
    hum[filled] = sum_h[filled] / cnt[filled]
    temp[~filled] = np.nanmedian(temp)
    hum[~filled] = np.nanmedian(hum)

    np.save(C.OUT / "env_temperature.npy", temp.astype(np.float32))
    np.save(C.OUT / "env_humidity.npy", hum.astype(np.float32))
    np.save(C.OUT / "env_count.npy", cnt)
    return temp.astype(np.float32), hum.astype(np.float32), int(filled.sum())


def main():
    gamma, tir, em = C.load_cubes()
    z = C.build_observation(gamma, tir, em)
    mask = C.load_valid_mask()
    gt = C.load_clay_prior()

    temp, hum, n_cells = build_env_fields()
    print(f"gridded cells   : {n_cells} / {mask.size}  "
          f"T {np.nanmin(temp):.1f}-{np.nanmax(temp):.1f} C  "
          f"RH {np.nanmin(hum):.1f}-{np.nanmax(hum):.1f} %")

    q = C.quality_field(temp.shape, temperature=temp, humidity=hum)

    base = C.fuse(z, C.H_MATRIX)
    env = C.fuse(z, C.H_MATRIX, quality=q)
    hard = C.fuse(z, C.H_MATRIX, quality=q ** 1.5)

    def weights(res):
        w = res["weights"][:, None, None] * q.mean(axis=(0))[None]
        return {
            "gamma": float(w[:3].sum() / w.sum()),
            "tir": float(w[3:7].sum() / w.sum()),
            "em": float(w[7:].sum() / w.sum()),
        }

    rows = {}
    for name, res in (("baseline", base), ("environment", env), ("environment_strong", hard)):
        m = C.detection_metrics(res["x"], gt, mask=mask)
        rows[name] = {**m, "weights": weights(res) if name != "baseline" else
                      {"gamma": 0.3, "tir": 0.4, "em": 0.3},
                      "clay_mean": float(res["x"][C.TARGET][mask].mean())}
        print(f"{name:20s} R={m['recall']:.4f} P={m['precision']:.4f} "
              f"F1={m['f1']:.4f} clay={rows[name]['clay_mean']:.4f}")

    # dry / wet subsets
    dry = mask & (hum < 25)
    wet = mask & (hum > 40)
    subsets = {}
    for name, mm in (("dry_RH<25", dry), ("wet_RH>40", wet)):
        if mm.sum() == 0 or (gt[mm] > 0.55).sum() == 0:
            continue
        m = C.detection_metrics(env["x"], gt, mask=mm)
        subsets[name] = {**m, "pixels": int(mm.sum())}
        print(f"{name:20s} pixels={mm.sum():7d} R={m['recall']:.4f} P={m['precision']:.4f} "
              f"F1={m['f1']:.4f}")

    diff = env["x"][C.TARGET] - base["x"][C.TARGET]
    C.save_json(C.OUT / "environment.json", {
        "cells": n_cells,
        "temperature_range": [float(np.nanmin(temp)), float(np.nanmax(temp))],
        "humidity_range": [float(np.nanmin(hum)), float(np.nanmax(hum))],
        "scenarios": rows,
        "subsets": subsets,
        "clay_diff_mean": float(diff[mask].mean()),
        "clay_diff_absmean": float(np.abs(diff[mask]).mean()),
    })

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    for ax, arr, title, cmap in (
        (axes[0, 0], temp, "Temperature (C)", "inferno"),
        (axes[0, 1], hum, "Relative humidity (%)", "Blues"),
        (axes[0, 2], q[3:7].mean(axis=0), "TIR quality factor", "viridis"),
        (axes[1, 0], base["x"][C.TARGET], "Clay, baseline", "viridis"),
        (axes[1, 1], env["x"][C.TARGET], "Clay, environment-weighted", "viridis"),
        (axes[1, 2], diff, "Clay difference (env - base)", "RdBu_r"),
    ):
        im = ax.imshow(arr, cmap=cmap)
        ax.set_title(title)
        ax.axis("off")
        plt.colorbar(im, ax=ax, fraction=0.046)
    plt.tight_layout()
    plt.savefig(C.OUT / "environment.png", dpi=300)
    plt.close()
    print("saved           : environment.json / environment.png")


if __name__ == "__main__":
    main()

