"""Main line of the paper: real ASTER TIR + real gamma + synthetic EM.

Every headline number of the manuscript comes from this module.  It runs the
experiments on three data branches, with one estimator, one mask and one
metric definition:

    real-aster         5 ASTER L1T emissivity bands (MAIN)
    synthetic-library  4 synthetic splib07 bands, library-sampled H rows
    synthetic-handset  4 synthetic bands, hand-set H rows (legacy reference)

and two EM models (legacy raw-resistivity rows, corrected log10 clay-only rows).

Two targets are reported side by side for every configuration:

    proxy    clay_prior > 0.55 (gamma-derived; F1, precision, recall, AP)
    geology  USGS SIM 3206 substrate contrast (independent; AUC)

All scoring uses the analysis mask = radiometric survey ∩ full ASTER coverage,
so the three branches are compared on identical pixels.

Experiments
-----------
A. ablation      gamma / gamma+TIR / gamma+EM / all, every branch x EM model
B. baselines     independent, simple average, fixed weight, PCA, GLS,
                 WLS only, WLS + Kalman (real-aster, corrected EM)
C. bootstrap     128-px block bootstrap (200 reps) of the main contrasts
D. repeats       10 runs with 1 % channel noise (main configuration)
E. calibration   forward-filter variance vs empirical error
F. autocorr      integral scale, design effect, N_eff for the main clay map

Outputs: processed/main_*.json/csv/png, processed/kf_main_abundance.npy
"""
from __future__ import annotations

import csv
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common as C
from run_advantage import coherence, pr_ap

BLOCK = 128
N_REP = 200
BRANCHES = ("real", "synthetic-library", "synthetic")
BRANCH_NAME = {"real": "real-aster", "synthetic-library": "synthetic-library",
               "synthetic": "synthetic-handset"}


# ------------------------------------------------------------------ helpers
def score(x, gt, mask, sel, pos):
    m = C.detection_metrics(x, gt, mask=mask)
    ap, _, _ = pr_ap(x, gt, mask)
    return {"f1": m["f1"], "recall": m["recall"], "precision": m["precision"],
            "iou": m["iou"], "ap": ap, "clay_mean": m["clay_mean"],
            "positive_rate": m["positive_rate"],
            "geo_auc": C.geology_auc(x, sel, pos)}


def apply_G(z_sub, G):
    m, h, w = z_sub.shape
    x = G @ z_sub.reshape(m, -1) + 1.0 / C.N_MIN
    return C.project_simplex(x).reshape(C.N_MIN, h, w)


def norm_rows(H, rows):
    sub = H[rows]
    d = np.linalg.norm(sub, axis=0, keepdims=True)
    return sub / np.where(d < 1e-12, 1.0, d)


def baselines(z, H, lay):
    """Generic baselines on the given layout (normalisation over used rows)."""
    zn = C.zscore(z)
    n = lay.n
    out = {}
    blocks = [lay.gamma, lay.tir, lay.em]
    parts = [apply_G(zn[b], np.linalg.pinv(norm_rows(H, b))) for b in blocks]
    out["Independent"] = C.project_simplex(sum(parts) / 3.0)

    Hn = norm_rows(H, list(range(n)))
    out["Simple average"] = apply_G(zn, np.linalg.pinv(Hn))

    wfix = np.ones(n, dtype=np.float32)
    wfix[lay.tir] = 0.5
    wfix[lay.em] = 2.0
    A = Hn.T @ (Hn * wfix[:, None]) + 0.1 * np.eye(C.N_MIN)
    out["Fixed weight"] = apply_G(zn, np.linalg.inv(A) @ (Hn.T * wfix[None, :]))

    flat = zn.reshape(n, -1)
    cov = np.cov(flat) + np.eye(n) * 1e-3
    _, vec = np.linalg.eigh(cov)
    P3 = vec[:, -3:]
    mu = flat.mean(axis=1, keepdims=True)
    recon = (P3 @ (P3.T @ (flat - mu)) + mu).reshape(zn.shape)
    out["PCA (3 comp.)"] = apply_G(recon, np.linalg.pinv(Hn))

    Si = np.linalg.inv(cov)
    G = np.linalg.inv(Hn.T @ Si @ Hn + 0.1 * np.eye(C.N_MIN)) @ Hn.T @ Si
    out["GLS / Bayesian"] = apply_G(zn, G)

    out["WLS only"] = C.fuse(z, H, kalman=False)["x"]
    out["WLS + Kalman"] = C.fuse(z, H)["x"]
    return out


