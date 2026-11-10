"""Step 9 - reproducibility and sensitivity checks.

  * multi-seed: 20 noise realisations, clay mean / recall / F1
  * resolution: 50, 100, 200, 400, 800 m by striding
  * weighting: uniform vs spatial-roughness weights (diagnostic; the latter is
    not used as the production model because it rewards smooth synthetic
    channels rather than true sensor quality)
"""
import csv
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common as C


def metrics_for(x, gt, mask):
    m = C.detection_metrics(x, gt, mask=mask)
    return m


def main():
    gamma, tir, em = C.load_cubes()
    z = C.build_observation(gamma, tir, em)
    mask = C.load_valid_mask()
    gt = C.load_clay_prior()

    # multi-seed -------------------------------------------------------------
    print("multi-seed (n=20, 2% channel noise)")
    rng_master = np.random.default_rng(2024)
    seeds = []
    for i in range(20):
        rng = np.random.default_rng(2024 + i)
        zz = z + rng.normal(0, 0.02 * z.std(axis=(1, 2), keepdims=True), z.shape)
        x = C.fuse(zz.astype(np.float32), C.H_MATRIX)["x"]
        m = metrics_for(x, gt, mask)
        seeds.append({"seed": i, **m})
        print(f"  seed {i:2d}: clay={m['clay_mean']:.4f} R={m['recall']:.4f} F1={m['f1']:.4f}")

    def stat(key):
        v = np.array([s[key] for s in seeds])
        return {"mean": float(v.mean()), "std": float(v.std(ddof=1)),
                "ci95": [float(v.mean() - 1.96 * v.std(ddof=1) / np.sqrt(len(v))),
                         float(v.mean() + 1.96 * v.std(ddof=1) / np.sqrt(len(v)))]}

    seed_stats = {k: stat(k) for k in ("clay_mean", "recall", "f1")}

    # resolution -------------------------------------------------------------
    print("\nresolution")
    res_rows = []
    for factor in (1, 2, 4, 8, 16):
        zz = z[:, ::factor, ::factor]
        gt_s = gt[::factor, ::factor]
        mask_s = mask[::factor, ::factor]
        t0 = time.time()
        x = C.fuse(zz, C.H_MATRIX)["x"]
        dt = time.time() - t0
        m = metrics_for(x, gt_s, mask_s)
        res_rows.append({"resolution_m": 50 * factor, "grid": f"{zz.shape[1]}x{zz.shape[2]}",
                         "clay": m["clay_mean"], "recall": m["recall"], "f1": m["f1"],
                         "time_s": dt})
        print(f"  {50*factor:4d} m  {zz.shape[1]:4d}x{zz.shape[2]:4d}  "
              f"clay={m['clay_mean']:.4f} R={m['recall']:.4f} t={dt:.2f}s")

    # weighting diagnostic ---------------------------------------------------
    print("\nweighting diagnostic")
    weight_rows = []
    for mode in ("uniform", "roughness"):
        t0 = time.time()
        res = C.fuse(z, C.H_MATRIX, weighting=mode)
        dt = time.time() - t0
        m = metrics_for(res["x"], gt, mask)
        weight_rows.append({"weighting": mode, **m, "time_s": dt,
                            "weights": res["weights"].tolist()})
        print(f"  {mode:10s} R={m['recall']:.4f} F1={m['f1']:.4f} "
              f"w={np.round(res['weights'], 2)}")

    C.save_json(C.OUT / "sensitivity.json", {
        "multi_seed": seeds, "multi_seed_stats": seed_stats,
        "resolution": res_rows, "weighting": weight_rows,
    })
    with open(C.OUT / "resolution.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(res_rows[0]))
        w.writeheader()
        w.writerows(res_rows)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].hist([s["recall"] for s in seeds], bins=8, color="#1f77b4", alpha=0.85)
    axes[0].axvline(seed_stats["recall"]["mean"], color="red", ls="--")
    axes[0].set_xlabel("Recall")
    axes[0].set_title("(a) 20-seed recall distribution")
    axes[0].grid(alpha=0.3)
    axes[1].plot([r["resolution_m"] for r in res_rows],
                 [r["recall"] for r in res_rows], "o-", color="#2ca02c")
    axes[1].set_xscale("log")
    axes[1].set_xlabel("Pixel size (m)")
    axes[1].set_ylabel("Recall")
    axes[1].set_title("(b) Resolution sensitivity")
    axes[1].grid(alpha=0.3, which="both")
    plt.tight_layout()
    plt.savefig(C.OUT / "sensitivity.png", dpi=300)
    plt.close()

    print(f"\nseed recall: {seed_stats['recall']['mean']:.4f} "
          f"+/- {seed_stats['recall']['std']:.4f}")
    print("saved           : sensitivity.json / resolution.csv / sensitivity.png")


if __name__ == "__main__":
    main()

