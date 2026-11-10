"""Scenario-level 128-px block bootstrap confidence intervals.

The validation scenarios (degradation, temperature, leave-2-out, cross-domain)
are reported as point estimates only in validation_emfix.json. This module
adds honest block-bootstrap 95 % CIs:

1. rebuilds each corrected-EM scenario exactly as run_validation.py --emfix
   (same seeds; the point estimates must match validation_emfix.json to 1e-9
   — a sync check fails loudly otherwise);
2. precomputes per-128-px-block TP/FP/FN counts (blocks >= 2x the measured
   53-px integral scale, see autocorr.json);
3. bootstraps the block counts (200 replicates) -> recall/F1 percentile CIs;
4. computes paired block-level deltas vs the normal scenario with BH-adjusted
   significance across the scenario family.

Outputs: processed/scenario_bootstrap.json/csv/png.
"""
from __future__ import annotations

import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import sqrtm
from scipy.ndimage import gaussian_filter

import common as C

BLOCK = 128
N_REP = 200
SEED = 2026

TEMPS = [-60, -40, -25, 0, 25, 50, 70, 80]
FOLDS = [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)]
DEGRADATIONS = {
    "emi degraded x5": {7: 5.0, 8: 5.0, 9: 5.0},
    "emi failed x20": {7: 20.0, 8: 20.0, 9: 20.0},
    "tir degraded x5": {3: 5.0, 4: 5.0, 5: 5.0, 6: 5.0},
    "gamma degraded x5": {0: 5.0, 1: 5.0, 2: 5.0},
    "emi+tir failed": {3: 20.0, 4: 20.0, 5: 20.0, 6: 20.0, 7: 20.0, 8: 20.0, 9: 20.0},
}


def add_noise(z, idx, factor, seed):
    if factor <= 1:
        return z
    rng = np.random.default_rng(seed)
    out = z.copy()
    for i in idx:
        out[i] += rng.normal(0, z[i].std() * (factor - 1) * 0.3, z[i].shape)
    return out


def channel_quality(factors):
    q = np.ones(10, dtype=np.float32)
    for idx, f in factors.items():
        q[idx] = 1.0 / f
    return q


# ---------------------------------------------------------------- scenarios
def build_scenarios(gamma, tir, em):
    """Yield (case, zz, q). Recipes are copied from run_validation.py --emfix;
    keep the two files in sync (the sync check below enforces it)."""
    z0 = C.build_observation(gamma, tir, em)
    zfix = C.emfix_observation(z0)
    H = C.emfix_H()
    out = []

    out.append(("normal", zfix, H, None))

    for a, b in FOLDS:
        q = np.ones(10, dtype=np.float32)
        q[[a, b]] = 0.0
        out.append((f"leave-out ch{a},{b}", zfix, H, q))

    deg_seed = {"emi degraded x5": 43, "emi failed x20": 44,
                "tir degraded x5": 45, "gamma degraded x5": 46,
                "emi+tir failed": 47}
    for label, factors in DEGRADATIONS.items():
        zz = zfix
        for idx, f in factors.items():
            zz = add_noise(zz, [idx], f, seed=deg_seed[label])
        q = channel_quality(factors) if factors else None
        out.append((label, zz, H, q))

    for T in TEMPS:
        rng = np.random.default_rng(42)
        dcr = 2 ** ((T - 25) / 8.0)
        if T < -25:
            tf = max(0.1, 1.0 - 0.05 * (-25 - T))
        elif T < -10:
            tf = 1.0 - 0.02 * (-10 - T)
        elif T > 45:
            tf = max(0.3, 1.0 - 0.03 * (T - 45))
        else:
            tf = 1.0
        if T > 25:
            eq = 1.0 - 0.003 * (T - 25)
        elif T < 0:
            eq = 1.0 - 0.005 * T
        else:
            eq = 1.0
        gq = 1.0 / (1.0 + 0.1 * np.sqrt(dcr))
        tq = tf / (1.0 + 0.02 * abs(T - 25))

        g = gamma + rng.normal(0, gamma.std() * 0.02 * np.sqrt(dcr), gamma.shape)
        t = tir[list(C.TIR_BANDS)] * tf + rng.normal(
            0, tir[list(C.TIR_BANDS)].std() * 0.03 * (1 + 0.02 * abs(T - 25)),
            (4, *gamma.shape[1:]))
        e = em[list(C.EM_LAYERS)] * (1 + 0.004 * (T - 25)) + rng.normal(
            0, em[list(C.EM_LAYERS)].std() * 0.02 / eq, (3, *gamma.shape[1:]))
        e = np.log10(np.clip(e, 1.0, 1e5))
        zz = np.concatenate([g, t, e], axis=0).astype(np.float32)
        q = np.array([gq] * 3 + [tq] * 4 + [eq] * 3, dtype=np.float32)
        out.append((f"T={T:>4}C", zz, H, q))

    # cross-domain
    rng = np.random.default_rng(42)
    gt_t = gamma.copy()
    gt_t[0] = gamma[0] * 2.0 + rng.normal(0, 0.15, gamma.shape[1:])
    gt_t[1] = gamma[1] * 0.5 + rng.normal(0, 0.15, gamma.shape[1:])
    gt_t[2] = gamma[2] * 1.8 + rng.normal(0, 0.15, gamma.shape[1:])
    tt = tir * 0.85 + rng.normal(0, 0.02, tir.shape)
    et = em * 3.0 + rng.normal(0, 10.0, em.shape)
    et = np.log10(np.clip(et, 1.0, 1e5))
    z_tgt = np.concatenate(
        [gt_t, tt[list(C.TIR_BANDS)], et[list(C.EM_LAYERS)]], axis=0
    ).astype(np.float32)
    out.append(("target: direct transfer", z_tgt, H, None))

    M = 10
    src_flat = zfix.reshape(M, -1)
    tgt_flat = z_tgt.reshape(M, -1)
    tgt_mean = tgt_flat.mean(axis=1, keepdims=True)
    Cs = np.cov(src_flat) + np.eye(M) * 1e-3
    Ct = np.cov(tgt_flat) + np.eye(M) * 1e-3
    A_coral = np.real(sqrtm(Cs)) @ np.linalg.inv(np.real(sqrtm(Ct)))
    z_coral = (A_coral @ (tgt_flat - tgt_mean)).reshape(z_tgt.shape).astype(np.float32)
    out.append(("target: CORAL", z_coral, H, None))
    return out


