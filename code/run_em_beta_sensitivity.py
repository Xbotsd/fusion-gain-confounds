"""Depth profile of the clay-only EM response: where beta comes from and how
much the corrected result depends on it.

The synthetic EM recipe (prepare_em.py) writes

    log10 rho_k = log10(median_k) + 0.50 * (0.55 * clay_z * exp(-d_k/250) + ...)

so the clay sensitivity of layer k decays as exp(-d_k/250).  Evaluating this at
the three sampled layer centres gives [1.000, 0.949, 0.377] after normalising to
the shallow layer; the rounded profile used in production is EM_FIX_BETA =
[0.90, 0.86, 0.36].

This script (a) prints the generator decay next to the production profile and
(b) sweeps four profiles through the full estimator, so a reader can see how
much of the gain is carried by the exact numbers.
"""
from __future__ import annotations

import csv

import numpy as np

import common as C

PROFILES = {
    "production [0.90, 0.86, 0.36]": np.array([0.90, 0.86, 0.36]),
    "generator decay exp(-d/250)": None,      # filled in main()
    "uniform [1, 1, 1]": np.ones(3),
    "reversed [0.36, 0.86, 0.90]": np.array([0.36, 0.86, 0.90]),
}


def main():
    top = np.load(C.ASSETS / "em_dep_top.npy")
    bot = np.load(C.ASSETS / "em_dep_bot.npy")
    mid = 0.5 * (top + bot)
    centres = mid[list(C.EM_LAYERS)]
    decay = np.exp(-centres / 250.0)
    decay = decay / decay[0]
    PROFILES["generator decay exp(-d/250)"] = decay

    gamma, tir, em = C.load_cubes()
    z = C.emfix_observation(C.build_observation(gamma, tir, em))
    mask = C.load_valid_mask()
    gt = C.load_clay_prior() > 0.55

    legacy = C.detection_metrics(C.fuse(C.build_observation(gamma, tir, em),
                                        C.H_MATRIX)["x"], gt, mask=mask)

    rows = []
    for name, beta in PROFILES.items():
        H = C.H_MATRIX.copy()
        H[7:] = 0.0
        H[7:, C.TARGET] = beta
        for kalman in (False, True):
            x = C.fuse(z, H, kalman=kalman)["x"]
            m = C.detection_metrics(x, gt, mask=mask)
            rows.append({
                "profile": name,
                "beta_shallow": float(beta[0]),
                "beta_mid": float(beta[1]),
                "beta_deep": float(beta[2]),
                "kalman": bool(kalman),
                "f1": m["f1"], "recall": m["recall"], "precision": m["precision"],
            })
            print(f"{name:32s} kalman={kalman!s:5s} "
                  f"F1={m['f1']:.4f} R={m['recall']:.4f} P={m['precision']:.4f}")

    f1s = [r["f1"] for r in rows]
    C.save_json(C.PROC / "em_beta_sensitivity_emfix.json", {
        "layer_centres_m": [float(v) for v in centres],
        "generator_decay": [float(v) for v in decay],
        "production_beta": C.EM_FIX_BETA,
        "legacy_f1": legacy["f1"],
        "rows": rows,
        "f1_min": float(min(f1s)),
        "f1_max": float(max(f1s)),
        "note": "Every profile uses log10 EM with clay-only rows; only the "
                "depth weight changes.",
    })
    with open(C.PROC / "em_beta_sensitivity_emfix.csv", "w", newline="",
              encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=list(rows[0]))
        wri.writeheader()
        wri.writerows(rows)
    print(f"legacy F1 {legacy['f1']:.4f}; corrected F1 range "
          f"{min(f1s):.4f}-{max(f1s):.4f}")
    print("saved em_beta_sensitivity_emfix.json/csv")


if __name__ == "__main__":
    main()
