"""V2 controlled testbed: TIR and EM generated from one truth field.

This is a *variant*, not the main dataset.  Clay is set to the evaluation proxy
(`clay_prior`), the other minerals fill the remainder, TIR is generated from the
USGS endmembers, and EM uses a clay-only log10 response.  The inversion uses
log10 EM and the matching clay-only H rows.  It therefore removes the two
inconsistencies exposed by the main audit, at the cost of an inverse crime that
is stated explicitly.

Outputs are written under processed/v2/.
"""
from __future__ import annotations

import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter

import common as C

OUT = C.PROC / "v2"
TIR_NOISE = 0.005
SEED = 2024
BETA0, DEPTH_SCALE = 0.90, 250.0
A_INDEP, A_NOISE, A_NONLINEAR = 0.15, 0.05, 0.08


def standardize(x):
    return (x - x.mean()) / (x.std() + 1e-6)


def build_truth():
    gamma = C.load_gamma_planes()
    k, u, th = (C.normalize_p2p98(gamma[i]) for i in range(3))
    clay = C.clay_prior_from_gamma(gamma)
    q = 0.5 * (1 - k) + 0.3 * (1 - u) + 0.2
    f = 0.5 * k + 0.3 * (1 - th) + 0.2
    c = 0.5 * u * (1 - k) + 0.2
    d = 0.5 * th * (1 - k) + 0.2
    q, f, c, d = (x / (q + f + c + d) for x in (q, f, c, d))
    truth = np.stack([(1 - clay) * q, (1 - clay) * f, clay,
                      (1 - clay) * c, (1 - clay) * d]).astype(np.float32)
    return truth, clay


def build_tir(truth):
    emis = []
    for m in C.MINERALS:
        spec = np.load(C.SPEC / f"{m}_TIR.npy")
        mean = spec if spec.ndim == 1 else np.nanmean(spec, axis=0)
        emis.append(np.clip(1.0 - mean, 0.5, 1.0).astype(np.float32))
    emis = np.stack(emis, axis=1)  # 200 x 5
    tir = np.tensordot(emis, truth, axes=(1, 0)).astype(np.float32)
    rng = np.random.default_rng(SEED)
    tir += rng.normal(0, TIR_NOISE, tir.shape).astype(np.float32)
    valid = C.load_valid_mask()
    tir[:, ~valid] = np.nan
    return tir, emis


def build_em(clay):
    med = np.load(C.ASSETS / "em_layer_medians.npy")
    top = np.load(C.ASSETS / "em_dep_top.npy")
    bot = np.load(C.ASSETS / "em_dep_bot.npy")
    valid_m = np.isfinite(med)
    med = np.interp(np.arange(len(med)), np.arange(len(med))[valid_m], med[valid_m])
    rng = np.random.default_rng(SEED)
    h, w = clay.shape
    indep = standardize(gaussian_filter(rng.normal(0, 1, (h, w)), 25))
    cube = np.zeros((len(med), h, w), dtype=np.float32)
    for k in range(len(med)):
        depth = (top[k] + bot[k]) / 2
        beta = BETA0 * np.exp(-depth / DEPTH_SCALE)
        noise = standardize(gaussian_filter(rng.normal(0, 1, (h, w)), 15))
        log_rho = (np.log10(med[k]) + beta * (0.5 - clay)
                   + A_INDEP * indep + A_NOISE * noise
                   + A_NONLINEAR * (0.5 - clay) ** 2)
        cube[k] = np.clip(10 ** log_rho, 1.0, 10000.0)
    return cube


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    truth, clay = build_truth()
    tir, emis = build_tir(truth)
    em = build_em(clay)
    np.save(OUT / "truth_abundance_v2.npy", truth)
    np.save(OUT / "tir_cube_v2.npy", tir)
    np.save(OUT / "em_cube_v2.npy", em)
    np.save(OUT / "endmembers_v2.npy", emis)

    H = C.H_MATRIX.copy()
    H[3:7] = C.H_MATRIX[3:7]
    H[7:] = np.array([[0, 0, 0.90, 0, 0],
                      [0, 0, 0.86, 0, 0],
                      [0, 0, 0.36, 0, 0]])
    np.save(OUT / "H_v2.npy", H)

    gamma = C.load_gamma_planes()
    valid = C.load_valid_mask()
    z = np.concatenate(
        [gamma, tir[list(C.TIR_BANDS)],
         np.log10(np.clip(em[list(C.EM_LAYERS)], 1, 1e5))],
        axis=0,
    ).astype(np.float32)
    gt = C.clay_prior_from_gamma(gamma)

    rows = []
    for name, idx in {
        "gamma": [0, 1, 2],
        "gamma+tir": [0, 1, 2, 3, 4, 5, 6],
        "gamma+em": [0, 1, 2, 7, 8, 9],
        "all": list(range(10)),
    }.items():
        q = np.zeros(10, dtype=np.float32)
        q[idx] = 1.0
        res = C.fuse(z, H, channel_quality=q)
        m = C.detection_metrics(res["x"], gt, mask=valid)
        rows.append({"config": name, **m})
        print(f"{name:10s} clay={m['clay_mean']:.4f} R={m['recall']:.4f} "
              f"P={m['precision']:.4f} F1={m['f1']:.4f}")

    C.save_json(OUT / "ablation_v2.json", rows)
    with open(OUT / "ablation_v2.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar([r["config"] for r in rows], [r["f1"] for r in rows],
           color="#1f77b4", alpha=0.85)
    ax.set_ylabel("F1")
    ax.set_title("V2 controlled testbed: one truth field, log10 EM")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT / "fig_v2.png", dpi=300)
    plt.close()
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()

