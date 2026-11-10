"""Audit the real data, the synthetic truth fields and the two H matrices.

Writes docs/data_audit.json and docs/model_audit.json.  No pipeline decision is
taken here; the script exists so that the provenance and the model discrepancy
are reproducible rather than asserted in prose.
"""
import hashlib
import json
import math
import struct
from pathlib import Path

import numpy as np
import pandas as pd
from osgeo import gdal

import common as C

CSV = C.ROOT / "Radiometric_Data.csv"
STEP = 3

H_A = np.array(
    [
        [0.5, 3.5, 1.0, 0.3, 0.3],
        [2.0, 1.0, 3.0, 2.0, 1.0],
        [1.0, 1.5, 4.0, 1.0, 0.5],
        [0.92, 0.85, 0.88, 0.80, 0.82],
        [0.95, 0.92, 0.90, 0.90, 0.88],
        [0.85, 0.90, 0.92, 0.95, 0.93],
        [0.90, 0.88, 0.90, 0.92, 0.94],
        [100.0, 200.0, 20.0, 500.0, 400.0],
        [80.0, 150.0, 15.0, 600.0, 500.0],
        [120.0, 180.0, 25.0, 800.0, 700.0],
    ],
    dtype=np.float64,
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def csv_stats():
    df = pd.read_csv(CSV, usecols=["x", "y", "lat", "lon", "date", "line",
                                   "flight_number", "kcorr", "thcorr", "ucorr"])
    x = df["x"].to_numpy()
    y = df["y"].to_numpy()
    dist = float(np.sum(np.hypot(np.diff(x), np.diff(y))) / 1000.0)
    dt = 1.0  # 1 Hz
    step = np.hypot(np.diff(x), np.diff(y))
    step = step[step < 200]  # drop line-to-line repositioning jumps
    return {
        "rows": int(len(df)),
        "dates": [str(df["date"].min()), str(df["date"].max())],
        "n_dates": int(df["date"].nunique()),
        "n_flights": int(df["flight_number"].nunique()),
        "n_lines": int(df["line"].nunique()),
        "bbox_lat": [float(df["lat"].min()), float(df["lat"].max())],
        "bbox_lon": [float(df["lon"].min()), float(df["lon"].max())],
        "trajectory_km": dist,
        "median_speed_mps": float(np.median(step)),
        "kcorr_median": float(df["kcorr"].median()),
        "thcorr_median": float(df["thcorr"].median()),
        "ucorr_median": float(df["ucorr"].median()),
    }


def grid_stats():
    ds = gdal.Open(str(C.RAW / "K.gxf"), gdal.GA_ReadOnly)
    gt = ds.GetGeoTransform()
    w, h = ds.RasterXSize, ds.RasterYSize
    srs = ds.GetSpatialRef()
    epsg = None
    if srs is not None:
        srs.AutoIdentifyEPSG()
        epsg = srs.GetAuthorityCode(None)
        wkt = srs.ExportToWkt()
        if epsg is None and "NAD83" in wkt and "UTM zone 11N" in wkt:
            epsg = "26911"
    ds = None
    gamma = C.load_gamma_planes()
    valid = np.isfinite(gamma).all(axis=0)
    med = [float(np.nanmedian(gamma[i][valid])) for i in range(3)]
    return {
        "shape": [h, w],
        "pixel_m": [abs(gt[1]), abs(gt[5])],
        "origin": [gt[0], gt[3]],
        "epsg": epsg,
        "valid_fraction": float(valid.mean()),
        "median": dict(zip(["K_pct", "eU_ppm", "eTh_ppm"], med)),
    }


def shp_stats(path: Path):
    with open(path, "rb") as f:
        f.seek(100)
        total = 0.0
        nfeat = npts = 0
        while True:
            head = f.read(8)
            if len(head) < 8:
                break
            _, length = struct.unpack(">ii", head)
            rec = f.read(length * 2)
            if not rec:
                break
            stype, = struct.unpack("<i", rec[0:4])
            if stype == 3:
                nparts, = struct.unpack("<i", rec[36:40])
                np_, = struct.unpack("<i", rec[40:44])
                off = 44 + 4 * nparts
                pts = [struct.unpack("<2d", rec[off + i * 16: off + i * 16 + 16])
                       for i in range(np_)]
                total += sum(math.hypot(pts[i + 1][0] - pts[i][0],
                                        pts[i + 1][1] - pts[i][1])
                             for i in range(np_ - 1))
                npts += np_
            elif stype == 1:
                npts += 1
            nfeat += 1
    return {"features": nfeat, "vertices": npts, "length_km": total / 1000.0}


def truth_consistency():
    prior = C.load_clay_prior()
    tir_clay = np.load(C.OUT / "truth_abundance.npy")[C.TARGET]
    m = np.isfinite(tir_clay)
    return {
        "corr_clay_prior_vs_tir_truth": float(np.corrcoef(prior[m], tir_clay[m])[0, 1]),
        "clay_prior_mean": float(prior[m].mean()),
        "tir_truth_mean": float(tir_clay[m].mean()),
        "note": "TIR truth is K+Th-derived; the alteration proxy is K-high/Th-low. "
                "They are different fields, so a single 'clay' target does not exist "
                "in the synthetic dataset.",
    }


def h_audit():
    gamma, tir, em = C.load_cubes()
    z, _, _, _ = C.load_main("real", emfix=True); z = z[:, ::STEP, ::STEP]
    gt = C.load_clay_prior()[::STEP, ::STEP]
    mask = C.load_analysis_mask()[::STEP, ::STEP]
    out = {}
    lay = C.layout("real")
    for tag, H in (("legacy_EM", lay.H), ("corrected_EM", lay.H_emfix())):
        for name, idx in (("gamma", [0, 1, 2]), ("all", list(range(z.shape[0])))):
            q = np.zeros(z.shape[0], dtype=np.float32)
            q[idx] = 1.0
            x = C.fuse(z, H, channel_quality=q)["x"]
            m = C.detection_metrics(x, gt, mask=mask)
            out[f"{tag}:{name}"] = {k: m[k] for k in ("clay_mean", "recall", "precision", "f1")}
    return out


def main():
    data = {
        "csv": csv_stats(),
        "grid": grid_stats(),
        "truth": truth_consistency(),
        "shapefiles": {
            p.name: shp_stats(p) for p in C.ROOT.glob("*.shp")
        },
        "checksums": {
            "K.gxf": sha256(C.RAW / "K.gxf"),
            "eU.gxf": sha256(C.RAW / "eU.gxf"),
            "eTh.gxf": sha256(C.RAW / "eTh.gxf"),
            "Radiometric_Data.csv": sha256(CSV),
        },
    }
    C.save_json(C.DOCS / "data_audit.json", data)

    models = {"H_audit": h_audit(), "truth": data["truth"]}
    C.save_json(C.DOCS / "model_audit.json", models)

    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("\nH audit")
    for k, v in models["H_audit"].items():
        print(f"  {k:28s} clay={v['clay_mean']:.4f} R={v['recall']:.4f} F1={v['f1']:.4f}")


if __name__ == "__main__":
    main()
