"""Decisive controls: is the TIR gain information or conditioning?

If adding a modality helps only because the inverse problem becomes
overdetermined, then *any* extra channels with the right column structure
should help, even when they carry no spatial information about the target.
If it helps because the data carry independent mineralogy, the real ASTER cube
should beat a shuffled copy of itself and should work on its own.

Configurations (corrected EM matrix where EM is involved, analysis mask):

  gamma                       3 channels, underdetermined (5 unknowns)
  tir only                    real / synthetic
  gamma + tir                 real / synthetic-library
  gamma + tir (shuffled)      real ASTER, pixels permuted in 128-px blocks
                              (marginals and within-block texture kept,
                              geographic registration destroyed)
  gamma + tir (pixel-shuffle) real ASTER, all pixels permuted
  gamma + noise               5 iid Gaussian channels with the real TIR
                              rows of H (pure conditioning, zero information)
  gamma + ridge x10           gamma only, lambda raised 10x (regularisation
                              alone, no extra channels)

Each is scored on the proxy (F1, AP) and on the independent geology (AUC).
Outputs: processed/tir_controls.json, tir_controls.csv
"""
from __future__ import annotations

import csv

import numpy as np

import common as C
from run_advantage import pr_ap

BLOCK = 128


def block_shuffle(cube, mask, rng, block=BLOCK):
    """Permute whole blocks: keeps texture, destroys geographic registration."""
    h, w = mask.shape
    nb_y, nb_x = (h + block - 1) // block, (w + block - 1) // block
    out = np.full_like(cube, np.nan)
    tiles = [(by, bx) for by in range(nb_y) for bx in range(nb_x)]
    perm = rng.permutation(len(tiles))
    for (by, bx), k in zip(tiles, perm):
        sy, sx = tiles[k]
        ys, xs = slice(by * block, min((by + 1) * block, h)), slice(bx * block, min((bx + 1) * block, w))
        ysrc = slice(sy * block, sy * block + (ys.stop - ys.start))
        xsrc = slice(sx * block, sx * block + (xs.stop - xs.start))
        src = cube[:, ysrc, xsrc]
        if src.shape[1:] == (ys.stop - ys.start, xs.stop - xs.start):
            out[:, ys, xs] = src
    return out


def pixel_shuffle(cube, mask, rng):
    out = cube.copy()
    idx = np.flatnonzero(mask.ravel())
    perm = rng.permutation(idx)
    for i in range(cube.shape[0]):
        flat = out[i].ravel()
        flat[idx] = cube[i].ravel()[perm]
        out[i] = flat.reshape(mask.shape)
    return out


def main():
    gamma, tir_syn, em = C.load_cubes()
    real = C.load_real_tir()
    mask = C.load_analysis_mask()
    gt = C.load_clay_prior() > 0.55
    sel, pos = C.load_geology_target(mask)
    lay_r = C.layout("real")
    lay_s = C.layout("synthetic-library")
    rng = np.random.default_rng(7)

    fill = lambda a: np.nan_to_num(a, nan=np.nanmedian(a))  # noqa: E731
    real_f = np.stack([fill(real[i]) for i in range(real.shape[0])])
    syn4 = tir_syn[list(C.TIR_BANDS)]

    shuffled_b = block_shuffle(real, mask, rng)
    shuffled_b = np.stack([fill(shuffled_b[i]) for i in range(5)])
    shuffled_p = np.stack([fill(pixel_shuffle(real, mask, rng)[i]) for i in range(5)])
    noise = rng.standard_normal(real.shape).astype(np.float32)

    def run(name, tir_block, H_tir, lam=0.1, use_gamma=True):
        parts, rows = [], []
        if use_gamma:
            parts.append(gamma)
            rows.append(C.H_MATRIX[:3])
        if tir_block is not None:
            parts.append(tir_block)
            rows.append(H_tir)
        z = np.concatenate(parts).astype(np.float32)
        H = np.vstack(rows)
        x = C.fuse(z, H, lam=lam)["x"]
        m = C.detection_metrics(x, gt, mask=mask)
        ap, _, _ = pr_ap(x, gt, mask)
        r = {"config": name, "n_channels": int(z.shape[0]), "lambda": lam,
             "f1": m["f1"], "ap": ap, "recall": m["recall"],
             "precision": m["precision"], "geo_auc": C.geology_auc(x, sel, pos),
             "clay_mean": m["clay_mean"]}
        print(f"{name:34s} n={r['n_channels']:2d} F1={r['f1']:.4f} "
              f"AP={r['ap']:.4f} geoAUC={r['geo_auc']:.4f}")
        return r

    Hr = lay_r.H[lay_r.tir]
    Hs = lay_s.H[lay_s.tir]
    rows = [
        run("gamma", None, None),
        run("gamma, ridge x10", None, None, lam=1.0),
        run("gamma, ridge x100", None, None, lam=10.0),
        run("real TIR only", real_f, Hr, use_gamma=False),
        run("synthetic TIR only", syn4, Hs, use_gamma=False),
        run("gamma + real TIR", real_f, Hr),
        run("gamma + synthetic TIR", syn4, Hs),
        run("gamma + real TIR, block-shuffled", shuffled_b, Hr),
        run("gamma + real TIR, pixel-shuffled", shuffled_p, Hr),
        run("gamma + 5 noise channels", noise, Hr),
    ]

    # information content: how much of each TIR cube is explained by gamma?
    g = C.zscore(gamma)[:, mask].T
    expl = {}
    for name, cube in (("real", real_f), ("synthetic", syn4)):
        y = C.zscore(cube)[:, mask].T
        X = np.c_[g, np.ones(len(g))]
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ beta
        expl[name] = [float(1 - resid[:, i].var() / y[:, i].var())
                      for i in range(y.shape[1])]
        print(f"R^2 of {name} TIR bands on gamma: {np.round(expl[name], 3)}")

    C.save_json(C.PROC / "tir_controls.json", {
        "rows": rows, "r2_tir_on_gamma": expl,
        "note": "Shuffles keep the marginal distribution of the real ASTER "
                "emissivity and destroy its geographic registration; noise "
                "channels carry zero information but the same H rows.",
    })
    with open(C.PROC / "tir_controls.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("saved tir_controls.json/csv")


if __name__ == "__main__":
    main()
