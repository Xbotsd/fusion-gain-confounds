"""Repeat the 2-D fusion over N noise realisations and average the outputs.

This is the "multiple runs, then average" check:
  * N = 10 independent 1 % channel-noise realisations;
  * per-run metrics (clay, recall, precision, F1);
  * mean/std/95 % CI of the metrics;
  * pixel-wise mean and std of the abundance cube.

Writes processed/repeats.json, repeat_mean_abundance.npy,
repeat_std_abundance.npy.
"""
from __future__ import annotations

import time

import numpy as np

import common as C

N_RUNS = 10
NOISE_FRAC = 0.01


def main():
    gamma, tir, em = C.load_cubes()
    z = C.build_observation(gamma, tir, em)
    mask = C.load_valid_mask()
    gt = C.load_clay_prior()
    truth = np.load(C.PROC / "truth_abundance.npy")

    base = C.fuse(z, C.H_MATRIX)
    base_m = C.detection_metrics(base["x"], gt, mask=mask)
    base_r = C.recovery_metrics(base["x"], truth, mask=mask)["Clay"]

    sigma = z.std(axis=(1, 2), keepdims=True) + 1e-6
    acc = np.zeros((C.N_MIN,) + z.shape[1:], dtype=np.float64)
    acc2 = np.zeros_like(acc)
    runs = []
    t0 = time.time()

    for seed in range(N_RUNS):
        rng = np.random.default_rng(2024 + seed)
        zz = z + rng.normal(0.0, NOISE_FRAC * sigma, z.shape).astype(np.float32)
        res = C.fuse(zz.astype(np.float32), C.H_MATRIX)
        m = C.detection_metrics(res["x"], gt, mask=mask)
        r = C.recovery_metrics(res["x"], truth, mask=mask)["Clay"]
        runs.append({"seed": seed, "noise_frac": NOISE_FRAC, **m,
                     "rmse_truth": r["rmse"], "r_truth": r["r"]})
        acc += res["x"]
        acc2 += res["x"].astype(np.float64) ** 2
        print(f"  run {seed+1:2d}/{N_RUNS}: clay={m['clay_mean']:.4f} "
              f"R={m['recall']:.4f} F1={m['f1']:.4f}")

    mean_map = (acc / N_RUNS).astype(np.float32)
    var_map = np.maximum(acc2 / N_RUNS - (acc / N_RUNS) ** 2, 0.0)
    std_map = np.sqrt(var_map).astype(np.float32)
    np.save(C.PROC / "repeat_mean_abundance.npy", mean_map)
    np.save(C.PROC / "repeat_std_abundance.npy", std_map)

    def stat(key):
        v = np.array([r[key] for r in runs], dtype=float)
        return {
            "mean": float(v.mean()),
            "std": float(v.std(ddof=1)),
            "ci95": [float(v.mean() - 1.96 * v.std(ddof=1) / np.sqrt(len(v))),
                     float(v.mean() + 1.96 * v.std(ddof=1) / np.sqrt(len(v)))],
            "min": float(v.min()),
            "max": float(v.max()),
        }

    stats = {k: stat(k) for k in ("clay_mean", "recall", "precision", "f1",
                                  "rmse_truth", "r_truth")}
    mean_vs_base = {
        "clay_mean": float(mean_map[C.TARGET][mask].mean()),
        "delta_clay_vs_base": float(mean_map[C.TARGET][mask].mean() - base_m["clay_mean"]),
        "mean_map_finite_fraction": float(np.isfinite(mean_map[:, mask]).mean()),
        "mean_pixel_std_clay": float(std_map[C.TARGET][mask].mean()),
    }

    C.save_json(C.PROC / "repeats.json", {
        "n_runs": N_RUNS,
        "noise_frac": NOISE_FRAC,
        "runtime_s": time.time() - t0,
        "baseline": {"metrics": base_m, "rmse_truth": base_r["rmse"],
                     "r_truth": base_r["r"]},
        "runs": runs,
        "stats": stats,
        "mean_map": mean_vs_base,
    })

    print(f"\nmean recall : {stats['recall']['mean']:.4f} +/- {stats['recall']['std']:.5f}")
    print(f"mean F1     : {stats['f1']['mean']:.4f} +/- {stats['f1']['std']:.5f}")
    print(f"mean clay   : {stats['clay_mean']['mean']:.4f} +/- {stats['clay_mean']['std']:.5f}")
    print(f"runtime     : {time.time()-t0:.1f} s")
    print("saved       : repeats.json / repeat_mean_abundance.npy / repeat_std_abundance.npy")


if __name__ == "__main__":
    main()
