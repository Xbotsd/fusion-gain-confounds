"""Corrected-EM model: log10 resistivity with clay-only response.

The legacy EM row uses raw ohm.m and gives all five minerals a response.  This
script tests the physically motivated alternative: z_EM = log10(rho), and H_EM
has a clay-only response.  It compares the corrected model with the legacy
fusion and the strongest baselines, and runs a spatial block bootstrap.
"""
from __future__ import annotations

import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common as C
from run_advantage import methods, pr_ap, coherence


def metrics(x, gt, mask):
    m = C.detection_metrics(x, gt, mask=mask)
    ap, _, _ = pr_ap(x, gt, mask)
    coh = coherence(x, gt, mask)
    return {**m, "ap": ap, **coh, "gradient": C.spatial_gradient(x)}


def main():
    gamma, tir, em = C.load_cubes()
    z_raw = C.build_observation(gamma, tir, em)
    z, Hfix = C.load_emfix_inputs()
    mask = C.load_valid_mask()
    gt = C.load_clay_prior() > 0.55

    xs = methods(z_raw, C.H_MATRIX)
    xs["EM-fix WLS"] = C.fuse(z, Hfix, kalman=False)["x"]
    xs["EM-fix Kalman"] = C.fuse(z, Hfix)["x"]
    names = ["Independent", "GLS / Bayesian", "WLS + Kalman",
             "EM-fix WLS", "EM-fix Kalman"]
    rows = []
    pred = {}
    for n in names:
        m = metrics(xs[n], gt, mask)
        rows.append({"method": n, **m})
        pred[n] = ((xs[n][C.TARGET] > 0.25) & C.topk_mask(xs[n], 2)[C.TARGET] & mask)
        print(f"{n:16s} F1={m['f1']:.4f} AP={m['ap']:.4f} "
              f"R={m['recall']:.4f} P={m['precision']:.4f} "
              f"comp={m['components']} grad={m['gradient']:.5f}")

    # block bootstrap EM-fix Kalman vs Independent
    h, w = mask.shape
    bid = (np.arange(h)[:, None] // 128) * ((w + 127) // 128) + (np.arange(w)[None, :] // 128)
    blocks = np.unique(bid[mask])
    rng = np.random.default_rng(2024)
    reps = {n: [] for n in ("Independent", "EM-fix Kalman")}
    for i in range(200):
        pick = rng.choice(blocks, size=len(blocks), replace=True)
        mm = np.isin(bid, pick) & mask
        for n in reps:
            p = pred[n][mm]
            y = gt[mm]
            tp = np.sum(p & y); fp = np.sum(p & ~y); fn = np.sum(~p & y)
            reps[n].append(2 * tp / max(2 * tp + fp + fn, 1))
    base = np.array(reps["Independent"]); fix = np.array(reps["EM-fix Kalman"])
    d = fix - base
    boot = {
        "independent": {"mean": float(base.mean()),
                        "ci95": [float(np.percentile(base, 2.5)),
                                 float(np.percentile(base, 97.5))]},
        "em_fix": {"mean": float(fix.mean()),
                   "ci95": [float(np.percentile(fix, 2.5)),
                            float(np.percentile(fix, 97.5))]},
        "delta": {"mean": float(d.mean()),
                  "ci95": [float(np.percentile(d, 2.5)),
                           float(np.percentile(d, 97.5))],
                  "p_better": float(np.mean(d > 0))},
    }
    C.save_json(C.PROC / "em_fix.json", {
        "H_em_rows": Hfix[7:].tolist(),
        "rows": rows,
        "bootstrap": boot,
        "note": "EM uses log10(rho); H_EM is clay-only. Main data are unchanged.",
    })
    with open(C.PROC / "em_fix.csv", "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=list(rows[0]))
        wri.writeheader()
        wri.writerows(rows)

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    axes[0].bar([r["method"] for r in rows], [r["f1"] for r in rows],
                color="#2ca02c", alpha=0.85)
    axes[0].set_ylabel("F1")
    axes[0].set_title("(a) F1: legacy vs corrected EM")
    axes[0].tick_params(axis="x", rotation=25)
    axes[0].grid(axis="y", alpha=0.3)
    axes[1].bar([r["method"] for r in rows], [r["components"] for r in rows],
                color="#1f77b4", alpha=0.85)
    axes[1].set_ylabel("Connected components")
    axes[1].set_title("(b) Map fragmentation")
    axes[1].tick_params(axis="x", rotation=25)
    axes[1].grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(C.PROC / "em_fix.png", dpi=300)
    plt.close()

    print("bootstrap:", boot)
    print("saved em_fix.json/csv/png")


if __name__ == "__main__":
    main()

