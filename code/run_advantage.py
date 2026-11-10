"""Ablation and comparison to locate the actual advantage (if any).

Experiments
  1. component ablation: WLS only vs WLS+Kalman; Q/R sweep
  2. method comparison: independent, simple average, fixed weight, PCA, GLS,
     WLS-only, WLS+Kalman
  3. metrics beyond fixed-threshold F1: average precision (AP), precision at
     matched prevalence, spatial-tolerance recall/precision, runtime
  4. noise robustness: 5 % and 10 % channel noise; F1/AP drop

Writes processed/advantage.json, advantage.csv, advantage.png.
"""
from __future__ import annotations

import csv
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import binary_dilation, label

import common as C


def apply_G(z_sub, G):
    m, h, w = z_sub.shape
    x = G @ z_sub.reshape(m, -1) + 1.0 / C.N_MIN
    return C.project_simplex(x).reshape(C.N_MIN, h, w)


def methods(z, H):
    zn = C.zscore(z)
    Hn = C.normalize_H(H)
    out = {}

    xg = apply_G(zn[:3], np.linalg.pinv(Hn[:3]))
    xt = apply_G(zn[3:7], np.linalg.pinv(Hn[3:7]))
    xe = apply_G(zn[7:], np.linalg.pinv(Hn[7:]))
    out["Independent"] = C.project_simplex((xg + xt + xe) / 3.0)

    out["Simple average"] = apply_G(zn, np.linalg.pinv(Hn))

    wfix = np.array([1, 1, 1, .5, .5, .5, .5, 2, 2, 2], dtype=np.float32)
    A = Hn.T @ (Hn * wfix[:, None]) + 0.1 * np.eye(C.N_MIN)
    out["Fixed weight"] = apply_G(zn, np.linalg.inv(A) @ (Hn.T * wfix[None, :]))

    flat = zn.reshape(10, -1)
    cov = np.cov(flat) + np.eye(10) * 1e-3
    eigval, eigvec = np.linalg.eigh(cov)
    P3 = eigvec[:, -3:]
    recon = (P3 @ (P3.T @ (flat - flat.mean(axis=1, keepdims=True)))
             + flat.mean(axis=1, keepdims=True)).reshape(zn.shape)
    out["PCA (3 comp.)"] = apply_G(recon, np.linalg.pinv(Hn))

    Si = np.linalg.inv(cov)
    G = np.linalg.inv(Hn.T @ Si @ Hn + 0.1 * np.eye(C.N_MIN)) @ Hn.T @ Si
    out["GLS / Bayesian"] = apply_G(zn, G)

    out["WLS only"] = C.fuse(z, H, kalman=False)["x"]
    out["WLS + Kalman"] = C.fuse(z, H)["x"]
    return out


def pr_ap(x, gt, mask):
    clay = x[C.TARGET]
    top = C.topk_mask(x, 2)[C.TARGET]
    score = np.where(top, clay, 0.0)
    s = score[mask]
    y = gt[mask].astype(bool)
    order = np.argsort(-s)
    y = y[order]
    tp = np.cumsum(y)
    fp = np.cumsum(~y)
    precision = tp / np.maximum(tp + fp, 1)
    recall = tp / max(y.sum(), 1)
    ap = float(np.sum(np.diff(np.concatenate([[0.0], recall])) * precision))
    return ap, s[order], y


def matched_precision(s, y, prev):
    thr = np.quantile(s, 1.0 - prev)
    pred = s >= thr
    tp = np.sum(pred & y)
    return float(tp / max(pred.sum(), 1)), float(tp / max(y.sum(), 1))


def tolerance(x, gt, mask, px):
    pred = (x[C.TARGET] > 0.25) & C.topk_mask(x, 2)[C.TARGET]
    pred = pred & mask
    g = gt & mask
    gd = binary_dilation(g, iterations=px) & mask
    tp = np.sum(pred & gd)
    fp = np.sum(pred & ~gd)
    fn = np.sum(~pred & g)
    return float(tp / max(tp + fn, 1)), float(tp / max(tp + fp, 1))


def coherence(x, gt, mask):
    pred = (x[C.TARGET] > 0.25) & C.topk_mask(x, 2)[C.TARGET] & mask
    lab, n = label(pred)
    sizes = np.bincount(lab.ravel())[1:] if n else np.array([0])
    fp = pred & ~gt & mask
    labf, nf = label(fp)
    sf = np.bincount(labf.ravel())[1:] if nf else np.array([0])
    return {
        "components": int(n),
        "mean_component": float(sizes.mean()),
        "largest_fraction": float(sizes.max() / max(sizes.sum(), 1)),
        "fp_components": int(nf),
        "mean_fp_component": float(sf.mean()),
    }


