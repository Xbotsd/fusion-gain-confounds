"""Step 6 - Depth-Kalman 3-D inversion (40 EM layers, 0-600 m).

The 40-layer EM section is treated as a sequence along depth; surface gamma and
TIR are repeated at every layer as anchors, the EM row is modulated with depth,
and the observation noise grows with depth.  Output is a (40, 5, H, W) abundance
cube plus a per-layer uncertainty profile.
"""
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import uniform_filter

import common as C

EM_FIX = "--emfix" in sys.argv
SUFFIX = "_emfix" if EM_FIX else ""


def out(name):
    p = Path(name)
    return C.OUT / (p.stem + SUFFIX + p.suffix)


def get_H_layer(k, depth, lay):
    """Response matrix for one depth layer: gamma | TIR | single EM layer."""
    H = lay.H.copy()
    em = lay.em
    if EM_FIX:
        H[em] = 0.0
        H[em[0], C.TARGET] = 0.90 * np.exp(-depth / 250.0)
    else:
        depth_factor = np.clip(depth / 300.0, 0.3, 1.5)
        H[em[0]] = np.maximum(
            H[em[0]] * (1.0 + 0.2 * depth_factor * np.array([1.0, 0.5, -0.8, 1.2, 1.0])),
            5.0,
        )
    only = lay.gamma + lay.tir + [em[0]]
    d = np.linalg.norm(H[only], axis=0, keepdims=True)
    Hn = np.zeros_like(H)
    Hn[only] = H[only] / np.where(d < 1e-12, 1.0, d)
    return Hn, only


def get_R_layer(depth, n):
    depth_factor = np.clip(depth / 300.0, 0.0, 1.0)
    R = np.ones(n, dtype=np.float32)
    R[:-1] = 1.0 + 5.0 * depth_factor
    R[-1] = 1.0
    return R


