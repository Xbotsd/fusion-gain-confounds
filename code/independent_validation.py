"""Independent geological check of the MAIN clay map (USGS SIM 3206).

Uses the real ASTER main-line abundance cube and the analysis mask.  Reports
clay by substrate class, a Kruskal-Wallis test across classes, the felsic >
carbonate one-sided test, and the AUC of the binary clay-bearing vs clay-poor
contrast (the same target used by run_main.py).

Outputs: processed/independent_validation.json/csv/png
"""
from __future__ import annotations

import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import kruskal, mannwhitneyu

import common as C


def main():
    arr = np.load(C.PROC / "geology_substrate.npy")
    groups = C.load_geology_groups()
    gid = {g: i + 1 for i, g in enumerate(groups)}
    x = np.load(C.OUT / "kf_main_abundance.npy")
    mask = C.load_analysis_mask()
    sel, pos = C.load_geology_target(mask)

    rows = []
    for g in groups:
        m = mask & (arr == gid[g])
        if m.sum() < 100:
            continue
        rows.append({"substrate": g, "pixels": int(m.sum()),
                     "clay_mean": float(x[C.TARGET][m].mean()),
                     "quartz_mean": float(x[0][m].mean()),
                     "calcite_mean": float(x[3][m].mean())})
    rows.sort(key=lambda r: -r["clay_mean"])

    samples = [x[C.TARGET][mask & (arr == gid[g])].astype(np.float64)
               for g in groups if (mask & (arr == gid[g])).sum() >= 100]
    kw = kruskal(*samples)
    fel = x[C.TARGET][mask & (arr == gid["felsic plutonic"])].astype(np.float64)
    car = x[C.TARGET][mask & (arr == gid["carbonate"])].astype(np.float64)
    mw = mannwhitneyu(fel, car, alternative="greater")

    C.save_json(C.PROC / "independent_validation.json", {
        "source": "USGS SIM 3206 surficial geologic map, Ivanpah 30x60' quadrangle",
        "doi": "10.3133/sim3206", "groups": groups, "rows": rows,
        "abundance_source": "kf_main_abundance.npy (real ASTER main line)",
        "mask": "analysis mask (survey ∩ ASTER)", "mask_pixels": int(mask.sum()),
        "kruskal": {"H": float(kw.statistic), "p": float(kw.pvalue)},
        "felsic_vs_carbonate": {"n_felsic": int(fel.size),
                                "n_carbonate": int(car.size),
                                "p_greater": float(mw.pvalue),
                                "median_felsic": float(np.median(fel)),
                                "median_carbonate": float(np.median(car))},
        "binary_target": {"pixels": int(sel.sum()), "positive": int(pos.sum()),
                          "auc": C.geology_auc(x, sel, pos),
                          "definition": " + ".join(C.GEO_HIGH) + " vs "
                                        + " + ".join(C.GEO_LOW)},
        "note": "Substrate groups are qualitative; no alteration label is implied.",
    })
    with open(C.PROC / "independent_validation.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar([r["substrate"] for r in rows], [r["clay_mean"] for r in rows],
           color="#2ca02c", alpha=0.85)
    ax.set_ylabel("Mean clay abundance (real ASTER main line)")
    ax.set_title("Clay by independent geological substrate (USGS SIM 3206)")
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(C.PROC / "independent_validation.png", dpi=300)
    plt.close()

    for r in rows:
        print(f"{r['substrate']:22s} n={r['pixels']:8d} clay={r['clay_mean']:.4f}")
    print(f"Kruskal H={kw.statistic:.1f} p={kw.pvalue:.2e}; "
          f"felsic>carbonate p={mw.pvalue:.2e}; AUC {C.geology_auc(x, sel, pos):.3f}")
    print("saved independent_validation.json/csv/png")


if __name__ == "__main__":
    main()
