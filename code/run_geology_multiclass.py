"""Harder independent target: a multi-class geology task where gamma is not enough.

The binary geology contrast (alluvium + felsic vs carbonate + sedimentary) is
98.7 % / 1.3 % imbalanced and K alone separates it (AUC 0.986), so it cannot
reveal what a second modality adds.  This experiment uses the four large
SIM 3206 classes, which are radiometrically similar:

    felsic plutonic | volcanic | metasedimentary | surficial/alluvium

A multinomial logistic model with 128-px spatial-block cross-validation and
balanced classes (chance = 0.25) is fitted to several channel sets.  The model
has no response matrix, so extra channels cannot help by regularising an
underdetermined inversion — only by carrying information.

Every repeat redraws the class subsample, the block-to-fold assignment and the
block shuffle, so the reported spread includes sampling and fold variability.

Outputs: processed/geology_multiclass.json, geology_multiclass.csv
"""
from __future__ import annotations

import csv

import numpy as np

import common as C

BLOCK = 128
N_FOLD = 5
N_REPEATS = 20
PER_CLASS = 15_000
CLASSES = ("felsic plutonic", "volcanic", "metasedimentary", "surficial/alluvium")


def softmax_fit(X, y, k, l2=1e-2, iters=300, lr=0.5):
    """Multinomial logistic regression by full-batch gradient descent."""
    n, d = X.shape
    X1 = np.c_[np.ones(n), X]
    W = np.zeros((d + 1, k))
    Y = np.eye(k)[y]
    for _ in range(iters):
        S = X1 @ W
        S -= S.max(axis=1, keepdims=True)
        P = np.exp(S)
        P /= P.sum(axis=1, keepdims=True)
        G = X1.T @ (P - Y) / n
        G[1:] += l2 * W[1:]
        W -= lr * G
    return W


def predict(W, X):
    return np.argmax(np.c_[np.ones(len(X)), X] @ W, axis=1)


def block_shuffle(cube, mask, rng, block=BLOCK):
    """Permute whole tiles: keeps texture, destroys geographic registration."""
    h, w = mask.shape
    tiles = [(y, x) for y in range(0, h - block + 1, block)
             for x in range(0, w - block + 1, block)]
    perm = rng.permutation(len(tiles))
    out = cube.copy()
    for (ty, tx), kk in zip(tiles, perm):
        sy, sx = tiles[kk]
        out[:, ty:ty + block, tx:tx + block] = cube[:, sy:sy + block, sx:sx + block]
    return out


