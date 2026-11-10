"""Step 11 - figures that match the implemented pipeline.

fig_data.png    real gamma vs synthetic TIR/EM vs evaluation proxy
fig_method.png  WLS -> spatial Kalman -> depth Kalman, with quality weights
fig_results.png clay map, uncertainty, ablation and validation summaries
No unimplemented module (AI residual learner, edge runtime) is drawn.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

import common as C


def box(ax, x, y, w, h, text, fc="#E8F1F8", ec="#2C5F7C", fs=9):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                                facecolor=fc, edgecolor=ec, linewidth=1.1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def arrow(ax, xy, xytext):
    ax.annotate("", xy=xy, xytext=xytext,
                arrowprops=dict(arrowstyle="->", lw=1.8, color="#2C5F7C"))


def fig_data():
    gamma, tir, em = C.load_cubes()
    prior = C.load_clay_prior()
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    panels = [
        (gamma[0], "K (%) - real", "viridis"),
        (gamma[1], "eU (ppm) - real", "viridis"),
        (gamma[2], "eTh (ppm) - real", "viridis"),
        (tir[53], "TIR 9.6 um - synthetic", "inferno"),
        (np.log10(em[0]), "log10 EM 0 m - synthetic", "jet_r"),
        (prior, "clay_prior (evaluation proxy)", "magma"),
    ]
    for ax, (arr, title, cmap) in zip(axes.flatten(), panels):
        im = ax.imshow(arr, cmap=cmap)
        ax.set_title(title)
        ax.axis("off")
        plt.colorbar(im, ax=ax, fraction=0.046)
    plt.tight_layout()
    plt.savefig(C.OUT / "fig_data.png", dpi=300)
    plt.close()


def fig_method():
    fig, ax = plt.subplots(figsize=(10, 7.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.text(5, 9.6, "Implemented estimator", ha="center", fontsize=13, fontweight="bold")
    ax.text(5, 9.2, "standardised relative-signature WLS + forward Kalman",
            ha="center", fontsize=9, style="italic")

    box(ax, 0.4, 7.9, 2.9, 0.9, "z: 11 channels\n3 gamma + 5 ASTER TIR + 3 EM")
    box(ax, 3.6, 7.9, 2.9, 0.9, "z-score per channel\nclip +/-3")
    box(ax, 6.8, 7.9, 2.8, 0.9, "WLS\n(H^T W H + lambda I)^-1 H^T W z")
    arrow(ax, (3.55, 8.35), (3.35, 8.35))
    arrow(ax, (6.75, 8.35), (6.55, 8.35))

    box(ax, 0.4, 6.2, 2.9, 1.0, "quality weights\nq(T, RH, fault flag)\nW = diag(q)", fc="#FFF1E0")
    arrow(ax, (3.55, 6.75), (3.35, 6.75))
    arrow(ax, (1.85, 7.85), (1.85, 7.25))

    box(ax, 3.6, 6.2, 2.9, 1.0, "non-negative\n+ closure\nsum a = 1")
    box(ax, 6.8, 6.2, 2.8, 1.0, "spatial Kalman (W axis)\nP = P + Q; K = P/(P+R_obs)")
    arrow(ax, (6.55, 6.7), (6.75, 6.7))
    arrow(ax, (5.0, 7.85), (5.0, 7.25))

    box(ax, 3.6, 4.4, 2.9, 1.0, "posterior abundance x\nand variance P")
    arrow(ax, (5.0, 6.15), (5.0, 5.45))

    box(ax, 0.4, 2.5, 2.9, 1.1, "2-D maps\n5 minerals + uncertainty")
    box(ax, 3.6, 2.5, 2.9, 1.1, "depth Kalman\n40 layers, 0-600 m")
    box(ax, 6.8, 2.5, 2.8, 1.1, "3-D cube\n(40, 5, H, W)")
    arrow(ax, (3.55, 2.95), (3.35, 2.95))
    arrow(ax, (6.75, 2.95), (6.55, 2.95))
    arrow(ax, (5.0, 4.35), (5.0, 3.65))

    ax.text(5, 1.2, "Environment enters through the quality weights; it is not a Kalman state.",
            ha="center", fontsize=9, style="italic", color="#555")
    ax.text(5, 0.7, "P is the forward-filter variance, not a calibrated confidence interval.",
            ha="center", fontsize=9, style="italic", color="#555")
    plt.tight_layout()
    plt.savefig(C.OUT / "fig_method.png", dpi=300)
    plt.close()


def fig_results():
    x = np.load(C.OUT / "kf_main_abundance.npy")
    P = np.load(C.OUT / "kf_uncertainty.npy")
    mask = C.load_analysis_mask()
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))

    im = axes[0, 0].imshow(x[C.TARGET], cmap="viridis", vmin=0, vmax=0.7)
    axes[0, 0].set_title(f"Clay abundance (mean={x[C.TARGET][mask].mean():.3f})")
    axes[0, 0].axis("off")
    plt.colorbar(im, ax=axes[0, 0], fraction=0.046)

    im = axes[0, 1].imshow(P.sum(axis=0), cmap="magma")
    axes[0, 1].set_title("Posterior variance  sum_i P_i")
    axes[0, 1].axis("off")
    plt.colorbar(im, ax=axes[0, 1], fraction=0.046)

    abl = C.load_json(C.OUT / "ablation.json")
    names = [r["config"] for r in abl]
    vals = [r["f1"] for r in abl]
    axes[1, 0].bar(names, vals, color="#1f77b4", alpha=0.85)
    axes[1, 0].set_title("Ablation: F1 vs clay_prior proxy")
    axes[1, 0].set_ylim(0, max(vals) * 1.25)
    for i, v in enumerate(vals):
        axes[1, 0].text(i, v, f"{v:.3f}", ha="center", va="bottom", fontsize=8)
    axes[1, 0].grid(axis="y", alpha=0.3)

    val = C.load_json(C.OUT / "validation.json")
    fam = val["family_recall"]
    axes[1, 1].barh(list(fam), list(fam.values()), color="#2ca02c", alpha=0.85)
    axes[1, 1].axvline(val["overall_recall"], color="red", ls="--",
                       label=f"mean {val['overall_recall']:.3f}")
    axes[1, 1].set_xlim(0, 1)
    axes[1, 1].set_title("Validation recall by scenario family")
    axes[1, 1].legend()
    axes[1, 1].grid(axis="x", alpha=0.3)

    plt.tight_layout()
    plt.savefig(C.OUT / "fig_results.png", dpi=300)
    plt.close()


def main():
    fig_data()
    fig_method()
    if (C.OUT / "validation.json").exists():
        fig_results()
    print("saved: fig_data.png / fig_method.png" +
          (" / fig_results.png" if (C.OUT / "validation.json").exists() else ""))


if __name__ == "__main__":
    main()


