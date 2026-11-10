"""Published-method baselines on the MAIN (real ASTER) line.

Five published practices, scored with the same mask, metric and independent
geological target as every other number in the paper:

1. Ternary K-dominance (IAEA 2003 practice)
2. F-parameter  K * eU / eTh          (Gnojek & Prichystal 1985)
3. Low eTh/K ratio                    (Dickson & Scott 1997)
4. Spectral Angle Mapper on the REAL ASTER TIR bands (Kruse et al. 1993)
5. EM conductor index: -log10(rho) shallow (Fountain 1998)

References for the fusion/independent inversion are added for context.

Outputs: processed/published_baselines.json/csv/png
"""
from __future__ import annotations

import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common as C
from run_advantage import pr_ap

REFS = [
    ("Ternary K-dominance", "IAEA 2003"),
    ("F-parameter K*eU/eTh", "Gnojek & Prichystal 1985"),
    ("Low eTh/K", "Dickson & Scott 1997"),
    ("SAM on real ASTER TIR", "Kruse et al. 1993"),
    ("EM conductor index", "Fountain 1998"),
]


def norm01(a, mask):
    v = a[mask]
    lo, hi = np.nanpercentile(v, [2, 98])
    return np.clip((a - lo) / (hi - lo + 1e-9), 0, 1)


def main():
    gamma, _tir, em = C.load_cubes()
    real = C.fill_median(C.load_real_tir())
    mask = C.load_analysis_mask()
    gt = C.load_clay_prior() > 0.55
    sel, pos = C.load_geology_target(mask)
    k, u, th = (C.normalize_p2p98(gamma[i]) for i in range(3))

    scores = {}
    scores["Ternary K-dominance"] = norm01(k, mask)
    scores["F-parameter K*eU/eTh"] = norm01(k * (u + 1e-3) / (th + 1e-3), mask)
    scores["Low eTh/K"] = norm01(1.0 - th / (k + 1e-3), mask)

    # SAM between each pixel spectrum and the mean clay spectrum of the library
    lib = C.library_tir_rows(C.ASTER_CENTRES, C.ASTER_WIDTHS)
    clay_spec = lib[:, C.TARGET]
    denom = (np.linalg.norm(real, axis=0) * np.linalg.norm(clay_spec) + 1e-9)
    cos = np.tensordot(clay_spec, real, axes=(0, 0)) / denom
    scores["SAM on real ASTER TIR"] = norm01(np.clip(cos, 0, 1), mask)

    em_shallow = em[C.EM_LAYERS[0]]
    scores["EM conductor index"] = norm01(-np.log10(np.clip(em_shallow, 1, 1e5)), mask)

    rows = []
    for name, ref in REFS:
        s = scores[name]
        prev = float(gt[mask].mean())
        thr = np.quantile(s[mask], 1 - prev)
        pred = (s >= thr) & mask
        tp = np.sum(pred & gt & mask)
        fp = np.sum(pred & ~gt & mask)
        fn = np.sum(~pred & gt & mask)
        rec = tp / max(tp + fn, 1)
        prec = tp / max(tp + fp, 1)
        rows.append({"method": name, "reference": ref,
                     "f1_matched": float(2 * tp / max(2 * tp + fp + fn, 1)),
                     "precision_matched": float(prec), "recall_matched": float(rec),
                     "auc_geology": C.auc_score(s[sel], pos),
                     "ap": pr_ap(np.stack([s, s, s, s, s]), gt, mask)[0]})
        print(f"{name:24s} matchedF1 {rows[-1]['f1_matched']:.3f}  "
              f"geoAUC {rows[-1]['auc_geology']:.3f}")

    # reference rows from the estimator itself
    x = np.load(C.OUT / "kf_main_abundance.npy")
    for name, src in (("Independent inversion", None), ("WLS + Kalman (ours)", x)):
        if name.startswith("Independent"):
            base = C.load_json(C.OUT / "main_results.json")
            r = next(b for b in base["baselines"] if b["method"] == "Independent")
            rows.append({"method": name, "reference": "this work",
                         "f1_matched": r["f1"], "precision_matched": r["precision"],
                         "recall_matched": r["recall"], "auc_geology": r["geo_auc"],
                         "ap": r["ap"]})
        else:
            m = C.detection_metrics(x, gt, mask=mask)
            ap, _, _ = pr_ap(x, gt, mask)
            rows.append({"method": name, "reference": "this work",
                         "f1_matched": m["f1"], "precision_matched": m["precision"],
                         "recall_matched": m["recall"],
                         "auc_geology": C.geology_auc(x, sel, pos), "ap": ap})

    C.save_json(C.PROC / "published_baselines.json", {
        "rows": rows, "prevalence": float(gt[mask].mean()),
        "note": "Published indices are single-modality scores evaluated with the "
                "matched-prevalence decision rule; the fusion rows use the "
                "paper's estimator. SAM uses the REAL ASTER emissivity.",
    })
    with open(C.PROC / "published_baselines.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    fig, ax = plt.subplots(figsize=(10, 4.6))
    names = [r["method"] for r in rows]
    vals = [r["f1_matched"] for r in rows]
    colors = ["#1f77b4"] * len(REFS) + ["#7f7f7f", "#2ca02c"]
    ax.barh(names, vals, color=colors[:len(names)], alpha=0.85)
    for i, v in enumerate(vals):
        ax.text(v, i, f" {v:.3f}", va="center", fontsize=8)
    ax.set_xlabel("Matched-prevalence F1")
    ax.set_title("Published single-modality methods vs the fusion (real ASTER)")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(C.PROC / "published_baselines.png", dpi=300)
    plt.close()
    print("saved published_baselines.json/csv/png")


if __name__ == "__main__":
    main()