# ------------------------------------------------------------ block counts
def block_counts(pred, gt, mask, bid):
    """Per-block TP/FP/FN for the fixed decision rule."""
    nb = bid.max() + 1
    lab = bid.ravel()
    tp = np.bincount(lab, weights=(pred & gt).ravel(), minlength=nb)
    fp = np.bincount(lab, weights=(pred & ~gt).ravel(), minlength=nb)
    fn = np.bincount(lab, weights=((~pred) & gt).ravel(), minlength=nb)
    return tp.astype(np.int64), fp.astype(np.int64), fn.astype(np.int64)


def metrics_from_counts(tp, fp, fn):
    tp, fp, fn = tp.sum(), fp.sum(), fn.sum()
    rec = tp / max(tp + fn, 1)
    prec = tp / max(tp + fp, 1)
    f1 = 2 * prec * rec / max(prec + rec, 1e-12)
    return float(rec), float(prec), float(f1)


def main():
    gamma, tir, em = C.load_cubes()
    mask = C.load_valid_mask()
    gt_full = C.load_clay_prior() > 0.55

    h, w = mask.shape
    bid = (np.arange(h)[:, None] // BLOCK) * ((w + BLOCK - 1) // BLOCK) \
        + (np.arange(w)[None, :] // BLOCK)
    n_blocks = bid.max() + 1

    rng = np.random.default_rng(SEED)
    scen = build_scenarios(gamma, tir, em)

    # ---- sync check against validation_emfix.json --------------------------
    ve = C.load_json(C.PROC / "validation_emfix.json")
    ve_recall = {r["case"]: r["recall"] for r in ve["scenarios"]}
    ve_f1 = {r["case"]: r["f1"] for r in ve["scenarios"]}

    rows = []
    per_block = {}
    for case, zz, H, q in scen:
        res = C.fuse(zz, H, channel_quality=q)
        x = res["x"]
        pred = (x[C.TARGET] > 0.25) & C.topk_mask(x, 2)[C.TARGET] & mask
        gt = gt_full & mask
        if case in ve_recall:
            d = abs(C.detection_metrics(x, gt_full, mask=mask)["recall"]
                    - ve_recall[case])
            if d > 1e-9:
                raise SystemExit(f"sync check failed for {case}: recall delta {d}")
        tp, fp, fn = block_counts(pred, gt, mask, bid)
        r0, p0, f0 = metrics_from_counts(tp, fp, fn)
        reps = []
        for _ in range(N_REP):
            pick = rng.integers(0, n_blocks, n_blocks)
            reps.append(metrics_from_counts(tp[pick], fp[pick], fn[pick]))
        reps = np.array(reps)
        rows.append({
            "case": case, "recall": r0, "precision": p0, "f1": f0,
            "recall_ci95": [float(np.percentile(reps[:, 0], 2.5)),
                            float(np.percentile(reps[:, 0], 97.5))],
            "f1_ci95": [float(np.percentile(reps[:, 2], 2.5)),
                        float(np.percentile(reps[:, 2], 97.5))],
            "recall_block_std": float(reps[:, 0].std(ddof=1)),
        })
        per_block[case] = (tp, fp, fn)
        print(f"{case:22s} R={r0:.4f} [CI {rows[-1]['recall_ci95'][0]:.3f}, "
              f"{rows[-1]['recall_ci95'][1]:.3f}]  F1={f0:.4f}")

    # ---- paired deltas vs normal + BH correction ----------------------------
    ref = "normal"
    tp0, fp0, fn0 = per_block[ref]
    r_ref = metrics_from_counts(tp0, fp0, fn0)[0]
    deltas = []
    for case in [r["case"] for r in rows if r["case"] != ref]:
        tp, fp, fn = per_block[case]
        n = n_blocks
        # per-block recall difference (0 where no positives)
        with np.errstate(divide="ignore", invalid="ignore"):
            rb = np.where((tp + fn) > 0, tp / np.maximum(tp + fn, 1), np.nan)
            rb0 = np.where((tp0 + fn0) > 0, tp0 / np.maximum(tp0 + fn0, 1), np.nan)
        d = np.nan_to_num(rb - rb0, nan=0.0)
        boots = [float(d[rng.integers(0, n, n)].mean()) for _ in range(N_REP)]
        lo, hi = np.percentile(boots, [2.5, 97.5])
        p_emp = float(np.mean(np.array(boots) <= 0)) if np.mean(d) > 0 \
            else float(np.mean(np.array(boots) >= 0))
        deltas.append({"case": case, "delta_recall": float(np.mean(d)),
                       "ci95": [float(lo), float(hi)],
                       "p_bootstrap": min(p_emp * 2, 1.0)})

    # Benjamini-Hochberg across the scenario family
    m = len(deltas)
    order = np.argsort([d["p_bootstrap"] for d in deltas])
    for rank, i in enumerate(order):
        deltas[i]["p_bh"] = min(1.0, deltas[i]["p_bootstrap"] * m / (rank + 1))
        deltas[i]["significant_05"] = deltas[i]["p_bh"] < 0.05

    C.save_json(C.PROC / "scenario_bootstrap.json",
                {"block": BLOCK, "n_rep": N_REP, "rows": rows, "deltas": deltas})
    with open(C.PROC / "scenario_bootstrap.csv", "w", newline="",
              encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["case", "recall", "ci_low", "ci_high", "f1",
                     "f1_low", "f1_high", "delta_vs_normal", "p_bh"])
        dm = {d["case"]: d for d in deltas}
        for r in rows:
            d = dm.get(r["case"])
            wr.writerow([r["case"], round(r["recall"], 4),
                         round(r["recall_ci95"][0], 4), round(r["recall_ci95"][1], 4),
                         round(r["f1"], 4), round(r["f1_ci95"][0], 4),
                         round(r["f1_ci95"][1], 4),
                         round(d["delta_recall"], 4) if d else "",
                         round(d["p_bh"], 4) if d else ""])

    # ---- figure -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(13, 6))
    names = [r["case"] for r in rows]
    xs = np.arange(len(names))
    rec = [r["recall"] for r in rows]
    lo = [max(r["recall"] - r["recall_ci95"][0], 0.0) for r in rows]
    hi = [max(r["recall_ci95"][1] - r["recall"], 0.0) for r in rows]
    ax.errorbar(xs, rec, yerr=[lo, hi], fmt="o", capsize=3, lw=1, ms=4,
                color="#1f77b4", label="recall + 95 % block-bootstrap CI")
    ax.set_xticks(xs)
    ax.set_xticklabels(names, rotation=55, ha="right", fontsize=7)
    ax.set_ylabel("Recall (proxy target)")
    ax.set_title(f"Scenario recall with {BLOCK}-px block-bootstrap CIs "
                 f"({N_REP} replicates, corrected EM)")
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(C.PROC / "scenario_bootstrap.png", dpi=300)
    plt.close()
    print("saved scenario_bootstrap.json/csv/png (sync check passed)")


if __name__ == "__main__":
    main()
