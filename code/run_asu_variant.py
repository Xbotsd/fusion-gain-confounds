"""Build an ASU-endmember TIR variant and compare it with the USGS main run.

This does *not* overwrite the main cubes/results.  It answers the reviewer
question "where do the TIR endmembers come from?" by repeating the TIR synthesis
and the fusion/ablation with measured ASU emissivity spectra.

Inputs : raw/ASU_spectra/*.txt (written by fetch_asu_spectra.py)
Outputs: processed/asu_endmembers.npy, processed/tir_cube_asu.npy,
         processed/H_asu.npy, processed/fusion_asu.json,
         processed/ablation_asu.csv/json, processed/fig_asu_endmembers.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common as C

ASU_DIR = C.ROOT / "raw" / "ASU_spectra"
WAVELENGTHS = np.linspace(8.0, 14.0, 200)


def load_asu():
    out = {}
    for path in sorted(ASU_DIR.glob("*.txt")):
        mineral = path.stem.split("_")[0]
        if mineral not in C.MINERALS:
            continue
        wn, em = np.loadtxt(path, comments="#", unpack=True)
        wl = 10000.0 / wn
        mask = (wl >= 8.0) & (wl <= 14.0) & np.isfinite(em)
        if mask.sum() < 10:
            continue
        wl, em = wl[mask], em[mask]
        order = np.argsort(wl)
        spec = np.interp(WAVELENGTHS, wl[order], em[order])
        out[mineral] = np.clip(spec, 0.5, 1.0)
    missing = [m for m in C.MINERALS if m not in out]
    if missing:
        raise RuntimeError(f"missing ASU spectra: {missing}")
    return np.stack([out[m] for m in C.MINERALS], axis=1)  # (200, 5)


def main():
    endmembers = load_asu()
    np.save(C.PROC / "asu_endmembers.npy", endmembers)

    truth = np.load(C.PROC / "truth_abundance.npy")
    tir = np.zeros((200,) + truth.shape[1:], dtype=np.float32)
    for i in range(200):
        tir[i] = np.tensordot(endmembers[i], truth, axes=(0, 0))
    valid = C.load_valid_mask()
    tir[:, ~valid] = np.nan
    np.save(C.PROC / "tir_cube_asu.npy", tir)

    H = C.H_MATRIX.copy()
    H[3:7] = endmembers[list(C.TIR_BANDS)]
    np.save(C.PROC / "H_asu.npy", H)

    gamma, _, em = C.load_cubes()
    z = np.concatenate(
        [gamma, tir[list(C.TIR_BANDS)], em[list(C.EM_LAYERS)]], axis=0
    ).astype(np.float32)
    mask = C.load_valid_mask()
    gt = C.load_clay_prior()

    # full fusion
    res = C.fuse(z, H)
    m = C.detection_metrics(res["x"], gt, mask=mask)
    main = C.load_json(C.PROC / "fusion.json")["proxy"]
    C.save_json(C.PROC / "fusion_asu.json", {
        "endmember_source": "ASU Thermal Emission Spectral Library",
        "ids": {"Quartz": 479, "Feldspar": 468, "Clay": 571,
                "Calcite": 604, "Dolomite": 515},
        "proxy": m,
        "main_proxy": main,
        "delta_recall": m["recall"] - main["recall"],
        "delta_f1": m["f1"] - main["f1"],
        "runtime_s": None,
    })

    # ablation with ASU TIR
    rows = []
    for name, idx in {
        "gamma": [0, 1, 2],
        "gamma+tir": [0, 1, 2, 3, 4, 5, 6],
        "gamma+em": [0, 1, 2, 7, 8, 9],
        "all": list(range(10)),
    }.items():
        q = np.zeros(10, dtype=np.float32)
        q[idx] = 1.0
        r = C.fuse(z, H, channel_quality=q)
        mm = C.detection_metrics(r["x"], gt, mask=mask)
        rows.append({"config": name, "clay_mean": mm["clay_mean"],
                     "recall": mm["recall"], "precision": mm["precision"],
                     "f1": mm["f1"]})

    import csv
    with open(C.PROC / "ablation_asu.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    C.save_json(C.PROC / "ablation_asu.json", rows)

    # figure: endmembers
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for j, name in enumerate(C.MINERALS):
        axes[0].plot(WAVELENGTHS, endmembers[:, j], label=name)
    axes[0].set_xlabel("Wavelength (um)")
    axes[0].set_ylabel("Emissivity")
    axes[0].set_title("ASU endmembers (8-14 um)")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)

    axes[1].bar([r["config"] for r in rows], [r["f1"] for r in rows],                color="#1f77b4", alpha=0.85)
    axes[1].set_ylabel("F1")
    axes[1].set_title("Ablation with ASU endmembers")
    axes[1].grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(C.PROC / "fig_asu_endmembers.png", dpi=300)
    plt.close()

    print("ASU fusion :", {k: round(m[k], 4) for k in ("recall", "precision", "f1")})
    print("USGS fusion:", {k: round(main[k], 4) for k in ("recall", "precision", "f1")})
    print("ablation   :")
    for r in rows:
        print(f"  {r['config']:10s} clay={r['clay_mean']:.4f} "
              f"R={r['recall']:.4f} F1={r['f1']:.4f}")
    print("saved      : asu_endmembers.npy / tir_cube_asu.npy / H_asu.npy / "
          "fusion_asu.json / ablation_asu.* / fig_asu_endmembers.png")


if __name__ == "__main__":
    main()

