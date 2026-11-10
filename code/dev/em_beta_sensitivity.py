"""Does the corrected-EM result depend on the beta values? (Section 4.8)"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

top = np.load(C.ASSETS / "em_dep_top.npy")
bot = np.load(C.ASSETS / "em_dep_bot.npy")
mid = 0.5 * (top + bot)
print("layer centres", np.round(mid[[0, 15, 35]], 1))
decay = np.exp(-mid[[0, 15, 35]] / 250.0)
print("generator decay e^-d/250", np.round(decay, 4))
print("normalised", np.round(decay / decay[0], 3))

gamma, tir, em = C.load_cubes()
z0 = C.build_observation(gamma, tir, em)
z = C.emfix_observation(z0)
mask, gt = C.load_valid_mask(), C.load_clay_prior() > 0.55

sets = {
    "legacy beta [0.90,0.86,0.36]": np.array([0.90, 0.86, 0.36]),
    "uniform [1,1,1]": np.ones(3),
    "generator decay": decay / decay[0],
    "reversed [0.36,0.86,0.90]": np.array([0.36, 0.86, 0.90]),
    "clay-only uniform, all 40": None,
}
for name, beta in sets.items():
    if beta is None:
        continue
    H = C.H_MATRIX.copy()
    H[7:] = 0.0
    H[7:, C.TARGET] = beta
    for kal in (False, True):
        x = C.fuse(z, H, kalman=kal)["x"]
        m = C.detection_metrics(x, gt, mask=mask)
        print(f"{name:30s} kalman={kal!s:5s} F1={m['f1']:.4f} R={m['recall']:.4f} P={m['precision']:.4f}")
