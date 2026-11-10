"""Experiments 2-4: robustness of the real-ASTER-TIR conclusion.

* **2. Uncertainty** — 128-px block bootstrap (200 replicates) of the F1 gain of
  `gamma+TIR` over `gamma` on the real cube.
* **3. TES sensitivity** — the emissivity normalisation assumes a maximum
  emissivity; vary it (0.95 / 0.98 / 1.00) and drop the band whose emissivity
  retains a residual temperature correlation (11.29 µm).
* **4. Date sensitivity** — rebuild the cube from a second ASTER date that also
  covers the footprint (2006-09-25) and rerun.

Cubes are cached under `processed/real_cache/` so repeated runs do not re-download.

Outputs: processed/real_tir_robust.json, .csv, .png
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
WL = np.linspace(8.0, 14.0, 200)
ASTER_C = np.array([8.291, 8.634, 9.075, 10.657, 11.289])
ASTER_W = np.array([0.350, 0.350, 0.350, 0.700, 0.700])

VARIANTS = [
    ("baseline 2006-10-18", "2006-10-18", 0.98, False),
    ("eps_max 0.95", "2006-10-18", 0.95, False),
    ("eps_max 1.00", "2006-10-18", 1.00, False),
    ("no 11.29 um band", "2006-10-18", 0.98, True),
    ("second date 2006-09-25", "2006-09-25", 0.98, False),
]


def cached_cube(date, eps_max, drop5):
    CACHE.mkdir(parents=True, exist_ok=True)
    tag = hashlib.md5(f"{date}|{eps_max}|{drop5}".encode()).hexdigest()[:10]
    f = CACHE / f"tir_{date}_{tag}.npz"
    if f.exists():
        d = np.load(f, allow_pickle=True)
        return d["cube"], d["meta"].item()
    cube, meta = build_cube(date, eps_max=eps_max, drop_band5=drop5)
    np.savez_compressed(f, cube=cube, meta=np.array(meta, dtype=object))
    return cube, meta


def library_rows(centres, widths):
    rows = np.zeros((len(centres), C.N_MIN))
    for j, m in enumerate(C.MINERALS):
        sp = np.load(C.SPEC / f"{m}_TIR.npy").astype(np.float64)
        if sp.ndim > 1:
            sp = np.nanmean(sp, axis=0)
        for b, (c, w) in enumerate(zip(centres, widths)):
            sel = (WL >= c - w / 2) & (WL <= c + w / 2)
            rows[b, j] = float(np.nanmean(1.0 - sp[sel]))
    return rows


def score(cube, mask, gt, drop5):
    gamma, _tir, em = C.load_cubes()
    n_tir = cube.shape[0]
    z0 = np.concatenate([gamma, np.nan_to_num(cube, nan=0.5),
                         em[list(C.EM_LAYERS)]]).astype(np.float32)
    centers = ASTER_C[:4] if drop5 else ASTER_C
    widths = ASTER_W[:4] if drop5 else ASTER_W
    H = np.vstack([C.H_MATRIX[:3], library_rows(centers, widths),
                   C.H_MATRIX[7:]])
    H[3 + n_tir:] = 0.0
    H[3 + n_tir:, C.TARGET] = C.EM_FIX_BETA
    z = C.emfix_observation(z0)
    out = {}
    for cfg, idx in (("gamma", [0, 1, 2]),
                     ("gamma+tir", list(range(3 + n_tir))),
                     ("all", list(range(z.shape[0])))):
        active = np.zeros(z.shape[0], dtype=np.float32)
        active[idx] = 1.0
        x = C.fuse(z, H, channel_quality=active)["x"]
        m = C.detection_metrics(x, gt, mask=mask)
        ap, _, _ = pr_ap(x, gt, mask)
        out[cfg] = {"f1": m["f1"], "ap": ap, "recall": m["recall"],
                    "precision": m["precision"],
                    "clay": float(x[C.TARGET][mask].mean()),
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
        pick = rng.choice(blocks, size=len(blocks), replace=True)
        mm = np.isin(bid, pick) & mask
        vals = []
        for p in (pred_a, pred_b):
            pp = p[mm]
            y = gt[mm]
            tp = np.sum(pp & y)
            fp = np.sum(pp & ~y)
            fn = np.sum(~pp & y)
            vals.append(2 * tp / max(2 * tp + fp + fn, 1))
        d.append(vals[1] - vals[0])
    d = np.array(d)
    return {"delta_mean": float(d.mean()),
            "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
            "p_better": float(np.mean(d > 0))}


def main():
    gamma, _tir, em = C.load_cubes()
    mask = C.load_valid_mask()
    gt = C.load_clay_prior() > 0.55

    rows, boot, metas = [], {}, {}
    for name, date, eps, drop5 in VARIANTS:
        cube, meta = cached_cube(date, eps, drop5)
        metas[name] = {"date": date, "eps_max": eps, "drop_band5": drop5,
                       "bands": meta["bands_um"],
                       "coverage": meta["coverage_after_mask"]}
        r = score(cube, mask, gt, drop5)
        for cfg in ("gamma", "gamma+tir", "all"):
            rows.append({"variant": name, "config": cfg,
                         "f1": r[cfg]["f1"], "ap": r[cfg]["ap"],
                         "recall": r[cfg]["recall"],
                         "precision": r[cfg]["precision"],
                         "clay": r[cfg]["clay"]})
        print(f"{name:24s} gamma {r['gamma']['f1']:.4f}  "
              f"gamma+tir {r['gamma+tir']['f1']:.4f}  all {r['all']['f1']:.4f}")
        if name.startswith("baseline"):
            boot = bootstrap(r["gamma"]["_pred"], r["gamma+tir"]["_pred"], gt, mask)

    C.save_json(C.PROC / "real_tir_robust.json", {
        "variants": metas, "rows": rows, "bootstrap": boot,
        "note": "Corrected-EM model; real ASTER TIR throughout. Bootstrap is "
                "gamma+TIR minus gamma on the baseline cube.",
    })
    with open(C.PROC / "real_tir_robust.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    fig, ax = plt.subplots(figsize=(9, 4.4))
    names = [v[0] for v in VARIANTS]
    for i, cfg in enumerate(("gamma", "gamma+tir", "all")):
        vals = [next(r["f1"] for r in rows if r["variant"] == n and r["config"] == cfg)
                for n in names]
        ax.bar(np.arange(len(names)) + (i - 1) * 0.27, vals, 0.27, label=cfg)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=20, ha="right", fontsize=8)
    ax.set_ylabel("F1")
    ax.set_title("Real ASTER TIR: TES, band and date sensitivity")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.savefig(C.PROC / "real_tir_robust.png", dpi=300)
    plt.close()
    print("bootstrap:", boot)
    print("saved real_tir_robust.json/csv/png")


if __name__ == "__main__":
    main()
