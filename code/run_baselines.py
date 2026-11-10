"""Step 8 - baseline comparison under identical metrics.

Independent per-modality inversion, simple average, fixed weights, PCA fusion,
GLS/Bayesian fusion and the proposed WLS+Kalman estimator.
"""
import csv
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common as C


def apply_G(z_sub, G, block=400):
    m, h, w = z_sub.shape
    x = np.zeros((C.N_MIN, h, w), dtype=np.float32)
    for h0 in range(0, h, block):
        h1 = min(h0 + block, h)
        xx = G @ z_sub[:, h0:h1, :].reshape(m, -1) + 1.0 / C.N_MIN
        x[:, h0:h1, :] = C.project_simplex(xx).reshape(C.N_MIN, h1 - h0, w)
    return x


def wls_G(Hn, w, lam=0.1):
    A = Hn.T @ (Hn * w[:, None]) + lam * np.eye(C.N_MIN)
    return np.linalg.inv(A) @ (Hn.T * w[None, :])


def main():
    gamma, tir, em = C.load_cubes()
    z = C.build_observation(gamma, tir, em)
    zn = C.zscore(z)
    Hn = C.normalize_H(C.H_MATRIX)
    mask = C.load_valid_mask()
    gt = C.load_clay_prior()
    truth = np.load(C.OUT / "truth_abundance.npy")

    flat = zn.reshape(10, -1)
    cov = np.cov(flat) + np.eye(10) * 1e-3
    eigval, eigvec = np.linalg.eigh(cov)
    P3 = eigvec[:, -3:]
    recon = (P3 @ (P3.T @ (flat - flat.mean(axis=1, keepdims=True)))
             + flat.mean(axis=1, keepdims=True)).reshape(zn.shape)

    methods = {}

    # independent per-modality inversions, then average
    xg = apply_G(zn[:3], np.linalg.pinv(Hn[:3]))
    xt = apply_G(zn[3:7], np.linalg.pinv(Hn[3:7]))
    xe = apply_G(zn[7:], np.linalg.pinv(Hn[7:]))
    methods["Independent"] = C.project_simplex((xg + xt + xe) / 3.0)

    methods["Simple average"] = apply_G(zn, np.linalg.pinv(Hn))
    methods["Fixed weight"] = apply_G(
        zn, wls_G(Hn, np.array([1, 1, 1, .5, .5, .5, .5, 2, 2, 2], dtype=np.float32))
    )
    methods["PCA (3 comp.)"] = apply_G(recon, np.linalg.pinv(Hn))

    Sigma_inv = np.linalg.inv(cov)
    G_gls = (np.linalg.inv(Hn.T @ Sigma_inv @ Hn + 0.1 * np.eye(C.N_MIN))
             @ Hn.T @ Sigma_inv)
    methods["GLS / Bayesian"] = apply_G(zn, G_gls)

    t0 = time.time()
    ours = C.fuse(z, C.H_MATRIX)["x"]
    t_ours = time.time() - t0
    methods["WLS + Kalman (ours)"] = ours

    rows = []
    for name, x in methods.items():
        m = C.detection_metrics(x, gt, mask=mask)
        rec = C.recovery_metrics(x, truth, mask=mask)["Clay"]
        row = {"method": name, "clay_mean": float(x[C.TARGET][mask].mean()),
               "gradient": C.spatial_gradient(x), "recall": m["recall"],
               "precision": m["precision"], "f1": m["f1"], "iou": m["iou"],
               "rmse_truth": rec["rmse"], "r_truth": rec["r"],
               "time_s": t_ours if name.startswith("WLS") else np.nan}
        rows.append(row)
        print(f"{name:22s} clay={row['clay_mean']:.4f} grad={row['gradient']:.5f} "
              f"R={row['recall']:.4f} P={row['precision']:.4f} F1={row['f1']:.4f}")

    with open(C.OUT / "baselines.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    C.save_json(C.OUT / "baselines.json", rows)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    names = [r["method"] for r in rows]
    for ax, key, title, color in (
        (axes[0], "clay_mean", "Clay mean abundance", "#2ca02c"),
        (axes[1], "f1", "F1 vs clay_prior proxy", "#1f77b4"),
        (axes[2], "gradient", "Spatial gradient", "#d62728"),
    ):
        vals = [r[key] for r in rows]
        ax.barh(names, vals, color=color, alpha=0.85)
        ax.set_title(title)
        ax.grid(axis="x", alpha=0.3)
        for i, v in enumerate(vals):
            ax.text(v, i, f" {v:.3f}", va="center", fontsize=8)
    plt.tight_layout()
    plt.savefig(C.OUT / "baselines.png", dpi=300)
    plt.close()
    print("saved           : baselines.csv / baselines.json / baselines.png")


if __name__ == "__main__":
    main()

