"""Step 7 - unified validation: one metric definition for every scenario.

Scenarios
  normal                 full tri-modal fusion
  leave-2-channels-out   5 folds, two observation channels hidden
  sensor degradation     noise injection + explicit quality down-weighting
  temperature            -60..+80 C, physics-based quality weights
  cross-domain           Wyoming-like target, direct transfer vs CORAL
  H sensitivity          response-matrix perturbation +/-30 %

All metrics are pixel recall / precision / F1 / IoU against
clay_prior > 0.55, computed on valid survey pixels only.  "Overall" is the
mean of the six scenario means and is labelled mean proxy recall, not a
detection rate.
"""
import csv
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import sqrtm

import common as C

EM_FIX = "--emfix" in sys.argv
SUFFIX = "_emfix" if EM_FIX else ""

TEMPS = [-60, -40, -25, 0, 25, 50, 70, 80]
FOLDS = [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)]
GAMMA_IDX, TIR_IDX, EM_IDX = [0, 1, 2], [3, 4, 5, 6], [7, 8, 9]


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


def modality_weights(w):
    return {
        "gamma": float(w[GAMMA_IDX].sum() / w.sum()),
        "tir": float(w[TIR_IDX].sum() / w.sum()),
        "em": float(w[EM_IDX].sum() / w.sum()),
    }


def run_case(label, z, H, mask, gt, truth, q=None, quality=None):
    res = C.fuse(z, H, channel_quality=q, quality=quality)
    m = C.detection_metrics(res["x"], gt, mask=mask)
    rec = C.recovery_metrics(res["x"], truth, mask=mask)["Clay"]
    row = {"case": label, **m, "rmse_truth": rec["rmse"], "r_truth": rec["r"],
           **modality_weights(res["weights"])}
    print(f"  {label:34s} R={m['recall']:.4f} P={m['precision']:.4f} "
          f"F1={m['f1']:.4f} clay={m['clay_mean']:.3f}")
    return row


