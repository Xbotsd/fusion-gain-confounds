"""Experiment 1 — does fusion help on a target that is NOT gamma-derived?

Every other number in the paper is scored against `clay_prior`, which is built
from K and eTh.  Here the target is the USGS SIM 3206 surficial geology, which is
independent of both the radiometrics and the TIR data.

Expected ordering from the map: alluvium and felsic plutonic substrates carry
more clay (weathering, alteration of feldspar) than carbonate and sedimentary
substrates.  We measure how well each model configuration separates the two
pools (AUC), how much of the across-group variance it explains (Kruskal-Wallis),
and the effect size (Cohen's d).  No gamma information enters the label.

Outputs: processed/independent_target.json, independent_target.csv, .png
"""
from __future__ import annotations

import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import kruskal

import common as C
from run_advantage import pr_ap

HIGH = {"surficial/alluvium", "felsic plutonic"}
LOW = {"carbonate", "sedimentary"}


def auc(scores, positive):
    """Rank-based AUC (Mann-Whitney U / (n1 n0))."""
    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty(scores.size, dtype=np.float64)
    ranks[order] = np.arange(1, scores.size + 1, dtype=np.float64)
    n1 = int(positive.sum())
    n0 = int(scores.size - n1)
    if n1 == 0 or n0 == 0:
        return float("nan")
    return float((ranks[positive].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def main():
    gamma, tir_syn, em = C.load_cubes()
    tir_real = np.load(C.OUT / "tir_cube_real.npy")
    mask = C.load_valid_mask()
    sub = np.load(C.PROC / "geology_substrate.npy")
    groups = C.load_json(C.PROC / "independent_validation.json")["groups"]
    gid = {g: i + 1 for i, g in enumerate(groups)}
    high_ids = [gid[g] for g in HIGH if g in gid]
    low_ids = [gid[g] for g in LOW if g in gid]
    sel = np.isin(sub, high_ids) | np.isin(sub, low_ids)
    sel &= mask
    pos = np.isin(sub, high_ids)[sel]
    print(f"independent target: {int(sel.sum())} pixels, "
          f"{int(pos.sum())} in the high-clay pool")
    print("  high:", sorted(HIGH & set(groups)), " low:", sorted(LOW & set(groups)))

    wl = np.linspace(8.0, 14.0, 200)
    ast_c = np.array([8.291, 8.634, 9.075, 10.657, 11.289])
    ast_w = np.array([0.350, 0.350, 0.350, 0.700, 0.700])
    syn_c = np.array(C.TIR_WAVELENGTHS, dtype=float)
    syn_w = np.full(syn_c.size, 0.5)

    def rows(c, w):
        out = np.zeros((len(c), C.N_MIN))
        for j, m in enumerate(C.MINERALS):
            sp = np.load(C.SPEC / f"{m}_TIR.npy").astype(np.float64)
            if sp.ndim > 1:
                sp = np.nanmean(sp, axis=0)
            for b in range(len(c)):
                k = (wl >= c[b] - w[b] / 2) & (wl <= c[b] + w[b] / 2)
                out[b, j] = float(np.nanmean(1.0 - sp[k]))
        return out

    H_syn = np.vstack([C.H_MATRIX[:3], rows(syn_c, syn_w), C.H_MATRIX[7:]])
    H_ast = np.vstack([C.H_MATRIX[:3], rows(ast_c, ast_w), C.H_MATRIX[7:]])

    branches = {
        "synthetic-handset": (np.concatenate(
            [gamma, tir_syn[list(C.TIR_BANDS)], em[list(C.EM_LAYERS)]]).astype(np.float32),
            C.H_MATRIX),
        "real-aster": (np.concatenate(
            [gamma, np.nan_to_num(tir_real, nan=0.5),
             em[list(C.EM_LAYERS)]]).astype(np.float32), H_ast),
    }

    out_rows = []
    for bname, (z0, H0) in branches.items():
        n_tir = z0.shape[0] - 6
        H_fix = H0.copy()
        H_fix[3 + n_tir:] = 0.0
        H_fix[3 + n_tir:, C.TARGET] = C.EM_FIX_BETA
        for model, H in (("legacy", H0), ("corrected", H_fix)):
            z = z0 if model == "legacy" else C.emfix_observation(z0)
            subsets = {
                "gamma": [0, 1, 2],
                "gamma+tir": list(range(3 + n_tir)),
                "gamma+em": [0, 1, 2] + list(range(3 + n_tir, z.shape[0])),
                "all": list(range(z.shape[0])),
            }
            for cfg, idx in subsets.items():
                active = np.zeros(z.shape[0], dtype=np.float32)
                active[idx] = 1.0
                x = C.fuse(z, H, channel_quality=active)["x"][C.TARGET]
                s = x[sel]
                a = auc(s, pos)
                hi = s[pos]
                lo = s[~pos]
                d = ((hi.mean() - lo.mean())
                     / np.sqrt((hi.var() + lo.var()) / 2.0))
                samples = [x[mask & (sub == gid[g])].astype(np.float64)
                           for g in groups if (mask & (sub == gid[g])).sum() > 100]
                kw = kruskal(*samples)
                out_rows.append({
                    "branch": bname, "em_model": model, "config": cfg,
                    "auc": a, "cohens_d": float(d), "kruskal_H": float(kw.statistic),
                    "clay_high": float(hi.mean()), "clay_low": float(lo.mean()),
                })
                print(f"{bname:18s} {model:9s} {cfg:9s} AUC={a:.4f} "
                      f"d={d:+.3f} KW={kw.statistic:8.1f} "
                      f"clay {hi.mean():.3f} vs {lo.mean():.3f}")

    C.save_json(C.PROC / "independent_target.json", {
        "target": "USGS SIM 3206 substrate (independent of gamma and TIR)",
        "high_groups": sorted(HIGH & set(groups)),
        "low_groups": sorted(LOW & set(groups)),
        "n_pixels": int(sel.sum()), "n_high": int(pos.sum()),
        "rows": out_rows,
        "note": "AUC of clay abundance for the high-clay substrate pool vs the "
                "low-clay pool; labels never see gamma or TIR.",
    })
    with open(C.PROC / "independent_target.csv", "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0]))
        w.writeheader()
        w.writerows(out_rows)

    cfgs = ["gamma", "gamma+tir", "gamma+em", "all"]
    fig, ax = plt.subplots(figsize=(9, 4.4))
    xs = np.arange(len(cfgs))
    for i, (bname, color) in enumerate((("synthetic-handset", "#1f77b4"),
                                        ("real-aster", "#d62728"))):
        vals = [next(r["auc"] for r in out_rows
                     if r["branch"] == bname and r["em_model"] == "corrected"
                     and r["config"] == c) for c in cfgs]
        ax.bar(xs + (i - 0.5) * 0.36, vals, 0.36, label=bname, color=color)
        for x, v in zip(xs + (i - 0.5) * 0.36, vals):
            ax.text(x, v, f"{v:.3f}", ha="center", va="bottom", fontsize=8)
    ax.axhline(0.5, color="k", ls="--", lw=0.9)
    ax.set_xticks(xs)
    ax.set_xticklabels(cfgs)
    ax.set_ylabel("AUC vs independent geology")
    ax.set_title("Corrected EM: separation of high- vs low-clay substrates")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.savefig(C.PROC / "independent_target.png", dpi=300)
    plt.close()
    print("saved independent_target.json/csv/png")


if __name__ == "__main__":
    main()
