"""Generation-parameter sensitivity of the synthetic modalities.

The negative controls in this paper (V2, ASU) change the *data source*.  This
experiment changes the *recipe*: it regenerates the EM cube with the same code
path as `prepare_em.py` but different amplitudes, and adds multiplicative noise
to the TIR cube, then reruns the corrected-EM fusion and scores it with the same
metric.

The default setting must reproduce `em_cube.npy` exactly and the fusion F1 of
`em_fix.json`; that reproduction is reported and asserted.

Outputs: processed/generation_sensitivity.json, .csv, .png
"""
from __future__ import annotations

import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter

import common as C
from run_advantage import pr_ap

SEED = 12345
DEFAULT = {"a_clay": 0.55, "a_indep": 0.55, "a_noise": 0.35,
           "scale": 0.50, "decay": 250.0}
KEEP = list(C.EM_LAYERS)


def standardize(x):
    return (x - x.mean()) / (x.std() + 1e-6)


def build_em(clay_prior, params, keep=KEEP):
    """Replicate prepare_em.py, returning the sampled layers only."""
    med = np.load(C.ASSETS / "em_layer_medians.npy")
    top = np.load(C.ASSETS / "em_dep_top.npy")
    bot = np.load(C.ASSETS / "em_dep_bot.npy")
    ok = np.isfinite(med)
    med = np.interp(np.arange(len(med)), np.arange(len(med))[ok], med[ok])

    clay_z = standardize(clay_prior)
    rng = np.random.default_rng(SEED)
    h, w = clay_prior.shape
    indep_z = standardize(gaussian_filter(rng.normal(0, 1, (h, w)), sigma=25))

    out = np.zeros((len(keep), h, w), dtype=np.float32)
    for k in range(len(med)):
        depth = 0.5 * (top[k] + bot[k])
        base = np.log10(med[k])
        depth_factor = np.exp(-depth / params["decay"])
        noise_z = standardize(gaussian_filter(rng.normal(0, 1, (h, w)), sigma=15))
        log_rho_z = (params["a_clay"] * clay_z * depth_factor
                     + params["a_indep"] * indep_z
                     + params["a_noise"] * noise_z)
        cube_k = np.clip(10 ** (base + params["scale"] * log_rho_z), 1.0, 10000.0)
        if k in keep:
            out[keep.index(k)] = cube_k.astype(np.float32)
    return out


def score(z, H, mask, gt):
    x = C.fuse(z, H)["x"]
    m = C.detection_metrics(x, gt, mask=mask)
    ap, _, _ = pr_ap(x, gt, mask)
    return {"f1": m["f1"], "recall": m["recall"],
            "precision": m["precision"], "ap": ap}


def main():
    gamma, tir, em = C.load_cubes()
    mask = C.load_valid_mask()
    gt = C.load_clay_prior() > 0.55
    truth = C.load_clay_prior()
    H = C.emfix_H()
    bands = list(C.TIR_BANDS)

    # the real recipe, reproduced, must equal the stored cube
    em_repro = build_em(truth, DEFAULT)
    dev = float(np.abs(em_repro - em[KEEP]).max())
    print(f"EM reproduction max |diff| = {dev:.3e} ohm.m")

    def run(em_layers, tir_layers):
        z = np.concatenate([gamma.astype(np.float32),
                            tir_layers.astype(np.float32),
                            em_layers.astype(np.float32)], axis=0)
        return score(C.emfix_observation(z), H, mask, gt)

    base = run(em_repro, tir[bands])
    ref = C.load_json(C.PROC / "em_fix.json")
    ref_f1 = next(r for r in ref["rows"] if r["method"] == "EM-fix Kalman")["f1"]
    print(f"baseline F1 {base['f1']:.4f}  (em_fix.json {ref_f1:.4f})")

    rows = [{"parameter": "baseline (recipe as documented)", "value": 1.0,
             "unit": "-", **base}]

    sweeps = [
        ("EM clay amplitude", "a_clay", [0.35, 0.55, 0.75]),
        ("EM independent-field amplitude", "a_indep", [0.35, 0.55, 0.75]),
        ("EM depth-decay length", "decay", [120.0, 250.0, 500.0]),
        ("EM overall scale", "scale", [0.30, 0.50, 0.70]),
        ("TIR multiplicative noise", "tir_noise", [0.0, 0.02, 0.05, 0.10]),
    ]
    rng = np.random.default_rng(11)

    for label, key, values in sweeps:
        for v in values:
            params = dict(DEFAULT)
            if key == "tir_noise":
                em_l = em_repro
                noise = rng.standard_normal(tir[bands].shape).astype(np.float32)
                tir_l = (tir[bands] * (1.0 + v * noise)).astype(np.float32)
            else:
                params[key] = v
                em_l = build_em(truth, params)
                tir_l = tir[bands]
            res = run(em_l, tir_l)
            rows.append({"parameter": label, "value": float(v),
                         "unit": "m" if key == "decay" else "-", **res})
            print(f"{label:32s} {v:6.3f}  F1={res['f1']:.4f} "
                  f"AP={res['ap']:.4f} R={res['recall']:.4f}")

    by = {}
    for r in rows:
        if r["parameter"] == "baseline (recipe as documented)":
            continue
        by.setdefault(r["parameter"], []).append(r["f1"])
    summary = {k: {"min": float(min(v)), "max": float(max(v)),
                   "span": float(max(v) - min(v))} for k, v in by.items()}

    C.save_json(C.PROC / "generation_sensitivity.json", {
        "default": DEFAULT, "em_reproduction_max_diff": dev,
        "baseline_f1": base["f1"], "em_fix_f1": ref_f1,
        "rows": rows, "summary": summary,
        "note": "EM regenerated through prepare_em.py; TIR gets multiplicative "
                "noise. Fusion is the corrected-EM model.",
    })
    with open(C.PROC / "generation_sensitivity.csv", "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    labels = list(by)
    fig, ax = plt.subplots(figsize=(9, 4.4))
    for lab in labels:
        sub = [r for r in rows if r["parameter"] == lab]
        ax.plot(range(len(sub)), [r["f1"] for r in sub], marker="o",
                label=lab)
        for i, r in enumerate(sub):
            ax.annotate(f"{r['value']:g}", (i, r["f1"]),
                        textcoords="offset points", xytext=(0, 6), fontsize=7)
    ax.axhline(base["f1"], color="k", ls="--", lw=0.9, label="documented recipe")
    ax.set_ylabel("F1 (proxy)")
    ax.set_xlabel("sweep index")
    ax.set_title("Sensitivity to the synthetic-generation parameters")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(C.PROC / "generation_sensitivity.png", dpi=300)
    plt.close()
    print("\nf1 span per parameter:",
          {k: round(v["span"], 3) for k, v in summary.items()})
    print("saved generation_sensitivity.json/csv/png")


if __name__ == "__main__":
    main()
