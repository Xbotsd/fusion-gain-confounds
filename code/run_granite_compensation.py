"""Granite interference compensation (the module that was never implemented).

Mechanism: in mapped granite terrain (SIM 3206 felsic plutonic + magnetic
smoothness, indicator G), the gamma channels' clay information is confounded by
the granite's own K/eTh chemistry. The compensation blends, per pixel, the
standard corrected-EM fusion with a gamma-free (TIR+EM only) fusion weighted by
G.

Outputs: processed/granite_compensation.json/csv/png.
"""
from __future__ import annotations

import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import kruskal

import common as C


def emfix_inputs():
    z, H, lay, mask = C.load_main("real", emfix=True); return z, H


def substrate_rows(x, substrate, mask, groups):
    rows = []
    for g in groups:
        gid = groups.index(g) + 1
        m = mask & (substrate == gid)
        if m.sum() < 100:
            continue
        rows.append({"substrate": g, "pixels": int(m.sum()),
                     "clay_mean": float(x[C.TARGET][m].mean())})
    rows.sort(key=lambda r: -r["clay_mean"])
    return rows


def main():
    z, H = emfix_inputs()
    mask = C.load_analysis_mask()
    gt = C.load_clay_prior() > 0.55
    substrate = np.load(C.PROC / "geology_substrate.npy")
    G = np.load(C.PROC / "granite_indicator.npy")
    groups = ["carbonate", "felsic plutonic", "mafic plutonic",
              "metasedimentary", "partly consolidated", "sedimentary",
              "surficial/alluvium", "volcanic"]
    felsic = (substrate == groups.index("felsic plutonic") + 1) & mask

    # three estimators
    x_full = C.fuse(z, H)["x"]                       # gamma + TIR + EM
    q = np.ones(z.shape[0], dtype=np.float32)
    q[:3] = 0.0                                      # gamma off
    x_nogamma = C.fuse(z, H, channel_quality=q)["x"]  # TIR + EM only
    x_comp = ((1.0 - G)[None] * x_full + G[None] * x_nogamma).astype(np.float32)
    x_comp = C.project_simplex(x_comp)

    results = {}
    for name, x in (("gamma+TIR+EM", x_full), ("TIR+EM (no gamma)", x_nogamma),
                    ("granite compensated", x_comp)):
        m = C.detection_metrics(x, gt, mask=mask)
        fel_clay = float(x[C.TARGET][felsic].mean())
        oth_clay = float(x[C.TARGET][mask & ~felsic].mean())
        results[name] = {
            "f1": m["f1"], "recall": m["recall"], "precision": m["precision"],
            "clay_mean": m["clay_mean"], "gradient": C.spatial_gradient(x),
            "clay_on_felsic": fel_clay, "clay_on_other": oth_clay,
            "felsic_excess": fel_clay - oth_clay,
        }
        print(f"{name:22s} F1={m['f1']:.4f} clay={m['clay_mean']:.4f} "
              f"felsic={fel_clay:.4f} other={oth_clay:.4f} "
              f"excess={fel_clay-oth_clay:+.4f}")

    # substrate ranking + Kruskal for compensated vs full
    sub = {}
    for name, x in (("gamma+TIR+EM", x_full), ("granite compensated", x_comp)):
        rows = substrate_rows(x, substrate, mask, groups)
        samples = [x[C.TARGET][mask & (substrate == groups.index(g) + 1)]
                   .astype(np.float64) for g in groups
                   if (mask & (substrate == groups.index(g) + 1)).sum() >= 100]
        kw = kruskal(*samples)
        sub[name] = {"rows": rows, "kruskal_H": float(kw.statistic),
                     "kruskal_p": float(kw.pvalue)}
        print(f"{name}: Kruskal H={kw.statistic:.0f} p={kw.pvalue:.2e} "
              f"felsic rank {[r['substrate'] for r in rows].index('felsic plutonic')+1}/8")

    C.save_json(C.PROC / "granite_compensation.json",
                {"results": results, "substrate": sub,
                 "indicator": "geology-primary felsic plutonic + TMI smoothness"})
    with open(C.PROC / "granite_compensation.csv", "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["estimator", "f1", "recall", "precision", "clay_mean",
                    "clay_on_felsic", "clay_on_other", "felsic_excess"])
        for k, v in results.items():
            w.writerow([k, v["f1"], v["recall"], v["precision"], v["clay_mean"],
                        v["clay_on_felsic"], v["clay_on_other"], v["felsic_excess"]])

    # figure
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
    for ax, (name, x) in zip(axes, (("gamma+TIR+EM", x_full),
                                    ("TIR+EM only", x_nogamma),
                                    ("granite compensated", x_comp))):
        im = ax.imshow(np.where(mask, x[C.TARGET], np.nan),
                       cmap="viridis", vmin=0, vmax=0.6)
        ax.set_title(f"{name}\nF1={results[name if name != 'TIR+EM only' else 'TIR+EM (no gamma)']['f1']:.3f} "
                     f"felsic clay={x[C.TARGET][felsic].mean():.3f}")
        ax.axis("off")
        plt.colorbar(im, ax=ax, fraction=0.04)
    plt.tight_layout()
    plt.savefig(C.PROC / "granite_compensation.png", dpi=300)
    plt.close()
    print("saved granite_compensation.json/csv/png")


if __name__ == "__main__":
    main()

