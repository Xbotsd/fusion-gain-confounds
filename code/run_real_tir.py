"""Ablation and fusion with the REAL ASTER TIR cube, against two controls.

Three branches, all on the same mask, metric and estimator:

1. `synthetic-handset` — the published pipeline: 4 synthetic splib07 bands with
   the hand-set TIR rows of `H`.  Reference for every earlier number.
2. `synthetic-library` — the same 4 synthetic bands, but the TIR rows of `H`
   are sampled from splib07 over those band passes.  This isolates the effect of
   how `H` is built.
3. `real-aster` — 5 ASTER L1T emissivity bands (2006-10-18, emissivity
   normalisation) with TIR rows sampled from the same library over the ASTER
   band passes.  This isolates the effect of real versus synthetic data
   (compare with branch 2).

EM stays synthetic in all three (no measured AEM exists at this site).

Outputs: processed/real_tir.json, real_tir.csv, real_tir.png
"""
from __future__ import annotations

import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common as C
from run_advantage import pr_ap

WL = np.linspace(8.0, 14.0, 200)          # the splib07 resampling grid
ASTER_C = np.array([8.291, 8.634, 9.075, 10.657, 11.289])
ASTER_W = np.array([0.350, 0.350, 0.350, 0.700, 0.700])
SYNTH_C = np.array(C.TIR_WAVELENGTHS, dtype=float)
SYNTH_W = np.full(SYNTH_C.size, 0.5)


def library_rows(centres, widths):
    """Emissivity per mineral averaged over each band pass."""
    rows = np.zeros((len(centres), C.N_MIN))
    for j, mineral in enumerate(C.MINERALS):
        spec = np.load(C.SPEC / f"{mineral}_TIR.npy").astype(np.float64)
        if spec.ndim > 1:
            spec = np.nanmean(spec, axis=0)
        for b, (c, w) in enumerate(zip(centres, widths)):
            sel = (WL >= c - w / 2) & (WL <= c + w / 2)
            rows[b, j] = float(np.nanmean(1.0 - spec[sel]))
    return rows


def main():
    gamma, tir_syn, em = C.load_cubes()
    tir_real = np.load(C.OUT / "tir_cube_real.npy")
    mask = C.load_valid_mask()
    gt = C.load_clay_prior() > 0.55
    em3 = em[list(C.EM_LAYERS)]

    H_syn_lib = library_rows(SYNTH_C, SYNTH_W)
    H_ast_lib = library_rows(ASTER_C, ASTER_W)
    print("ASTER TIR rows of H:")
    for b in range(5):
        print(f"  {ASTER_C[b]:6.3f} um  " +
              "  ".join(f"{m[:4]} {H_ast_lib[b, j]:.3f}"
                        for j, m in enumerate(C.MINERALS)))

    branches = []
    # 1. published pipeline
    branches.append(("synthetic-handset", np.concatenate(
        [gamma, tir_syn[list(C.TIR_BANDS)], em3]).astype(np.float32),
        C.H_MATRIX.copy(), C.TIR_BANDS))
    # 2. synthetic data, library-sampled H
    H2 = np.vstack([C.H_MATRIX[:3], H_syn_lib, C.H_MATRIX[7:]])
    branches.append(("synthetic-library", np.concatenate(
        [gamma, tir_syn[list(C.TIR_BANDS)], em3]).astype(np.float32),
        H2, C.TIR_BANDS))
    # 3. real ASTER data, library-sampled H
    H3 = np.vstack([C.H_MATRIX[:3], H_ast_lib, C.H_MATRIX[7:]])
    branches.append(("real-aster", np.concatenate(
        [gamma, np.nan_to_num(tir_real, nan=0.5), em3]).astype(np.float32),
        H3, [0, 1, 2, 3, 4]))

    rows = []
    for name, z, H_base, tir_idx in branches:
        n = z.shape[0]
        em_rows = list(range(3 + len(tir_idx), n))
        H_legacy = H_base.copy()
        H_fix = H_base.copy()
        H_fix[3 + len(tir_idx):] = 0.0
        H_fix[3 + len(tir_idx):, C.TARGET] = C.EM_FIX_BETA
        subsets = {
            "gamma": [0, 1, 2],
            "gamma+tir": [0, 1, 2] + [3 + i for i in range(len(tir_idx))],
            "gamma+em": [0, 1, 2] + em_rows,
            "all": list(range(n)),
        }
        for model, H in (("legacy", H_legacy), ("corrected", H_fix)):
            z_model = z if model == "legacy" else C.emfix_observation(z)
            for cfg, idx in subsets.items():
                active = np.zeros(n, dtype=np.float32)
                active[idx] = 1.0
                res = C.fuse(z_model, H, channel_quality=active)
                m = C.detection_metrics(res["x"], gt, mask=mask)
                ap, _, _ = pr_ap(res["x"], gt, mask)
                rows.append({"branch": name, "em_model": model, "config": cfg,
                             "f1": m["f1"], "recall": m["recall"],
                             "precision": m["precision"], "ap": ap,
                             "clay_mean": float(res["x"][C.TARGET][mask].mean())})
                print(f"{name:18s} {model:9s} {cfg:9s} F1={m['f1']:.4f} "
                      f"AP={ap:.4f} R={m['recall']:.4f} P={m['precision']:.4f}")

    C.save_json(C.PROC / "real_tir.json", {
        "tir_bands_um": ASTER_C.tolist(),
        "H_tir_aster": H_ast_lib.tolist(),
        "H_tir_library_4band": H_syn_lib.tolist(),
        "rows": rows,
        "note": "Real TIR = ASTER L1T 2006-10-18 emissivity normalisation "
                "(5 bands). EM is synthetic in every branch.",
    })
    with open(C.PROC / "real_tir.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    cfgs = ["gamma", "gamma+tir", "gamma+em", "all"]
    names = [b[0] for b in branches]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    for ax, model in zip(axes, ("legacy", "corrected")):
        for i, name in enumerate(names):
            vals = [next(r for r in rows if r["branch"] == name
                         and r["em_model"] == model and r["config"] == c)["f1"]
                    for c in cfgs]
            ax.bar(np.arange(4) + (i - 1) * 0.27, vals, 0.27, label=name)
        ax.set_xticks(range(4))
        ax.set_xticklabels(cfgs, rotation=12)
        ax.set_ylabel("F1")
        ax.set_title(f"{model} EM matrix")
        ax.grid(axis="y", alpha=0.3)
        ax.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(C.PROC / "real_tir.png", dpi=300)
    plt.close()
    print("saved real_tir.json/csv/png")


if __name__ == "__main__":
    main()
