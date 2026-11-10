"""EM-only diagnostic: does the legacy row pull clay the wrong way?"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

gamma, tir, em = C.load_cubes()
z0 = C.build_observation(gamma, tir, em)
mask = C.load_valid_mask()
truth = C.load_clay_prior()

H = C.H_MATRIX
Hf = C.emfix_H()
# EM block only (rows 7:)
z_em_raw = z0[7:]
z_em_log = np.log10(np.clip(z_em_raw, 1.0, 1e5))
H_em_legacy = H[7:]
H_em_fix = Hf[7:]


def wls_only(zblock, Hblock):
    zn = np.array([(c - c.mean()) / (c.std() + 1e-6) for c in zblock])
    Hn = C.normalize_H(Hblock)
    return C.wls_global(zn, Hn, np.ones(len(zblock)), lam=0.1)


for tag, zb, Hb in (("legacy EM rows, raw ohm.m", z_em_raw, H_em_legacy),
                    ("legacy H, log10 ohm.m", z_em_log, H_em_legacy)):
    x = wls_only(zb, Hb)
    c = x[C.TARGET][mask]
    t = truth[mask]
    print(f"{tag:28s} corr(clay, truth) = {np.corrcoef(c, t)[0,1]:+.3f}  "
          f"mean clay = {c.mean():.3f}")
    m = C.detection_metrics(x, truth > 0.55, mask=mask)
    print(f"{'':28s} F1 = {m['f1']:.4f}  R = {m['recall']:.4f}")
