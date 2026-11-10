"""Threshold / top-k sensitivity for the main methods.

The benchmark uses clay > 0.25, top-2 and clay_prior > 0.55.  This script sweeps
the clay threshold (0.15-0.45), top-k (1-3) and the proxy threshold (0.45-0.65)
to show whether the comparison depends on those arbitrary choices.
"""
from __future__ import annotations

import csv
from itertools import product

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common as C
from run_advantage import methods


def f1(pred, gt):
    tp = np.sum(pred & gt)
    fp = np.sum(pred & ~gt)
    fn = np.sum(~pred & gt)
    return float(2 * tp / max(2 * tp + fp + fn, 1))


def main():
    gamma, tir, em = C.load_cubes()
    z = C.build_observation(gamma, tir, em)
    mask = C.load_valid_mask()
    clay_prior = C.load_clay_prior()
    xs = methods(z, C.H_MATRIX)
    zfix, Hfix = C.load_emfix_inputs()
    xs["EM-fix Kalman"] = C.fuse(zfix, Hfix)["x"]
    names = ["Independent", "GLS / Bayesian", "WLS + Kalman", "EM-fix Kalman"]
    tops = {k: C.topk_mask(xs["WLS + Kalman"], k) for k in (1, 2, 3)}

    rows = []
    for name, thr, k, gt_thr in product(names, [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45],
                                        (1, 2, 3), [0.45, 0.55, 0.65]):
        x = xs[name]
        # top-k is defined on each method's own abundance ranking
        top = C.topk_mask(x, k)[C.TARGET]
        pred = (x[C.TARGET] > thr) & top & mask
        gt = (clay_prior > gt_thr) & mask
        rows.append({"method": name, "thr": thr, "top_k": k,
                     "gt_thr": gt_thr, "f1": f1(pred, gt)})

    C.save_json(C.PROC / "threshold_sensitivity.json", rows)
    with open(C.PROC / "threshold_sensitivity.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    summary = {}
    for n in names:
        sub = [r for r in rows if r["method"] == n]
        best = max(sub, key=lambda r: r["f1"])
        default = next(r for r in sub if r["thr"] == 0.25 and r["top_k"] == 2 and r["gt_thr"] == 0.55)
        summary[n] = {"default": default["f1"], "best": best}
        print(f"{n:16s} default={default['f1']:.4f} best={best['f1']:.4f} "
              f"(thr={best['thr']}, k={best['top_k']}, gt={best['gt_thr']})")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for n in names:
        sub = [r for r in rows if r["method"] == n and r["top_k"] == 2 and r["gt_thr"] == 0.55]
        ax.plot([r["thr"] for r in sub], [r["f1"] for r in sub], "o-", label=n)
    ax.set_xlabel("Clay threshold")
    ax.set_ylabel("F1 (top-2, GT > 0.55)")
    ax.set_title("Threshold sensitivity")
    ax.grid(alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.savefig(C.PROC / "threshold_sensitivity.png", dpi=300)
    plt.close()
    C.save_json(C.PROC / "threshold_summary.json", summary)
    print("saved threshold_sensitivity.json/csv/png and threshold_summary.json")


if __name__ == "__main__":
    main()

