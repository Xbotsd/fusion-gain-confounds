"""Numbers quoted in Section 4.8 (corrected EM model)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

H = C.H_MATRIX
Hf = C.emfix_H()
Hn, Hfn = C.normalize_H(H), C.normalize_H(Hf)

print("legacy cond      %.1f" % np.linalg.cond(Hn))
print("corrected cond   %.1f" % np.linalg.cond(Hfn))

# EM rows in the normalised clay column
print("legacy EM clay weights   ", np.round(Hn[7:, C.TARGET], 4))
print("corrected EM clay weights", np.round(Hfn[7:, C.TARGET], 4))
print("corrected other minerals ", np.round(Hfn[7:].sum(axis=1), 4))

# per-channel mineral contrast (max-min) of the normalised matrix
for name, M in (("legacy", Hn), ("corrected", Hfn)):
    rng = M.max(axis=1) - M.min(axis=1)
    print(name, "EM contrast", np.round(rng[7:], 4),
          "TIR contrast", np.round(rng[3:7], 4))

# raw legacy EM clay rank: clay is the minimum resistivity per row?
print("legacy EM clay rank per row", [int(np.argsort(r).tolist().index(C.TARGET)) for r in H[7:]])
print("legacy EM clay/median ratio", np.round(H[7:, C.TARGET] / np.median(H[7:], axis=1), 3))

# resistivity span in the real EM cube
em = np.load(Path(C.PROC) / "em_cube.npy")
print("EM cube p1/p50/p99", np.round(np.percentile(em, [1, 50, 99]), 1))
print("EM log10 range", np.round(np.log10(np.percentile(em, [1, 99])), 2))
