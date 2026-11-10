"""Unit tests for the core numerical functions (run with the geo env).

Run:  python code\\test_core.py
Exits 0 when all tests pass. No pytest dependency.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f"  {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


def test_project_simplex():
    # semantics: non-negative, normalised along axis 0 (per-pixel column)
    x = np.zeros((5, 2, 2), dtype=np.float32)
    x[:, 0, 0] = [0.3, -0.2, 0.9, 0.1, 0.4]   # -> [0.25, 0, 0.75, 1/12, 1/3]
    x[:, 1, 0] = 1.0                            # uniform column
    x[:, 0, 1] = -1.0                           # all-negative -> stays zero
    p = C.project_simplex(x)
    check("simplex: pixel sums are 1 (non-empty pixels)",
          np.allclose([p[:, 0, 0].sum(), p[:, 1, 0].sum()], 1.0),
          f"sums {p[:, 0, 0].sum()}, {p[:, 1, 0].sum()}")
    check("simplex: non-negative", (p >= 0).all())
    check("simplex: uniform column -> 1/5 each",
          np.allclose(p[:, 1, 0], 0.2))
    check("simplex: empty pixel stays zero", np.allclose(p[:, 0, 1], 0.0))
    check("simplex: negative clipped",
          abs(p[1, 0, 0]) < 1e-9, str(p[1, 0, 0]))


def test_detection_metrics():
    gt = np.zeros((4, 4), dtype=bool)
    gt[0, :2] = True  # 2 positives
    x = np.zeros((5, 4, 4), dtype=np.float32)
    x[C.TARGET, 0, 0] = 0.9   # hit (clay top)
    x[C.TARGET, 1, 1] = 0.02  # miss (clay < 0.25)
    # (2,2): clay 0.9 but quartz AND feldspar higher -> clay rank 3 -> excluded
    x[0, 2, 2] = 0.95
    x[1, 2, 2] = 0.92
    x[C.TARGET, 2, 2] = 0.9
    x[C.TARGET, 3, 3] = 0.5    # false positive (clay top, not in gt)
    m = C.detection_metrics(x, gt)
    check("metrics: recall = 1/2", abs(m["recall"] - 0.5) < 1e-9, str(m["recall"]))
    check("metrics: precision = 1/2", abs(m["precision"] - 0.5) < 1e-9,
          str(m["precision"]))
    check("metrics: f1 harmonic", abs(m["f1"] - 0.5) < 1e-9, str(m["f1"]))


def test_emfix_helpers():
    z = np.ones((10, 4, 4), dtype=np.float32)
    z[7:] = 100.0  # 100 ohm.m
    ze = C.emfix_observation(z)
    check("emfix: log10 applied", np.allclose(ze[7:], 2.0))
    check("emfix: gamma untouched", np.allclose(ze[:3], 1.0))
    H = C.emfix_H()
    check("emfix H: EM rows zero except clay",
          np.allclose(H[7:, [0, 1, 3, 4]], 0.0))
    check("emfix H: clay response", np.allclose(H[7:, C.TARGET], C.EM_FIX_BETA))
    check("emfix H: H_MATRIX not mutated",
          not np.allclose(C.H_MATRIX[7:, C.TARGET], C.EM_FIX_BETA))
    H2 = C.emfix_H(C.H_MATRIX * 2)
    check("emfix H: explicit H used", np.allclose(H2[:3], C.H_MATRIX[:3] * 2))


def test_zscore_normalize():
    rng = np.random.default_rng(1)
    z = rng.normal(5, 2, (10, 32, 32)).astype(np.float32)
    zn = C.zscore(z)
    check("zscore: mean ~0", abs(zn.mean()) < 0.1, str(zn.mean()))
    check("zscore: std ~1", abs(zn.std() - 1) < 0.1, str(zn.std()))
    check("zscore: clip bounded", np.abs(zn).max() <= 3.0 + 1e-6)


def test_load_valid_mask():
    m = C.load_valid_mask()
    check("mask: dtype bool", m.dtype == bool, str(m.dtype))
    check("mask: fraction in range", 0.05 < m.mean() < 0.99, str(m.mean()))
    check("mask: expected shape", m.shape == (1772, 1075), str(m.shape))


def test_save_load_json():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "t.json"
        obj = {"a": 1.5, "b": [1, 2, 3], "c": "x"}
        C.save_json(p, obj)
        import json
        back = json.loads(p.read_text(encoding="utf-8"))
        check("json: roundtrip", back == obj)


def test_fuse_shapes():
    rng = np.random.default_rng(2)
    z = rng.normal(0, 1, (10, 24, 24)).astype(np.float32)
    res = C.fuse(z, kalman=True)
    x, P = res["x"], res["P"]
    check("fuse: x shape", x.shape == (5, 24, 24), str(x.shape))
    check("fuse: P shape", P.shape == (5, 24, 24), str(P.shape))
    check("fuse: simplex on sample",
          np.allclose(x[:, 0, 0].sum(), 1.0, atol=1e-4),
          str(x[:, 0, 0].sum()))
    check("fuse: inactive rows do not change the estimate",
          np.allclose(
              C.fuse(z, C.H_MATRIX, channel_quality=np.array(
                  [1, 1, 1, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32))["x"],
              C.fuse(z, C.emfix_H(), channel_quality=np.array(
                  [1, 1, 1, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32))["x"],
              atol=1e-9))
    check("fuse: P non-negative", (P >= -1e-6).all())
    # switching a channel off must be identical to deleting it: neither the
    # column normalisation nor the effective ridge strength may depend on the
    # number of inactive channels
    off = np.array([1, 1, 1, 0, 0, 0, 0, 0, 0, 0], dtype=np.float32)
    x_off = C.fuse(z, C.H_MATRIX, channel_quality=off)["x"]
    x_del = C.fuse(z[:3], C.H_MATRIX[:3])["x"]
    check("fuse: switching channels off == deleting them",
          np.allclose(x_off, x_del, atol=1e-6),
          f"max diff {np.abs(x_off - x_del).max():.2e}")


def test_layouts():
    real = C.layout("real")
    syn = C.layout("synthetic")
    check("layout: real has 11 channels", real.n == 11, str(real.n))
    check("layout: synthetic has 10 channels", syn.n == 10, str(syn.n))
    check("layout: EM is the last block",
          real.em == [8, 9, 10] and syn.em == [7, 8, 9])
    check("layout: real TIR rows from library (not hand-set)",
          not np.allclose(real.H[3:7], C.H_MATRIX[3:7]))
    q = real.H[real.tir][:, C.MINERALS.index("Quartz")]
    check("layout: quartz reststrahlen dip in 8-9.5 um",
          q[:3].max() < 0.5 and q[3:].min() > 0.85, str(np.round(q, 3)))
    Hf = real.H_emfix()
    check("layout: emfix rows clay-only",
          np.allclose(np.delete(Hf[real.em], C.TARGET, axis=1), 0.0)
          and np.allclose(Hf[real.em, C.TARGET], C.EM_FIX_BETA))
    z = np.ones((11, 4, 4), dtype=np.float32) * 100.0
    ze = C.emfix_observation(z, real.em_slice)
    check("layout: emfix log only on EM block",
          np.allclose(ze[real.em], 2.0) and np.allclose(ze[:8], 100.0))


def test_auc():
    s = np.array([0.1, 0.4, 0.35, 0.8])
    y = np.array([False, False, True, True])
    check("auc: textbook value 0.75", abs(C.auc_score(s, y) - 0.75) < 1e-12,
          str(C.auc_score(s, y)))
    check("auc: perfect = 1", C.auc_score(np.arange(6.0), np.arange(6) >= 3) == 1.0)


def main():
    for fn in (test_project_simplex, test_detection_metrics, test_emfix_helpers,
               test_zscore_normalize, test_load_valid_mask, test_save_load_json,
               test_fuse_shapes, test_layouts, test_auc):
        fn()
    print()
    if FAILURES:
        print(f"FAILED ({len(FAILURES)}): {FAILURES}")
        sys.exit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