def main():
    t0 = time.time()
    gamma, tir, em = C.load_cubes()
    mask = C.load_analysis_mask()
    lay = C.layout("real")
    if EM_FIX:
        lay.H = lay.H_emfix()
    z0, _, _, _ = C.load_main("real", emfix=False)
    top = np.load(C.ASSETS / "em_dep_top.npy")
    bot = np.load(C.ASSETS / "em_dep_bot.npy")
    dep_mid = (top + bot) / 2.0
    n_layers = em.shape[0]

    em_s = np.stack([uniform_filter(em[i], size=3) for i in range(em.shape[0])])
    surface = z0[lay.gamma + lay.tir]          # gamma + real ASTER TIR

    h_grid, w_grid = gamma.shape[1], gamma.shape[2]
    x_all = np.zeros((n_layers, C.N_MIN, h_grid, w_grid), dtype=np.float32)
    p_mean = np.zeros(n_layers, dtype=np.float32)
    F = np.eye(C.N_MIN, dtype=np.float32) * 0.85 + 0.15 / C.N_MIN
    Q = 0.03

    # surface initialisation from gamma only
    Hg = C.H_MATRIX[:3] / np.linalg.norm(C.H_MATRIX[:3], axis=0, keepdims=True)
    G_gamma = np.linalg.inv(Hg.T @ Hg + 0.1 * np.eye(C.N_MIN)) @ Hg.T

    print("depth Kalman recursion ...")
    for k in range(n_layers):
        em_layer = em_s[k][None]
        if EM_FIX:
            em_layer = np.log10(np.clip(em_layer, 1.0, 1e5))
        z = np.concatenate([surface, em_layer], axis=0).astype(np.float32)
        mu = z.mean(axis=(1, 2), keepdims=True) + 1e-6
        sd = z.std(axis=(1, 2), keepdims=True) + 1e-6
        zn = np.clip((z - mu) / sd, -3, 3)

        Hk, only = get_H_layer(k, dep_mid[k], lay)
        Rk = get_R_layer(dep_mid[k], len(only))
        Hsub = Hk[only]

        if k == 0:
            x = G_gamma @ zn[:3].reshape(3, -1) + 1.0 / C.N_MIN
            x = C.project_simplex(x).reshape(C.N_MIN, h_grid, w_grid)
            P = np.full((C.N_MIN, h_grid, w_grid), 0.1, dtype=np.float32)
        else:
            x_pred = np.einsum("ij,jhw->ihw", F, x)
            P_pred = np.einsum("ij,jhw->ihw", F ** 2, P) + Q
            H_sq = Hsub ** 2
            denom = np.einsum("jk,khw->jhw", H_sq, P_pred) + Rk[:, None, None]
            K = np.clip(np.einsum("khw,jk,jhw->jkhw", P_pred, Hsub, 1.0 / denom), -0.5, 0.5)
            innov = np.clip(zn - np.einsum("ji,ihw->jhw", Hsub, x_pred), -5, 5)
            x = x_pred + np.einsum("jkhw,jhw->khw", K, innov)
            x = C.project_simplex(x)
            P = np.maximum(P_pred * (1 - 0.5 * np.einsum("jkhw,jk->khw", K, Hsub) / len(only)),
                           0.001)

        x_all[k] = x
        p_mean[k] = float(P.mean())
        if (k + 1) % 10 == 0:
            print(f"  layer {k+1}/{n_layers}  depth {dep_mid[k]:.0f} m")

    np.save(out("depth_kalman_3d.npy"), x_all)
    np.save(out("depth_uncertainty.npy"), p_mean)

    print("\nlayer   depth   Quartz  Feldspar  Clay  Calcite  Dolomite")
    for k in (0, 5, 10, 15, 20, 25, 30, 35, 39):
        means = [x_all[k, i][mask].mean() for i in range(C.N_MIN)]
        print(f"{k:5d} {dep_mid[k]:7.1f}  " + "  ".join(f"{v:.4f}" for v in means))

    # figures -----------------------------------------------------------------
    fig, axes = plt.subplots(3, 5, figsize=(22, 13))
    layer_ids = [0, 5, 10, 15, 20, 25, 28, 31, 34, 37, 39, 2, 7, 12, 17]
    for ax, k in zip(axes.flatten(), layer_ids):
        im = ax.imshow(x_all[k, C.TARGET], cmap="viridis", vmin=0, vmax=0.7)
        ax.set_title(f"Layer {k} ({dep_mid[k]:.0f} m)\nClay={x_all[k, C.TARGET][mask].mean():.3f}",
                     fontsize=10)
        ax.axis("off")
        plt.colorbar(im, ax=ax, fraction=0.046)
    plt.tight_layout()
    plt.savefig(out("depth_clay_layers.png"), dpi=120)
    plt.close()

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    for i, name in enumerate(C.MINERALS):
        ax.plot([x_all[k, i][mask].mean() for k in range(n_layers)], dep_mid, "o-",
                label=name, color=colors[i], markersize=4)
    ax.invert_yaxis()
    ax.set_xlabel("Mean abundance")
    ax.set_ylabel("Depth (m)")
    ax.set_title("Depth profile of mineral abundance")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out("depth_profiles.png"), dpi=300)
    plt.close()

    fig, axes = plt.subplots(1, 5, figsize=(22, 6))
    for i, name in enumerate(C.MINERALS):
        prof = x_all[:, i, :, 600]
        im = axes[i].imshow(prof, aspect="auto", cmap="viridis", vmin=0, vmax=0.7,
                            extent=[0, w_grid, dep_mid[-1], dep_mid[0]])
        axes[i].set_title(name)
        axes[i].set_xlabel("X (grid)")
        if i == 0:
            axes[i].set_ylabel("Depth (m)")
        plt.colorbar(im, ax=axes[i], fraction=0.046)
    plt.tight_layout()
    plt.savefig(out("depth_section.png"), dpi=300)
    plt.close()

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(p_mean, dep_mid, "o-", color="red")
    ax.invert_yaxis()
    ax.set_xlabel("Mean posterior variance")
    ax.set_ylabel("Depth (m)")
    ax.set_title("Uncertainty vs depth")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out("depth_uncertainty.png"), dpi=300)
    plt.close()

    C.save_json(out("depth.json"), {
        "layers": n_layers,
        "depth_m": dep_mid.tolist(),
        "layer_mean": [[float(x_all[k, i][mask].mean()) for i in range(C.N_MIN)]
                       for k in range(n_layers)],
        "uncertainty": p_mean.tolist(),
        "runtime_s": time.time() - t0,
    })
    print(f"runtime         : {time.time()-t0:.1f} s")
    print(f"saved           : depth_kalman_3d{SUFFIX}.npy / depth_uncertainty{SUFFIX}.npy / depth{SUFFIX}.json")


if __name__ == "__main__":
    main()


