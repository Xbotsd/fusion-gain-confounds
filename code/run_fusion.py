"""Step 4 - main 2-D fusion (WLS + Kalman) and the primary abundance map.

Outputs: kf_mineral_abundance.npy, kf_uncertainty.npy, wls_initial.npy,
         fusion.json, kf_fusion_final.png
"""
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common as C


def main():
    t0 = time.time()
    gamma, tir, em = C.load_cubes()
    z = C.build_observation(gamma, tir, em)
    mask = C.load_valid_mask()
    gt = C.load_clay_prior()
    truth = np.load(C.OUT / "truth_abundance.npy")

    res = C.fuse(z, C.H_MATRIX, weighting="uniform", kalman=True)
    x, P = res["x"], res["P"]

    np.save(C.OUT / "kf_mineral_abundance.npy", x)
    np.save(C.OUT / "kf_uncertainty.npy", P)
    np.save(C.OUT / "wls_initial.npy", res["x_init"])

    proxy = C.detection_metrics(x, gt, mask=mask)
    recover = C.recovery_metrics(x, truth, mask=mask)
    summary = {
        "grid": list(x.shape[1:]),
        "valid_fraction": float(mask.mean()),
        "weights": res["weights"].tolist(),
        "clay_mean_full": float(x[C.TARGET].mean()),
        "clay_mean_valid": proxy["clay_mean"],
        "spatial_gradient": C.spatial_gradient(x),
        "mean_uncertainty": float(P.mean()),
        "proxy": proxy,
        "recovery": recover,
        "residual_rms": dict(zip(
            ["K", "eU", "eTh", "TIR1", "TIR2", "TIR3", "TIR4", "EM1", "EM2", "EM3"],
            res["residual_rms"].tolist(),
        )),
        "runtime_s": time.time() - t0,
    }
    C.save_json(C.OUT / "fusion.json", summary)

    print(f"valid pixels    : {mask.mean():.3f}")
    print(f"clay mean       : {x[C.TARGET].mean():.4f}")
    print(f"proxy           : R={proxy['recall']:.4f} P={proxy['precision']:.4f} "
          f"F1={proxy['f1']:.4f} IoU={proxy['iou']:.4f}")
    print(f"recovery (clay) : RMSE={recover['Clay']['rmse']:.4f} "
          f"r={recover['Clay']['r']:.3f} bias={recover['Clay']['bias']:+.4f}")
    print(f"uncertainty     : {P.mean():.4f}")
    print(f"runtime         : {time.time()-t0:.1f} s")

    # Figure
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()
    for i, name in enumerate(C.MINERALS):
        im = axes[i].imshow(x[i], cmap="viridis", vmin=0, vmax=0.6)
        axes[i].set_title(f"{name} (mean={x[i][mask].mean():.3f})")
        axes[i].axis("off")
        plt.colorbar(im, ax=axes[i], fraction=0.046)
    comp = x[C.TARGET] - x[0]
    im = axes[5].imshow(comp, cmap="RdBu_r", vmin=-0.3, vmax=0.3)
    axes[5].set_title("Clay - Quartz")
    axes[5].axis("off")
    plt.colorbar(im, ax=axes[5], fraction=0.046)
    plt.tight_layout()
    plt.savefig(C.OUT / "kf_fusion_final.png", dpi=300)
    plt.close()

    fig, ax = plt.subplots(figsize=(9, 7))
    im = ax.imshow(P.sum(axis=0), cmap="magma")
    ax.set_title("Posterior uncertainty  sum_i P_i")
    ax.axis("off")
    plt.colorbar(im, ax=ax, fraction=0.046)
    plt.tight_layout()
    plt.savefig(C.OUT / "kf_uncertainty_map.png", dpi=300)
    plt.close()
    print("saved           : kf_mineral_abundance.npy / kf_uncertainty.npy / fusion.json")


if __name__ == "__main__":
    main()