# One bootstrap implementation for the whole project (common.paired_bootstrap)
BLOCK = C.BLOCK
N_REP = C.N_REP
block_ids = C.block_ids
pred_of = C.pred_of
paired_bootstrap = C.paired_bootstrap


def geo_bootstrap(xa, xb, sel, pos, mask, seed=2025):
    """Block bootstrap of geology AUC(b) - AUC(a)."""
    bid = block_ids(mask)[sel]
    sa = xa[C.TARGET][sel]
    sb = xb[C.TARGET][sel]
    blocks = np.unique(bid)
    idx_of = {b: np.flatnonzero(bid == b) for b in blocks}
    rng = np.random.default_rng(seed)
    d = []
    for _ in range(N_REP):
        pick = rng.choice(blocks, size=blocks.size, replace=True)
        ii = np.concatenate([idx_of[b] for b in pick])
        if pos[ii].all() or (~pos[ii]).all():
            continue
        d.append(C.auc_score(sb[ii], pos[ii]) - C.auc_score(sa[ii], pos[ii]))
    d = np.asarray(d)
    return {"delta_mean": float(d.mean()),
            "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
            "p_better": float(np.mean(d > 0)), "n_valid_reps": int(d.size)}


def integral_scale(field, mask, max_lag=80):
    f = np.where(mask, field, np.nanmean(field[mask])).astype(np.float64)
    f -= f.mean()
    F = np.fft.rfft2(f)
    ac = np.fft.irfft2(F * np.conj(F), s=f.shape)
    ac /= ac[0, 0] if ac[0, 0] != 0 else 1.0
    out = []
    for r in (ac[0, :max_lag].real, ac[:max_lag, 0].real):
        k = int(np.argmax(r <= 0)) if np.any(r <= 0) else len(r)
        out.append(float(np.sum(r[:k])))
    return out


