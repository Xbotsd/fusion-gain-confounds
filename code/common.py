"""Shared constants, data I/O and evaluation utilities.

Data reality (see docs/DATA_PROVENANCE.md):
  * gamma : real USGS airborne radiometric survey, Ivanpah / Clark Mtn, NV-CA,
            2019-12-13 .. 2020-03-21 (631 lines, 295,943 samples at 1 Hz)
  * TIR   : REAL ASTER L1T emissivity, 5 bands, 2006-10-18 (main line);
            the synthetic splib07 cube is kept only as a control
  * EM    : synthetic, Wisconsin AEM layer statistics + controlled correlated
            field (no measured AEM exists for this survey)
  * geology: real USGS SIM 3206 surficial map (independent target)

Model note: the inversion uses *standardised* channel vectors and *column-
normalised* mineral signatures (normalised over the active channels).  It is a
relative-signature mixture model, not an absolute concentration inversion.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter, uniform_filter

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
PROC = Path(os.environ.get("AMPROC", ROOT / "processed"))
OUT = Path(os.environ.get("AMOUT", PROC))
DOCS = ROOT / "docs"
ASSETS = ROOT / "processed"          # read-only assets (spectra, AEM stats)
SPEC = ASSETS / "spectra"

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------
MINERALS = ("Quartz", "Feldspar", "Clay", "Calcite", "Dolomite")
TARGET = MINERALS.index("Clay")
N_MIN = len(MINERALS)

TIR_BANDS = (20, 53, 110, 150)
TIR_WAVELENGTHS = (8.6, 9.6, 11.3, 12.5)
EM_LAYERS = (0, 15, 35)
EM_LAYER_LABELS = ("shallow", "mid", "deep")

# The single response matrix used by every experiment.  Clay is K-rich and
# Th-poor (hydrothermal illite) and electrically conductive.  The draft's
# ablation script used a different matrix; the discrepancy is documented in
# docs/MODEL_AUDIT.md.
H_MATRIX = np.array(
    [
        [0.5, 1.5, 4.0, 0.3, 0.3],       # K [%]
        [2.0, 1.0, 1.5, 2.0, 1.0],       # eU [ppm]
        [1.0, 1.5, 1.0, 1.0, 0.5],       # eTh [ppm]
        [0.92, 0.85, 0.88, 0.80, 0.82],  # TIR 8.6 um
        [0.95, 0.92, 0.90, 0.90, 0.88],  # TIR 9.6 um
        [0.85, 0.90, 0.92, 0.95, 0.93],  # TIR 11.3 um
        [0.90, 0.88, 0.90, 0.92, 0.94],  # TIR 12.5 um
        [100.0, 200.0, 20.0, 500.0, 400.0],  # EM shallow [ohm.m]
        [80.0, 150.0, 15.0, 600.0, 500.0],   # EM mid
        [120.0, 180.0, 25.0, 800.0, 700.0],  # EM deep
    ],
    dtype=np.float64,
)

# --------------------------------------------------------------------------
# I/O
# --------------------------------------------------------------------------
def read_gxf(path: Path | str) -> np.ndarray:
    """Read a single-band GXF grid (ReadRaster avoids gdal_array)."""
    try:
        from osgeo import gdal
    except ImportError as exc:
        raise ImportError(
            "GDAL (osgeo) is required to read GXF grids. Activate the `geo` "
            "conda environment or install GDAL, e.g. "
            "`conda activate geo` / `pip install GDAL`. "
            f"Current interpreter: {sys.executable}"
        ) from exc

    gdal.UseExceptions()
    ds = gdal.Open(str(path), gdal.GA_ReadOnly)
    if ds is None:
        raise IOError(f"cannot open {path}")
    band = ds.GetRasterBand(1)
    w, h = ds.RasterXSize, ds.RasterYSize
    buf = band.ReadRaster(0, 0, w, h, buf_type=gdal.GDT_Float32)
    arr = np.frombuffer(buf, dtype=np.float32).reshape(h, w).copy()
    nodata = band.GetNoDataValue()
    if nodata is not None:
        arr[arr == nodata] = np.nan
    arr[(arr < -1e30) | (arr > 1e30)] = np.nan
    ds = None
    return arr


def load_gamma_planes() -> np.ndarray:
    return np.stack([read_gxf(RAW / f"{n}.gxf") for n in ("K", "eU", "eTh")], axis=0)


def normalize_p2p98(x: np.ndarray) -> np.ndarray:
    valid = np.isfinite(x)
    out = np.full_like(x, 0.5, dtype=np.float32)
    if np.any(valid):
        p2, p98 = np.nanpercentile(x[valid], [2, 98])
        out[valid] = np.clip((x[valid] - p2) / (p98 - p2 + 1e-6), 0.0, 1.0)
    return out


def clay_prior_from_gamma(gamma: np.ndarray) -> np.ndarray:
    """Alteration proxy derived from K/eTh/eU (not independent truth)."""
    k, u, th = (normalize_p2p98(gamma[i]) for i in range(3))
    prior = 0.5 * k + 0.3 * (1.0 - th) + 0.2 * np.abs(u - th)
    prior = gaussian_filter(prior, sigma=15)
    return np.clip(prior, 0.0, 1.0).astype(np.float32)


def load_clay_prior(proc: Path | str | None = None) -> np.ndarray:
    proc = Path(proc or PROC)
    path = proc / "clay_prior.npy"
    if path.exists():
        return np.load(path)
    prior = clay_prior_from_gamma(load_gamma_planes())
    np.save(path, prior)
    return prior


def load_valid_mask(proc: Path | str | None = None) -> np.ndarray:
    proc = Path(proc or PROC)
    path = proc / "valid_mask.npy"
    if path.exists():
        m = np.load(path)
        if m.dtype != bool:
            raise ValueError(f"valid_mask dtype {m.dtype}, expected bool")
        if not (0.05 < m.mean() < 0.99):
            raise ValueError(f"valid_mask fraction {m.mean():.3f} outside 0.05-0.99")
        return m
    gamma = np.load(proc / "gamma_cube.npy")
    return np.isfinite(gamma).all(axis=0)


def _check_cube(a: np.ndarray, name: str) -> np.ndarray:
    """Basic reliability checks for a loaded data cube."""
    if a.ndim != 3:
        raise ValueError(f"{name}: expected 3-D cube, got shape {a.shape}")
    finite = np.isfinite(a).mean()
    if finite < 0.5:
        raise ValueError(f"{name}: only {finite:.1%} finite values")
    return a


def load_cubes(proc: Path | str | None = None):
    proc = Path(proc or PROC)
    gamma = _check_cube(np.load(proc / "gamma_cube.npy").astype(np.float32), "gamma_cube")
    for i in range(gamma.shape[0]):
        ch = gamma[i]
        gamma[i] = np.where(np.isfinite(ch), ch, np.nanmedian(ch))
    tir = _check_cube(np.load(proc / "tir_cube.npy").astype(np.float32), "tir_cube")
    tir = np.nan_to_num(tir, nan=0.5)
    em = _check_cube(np.load(proc / "em_cube.npy").astype(np.float32), "em_cube")
    em = np.nan_to_num(em, nan=100.0)
    if not (gamma.shape[1:] == tir.shape[1:] == em.shape[1:]):
        raise ValueError(f"grid mismatch: gamma {gamma.shape} tir {tir.shape} em {em.shape}")
    return gamma, tir, em


# ------------------------- corrected-EM helpers -----------------------------
EM_FIX_BETA = [0.90, 0.86, 0.36]  # clay-only EM response per layer


def emfix_observation(z: np.ndarray, em_slice: slice | None = None) -> np.ndarray:
    """Return a copy of z with the EM channels in log10(ohm.m).

    The EM block is always the last three channels, whatever the TIR layout.
    """
    out = z.copy()
    sl = em_slice if em_slice is not None else slice(z.shape[0] - 3, z.shape[0])
    out[sl] = np.log10(np.clip(out[sl], 1.0, 1e5)).astype(np.float32)
    return out


def emfix_H(H: np.ndarray | None = None) -> np.ndarray:
    """Return a copy of H with clay-only log10 EM rows (last three rows)."""
    out = (H if H is not None else H_MATRIX).copy()
    out[-3:] = 0.0
    out[-3:, TARGET] = EM_FIX_BETA
    return out


def load_emfix_inputs() -> tuple[np.ndarray, np.ndarray]:
    """Build the corrected-EM observation and H for the synthetic-TIR layout."""
    gamma, tir, em = load_cubes()
    z = build_observation(gamma, tir, em)
    return emfix_observation(z), emfix_H()


def build_observation(gamma, tir, em) -> np.ndarray:
    return np.concatenate(
        [gamma.astype(np.float32),
         tir[list(TIR_BANDS)].astype(np.float32),
         em[list(EM_LAYERS)].astype(np.float32)],
        axis=0,
    )


# --------------------------------------------------------------------------
# Real ASTER TIR main line
# --------------------------------------------------------------------------
# The main line of the paper uses five real ASTER L1T emissivity bands.  The
# TIR rows of H are *not* hand-set: they are the USGS splib07 emissivity of each
# mineral averaged over the ASTER band pass.  The synthetic 4-band cube survives
# only as an explicit control (`layout("synthetic")`).
ASTER_CENTRES = (8.291, 8.634, 9.075, 10.657, 11.289)        # um, bands 10-14
ASTER_WIDTHS = (0.350, 0.350, 0.350, 0.700, 0.700)
SPEC_WL = np.linspace(8.0, 14.0, 200)                         # splib07 grid
SYNTH_WIDTH = 0.5                                             # um, synthetic bands


def library_tir_rows(centres, widths) -> np.ndarray:
    """Mean emissivity (1 - reflectance) of each mineral over each band pass."""
    rows = np.zeros((len(centres), N_MIN), dtype=np.float64)
    for j, mineral in enumerate(MINERALS):
        spec = np.load(SPEC / f"{mineral}_TIR.npy").astype(np.float64)
        if spec.ndim > 1:
            spec = np.nanmean(spec, axis=0)
        for b, (c, w) in enumerate(zip(centres, widths)):
            sel = (SPEC_WL >= c - w / 2) & (SPEC_WL <= c + w / 2)
            rows[b, j] = float(np.nanmean(1.0 - spec[sel]))
    return rows


class Layout:
    """Channel layout of one observation vector: gamma | TIR | EM."""

    def __init__(self, name: str, n_tir: int, H: np.ndarray):
        self.name = name
        self.n_tir = n_tir
        self.n = 3 + n_tir + 3
        self.H = H
        self.gamma = [0, 1, 2]
        self.tir = list(range(3, 3 + n_tir))
        self.em = list(range(3 + n_tir, self.n))
        self.em_slice = slice(3 + n_tir, self.n)

    def subsets(self) -> dict:
        return {"gamma": self.gamma, "gamma+tir": self.gamma + self.tir,
                "gamma+em": self.gamma + self.em, "all": list(range(self.n))}

    def active(self, idx) -> np.ndarray:
        a = np.zeros(self.n, dtype=np.float32)
        a[list(idx)] = 1.0
        return a

    def H_emfix(self) -> np.ndarray:
        out = self.H.copy()
        out[self.em_slice] = 0.0
        out[self.em_slice, TARGET] = EM_FIX_BETA
        return out


def layout(kind: str = "real") -> Layout:
    if kind == "real":
        H = np.vstack([H_MATRIX[:3],
                       library_tir_rows(ASTER_CENTRES, ASTER_WIDTHS),
                       H_MATRIX[7:]])
        return Layout("real-aster", len(ASTER_CENTRES), H)
    if kind == "synthetic":
        return Layout("synthetic-handset", len(TIR_BANDS), H_MATRIX.copy())
    if kind == "synthetic-library":
        H = np.vstack([H_MATRIX[:3],
                       library_tir_rows(TIR_WAVELENGTHS,
                                        [SYNTH_WIDTH] * len(TIR_WAVELENGTHS)),
                       H_MATRIX[7:]])
        return Layout("synthetic-library", len(TIR_BANDS), H)
    raise ValueError(kind)


def load_real_tir(proc: Path | str | None = None) -> np.ndarray:
    proc = Path(proc or PROC)
    return np.load(proc / "tir_cube_real.npy").astype(np.float32)


def fill_median(cube: np.ndarray) -> np.ndarray:
    """Replace NaN by the per-band median (neutral value for z-scoring)."""
    out = cube.astype(np.float32).copy()
    for i in range(out.shape[0]):
        ch = out[i]
        med = np.nanmedian(ch)
        out[i] = np.where(np.isfinite(ch), ch, med)
    return out


def load_analysis_mask(proc: Path | str | None = None) -> np.ndarray:
    """Pixels covered by the gamma survey AND all five ASTER bands."""
    proc = Path(proc or PROC)
    path = proc / "analysis_mask.npy"
    if path.exists():
        m = np.load(path)
        if m.dtype != bool or not (0.05 < m.mean() < 0.99):
            raise ValueError(f"analysis_mask invalid ({m.dtype}, {m.mean():.3f})")
        return m
    m = load_valid_mask(proc) & np.isfinite(load_real_tir(proc)).all(axis=0)
    np.save(path, m)
    return m


def load_main(kind: str = "real", emfix: bool = True):
    """Observation, response matrix, layout and mask of a branch.

    kind  : "real" (5 ASTER bands, main line) | "synthetic" | "synthetic-library"
    emfix : True -> log10 EM with clay-only rows (the corrected model)

    All branches are scored on the same analysis mask (gamma ∩ ASTER), so the
    real and synthetic results are directly comparable.
    """
    gamma, tir_syn, em = load_cubes()
    lay = layout(kind)
    if kind == "real":
        tir = fill_median(load_real_tir())
    else:
        tir = tir_syn[list(TIR_BANDS)]
    z = np.concatenate([gamma.astype(np.float32), tir.astype(np.float32),
                        em[list(EM_LAYERS)].astype(np.float32)], axis=0)
    H = lay.H.copy()
    if emfix:
        z = emfix_observation(z, lay.em_slice)
        H = lay.H_emfix()
    return z, H, lay, load_analysis_mask()


# --------------------------------------------------------------------------
# Normalisation and weights
# --------------------------------------------------------------------------
def zscore(z: np.ndarray, clip: float = 3.0) -> np.ndarray:
    mean = np.nanmean(z, axis=(1, 2), keepdims=True)
    std = np.nanstd(z, axis=(1, 2), keepdims=True) + 1e-6
    out = (z - mean) / std
    out = np.where(np.isfinite(out), out, 0.0)
    return np.clip(out, -clip, clip).astype(np.float32)


def normalize_H(H: np.ndarray) -> np.ndarray:
    """Column-normalise mineral signatures (relative pattern matching)."""
    return H / np.linalg.norm(H, axis=0, keepdims=True)


def noise_sigma(z: np.ndarray, size: int = 5) -> np.ndarray:
    sigma = np.zeros(z.shape[0], dtype=np.float64)
    for i in range(z.shape[0]):
        ch = z[i].astype(np.float32)
        resid = ch - uniform_filter(ch, size=size, mode="nearest")
        med = np.median(resid)
        sigma[i] = 1.4826 * np.median(np.abs(resid - med)) + 1e-8
    return sigma


def channel_weights(z: np.ndarray, floor: float = 0.1, cap: float = 10.0) -> np.ndarray:
    """Inverse-roughness weights normalised to mean 1 (diagnostic only)."""
    w = 1.0 / noise_sigma(z) ** 2
    w = w / w.mean()
    return np.clip(w, floor, cap).astype(np.float32)


def quality_field(shape, temperature=None, humidity=None, lay=None) -> np.ndarray:
    """Per-pixel quality multipliers (M, H, W); higher = more trustworthy."""
    h, w = shape
    lay = lay or layout("synthetic")
    q = np.ones((lay.n, h, w), dtype=np.float32)
    if humidity is not None:
        rh = np.nan_to_num(humidity, nan=30.0)
        q[lay.gamma] *= np.exp(-0.006 * np.maximum(rh - 20.0, 0.0))[None]
        q[lay.tir] *= np.exp(-0.015 * np.maximum(rh - 20.0, 0.0))[None]
    if temperature is not None:
        t = np.nan_to_num(temperature, nan=20.0)
        q[lay.em] *= np.exp(-0.004 * np.abs(t - 20.0))[None]
    return q


# --------------------------------------------------------------------------
# Inversion
# --------------------------------------------------------------------------
def project_simplex(x: np.ndarray) -> np.ndarray:
    x = np.maximum(x, 0.0)
    s = x.sum(axis=0, keepdims=True)
    return (x / np.where(s < 1e-6, 1.0, s)).astype(np.float32)


def wls_global(z, Hn, w, lam: float = 0.1, block: int = 400) -> np.ndarray:
    A = Hn.T @ (Hn * w[:, None]) + lam * np.eye(N_MIN)
    G = np.linalg.inv(A) @ (Hn.T * w[None, :])
    m, h, wd = z.shape
    x = np.zeros((N_MIN, h, wd), dtype=np.float32)
    for h0 in range(0, h, block):
        h1 = min(h0 + block, h)
        xx = G @ z[:, h0:h1, :].reshape(m, -1) + 1.0 / N_MIN
        x[:, h0:h1, :] = project_simplex(xx).reshape(N_MIN, h1 - h0, wd)
    return x


def wls_pixel(z, Hn, w, lam: float = 0.1, block: int = 64) -> np.ndarray:
    """Per-pixel WLS; w has shape (M, H, W).  Float64 for stability."""
    Hn = Hn.astype(np.float64)
    m, h, wd = z.shape
    x = np.zeros((N_MIN, h, wd), dtype=np.float32)
    eye = lam * np.eye(N_MIN, dtype=np.float64)
    for h0 in range(0, h, block):
        h1 = min(h0 + block, h)
        hh = h1 - h0
        A = np.zeros((N_MIN, N_MIN, hh, wd), dtype=np.float64)
        b = np.zeros((N_MIN, hh, wd), dtype=np.float64)
        for i in range(m):
            hi = Hn[i]
            wi = w[i, h0:h1, :].astype(np.float64)
            A += wi[None, None] * np.outer(hi, hi)[:, :, None, None]
            b += (wi * z[i, h0:h1, :])[None] * hi[:, None, None]
        A += eye[:, :, None, None]
        A2 = A.transpose(2, 3, 0, 1).reshape(-1, N_MIN, N_MIN)
        b2 = b.transpose(1, 2, 0).reshape(-1, N_MIN, 1)
        sol = np.linalg.solve(A2, b2)[..., 0]
        x[:, h0:h1, :] = project_simplex(
            sol.reshape(hh, wd, N_MIN).transpose(2, 0, 1) + 1.0 / N_MIN
        )
    return x


def kalman_smooth(x_init, R_obs: float = 0.02, Q: float = 0.005, block: int = 200):
    """Forward Kalman recursion along W (F=I, observation = WLS estimate)."""
    n, h, wd = x_init.shape
    xs = np.zeros_like(x_init)
    ps = np.zeros_like(x_init)
    for h0 in range(0, h, block):
        h1 = min(h0 + block, h)
        hh = h1 - h0
        x = x_init[:, h0:h1, 0].copy()
        P = np.full((n, hh), R_obs, dtype=np.float32)
        xs[:, h0:h1, 0] = x
        ps[:, h0:h1, 0] = P
        for j in range(1, wd):
            P_pred = P + Q
            innov = x_init[:, h0:h1, j] - x
            K = P_pred / (P_pred + R_obs)
            x = x + K * innov
            P = (1.0 - K) * P_pred + 0.05 * (innov ** 2).mean(axis=0)[None]
            x = project_simplex(x)
            xs[:, h0:h1, j] = x
            ps[:, h0:h1, j] = P
    return xs, ps


def fuse(z, H=H_MATRIX, *, weighting="uniform", channel_quality=None,
         quality=None, lam=0.1, kalman=True, R_obs=0.02, Q=0.005, clip=3.0):
    """WLS + spatial Kalman fusion.

    channel_quality : optional (M,) multipliers; higher quality -> more weight.
                      A zero entry switches the channel off completely.
    quality         : optional (M,H,W) per-pixel quality field

    The response matrix is normalised **over the active channels only**.  Using
    all rows would let a switched-off modality rescale the columns of the active
    ones, so "gamma only" would give a different answer under two matrices that
    differ solely in rows multiplied by zero.
    """
    zn = zscore(z, clip=clip)

    if weighting == "uniform":
        w = np.ones(zn.shape[0], dtype=np.float32)
    elif weighting == "roughness":
        w = channel_weights(zn)
    else:
        raise ValueError(weighting)

    if channel_quality is not None:
        w = (w * np.asarray(channel_quality, dtype=np.float32)).astype(np.float32)

    active = w > 0
    # Normalise the weights over the ACTIVE channels only.  Normalising over all
    # channels (w / w.mean()) would scale the active weights by M / n_active,
    # i.e. silently change the effective ridge strength lambda with the number
    # of switched-off channels.
    if active.any():
        w = (w / w[active].mean()).astype(np.float32)
    Hn = np.zeros_like(H, dtype=np.float64)
    if active.any():
        denom = np.linalg.norm(H[active], axis=0, keepdims=True)
        denom = np.where(denom < 1e-12, 1.0, denom)
        Hn[active] = H[active] / denom
    Hn = Hn.astype(np.float64)

    if quality is None:
        x_init = wls_global(zn, Hn, w, lam=lam)
    else:
        x_init = wls_pixel(zn, Hn, w[:, None, None] * quality, lam=lam)

    x, P = kalman_smooth(x_init, R_obs=R_obs, Q=Q) if kalman else (x_init, None)
    residual = zn - np.einsum("ij,jhw->ihw", Hn, x)
    return {"x": x, "x_init": x_init, "P": P, "weights": w,
            "residual_rms": np.sqrt(np.mean(residual ** 2, axis=(1, 2)))}


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------
def topk_mask(x: np.ndarray, k: int = 2) -> np.ndarray:
    order = np.argsort(-x, axis=0)
    mask = np.zeros(x.shape, dtype=bool)
    np.put_along_axis(mask, order[:k], True, axis=0)
    return mask


def detection_metrics(x, gt, thr=0.25, top_k=2, gt_thr=0.55, mask=None) -> dict:
    """Single detection definition for every scenario.

    Positive = clay > thr AND clay in the top-k minerals.
    `mask` restricts scoring to valid survey pixels.
    """
    gt = np.asarray(gt)
    if gt.dtype != bool:
        gt = gt > gt_thr
    clay = x[TARGET]
    pred = (clay > thr) & topk_mask(x, top_k)[TARGET]
    if mask is not None:
        gt, pred, clay = gt[mask], pred[mask], clay[mask]
    tp = int(np.count_nonzero(pred & gt))
    fp = int(np.count_nonzero(pred & ~gt))
    fn = int(np.count_nonzero(~pred & gt))
    recall = tp / (tp + fn + 1e-9)
    precision = tp / (tp + fp + 1e-9)
    f1 = 2 * precision * recall / (precision + recall + 1e-9)
    iou = tp / (tp + fp + fn + 1e-9)
    return {"recall": float(recall), "precision": float(precision),
            "f1": float(f1), "iou": float(iou), "tp": tp, "fp": fp, "fn": fn,
            "n_gt": int(gt.sum()), "positive_rate": float(pred.mean()),
            "clay_mean": float(clay.mean())}


# --------------------------------------------------------------------------
# Spatial block bootstrap (one implementation for every script)
# --------------------------------------------------------------------------
BLOCK = 128
N_REP = 200


def block_ids(mask: np.ndarray, block: int = BLOCK) -> np.ndarray:
    """Contiguous `block`-pixel tiles; ids are unique over the full grid."""
    h, w = mask.shape
    return ((np.arange(h)[:, None] // block) * ((w + block - 1) // block)
            + (np.arange(w)[None, :] // block))


def pred_of(x: np.ndarray, mask: np.ndarray, thr: float = 0.25) -> np.ndarray:
    """Detection definition shared with `detection_metrics`."""
    return (x[TARGET] > thr) & topk_mask(x, 2)[TARGET] & mask


def _block_counts(pred, gt, bid, nb):
    lab = bid.ravel()
    tp = np.bincount(lab, weights=(pred & gt).ravel(), minlength=nb)
    fp = np.bincount(lab, weights=(pred & ~gt).ravel(), minlength=nb)
    fn = np.bincount(lab, weights=(~pred & gt).ravel(), minlength=nb)
    return tp, fp, fn


def _f1_from_counts(tp, fp, fn) -> float:
    tp, fp, fn = tp.sum(), fp.sum(), fn.sum()
    return float(2 * tp / max(2 * tp + fp + fn, 1))


def paired_bootstrap(xa: np.ndarray, xb: np.ndarray, gt: np.ndarray,
                     mask: np.ndarray, seed: int = 2024,
                     reps: int = N_REP) -> dict:
    """Block bootstrap of F1(b) - F1(a); blocks are resampled from the mask.

    Both maps are thresholded with `pred_of`, so this is the only bootstrap in
    the project and every script that quotes a Delta-F1 confidence interval
    calls it.
    """
    bid = block_ids(mask)
    nb = int(bid.max() + 1)
    g = np.asarray(gt, dtype=bool) & mask
    ca = _block_counts(pred_of(xa, mask), g, bid, nb)
    cb = _block_counts(pred_of(xb, mask), g, bid, nb)
    occupied = np.unique(bid[mask])
    rng = np.random.default_rng(seed)
    d, fa, fb = [], [], []
    for _ in range(reps):
        pick = rng.choice(occupied, size=occupied.size, replace=True)
        a = _f1_from_counts(*(c[pick] for c in ca))
        b = _f1_from_counts(*(c[pick] for c in cb))
        fa.append(a)
        fb.append(b)
        d.append(b - a)
    d = np.asarray(d)
    return {"f1_a": _f1_from_counts(*ca), "f1_b": _f1_from_counts(*cb),
            "delta_mean": float(d.mean()),
            "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
            "a_ci95": [float(np.percentile(fa, 2.5)), float(np.percentile(fa, 97.5))],
            "b_ci95": [float(np.percentile(fb, 2.5)), float(np.percentile(fb, 97.5))],
            "p_better": float(np.mean(d > 0)), "n_blocks": int(occupied.size),
            "n_reps": int(reps)}


def spatial_gradient(x: np.ndarray) -> float:
    return float((np.abs(np.diff(x, axis=1)).mean()
                  + np.abs(np.diff(x, axis=2)).mean()) / 2)


# --------------------------------------------------------------------------
# Independent target (USGS SIM 3206), never derived from gamma or TIR
# --------------------------------------------------------------------------
GEO_HIGH = ("surficial/alluvium", "felsic plutonic")     # clay-bearing
GEO_LOW = ("carbonate", "sedimentary")                   # clay-poor


def auc_score(scores: np.ndarray, positive: np.ndarray) -> float:
    """Rank AUC (Mann-Whitney U / n1 n0), ties broken stably."""
    scores = np.asarray(scores, dtype=np.float64)
    positive = np.asarray(positive, dtype=bool)
    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty(scores.size, dtype=np.float64)
    ranks[order] = np.arange(1, scores.size + 1, dtype=np.float64)
    n1 = int(positive.sum())
    n0 = int(scores.size - n1)
    if n1 == 0 or n0 == 0:
        return float("nan")
    return float((ranks[positive].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def load_geology_groups() -> list:
    """Substrate group names; raster value = index + 1 (0 = unmapped)."""
    return load_json(PROC / "geology_groups.json")["groups"]


def load_geology_target(mask: np.ndarray | None = None):
    """(selection mask, positive labels) for the SIM 3206 substrate contrast."""
    sub = np.load(PROC / "geology_substrate.npy")
    groups = load_geology_groups()
    gid = {g: i + 1 for i, g in enumerate(groups)}
    hi = [gid[g] for g in GEO_HIGH if g in gid]
    lo = [gid[g] for g in GEO_LOW if g in gid]
    sel = np.isin(sub, hi) | np.isin(sub, lo)
    if mask is not None:
        sel &= mask
    return sel, np.isin(sub, hi)[sel]


def geology_auc(x: np.ndarray, sel: np.ndarray, pos: np.ndarray) -> float:
    return auc_score(x[TARGET][sel], pos)


def recovery_metrics(x, truth, mask=None) -> dict:
    out = {}
    for i, name in enumerate(MINERALS):
        a, b = x[i], truth[i]
        if mask is not None:
            a, b = a[mask], b[mask]
        a, b = a.ravel(), b.ravel()
        diff = a - b
        out[name] = {"rmse": float(np.sqrt(np.mean(diff ** 2))),
                     "mae": float(np.mean(np.abs(diff))),
                     "bias": float(np.mean(diff)),
                     "r": float(np.corrcoef(a, b)[0, 1]),
                     "truth_mean": float(b.mean()),
                     "est_mean": float(a.mean())}
    return out


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def jsonable(obj):
    if isinstance(obj, dict):
        return {k: jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(v) for v in obj]
    if isinstance(obj, (np.floating, np.integer)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def save_json(path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(jsonable(obj), indent=2, ensure_ascii=False), encoding="utf-8")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fmt(x, nd=4):
    return f"{x:.{nd}f}"
