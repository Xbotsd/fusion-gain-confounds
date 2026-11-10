"""Identifiability of the clay estimate on the main line (real ASTER TIR).

Manuscript Section 5.  For each modality subset S of the real-ASTER layout and
for both EM models:

1. analytic covariance of the WLS estimate, mirroring `common.fuse` exactly
       G = (H^T W H + lambda I)^-1 H^T W,   Cov(x) = G Sigma G^T
   with Sigma the robust per-channel noise of the z-scored data, giving
   `var_clay(S)` and the gain index G(S -> S+m) = 1 - var_clay(S+m)/var_clay(S);
2. condition number of the column-normalised active matrix, number of
   equations versus unknowns, and the clay-column weight share per block;
3. the observed changes: F1 on the proxy, AUC on the independent geology.

The empirical F1 values must reproduce the main-line ablation exactly; that is
asserted (and cross-checked again in validate_pipeline.py).

Outputs: processed/identifiability.json, identifiability.csv, identifiability.png
"""
from __future__ import annotations

import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common as C

LAM = 0.1
ADDONS = {"tir": "gamma+tir", "em": "gamma+em", "both": "all"}


def analytic(H, active, sigma):
    """Clay variance and conditioning of the active sub-problem (as in fuse)."""
    rows = np.flatnonzero(active > 0)
    sub = H[rows]
    d = np.linalg.norm(sub, axis=0, keepdims=True)
    Hn = sub / np.where(d < 1e-12, 1.0, d)
    A = Hn.T @ Hn + LAM * np.eye(C.N_MIN)
    G = np.linalg.inv(A) @ Hn.T
    cov = (G * sigma[rows][None, :] ** 2) @ G.T
    sv = np.linalg.svd(Hn, compute_uv=False)
    return {"var_clay_pred": float(cov[C.TARGET, C.TARGET]),
            "kappa": float(sv[0] / sv[-1]) if sv[-1] > 1e-12 else float("inf"),
            "rank": int(np.sum(sv > 1e-8 * sv[0])),
            "n_equations": int(rows.size), "n_unknowns": C.N_MIN}


def clay_shares(H, lay):
    d = np.linalg.norm(H, axis=0, keepdims=True)
    col = (H / d)[:, C.TARGET] ** 2
    return {"gamma": float(col[lay.gamma].sum() / col.sum()),
            "tir": float(col[lay.tir].sum() / col.sum()),
            "em": float(col[lay.em].sum() / col.sum())}


def main():
    gt = C.load_clay_prior() > 0.55
    mask = C.load_analysis_mask()
    sel, pos = C.load_geology_target(mask)
    main_res = C.load_json(C.PROC / "main_results.json")
    ref = {(r["em_model"], r["config"]): r for r in main_res["ablation"]
           if r["branch"] == "real-aster"}

    out = {"lambda": LAM, "branch": "real-aster", "models": {}}
    rows_csv = []
    max_dev = 0.0
    for model, emfix in (("legacy", False), ("corrected", True)):
        z, H, lay, _ = C.load_main("real", emfix=emfix)
        sigma = C.noise_sigma(C.zscore(z))
        res = {"sigma": sigma.tolist(), "sets": {},
               "kappa_full": analytic(H, np.ones(lay.n), sigma)["kappa"],
               "clay_share": clay_shares(H, lay)}
        for cfg, idx in lay.subsets().items():
            act = lay.active(idx)
            a = analytic(H, act, sigma)
            x = C.fuse(z, H, channel_quality=act)["x"]
            m = C.detection_metrics(x, gt, mask=mask)
            geo = C.geology_auc(x, sel, pos)
            dev = abs(m["f1"] - ref[(model, cfg)]["f1"])
            max_dev = max(max_dev, dev)
            res["sets"][cfg] = {**a, "f1": m["f1"], "geo_auc": geo,
                                "f1_reproduction_dev": dev}
            rows_csv.append({"model": model, "set": cfg, **a,
                             "f1": m["f1"], "geo_auc": geo})
        gains = {}
        for addon, target in ADDONS.items():
            s0, s1 = res["sets"]["gamma"], res["sets"][target]
            gains[addon] = {"G": 1.0 - s1["var_clay_pred"] / s0["var_clay_pred"],
                            "d_f1": s1["f1"] - s0["f1"],
                            "d_geo_auc": s1["geo_auc"] - s0["geo_auc"]}
        res["gain"] = gains
        out["models"][model] = res
        print(f"--- {model}: kappa(full) {res['kappa_full']:.1f}  shares "
              + str({k: round(v, 3) for k, v in res["clay_share"].items()}))
        for cfg, d in res["sets"].items():
            print(f"    {cfg:9s} eq {d['n_equations']:2d}/5 rank {d['rank']} "
                  f"kappa {d['kappa']:8.1f} var {d['var_clay_pred']:.3e} "
                  f"F1 {d['f1']:.3f} geoAUC {d['geo_auc']:.3f}")
        for k, v in gains.items():
            print(f"    +{k:4s} G {v['G']:+.3f}  dF1 {v['d_f1']:+.3f}  "
                  f"dAUC {v['d_geo_auc']:+.3f}")

    out["f1_reproduction_max_dev"] = max_dev
    if max_dev > 1e-9:
        raise SystemExit(f"identifiability does not reproduce the ablation: {max_dev:.2e}")
    sign_f1, sign_geo = {}, {}
    for model, r in out["models"].items():
        for addon, v in r["gain"].items():
            sign_f1[f"{model}:{addon}"] = bool((v["G"] > 0) == (v["d_f1"] > 0))
            sign_geo[f"{model}:{addon}"] = bool((v["G"] > 0) == (v["d_geo_auc"] > 0))
    out["sign_agreement_f1"] = sign_f1
    out["sign_agreement_geo"] = sign_geo
    print(f"sign(G) == sign(dF1)  : {sum(sign_f1.values())}/{len(sign_f1)}")
    print(f"sign(G) == sign(dAUC) : {sum(sign_geo.values())}/{len(sign_geo)}")

    C.save_json(C.PROC / "identifiability.json", out)
    with open(C.PROC / "identifiability.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_csv[0]))
        w.writeheader()
        w.writerows(rows_csv)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    for ax, key, title in zip(axes, ("G", "d_f1", "d_geo_auc"),
                              ("(a) predicted G (clay variance)",
                               "(b) observed change in F1 (proxy)",
                               "(c) observed change in AUC (geology)")):
        for j, (model, color) in enumerate((("legacy", "#d62728"),
                                            ("corrected", "#2ca02c"))):
            vals = [out["models"][model]["gain"][a][key] for a in ADDONS]
            ax.bar(np.arange(3) + (j - 0.5) * 0.36, vals, 0.36, label=model, color=color)
        ax.axhline(0, color="k", lw=0.8)
        ax.set_xticks(range(3))
        ax.set_xticklabels([f"+{a}" for a in ADDONS])
        ax.set_title(title, fontsize=10)
        ax.grid(axis="y", alpha=0.3)
        ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(C.PROC / "identifiability.png", dpi=300)
    plt.close()
    print("saved identifiability.json/csv/png")


if __name__ == "__main__":
    main()