# --------------------------------------------------------------------- main
def main():
    t0 = time.time()
    gt = C.load_clay_prior() > 0.55
    mask = C.load_analysis_mask()
    sel, pos = C.load_geology_target(mask)
    print(f"analysis mask {int(mask.sum()):,} px; geology target "
          f"{int(sel.sum()):,} px ({int(pos.sum()):,} clay-bearing)")

    # ---------------- A. ablation, every branch x EM model ------------------
    ablation = []
    maps = {}
    for kind in BRANCHES:
        for emfix in (False, True):
            z, H, lay, _ = C.load_main(kind, emfix=emfix)
            model = "corrected" if emfix else "legacy"
            for cfg, idx in lay.subsets().items():
                res = C.fuse(z, H, channel_quality=lay.active(idx))
                s = score(res["x"], gt, mask, sel, pos)
                ablation.append({"branch": BRANCH_NAME[kind], "em_model": model,
                                 "config": cfg, "n_channels": len(idx), **s})
                maps[(kind, model, cfg)] = res
                print(f"A {BRANCH_NAME[kind]:18s} {model:9s} {cfg:9s} "
                      f"F1={s['f1']:.4f} AP={s['ap']:.4f} geoAUC={s['geo_auc']:.4f}")

    main_res = maps[("real", "corrected", "all")]
    x_main = main_res["x"]
    np.save(C.OUT / "kf_main_abundance.npy", x_main)
    np.save(C.OUT / "kf_main_uncertainty.npy", main_res["P"])

    # ---------------- B. baselines on the main branch -----------------------
    z, H, lay, _ = C.load_main("real", emfix=True)
    base_rows = []
    base_maps = baselines(z, H, lay)
    for name, x in base_maps.items():
        s = score(x, gt, mask, sel, pos)
        coh = coherence(x, gt, mask)
        base_rows.append({"method": name, **s, "gradient": C.spatial_gradient(x),
                          "components": coh["components"],
                          "mean_component": coh["mean_component"]})
        print(f"B {name:16s} F1={s['f1']:.4f} AP={s['ap']:.4f} "
              f"geoAUC={s['geo_auc']:.4f} comp={coh['components']}")
    # legacy EM reference on the same branch and mask
    zl, Hl, layl, _ = C.load_main("real", emfix=False)
    xl = C.fuse(zl, Hl)["x"]
    sl = score(xl, gt, mask, sel, pos)
    coh = coherence(xl, gt, mask)
    base_rows.append({"method": "WLS + Kalman (legacy EM)", **sl,
                      "gradient": C.spatial_gradient(xl),
                      "components": coh["components"],
                      "mean_component": coh["mean_component"]})

    # ---------------- C. block bootstrap of the main contrasts --------------
    g_only = maps[("real", "corrected", "gamma")]["x"]
    g_tir = maps[("real", "corrected", "gamma+tir")]["x"]
    syn_all = maps[("synthetic", "corrected", "all")]["x"]
    syn_gtir = maps[("synthetic-library", "corrected", "gamma+tir")]["x"]
    contrasts = {
        "corrected_vs_legacy_EM (real, all)": paired_bootstrap(xl, x_main, gt, mask),
        "corrected_vs_independent (real)": paired_bootstrap(
            base_maps["Independent"], x_main, gt, mask),
        "gamma+TIR_vs_gamma (real)": paired_bootstrap(g_only, g_tir, gt, mask),
        "real_vs_synthetic gamma+TIR": paired_bootstrap(syn_gtir, g_tir, gt, mask),
        "real_vs_synthetic all": paired_bootstrap(syn_all, x_main, gt, mask),
    }
    geo_contrasts = {
        "gamma+TIR_vs_gamma (real)": geo_bootstrap(g_only, g_tir, sel, pos, mask),
        "all_vs_gamma (real)": geo_bootstrap(g_only, x_main, sel, pos, mask),
        "real_vs_synthetic gamma+TIR": geo_bootstrap(syn_gtir, g_tir, sel, pos, mask),
    }
    for k, v in contrasts.items():
        print(f"C F1  {k:38s} {v['delta_mean']:+.4f} "
              f"[{v['ci95'][0]:+.4f}, {v['ci95'][1]:+.4f}] p_better {v['p_better']:.2f}")
    for k, v in geo_contrasts.items():
        print(f"C AUC {k:38s} {v['delta_mean']:+.4f} "
              f"[{v['ci95'][0]:+.4f}, {v['ci95'][1]:+.4f}] p_better {v['p_better']:.2f}")

    # ---------------- D. repeats -------------------------------------------
    sigma = z.std(axis=(1, 2), keepdims=True) + 1e-6
    reps = []
    for seed in range(10):
        rng = np.random.default_rng(seed)
        zz = (z + rng.normal(0, 0.01 * sigma, z.shape)).astype(np.float32)
        reps.append(score(C.fuse(zz, H)["x"], gt, mask, sel, pos))
    rep_summary = {k: {"mean": float(np.mean([r[k] for r in reps])),
                       "std": float(np.std([r[k] for r in reps], ddof=1))}
                   for k in ("f1", "ap", "recall", "precision", "geo_auc", "clay_mean")}
    print("D repeats F1 %.5f +/- %.5f" % (rep_summary["f1"]["mean"], rep_summary["f1"]["std"]))

    # ---------------- E. calibration ----------------------------------------
    prior = C.load_clay_prior()
    err = (x_main[C.TARGET] - prior)[mask].astype(np.float64)
    var = main_res["P"][C.TARGET][mask].astype(np.float64)
    sig = np.sqrt(np.maximum(var, 1e-12))
    s_scale = float(np.mean(err ** 2 / np.maximum(var, 1e-12)))
    calib = {"bias": float(err.mean()), "rmse": float(np.sqrt(np.mean(err ** 2))),
             "coverage_68": float(np.mean(np.abs(err) <= sig)),
             "coverage_95": float(np.mean(np.abs(err) <= 1.96 * sig)),
             "variance_scale": s_scale,
             "coverage_68_scaled": float(np.mean(np.abs(err) <= sig * np.sqrt(s_scale))),
             "coverage_95_scaled": float(np.mean(np.abs(err) <= 1.96 * sig * np.sqrt(s_scale)))}
    print("E calibration cov68 %.3f cov95 %.3f scale %.2f" %
          (calib["coverage_68"], calib["coverage_95"], s_scale))

    # ---------------- F. pseudo-replication ---------------------------------
    tx, ty = integral_scale(x_main[C.TARGET], mask)
    de = (2 * tx + 1) * (2 * ty + 1)
    n_valid = int(mask.sum())
    autoc = {"integral_scale_px": [tx, ty], "integral_scale_m": [tx * 50, ty * 50],
             "design_effect": de, "n_valid": n_valid, "n_eff": n_valid / de,
             "block_px": BLOCK, "block_ge_2tau": BLOCK >= 2 * max(tx, ty)}
    print(f"F tau {tx:.1f}/{ty:.1f} px, N_eff {n_valid/de:.0f}, block OK {autoc['block_ge_2tau']}")

    # ---------------- outputs ------------------------------------------------
    tir_meta = C.load_json(C.PROC / "tir_real.json")
    C.save_json(C.OUT / "main_results.json", {
        "definition": {
            "mask": "radiometric survey ∩ full five-band ASTER coverage",
            "proxy_target": "clay_prior > 0.55 (gamma-derived)",
            "geology_target": "SIM 3206: " + " + ".join(C.GEO_HIGH) + " vs "
                              + " + ".join(C.GEO_LOW),
            "positive": "clay > 0.25 AND clay in top-2 minerals",
            "em": "synthetic in every branch (no measured AEM exists here)",
        },
        "mask_pixels": n_valid, "geology_pixels": int(sel.sum()),
        "geology_positive": int(pos.sum()),
        "tir_source": {k: tir_meta[k] for k in ("source", "date", "scene_files")},
        "H_tir_real": C.layout("real").H[3:8].tolist(),
        "ablation": ablation, "baselines": base_rows,
        "bootstrap_f1": contrasts, "bootstrap_geo_auc": geo_contrasts,
        "repeats": {"n": 10, "noise_frac": 0.01, "summary": rep_summary},
        "calibration": calib, "autocorr": autoc,
        "runtime_s": time.time() - t0,
    })
    with open(C.OUT / "main_ablation.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(ablation[0]))
        w.writeheader()
        w.writerows(ablation)
    with open(C.OUT / "main_baselines.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(base_rows[0]))
        w.writeheader()
        w.writerows(base_rows)

    # figure: F1 and geology AUC per configuration, corrected EM
    cfgs = ["gamma", "gamma+tir", "gamma+em", "all"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    for i, kind in enumerate(BRANCHES):
        name = BRANCH_NAME[kind]
        for ax, key in zip(axes, ("f1", "geo_auc")):
            vals = [next(r[key] for r in ablation if r["branch"] == name
                         and r["em_model"] == "corrected" and r["config"] == c)
                    for c in cfgs]
            ax.bar(np.arange(4) + (i - 1) * 0.27, vals, 0.27, label=name)
    axes[0].set_ylabel("F1 vs gamma-derived proxy")
    axes[0].set_title("(a) Proxy target")
    axes[1].set_ylabel("AUC vs SIM 3206 geology")
    axes[1].axhline(0.5, color="k", ls="--", lw=0.8)
    axes[1].set_title("(b) Independent geological target")
    for ax in axes:
        ax.set_xticks(range(4))
        ax.set_xticklabels(cfgs)
        ax.grid(axis="y", alpha=0.3)
        ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(C.OUT / "main_ablation.png", dpi=300)
    plt.close()

    fig, axes = plt.subplots(1, 3, figsize=(17, 6))
    for ax, (title, arr) in zip(axes, (
            ("Clay — real ASTER, corrected EM", x_main[C.TARGET]),
            ("Clay — synthetic TIR, corrected EM", syn_all[C.TARGET]),
            ("clay_prior (gamma-derived proxy)", prior))):
        im = ax.imshow(np.where(mask, arr, np.nan), cmap="viridis", vmin=0, vmax=0.7)
        ax.set_title(title, fontsize=10)
        ax.axis("off")
        plt.colorbar(im, ax=ax, fraction=0.046)
    plt.tight_layout()
    plt.savefig(C.OUT / "main_maps.png", dpi=300)
    plt.close()
    print(f"saved main_results.json, main_ablation/baselines.csv, main_*.png "
          f"({time.time()-t0:.0f} s)")


if __name__ == "__main__":
    main()