def main():
    t0 = time.time()
    gamma, tir, em = C.load_cubes()
    z = C.build_observation(gamma, tir, em)
    mask = C.load_valid_mask()
    gt = C.load_clay_prior()
    truth = np.load(C.OUT / "truth_abundance.npy")
    H = C.H_MATRIX.copy()
    if EM_FIX:
        z[7:] = np.log10(np.clip(z[7:], 1.0, 1e5)).astype(np.float32)
        H[7:] = 0.0
        H[7:, C.TARGET] = C.EM_FIX_BETA
    rows = []

    # 1 normal ---------------------------------------------------------------
    print("\n[1/6] normal")
    normal = run_case("normal", z, H, mask, gt, truth)
    rows.append(normal)

    # 2 leave two channels out ----------------------------------------------
    print("\n[2/6] leave-2-channels-out")
    lcoo = []
    for fold, (a, b) in enumerate(FOLDS):
        q = np.ones(10, dtype=np.float32)
        q[[a, b]] = 0.0
        r = run_case(f"leave-out ch{a},{b}", z, H, mask, gt, truth, q=q)
        lcoo.append(r["recall"])
        rows.append(r)

    # 3 sensor degradation ---------------------------------------------------
    # NOTE: "normal" is already reported in step 1; it is NOT repeated here, so
    # that the sensor_degradation family mean is not contaminated by it.
    print("\n[3/6] sensor degradation")
    degradations = {
        "emi degraded x5": {7: 5.0, 8: 5.0, 9: 5.0},
        "emi failed x20": {7: 20.0, 8: 20.0, 9: 20.0},
        "tir degraded x5": {3: 5.0, 4: 5.0, 5: 5.0, 6: 5.0},
        "gamma degraded x5": {0: 5.0, 1: 5.0, 2: 5.0},
        "emi+tir failed": {3: 20.0, 4: 20.0, 5: 20.0, 6: 20.0, 7: 20.0, 8: 20.0, 9: 20.0},
    }
    deg = {}
    # explicit seeds so that adding/removing a scenario does not shift the
    # noise realisations of the others
    deg_seed = {"emi degraded x5": 43, "emi failed x20": 44,
                "tir degraded x5": 45, "gamma degraded x5": 46,
                "emi+tir failed": 47}
    for label, factors in degradations.items():
        zz = z.copy()
        for idx, f in factors.items():
            zz = add_noise(zz, [idx], f, seed=deg_seed[label])
        q = channel_quality(factors) if factors else None
        r = run_case(label, zz, H, mask, gt, truth, q=q)
        r["factors"] = factors
        deg[label] = r["recall"]
        rows.append(r)

    # 4 temperature ----------------------------------------------------------
    print("\n[4/6] temperature")
    temp_rows = []
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
        if EM_FIX:
            e = np.log10(np.clip(e, 1.0, 1e5))
        zz = np.concatenate([g, t, e], axis=0).astype(np.float32)
        q = np.array([gq] * 3 + [tq] * 4 + [eq] * 3, dtype=np.float32)
        r = run_case(f"T={T:>4}C", zz, H, mask, gt, truth, q=q)
        r["temperature"] = T
        r["quality"] = {"gamma": gq, "tir": tq, "em": eq}
        temp_rows.append(r)
        rows.append(r)

    # 5 cross-domain ---------------------------------------------------------
    print("\n[5/6] cross-domain")
    rng = np.random.default_rng(42)
    gt_t = gamma.copy()
    gt_t[0] = gamma[0] * 2.0 + rng.normal(0, 0.15, gamma.shape[1:])
    gt_t[1] = gamma[1] * 0.5 + rng.normal(0, 0.15, gamma.shape[1:])
    gt_t[2] = gamma[2] * 1.8 + rng.normal(0, 0.15, gamma.shape[1:])
    tt = tir * 0.85 + rng.normal(0, 0.02, tir.shape)
    et = em * 3.0 + rng.normal(0, 10.0, em.shape)
    if EM_FIX:
        et = np.log10(np.clip(et, 1.0, 1e5))
    z_tgt = np.concatenate(
        [gt_t, tt[list(C.TIR_BANDS)], et[list(C.EM_LAYERS)]], axis=0
    ).astype(np.float32)

    direct = run_case("target: direct transfer", z_tgt, H, mask, gt, truth)
    rows.append(direct)

    M = 10
    src_flat = z.reshape(M, -1)
    tgt_flat = z_tgt.reshape(M, -1)
    tgt_mean = tgt_flat.mean(axis=1, keepdims=True)
    Cs = np.cov(src_flat) + np.eye(M) * 1e-3
    Ct = np.cov(tgt_flat) + np.eye(M) * 1e-3
    A_coral = np.real(sqrtm(Cs)) @ np.linalg.inv(np.real(sqrtm(Ct)))
    z_coral = (A_coral @ (tgt_flat - tgt_mean)).reshape(z_tgt.shape).astype(np.float32)
    coral = run_case("target: CORAL", z_coral, H, mask, gt, truth)
    rows.append(coral)

    src_mean = C.fuse(z, H)["x"].mean(axis=(1, 2))
    x_direct = C.fuse(z_tgt, H)["x"]
    x_coral = C.fuse(z_coral, H)["x"]
    gap_direct = float(np.abs(x_direct.mean(axis=(1, 2)) - src_mean).mean() * 100)
    gap_coral = float(np.abs(x_coral.mean(axis=(1, 2)) - src_mean).mean() * 100)
    direct["domain_gap_pct"] = gap_direct
    coral["domain_gap_pct"] = gap_coral

    # 6 H sensitivity --------------------------------------------------------
    print("\n[6/6] H sensitivity")
    h_rows = []
    for p in (0.0, 0.05, 0.10, 0.15, 0.20, 0.30):
        rr = []
        for trial in range(5):
            rng = np.random.default_rng(trial)
            Hp = H * (1 + rng.uniform(-p, p, H.shape))
            res = C.fuse(z, Hp)
            m = C.detection_metrics(res["x"], gt, mask=mask)
            rr.append(m["recall"])
        r = {"case": f"H +/-{p*100:.0f}%", "perturbation": p,
             "recall": float(np.mean(rr)), "recall_std": float(np.std(rr))}
        h_rows.append(r)
        rows.append({"case": r["case"], "recall": r["recall"], "precision": np.nan,
                     "f1": np.nan, "clay_mean": np.nan})
        print(f"  +/-{p*100:>4.0f}%  R={r['recall']:.4f} +/- {r['recall_std']:.4f}")

    # summary ----------------------------------------------------------------
    family = {
        "normal": normal["recall"],
        "leave_channels_out": float(np.mean(lcoo)),
        "sensor_degradation": float(np.mean(list(deg.values()))),
        "temperature": float(np.mean([r["recall"] for r in temp_rows])),
        "cross_domain_coral": coral["recall"],
        "H_sensitivity": float(np.mean([r["recall"] for r in h_rows])),
    }
    overall = float(np.mean(list(family.values())))
    f1_family = [normal["f1"], np.nanmean([r["f1"] for r in rows if r["case"].startswith("leave")]),
                 np.nanmean([r["f1"] for r in rows if r["case"] in degradations]),
                 np.nanmean([r["f1"] for r in temp_rows]), coral["f1"], np.nan]
    overall_f1 = float(np.nanmean(f1_family))

    summary = {
        "definition": {
            "positive": "clay > 0.25 AND clay in top-2 minerals",
            "target": "clay_prior > 0.55 (gamma-derived alteration proxy)",
            "mask": "valid survey pixels (66.4%)",
            "overall": "mean of six scenario means; not a detection rate",
        },
        "family_recall": family,
        "overall_recall": overall,
        "overall_f1": overall_f1,
        "scenarios": rows,
        "temperature": temp_rows,
        "H_sensitivity": h_rows,
        "degradation": {k: {"recall": v} for k, v in deg.items()},
        "runtime_s": time.time() - t0,
    }
    C.save_json(C.OUT / ("validation" + SUFFIX + ".json"), summary)

    with open(C.OUT / ("validation" + SUFFIX + ".csv"), "w", newline="", encoding="utf-8") as f:
        keys = ["case", "recall", "precision", "f1", "iou", "clay_mean",
                "positive_rate", "rmse_truth", "r_truth", "gamma", "tir", "em"]
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    # markdown ---------------------------------------------------------------
    lines = [
        "# Validation results",
        "",
        "Positive = clay > 0.25 and clay in the top-2 minerals; target = "
        "`clay_prior > 0.55`; scored on valid survey pixels.",
        "",
        "| scenario | recall | precision | F1 | clay mean |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(f"| {r['case']} | {r['recall']:.4f} | "
                     f"{r['precision']:.4f} | {r['f1']:.4f} | {r['clay_mean']:.4f} |")
    lines += ["", "## Family means", "", "| family | recall |", "|---|---:|"]
    for k, v in family.items():
        lines.append(f"| {k} | {v:.4f} |")
    lines.append(f"| **overall (mean proxy recall)** | **{overall:.4f}** |")
    (C.OUT / ("validation" + SUFFIX + ".md")).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n" + "=" * 60)
    for k, v in family.items():
        print(f"{k:22s}: {v:.4f}")
    print(f"{'OVERALL (mean recall)':22s}: {overall:.4f}")
    print(f"runtime: {time.time()-t0:.1f} s")

    # figures ---------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    names = list(family)
    vals = list(family.values())
    axes[0].barh(names, vals, color="#2ca02c", alpha=0.85)
    axes[0].axvline(overall, color="red", ls="--", label=f"mean {overall:.3f}")
    axes[0].set_xlim(0, 1)
    axes[0].set_xlabel("Recall (proxy target)")
    axes[0].set_title("(a) Scenario recall")
    axes[0].legend()
    axes[0].grid(axis="x", alpha=0.3)
    axes[1].plot([r["temperature"] for r in temp_rows],
                 [r["recall"] for r in temp_rows], "o-", color="#d62728")
    axes[1].set_xlabel("Temperature (C)")
    axes[1].set_ylabel("Recall")
    axes[1].set_title("(b) Temperature sweep")
    axes[1].grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(C.OUT / ("validation" + SUFFIX + ".png"), dpi=300)
    plt.close()


if __name__ == "__main__":
    main()