class Data:
    def __init__(self):
        self.gamma, tir_syn, _ = C.load_cubes()
        self.syn = tir_syn[list(C.TIR_BANDS)]
        self.real = C.load_real_tir()
        self.tmi = np.load(C.PROC / "tmi_grid.npy")[None]
        self.mask = C.load_analysis_mask()
        self.sub = np.load(C.PROC / "geology_substrate.npy")
        groups = C.load_json(C.PROC / "independent_validation.json")["groups"]
        self.gid = {g: i + 1 for i, g in enumerate(groups)}
        h, w = self.mask.shape
        self.bid = (np.arange(h)[:, None] // BLOCK) * ((w + BLOCK - 1) // BLOCK) \
            + (np.arange(w)[None, :] // BLOCK)


def run_once(D, seed, verbose=False):
    rng = np.random.default_rng(1000 + seed)
    real_shuf = block_shuffle(D.real, D.mask, rng)
    ok = D.mask & np.isfinite(real_shuf).all(axis=0)

    idx, lab = [], []
    for c, name in enumerate(CLASSES):
        cand = np.flatnonzero((ok & (D.sub == D.gid[name])).ravel())
        take = rng.choice(cand, min(PER_CLASS, cand.size), replace=False)
        idx.append(take)
        lab.append(np.full(take.size, c))
        if verbose:
            print(f"class {name:20s} {cand.size:7d} px available, {take.size} used")
    idx = np.concatenate(idx)
    lab = np.concatenate(lab)
    blocks = D.bid.ravel()[idx]
    ub = np.unique(blocks)
    fold_of = dict(zip(ub, rng.permutation(len(ub)) % N_FOLD))
    folds = np.array([fold_of[b] for b in blocks])

    def feat(*cubes):
        return np.column_stack([cc.reshape(cc.shape[0], -1)[:, idx].T for cc in cubes])

    sets = {
        "gamma": feat(D.gamma),
        "real ASTER": feat(D.real),
        "gamma + real ASTER": feat(D.gamma, D.real),
        "gamma + block-shuffled ASTER": feat(D.gamma, real_shuf),
        "gamma + synthetic TIR": feat(D.gamma, D.syn),
        "gamma + TMI": feat(D.gamma, D.tmi),
        "gamma + real ASTER + TMI": feat(D.gamma, D.real, D.tmi),
    }
    k = len(CLASSES)
    balanced = {}
    for name, X in sets.items():
        tp = np.zeros(k)
        n_c = np.zeros(k)
        for f in range(N_FOLD):
            tr, te = folds != f, folds == f
            if te.sum() == 0:
                continue
            mu, sd = X[tr].mean(axis=0), X[tr].std(axis=0) + 1e-9
            W = softmax_fit((X[tr] - mu) / sd, lab[tr], k)
            pr = predict(W, (X[te] - mu) / sd)
            for c in range(k):
                sel = lab[te] == c
                tp[c] += np.sum(pr[sel] == c)
                n_c[c] += sel.sum()
        balanced[name] = float(np.mean(tp / np.maximum(n_c, 1)))
    if verbose:
        for n, v in balanced.items():
            print(f"  repeat {seed}: {n:30s} {v:.4f}")
    return {"seed": seed, "balanced": balanced}


def main():
    D = Data()
    reps = [run_once(D, s, verbose=(s == 0)) for s in range(N_REPEATS)]
    names = list(reps[0]["balanced"])
    summary = {}
    for n in names:
        vals = np.array([r["balanced"][n] for r in reps])
        gains = np.array([r["balanced"][n] - r["balanced"]["gamma"] for r in reps])
        summary[n] = {"balanced_accuracy_mean": float(vals.mean()),
                      "balanced_accuracy_sd": float(vals.std(ddof=1)),
                      "gain_vs_gamma_mean": float(gains.mean()),
                      "gain_vs_gamma_ci95": [float(np.percentile(gains, 2.5)),
                                             float(np.percentile(gains, 97.5))],
                      "repeats_improved": int((gains > 0).sum())}
        print(f"{n:30s} {vals.mean():.4f} +/- {vals.std(ddof=1):.4f}  gain "
              f"{gains.mean():+.4f} [{np.percentile(gains, 2.5):+.4f}, "
              f"{np.percentile(gains, 97.5):+.4f}] improved "
              f"{(gains > 0).sum()}/{len(gains)}")

    C.save_json(C.PROC / "geology_multiclass.json", {
        "classes": list(CLASSES), "per_class": PER_CLASS,
        "chance": 1.0 / len(CLASSES), "block_px": BLOCK, "n_folds": N_FOLD,
        "n_repeats": N_REPEATS, "summary": summary, "repeats": reps,
        "note": "Multinomial logistic, 128-px spatial-block CV, balanced "
                "classes; each repeat redraws the subsample, the fold "
                "assignment and the block shuffle. No response matrix.",
    })
    with open(C.PROC / "geology_multiclass.csv", "w", newline="", encoding="utf-8") as fh:
        wri = csv.writer(fh)
        wri.writerow(["features", "balanced_accuracy_mean", "sd", "gain_vs_gamma",
                      "gain_ci_low", "gain_ci_high", "repeats_improved"])
        for n, s in summary.items():
            wri.writerow([n, s["balanced_accuracy_mean"], s["balanced_accuracy_sd"],
                          s["gain_vs_gamma_mean"], *s["gain_vs_gamma_ci95"],
                          s["repeats_improved"]])
    print("saved geology_multiclass.json/csv")


if __name__ == "__main__":
    main()
