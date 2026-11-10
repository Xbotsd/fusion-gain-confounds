"""Ten-run average for the corrected-EM model (1 % channel noise)."""
from __future__ import annotations

import csv

import numpy as np

import common as C


def main():
    z, H = C.load_emfix_inputs()
    mask = C.load_valid_mask()
    gt = C.load_clay_prior() > 0.55
    sigma = z.std(axis=(1, 2), keepdims=True) + 1e-6

    rows = []
    for seed in range(10):
        rng = np.random.default_rng(seed)
        zz = (z + rng.normal(0, 0.01 * sigma, z.shape)).astype(np.float32)
        x = C.fuse(zz, H)["x"]
        m = C.detection_metrics(x, gt, mask=mask)
        rows.append({"seed": seed, **m})
        print(f"seed {seed}: F1={m['f1']:.4f} R={m['recall']:.4f} "
              f"P={m['precision']:.4f} clay={m['clay_mean']:.4f}")

    keys = ["recall", "precision", "f1", "clay_mean"]
    summary = {k: {"mean": float(np.mean([r[k] for r in rows])),
                   "std": float(np.std([r[k] for r in rows], ddof=1))} for k in keys}
    C.save_json(C.PROC / "em_fix_repeats.json", {"rows": rows, "summary": summary})
    with open(C.PROC / "em_fix_repeats.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(summary)
    print("saved em_fix_repeats.json/csv")


if __name__ == "__main__":
    main()
