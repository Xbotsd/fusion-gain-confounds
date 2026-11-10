"""Calibrate the forward-filter variance against the clay_prior proxy.

For clay, error = estimated clay - clay_prior and sigma = sqrt(P_clay).
Reports 68/95 % coverage, calibration error, a reliability curve and the
variance-scaling factor that matches the empirical squared error.

Pass --emfix to calibrate the corrected-EM fusion (log10 + clay-only EM);
the corrected x/P are recomputed in-memory and outputs use the _emfix suffix.

Writes processed/calibration.json and processed/calibration.png
(calibration_emfix.* with --emfix).
"""
from __future__ import annotations

import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common as C

EM_FIX = "--emfix" in sys.argv
SUFFIX = "_emfix" if EM_FIX else ""


def main():
    x = np.load(C.OUT / "kf_main_abundance.npy")
    P = np.load(C.OUT / "kf_main_uncertainty.npy")
    mask = C.load_analysis_mask()
    gt = C.load_clay_prior()

    err = (x[C.TARGET] - gt)[mask].astype(np.float64)
    var = P[C.TARGET][mask].astype(np.float64)
    sig = np.sqrt(np.maximum(var, 1e-12))

    out = {"n": int(err.size), "bias": float(err.mean()),
           "rmse": float(np.sqrt(np.mean(err ** 2))),
           "mean_sigma": float(sig.mean())}
    for z, name in ((1.0, "68"), (1.96, "95")):
        cov = float(np.mean(np.abs(err) <= z * sig))
        out[f"coverage_{name}"] = cov
        out[f"calibration_error_{name}"] = abs(cov - (0.68 if name == "68" else 0.95))

    # variance scaling: s = mean(err^2 / var)
    s = float(np.mean(err ** 2 / np.maximum(var, 1e-12)))
    out["variance_scale"] = s
    sig2 = np.sqrt(np.maximum(var * s, 1e-12))
    for z, name in ((1.0, "68"), (1.96, "95")):
        cov = float(np.mean(np.abs(err) <= z * sig2))
        out[f"coverage_{name}_scaled"] = cov
        out[f"calibration_error_{name}_scaled"] = abs(cov - (0.68 if name == "68" else 0.95))

    # reliability bins
    order = np.argsort(sig)
    bins = np.array_split(order, 10)
    rel = []
    for b in bins:
        rel.append({"mean_sigma": float(sig[b].mean()),
                    "rmse": float(np.sqrt(np.mean(err[b] ** 2))),
                    "n": int(b.size)})
    out["reliability"] = rel

    C.save_json(C.PROC / ("calibration" + SUFFIX + ".json"), out)
    with open(C.PROC / ("calibration" + SUFFIX + ".csv"), "w", encoding="utf-8") as f:
        f.write("bin,mean_sigma,rmse,n\n")
        for i, r in enumerate(rel):
            f.write(f"{i},{r['mean_sigma']:.6f},{r['rmse']:.6f},{r['n']}\n")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].scatter(sig[::50], np.abs(err[::50]), s=2, alpha=0.2)
    lim = np.percentile(sig, 99)
    axes[0].plot([0, lim], [0, lim], "r--", label="1:1")
    axes[0].set_xlabel("sqrt(P_clay)")
    axes[0].set_ylabel("|error|")
    axes[0].set_title("(a) Error vs predicted sigma")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    axes[1].plot([r["mean_sigma"] for r in rel], [r["rmse"] for r in rel], "o-")
    axes[1].plot([r["mean_sigma"] for r in rel], [r["mean_sigma"] for r in rel], "r--")
    axes[1].set_xlabel("mean predicted sigma")
    axes[1].set_ylabel("empirical RMSE")
    axes[1].set_title("(b) Reliability")
    axes[1].grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(C.PROC / ("calibration" + SUFFIX + ".png"), dpi=300)
    plt.close()

    print(json.dumps(out, indent=2))
    print(f"saved: calibration{SUFFIX}.json / calibration{SUFFIX}.csv / calibration{SUFFIX}.png")


if __name__ == "__main__":
    main()

