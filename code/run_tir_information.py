"""Does the real ASTER cube carry information beyond what the inversion invents?

Finding that motivates this script: appending five channels of *zeros* with the
ASTER rows of H to the three gamma channels raises the geology AUC from 0.387 to
0.919, almost exactly what the real ASTER data give (0.913).  The "TIR gain" of
the inversion is therefore created by the extra rows of H (they regularise a
3-equation / 5-unknown problem), not by the measurements.

To separate information from structure, this script asks the data-only
question with models that cannot benefit from extra H rows:

1. Per-band and per-index AUC of the raw channels against the independent
   geology (no inversion at all).
2. A cross-validated logistic model on the geology label, with spatial-block
   folds (128 px, 5 folds) so neighbouring pixels never sit on both sides:
       gamma only  vs  gamma + real ASTER  vs  gamma + block-shuffled ASTER
       vs gamma + synthetic TIR.
   Same model, same folds; the only difference is the information in the
   channels.
3. The same with the gamma-derived proxy as label (the circular target), to
   show how the conclusion depends on the target.

Outputs: processed/tir_information.json, tir_information.csv
"""
from __future__ import annotations

import csv

import numpy as np

import common as C

BLOCK = 128
N_FOLD = 5
N_SAMPLE = 200_000


def standard(X):
    mu = X.mean(axis=0)
    sd = X.std(axis=0) + 1e-9
    return (X - mu) / sd


def logistic_fit(X, y, l2=1e-2, iters=60):
    """Newton-Raphson logistic regression with an L2 penalty."""
    X1 = np.c_[np.ones(len(X)), X]
    w = np.zeros(X1.shape[1])
    reg = l2 * np.eye(X1.shape[1])
    reg[0, 0] = 0.0
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-np.clip(X1 @ w, -30, 30)))
        g = X1.T @ (p - y) + reg @ w
        Hs = (X1 * (p * (1 - p))[:, None]).T @ X1 + reg
        step = np.linalg.solve(Hs, g)
        w -= step
        if np.abs(step).max() < 1e-8:
            break
    return w


def logistic_predict(w, X):
    return np.c_[np.ones(len(X)), X] @ w


def block_shuffle(cube, mask, rng, block=BLOCK):
    h, w = mask.shape
    tiles = [(y, x) for y in range(0, h - block + 1, block)
             for x in range(0, w - block + 1, block)]
    perm = rng.permutation(len(tiles))
    out = cube.copy()
    for (ty, tx), k in zip(tiles, perm):
        sy, sx = tiles[k]
        out[:, ty:ty + block, tx:tx + block] = cube[:, sy:sy + block, sx:sx + block]
    return out


def cv_auc(features, y, folds):
    aucs = []
    for k in range(N_FOLD):
        tr, te = folds != k, folds == k
        if y[te].all() or (~y[te]).all():
            continue
        Xtr = features[tr]
        mu, sd = Xtr.mean(axis=0), Xtr.std(axis=0) + 1e-9
        w = logistic_fit((Xtr - mu) / sd, y[tr].astype(float))
        aucs.append(C.auc_score(logistic_predict(w, (features[te] - mu) / sd), y[te]))
    return float(np.mean(aucs)), float(np.std(aucs, ddof=1)), len(aucs)


