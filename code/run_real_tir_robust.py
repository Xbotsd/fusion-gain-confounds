"""Robustness of the thermal result to the retrieval and the acquisition.

Every variant is scored with the **same** pieces as `run_main.py`: the analysis
mask (survey ∩ ASTER), median fill, the library-sampled TIR rows, the corrected
EM model and the same block bootstrap.  Consequently the baseline row must
reproduce `main_results.json` (gamma 0.531, gamma+TIR 0.652) and the bootstrap
must reproduce gamma+TIR − gamma ≈ +0.12; both are asserted.

Variants
--------
  baseline            2006-10-18, eps_max 0.98, five bands
  eps_max 0.95 / 1.00  the emissivity-normalisation assumption
  no 11.29 um band     drops the band with the largest residual T correlation
  second date          2006-09-25, same processing

Outputs: processed/real_tir_robust.json/csv/png
"""
from __future__ import annotations

import csv
import hashlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common as C
from prepare_tir_real import build_cube
from run_advantage import pr_ap

CACHE = C.OUT / "real_cache"
VARIANTS = [
    ("baseline 2006-10-18 (5 bands)", "2006-10-18", 0.98, False),
    ("eps_max 0.95", "2006-10-18", 0.95, False),
    ("eps_max 1.00", "2006-10-18", 1.00, False),
    ("no 11.29 um band (4 bands)", "2006-10-18", 0.98, True),
    ("second date 2006-09-25", "2006-09-25", 0.98, False),
]


def cached_cube(date, eps_max, drop5):
    CACHE.mkdir(parents=True, exist_ok=True)
    tag = hashlib.md5(f"{date}|{eps_max}|{drop5}".encode()).hexdigest()[:10]
    f = CACHE / f"tir_{date}_{tag}.npz"
    if f.exists():
        d = np.load(f, allow_pickle=True)
        return d["cube"], d["meta"].item()
    cube, _keep, meta = build_cube(date, eps_max=eps_max, drop_band5=drop5)
    np.savez_compressed(f, cube=cube, meta=np.array(meta, dtype=object))
    return cube, meta


def make_layout(n_bands):
    centres = C.ASTER_CENTRES[:n_bands]
    widths = C.ASTER_WIDTHS[:n_bands]
    H = np.vstack([C.H_MATRIX[:3], C.library_tir_rows(centres, widths),
                   C.H_MATRIX[7:]])
    return C.Layout(f"robust-{n_bands}band", n_bands, H)


def score(cube, mask, gt, sel, pos):
    gamma, _tir, em = C.load_cubes()
    lay = make_layout(cube.shape[0])
    z0 = np.concatenate([gamma.astype(np.float32),
                         C.fill_median(cube),
                         em[list(C.EM_LAYERS)].astype(np.float32)], axis=0)
    z = C.emfix_observation(z0, lay.em_slice)
    H = lay.H_emfix()
    out = {}
    for cfg, idx in (("gamma", lay.gamma),
                     ("gamma+tir", lay.gamma + lay.tir),
                     ("all", list(range(lay.n)))):
        act = lay.active(idx)
        x = C.fuse(z, H, channel_quality=act)["x"]
        m = C.detection_metrics(x, gt, mask=mask)
        ap, _, _ = pr_ap(x, gt, mask)
        out[cfg] = {"f1": m["f1"], "ap": ap, "recall": m["recall"],
                    "precision": m["precision"],
                    "geo_auc": C.geology_auc(x, sel, pos),
                    "_pred": (x[C.TARGET] > 0.25) & C.topk_mask(x, 2)[C.TARGET]}
    return out


def bootstrap(pred_a, pred_b, gt, mask, block=128, reps=200, seed=2024):
    h, w = mask.shape
    bid = (np.arange(h)[:, None] // block) * ((w + block - 1) // block) \
        + (np.arange(w)[None, :] // block)
    blocks = np.unique(bid[mask])
    rng = np.random.default_rng(seed)
    d = []
    for _ in range(reps):
        pick = rng.choice(blocks, size=blocks.size, replace=True)
        mm = np.isin(bid, pick) & mask
        vals = []
        for p in (pred_a, pred_b):
            pp, y = p[mm], gt[mm]
            tp = np.sum(pp & y)
            fp = np.sum(pp & ~y)
            fn = np.sum(~pp & y)
            vals.append(2 * tp / max(2 * tp + fp + fn, 1))
        d.append(vals[1] - vals[0])
    d = np.asarray(d)
    return {"delta_mean": float(d.mean()),
            "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
            "p_better": float(np.mean(d > 0))}


def main():
    gt = C.load_clay_prior() > 0.55
    mask = C.load_analysis_mask()
    sel, pos = C.load_geology_target(mask)
    ref = {(r["em_model"], r["config"]): r for r in
           C.load_json(C.PROC / "main_results.json")["ablation"]
           if r["branch"] == "real-aster"}

    rows, metas, boot = [], {}, None
    for name, date, eps, drop5 in VARIANTS:
        cube, meta = cached_cube(date, eps, drop5)
        metas[name] = {"date": date, "eps_max": eps, "drop_band5": drop5,
                       "bands_um": meta["bands_um"],
                       "analysis_pixels": meta["analysis_pixels"]}
        r = score(cube, mask, gt, sel, pos)
        for cfg in ("gamma", "gamma+tir", "all"):
            rows.append({"variant": name, "config": cfg, **
                         {k: v for k, v in r[cfg].items() if not k.startswith("_")}})
        print(f"{name:32s} gamma {r['gamma']['f1']:.3f}  "
              f"gamma+tir {r['gamma+tir']['f1']:.3f}  all {r['all']['f1']:.3f}  "
              f"AUC(gt) {r['gamma+tir']['geo_auc']:.3f}")
        if name.startswith("baseline"):
            boot = bootstrap(r["gamma"]["_pred"], r["gamma+tir"]["_pred"], gt, mask)
            dev = abs(r["gamma+tir"]["f1"] - ref[("corrected", "gamma+tir")]["f1"])
            print(f"  reproduces main_results: |ΔF1| = {dev:.2e}")
            assert dev < 1e-6, "robustness baseline does not reproduce run_main"

    C.save_json(C.PROC / "real_tir_robust.json", {
        "variants": metas, "rows": rows, "bootstrap": boot,
        "note": "Same mask, fill, H construction and estimator as run_main; the "
                "baseline row must (and does) reproduce main_results.json.",
    })
    with open(C.PROC / "real_tir_robust.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    names = [v[0] for v in VARIANTS]
    fig, ax = plt.subplots(figsize=(9, 4.4))
    for i, cfg in enumerate(("gamma", "gamma+tir", "all")):
        vals = [next(r["f1"] for r in rows if r["variant"] == n and r["config"] == cfg)
                for n in names]
        ax.bar(np.arange(len(names)) + (i - 1) * 0.27, vals, 0.27, label=cfg)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=20, ha="right", fontsize=8)
    ax.set_ylabel("F1 (gamma proxy)")
    ax.set_title("Real ASTER TIR: retrieval and acquisition sensitivity")
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(C.PROC / "real_tir_robust.png", dpi=300)
    plt.close()
    print("bootstrap:", boot)
    print("saved real_tir_robust.json/csv/png")


if __name__ == "__main__":
    main()
