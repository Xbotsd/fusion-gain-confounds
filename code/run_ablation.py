"""Step 5 - modality ablation with one H matrix and one metric definition.

Configurations: gamma, gamma+TIR, gamma+EM, all.
Pass --emfix to run the ablation with the corrected EM model (log10
resistivity + clay-only response); outputs then use the _emfix suffix.

Outputs: ablation.csv, ablation.json, ablation.png (ablation_emfix.* with --emfix)
"""
import csv
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common as C

EM_FIX = "--emfix" in sys.argv
SUFFIX = "_emfix" if EM_FIX else ""

ROWS = {
    "gamma": [0, 1, 2],
    "gamma+tir": [0, 1, 2, 3, 4, 5, 6],
    "gamma+em": [0, 1, 2, 7, 8, 9],
    "all": list(range(10)),
}


def main():
    if EM_FIX:
        z, H = C.load_emfix_inputs()
    else:
        gamma, tir, em = C.load_cubes()
        z = C.build_observation(gamma, tir, em)
        H = C.H_MATRIX
    mask = C.load_valid_mask()
    gt = C.load_clay_prior()
    truth = np.load(C.OUT / "truth_abundance.npy")

    rows = []
    for name, idx in ROWS.items():
        active = np.zeros(10, dtype=np.float32)
        active[idx] = 1.0
        res = C.fuse(z, H, channel_quality=active)
        m = C.detection_metrics(res["x"], gt, mask=mask)
        rec = C.recovery_metrics(res["x"], truth, mask=mask)["Clay"]
        rows.append({
            "config": name,
            "modalities": len(idx),
            "clay_mean": float(res["x"][C.TARGET][mask].mean()),
            "gradient": C.spatial_gradient(res["x"]),
            "uncertainty": float(res["P"].mean()),
            "recall": m["recall"],
            "precision": m["precision"],
            "f1": m["f1"],
            "rmse_truth": rec["rmse"],
            "r_truth": rec["r"],
        })
        print(f"{name:10s} clay={rows[-1]['clay_mean']:.4f} grad={rows[-1]['gradient']:.5f} "
              f"R={m['recall']:.4f} P={m['precision']:.4f} F1={m['f1']:.4f} "
              f"RMSE={rec['rmse']:.4f} r={rec['r']:.3f}")

    import csv
    with open(C.OUT / ("ablation" + SUFFIX + ".csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    C.save_json(C.OUT / ("ablation" + SUFFIX + ".json"), rows)

    names = [r["config"] for r in rows]
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    for ax, key, label, color in (
        (axes[0], "clay_mean", "Clay mean abundance", "#2ca02c"),
        (axes[1], "f1", "F1 vs clay_prior proxy", "#1f77b4"),
        (axes[2], "gradient", "Spatial gradient (lower=smoother)", "#d62728"),
        (axes[3], "uncertainty", "Mean posterior variance", "#9467bd"),
    ):
        vals = [r[key] for r in rows]
        ax.bar(names, vals, color=color, alpha=0.85)
        ax.set_title(label)
        ax.grid(axis="y", alpha=0.3)
        for i, v in enumerate(vals):
            ax.text(i, v, f"{v:.3f}", ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    plt.savefig(C.OUT / ("ablation" + SUFFIX + ".png"), dpi=300)
    plt.close()
    print(f"saved           : ablation{SUFFIX}.csv / ablation{SUFFIX}.json / ablation{SUFFIX}.png")


if __name__ == "__main__":
    main()