def main():
    gamma, tir_syn, _em = C.load_cubes()
    real = C.load_real_tir()
    mask = C.load_analysis_mask()
    prior = C.load_clay_prior()
    sel, pos = C.load_geology_target(mask)
    rng = np.random.default_rng(11)

    syn4 = tir_syn[list(C.TIR_BANDS)]
    real_shuf = block_shuffle(real, mask, rng)
    # pixels where every cube (incl. the shuffled copy) is finite
    ok = sel & np.isfinite(real_shuf).all(axis=0)
    h, w = mask.shape
    bid = (np.arange(h)[:, None] // BLOCK) * ((w + BLOCK - 1) // BLOCK) \
        + (np.arange(w)[None, :] // BLOCK)

    # labels on the selected pixels
    geo_full = np.zeros(mask.shape, dtype=bool)
    geo_full[sel] = pos
    ii = np.flatnonzero(ok.ravel())
    if ii.size > N_SAMPLE:
        ii = np.sort(rng.choice(ii, N_SAMPLE, replace=False))
    yy = geo_full.ravel()[ii]
    blocks = bid.ravel()[ii]
    ub = np.unique(blocks)
    fold_of = dict(zip(ub, rng.permutation(len(ub)) % N_FOLD))
    folds = np.array([fold_of[b] for b in blocks])

    def feat(*cubes):
        return np.column_stack([c.reshape(c.shape[0], -1)[:, ii].T for c in cubes])

    # ---- 1. raw channel AUC (no inversion) --------------------------------
    raw = {}
    names = ["K", "eU", "eTh"] + [f"ASTER {c:.3f} um" for c in C.ASTER_CENTRES] \
        + [f"synthetic {c} um" for c in C.TIR_WAVELENGTHS]
    stack = np.concatenate([gamma, real, syn4])
    for n, ch in zip(names, stack):
        v = ch[sel]
        good = np.isfinite(v)
        a = C.auc_score(v[good], pos[good])
        raw[n] = max(a, 1 - a)          # direction-free separability
    # spectral contrast indices from real ASTER (quartz / silica indicators)
    qi = real[3] / real[1]                       # 10.66 / 8.63 (quartz index)
    si = (real[3] + real[4]) / (real[0] + real[2])
    for n, v in (("ASTER quartz index b13/b11", qi), ("ASTER silica index", si)):
        vv = v[sel]
        good = np.isfinite(vv)
        a = C.auc_score(vv[good], pos[good])
        raw[n] = max(a, 1 - a)
    for k, v in raw.items():
        print(f"raw separability {k:30s} {v:.3f}")

    # ---- 2. cross-validated models, geology label -------------------------
    sets = {
        "gamma": feat(gamma),
        "real ASTER only": feat(np.nan_to_num(real)),
        "gamma + real ASTER": feat(gamma, np.nan_to_num(real)),
        "gamma + block-shuffled ASTER": feat(gamma, np.nan_to_num(real_shuf)),
        "gamma + synthetic TIR": feat(gamma, syn4),
    }
    geo_rows = []
    for name, X in sets.items():
        m, s, n = cv_auc(X, yy, folds)
        geo_rows.append({"target": "geology", "features": name,
                         "cv_auc": m, "cv_auc_sd": s, "folds_used": n})
        print(f"CV geology  {name:30s} AUC {m:.4f} +/- {s:.4f} ({n} folds)")

    # ---- 3. same, circular proxy label ------------------------------------
    yp = (prior > 0.55).ravel()[ii]
    proxy_rows = []
    for name, X in sets.items():
        m, s, n = cv_auc(X, yp, folds)
        proxy_rows.append({"target": "proxy", "features": name,
                           "cv_auc": m, "cv_auc_sd": s, "folds_used": n})
        print(f"CV proxy    {name:30s} AUC {m:.4f} +/- {s:.4f} ({n} folds)")

    rows = geo_rows + proxy_rows
    get = lambda t, f: next(r["cv_auc"] for r in rows  # noqa: E731
                            if r["target"] == t and r["features"] == f)
    summary = {
        "geology_gain_real": get("geology", "gamma + real ASTER") - get("geology", "gamma"),
        "geology_gain_shuffled": get("geology", "gamma + block-shuffled ASTER")
        - get("geology", "gamma"),
        "geology_gain_synthetic": get("geology", "gamma + synthetic TIR")
        - get("geology", "gamma"),
        "proxy_gain_real": get("proxy", "gamma + real ASTER") - get("proxy", "gamma"),
    }
    print("summary:", {k: round(v, 4) for k, v in summary.items()})

    C.save_json(C.PROC / "tir_information.json", {
        "n_samples": int(ii.size), "block_px": BLOCK, "n_folds": N_FOLD,
        "geology_positive_fraction": float(yy.mean()),
        "raw_separability": raw, "rows": rows, "summary": summary,
        "note": "Logistic regression with spatial-block cross-validation; the "
                "model has no response matrix, so extra channels cannot help "
                "by regularising an underdetermined inversion.",
    })
    with open(C.PROC / "tir_information.csv", "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=list(rows[0]))
        wri.writeheader()
        wri.writerows(rows)
    print("saved tir_information.json/csv")


if __name__ == "__main__":
    main()