def main():
    gamma, tir, em = C.load_cubes()
    z = C.build_observation(gamma, tir, em)
    mask = C.load_valid_mask()
    gt = C.load_clay_prior() > 0.55
    prev = float(gt[mask].mean())

    rows = []
    curves = {}
    xs = methods(z, C.H_MATRIX)
    for name, x in xs.items():
        m = C.detection_metrics(x, gt, mask=mask)
        ap, s, y = pr_ap(x, gt, mask)
        mp, mr = matched_precision(s, y, prev)
        t1 = tolerance(x, gt, mask, 1)
        t2 = tolerance(x, gt, mask, 2)
        coh = coherence(x, gt, mask)
        row = {
            "method": name, "clay": m["clay_mean"], "gradient": C.spatial_gradient(x),
            "recall": m["recall"], "precision": m["precision"], "f1": m["f1"],
            "ap": ap, "matched_precision": mp, "matched_recall": mr,
            "tol1_recall": t1[0], "tol1_precision": t1[1],
            "tol2_recall": t2[0], "tol2_precision": t2[1],
            **coh,
        }
        rows.append(row)
        curves[name] = (s, y)
        print(f"{name:16s} F1={row['f1']:.4f} AP={ap:.4f} "
              f"mP={mp:.4f} tol1R={t1[0]:.4f} grad={row['gradient']:.5f} "
              f"comp={row['components']} mean={row['mean_component']:.0f} "
              f"fpcomp={row['fp_components']}")

    # Q/R sweep for WLS+Kalman
    sweep = []
    for Q in (0.001, 0.005, 0.02, 0.05):
        for R in (0.005, 0.02, 0.05):
            x = C.fuse(z, C.H_MATRIX, Q=Q, R_obs=R)["x"]
            m = C.detection_metrics(x, gt, mask=mask)
            ap, _, _ = pr_ap(x, gt, mask)
            sweep.append({"Q": Q, "R_obs": R, "f1": m["f1"], "ap": ap,
                          "gradient": C.spatial_gradient(x)})
    best = max(sweep, key=lambda r: r["f1"])
    print(f"best Q/R: Q={best['Q']} R={best['R_obs']} F1={best['f1']:.4f} AP={best['ap']:.4f}")

    # noise robustness
    noise_rows = []
    sigma = z.std(axis=(1, 2), keepdims=True) + 1e-6
    for frac in (0.05, 0.10):
        rng = np.random.default_rng(2024)
        zz = (z + rng.normal(0, frac * sigma, z.shape)).astype(np.float32)
        for name, x in methods(zz, C.H_MATRIX).items():
            m = C.detection_metrics(x, gt, mask=mask)
            ap, _, _ = pr_ap(x, gt, mask)
            base = next(r for r in rows if r["method"] == name)
            noise_rows.append({"noise": frac, "method": name, "f1": m["f1"],
                               "ap": ap, "d_f1": m["f1"] - base["f1"],
                               "d_ap": ap - base["ap"]})
            print(f"noise {frac:.0%} {name:16s} F1={m['f1']:.4f} "
                  f"dF1={m['f1']-base['f1']:+.4f} dAP={ap-base['ap']:+.4f}")

    C.save_json(C.PROC / "advantage.json", {
        "prevalence": prev,
        "methods": rows,
        "qr_sweep": sweep,
        "best_qr": best,
        "noise": noise_rows,
    })
    with open(C.PROC / "advantage.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    # figure: PR curves + F1/gradient scatter
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for name, (s, y) in curves.items():
        order = np.argsort(-s)
        yy = y[order]
        tp = np.cumsum(yy)
        fp = np.cumsum(~yy)
        rec = tp / max(tp[-1], 1)
        prec = tp / np.maximum(tp + fp, 1)
        axes[0].plot(rec, prec, label=f"{name} (AP={next(r['ap'] for r in rows if r['method']==name):.3f})")
    axes[0].set_xlabel("Recall")
    axes[0].set_ylabel("Precision")
    axes[0].set_title("(a) Precision-recall")
    axes[0].legend(fontsize=7)
    axes[0].grid(alpha=0.3)

    axes[1].scatter([r["gradient"] for r in rows], [r["f1"] for r in rows])
    for r in rows:
        axes[1].annotate(r["method"], (r["gradient"], r["f1"]), fontsize=7)
    axes[1].set_xlabel("Spatial gradient (lower = smoother)")
    axes[1].set_ylabel("F1")
    axes[1].set_title("(b) Accuracy vs smoothness")
    axes[1].grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(C.PROC / "advantage.png", dpi=300)
    plt.close()
    print("saved advantage.json / advantage.csv / advantage.png")


if __name__ == "__main__":
    main()

