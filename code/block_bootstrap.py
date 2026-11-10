"""Spatial block bootstrap for the F1 comparison.

Pixel-level bootstrap is invalid here because neighbouring pixels are strongly
autocorrelated. The measured integral scale of the clay fields is ~42-54 px
(2.1-2.7 km, see autocorr_sample_size.py), so blocks must be >= ~2*tau; we use
128 x 128 px (6.4 km) blocks with replacement (200 replicates) and recompute F1
for the main methods. Reports 95 % percentile intervals and the fraction of
replicates in which the proposed method beats a baseline.
"""
from __future__ import annotations

import csv

import numpy as np

import common as C
from run_advantage import methods

BLOCK = 128  # >= 2x integral scale (53 px); see autocorr.json


def f1_from_pred(pred, y):
    tp = np.sum(pred & y)
    fp = np.sum(pred & ~y)
    fn = np.sum(~pred & y)
    return float(2 * tp / max(2 * tp + fp + fn, 1))


def main():
    gamma, tir, em = C.load_cubes()
    z = C.build_observation(gamma, tir, em)
    mask = C.load_valid_mask()
    gt = C.load_clay_prior() > 0.55

    xs = methods(z, C.H_MATRIX)
    names = ["Independent", "Fixed weight", "GLS / Bayesian", "WLS only", "WLS + Kalman"]
    pred = {}
    for name in names:
        pred[name] = ((xs[name][C.TARGET] > 0.25)
                      & C.topk_mask(xs[name], 2)[C.TARGET] & mask)
    point = {n: f1_from_pred(pred[n][mask], gt[mask]) for n in names}

    h, w = mask.shape
    bh, bw = BLOCK, BLOCK
    bid = (np.arange(h)[:, None] // bh) * ((w + bw - 1) // bw) + (np.arange(w)[None, :] // bw)
    valid_blocks = np.unique(bid[mask])
    rng = np.random.default_rng(2024)
    n_rep = 200
    samples = {n: [] for n in names}
    for i in range(n_rep):
        pick = rng.choice(valid_blocks, size=len(valid_blocks), replace=True)
        m = np.isin(bid, pick) & mask
        for n in names:
            samples[n].append(f1_from_pred(pred[n][m], gt[m]))
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{n_rep}")

    out = {"n_rep": n_rep, "block": [bh, bw], "point": point, "methods": {}}
    for n in names:
        v = np.array(samples[n])
        out["methods"][n] = {
            "mean": float(v.mean()),
            "std": float(v.std(ddof=1)),
            "ci95": [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))],
        }
    base = np.array(samples["Independent"])
    ours = np.array(samples["WLS + Kalman"])
    d = ours - base
    out["delta_ours_minus_independent"] = {
        "mean": float(d.mean()),
        "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
        "p_ours_better": float(np.mean(d > 0)),
    }
    C.save_json(C.PROC / "bootstrap.json", out)

    with open(C.PROC / "bootstrap.csv", "w", newline="", encoding="utf-8") as f:
        wri = csv.writer(f)
        wri.writerow(["method", "point_f1", "boot_mean", "boot_std", "ci_low", "ci_high"])
        for n in names:
            r = out["methods"][n]
            wri.writerow([n, point[n], r["mean"], r["std"], r["ci95"][0], r["ci95"][1]])

    print("point F1:", {k: round(v, 4) for k, v in point.items()})
    for n in names:
        r = out["methods"][n]
        print(f"{n:16s} {r['mean']:.4f} [{r['ci95'][0]:.4f}, {r['ci95'][1]:.4f}]")
    print("delta ours-independent:", out["delta_ours_minus_independent"])
    print("saved bootstrap.json / bootstrap.csv")


if __name__ == "__main__":
    main()

