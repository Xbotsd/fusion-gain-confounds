"""Physically structured response-matrix perturbations.

Replaces the iid +/-30 % H test with perturbations that have a physical meaning:
modality gain, clay K/eTh signature, EM clay response, and a log10 clay-only EM
model.  Reports F1/AP/clay/gradient for each variant.

Writes processed/structured_perturbation.json/csv/png.
"""
from __future__ import annotations

import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common as C


def variants(H):
    out = {"baseline": (H.copy(), False)}
    for name, rows, factor in (
        ("gamma x0.8", slice(0, 3), 0.8), ("gamma x1.2", slice(0, 3), 1.2),
        ("TIR x0.8", slice(3, 7), 0.8), ("TIR x1.2", slice(3, 7), 1.2),
        ("EM x0.8", slice(7, 10), 0.8), ("EM x1.2", slice(7, 10), 1.2),
    ):
        h = H.copy()
        h[rows] *= factor
        out[name] = (h, False)
    for name, col, factor in (
        ("clay K x0.8", 0, 0.8), ("clay K x1.2", 0, 1.2),
        ("clay eTh x0.8", 2, 0.8), ("clay eTh x1.2", 2, 1.2),
        ("EM clay x0.5", 7, 0.5), ("EM clay x2.0", 7, 2.0),
    ):
        h = H.copy()
        if col == 0 or col == 2:
            h[col, C.TARGET] *= factor
        else:
            h[7:, C.TARGET] *= factor
        out[name] = (h, False)
    hlog = H.copy()
    hlog[7:] = 0.0
    hlog[7:, C.TARGET] = [0.90, 0.86, 0.36]
    out["EM log10 clay-only"] = (hlog, True)
    return out


def main():
    gamma, tir, em = C.load_cubes()
    z = C.build_observation(gamma, tir, em)
    mask = C.load_valid_mask()
    gt = C.load_clay_prior() > 0.55
    zlog = z.copy()
    zlog[7:] = np.log10(np.clip(zlog[7:], 1.0, 1e5)).astype(np.float32)

    rows = []
    for name, (H, use_log) in variants(C.H_MATRIX).items():
        res = C.fuse(zlog if use_log else z, H)
        m = C.detection_metrics(res["x"], gt, mask=mask)
        rows.append({"variant": name, "clay": m["clay_mean"],
                     "recall": m["recall"], "precision": m["precision"],
                     "f1": m["f1"], "gradient": C.spatial_gradient(res["x"])})
        print(f"{name:20s} clay={m['clay_mean']:.4f} R={m['recall']:.4f} "
              f"F1={m['f1']:.4f} grad={rows[-1]['gradient']:.5f}")

    C.save_json(C.PROC / "structured_perturbation.json", rows)
    with open(C.PROC / "structured_perturbation.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    base = rows[0]["f1"]
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.bar([r["variant"] for r in rows], [r["f1"] for r in rows],
           color="#1f77b4", alpha=0.85)
    ax.axhline(base, color="red", ls="--", label=f"baseline {base:.3f}")
    ax.set_ylabel("F1")
    ax.set_title("Physically structured H perturbations")
    ax.tick_params(axis="x", rotation=35)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(C.PROC / "structured_perturbation.png", dpi=300)
    plt.close()
    print("saved structured_perturbation.json/csv/png")


if __name__ == "__main__":
    main()

