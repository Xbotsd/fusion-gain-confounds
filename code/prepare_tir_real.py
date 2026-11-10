"""Real ASTER L1T thermal-infrared cube for the main line (offline).

Input  : raw/aster/<date>/*.TIR.tif  (archived by fetch_aster.py, SHA-256 in
         raw/aster/<date>/manifest.json)
Output : processed/tir_cube_real.npy   (5, H, W) emissivity, NaN off-coverage
         processed/tir_real.json       provenance + physical gate statistics
         processed/analysis_mask.npy   gamma survey ∩ all five ASTER bands

Processing
----------
1. Mosaic the TIR GeoTIFFs of one date (GDAL BuildVRT) and warp them onto the
   50 m analysis grid of the radiometric survey (bilinear).
2. DN -> at-sensor radiance with the ASTER L1 unit-conversion coefficients.
3. Brightness temperature per band by inverting the Planck function at the
   band centre.
4. Emissivity normalisation (Realmuto 1990): the surface temperature is taken
   from the hottest band with an assumed maximum emissivity `eps_max`, then
   emissivity is solved per band.  This is a simplification of the full ASTER
   TES; its sensitivity to eps_max, to the residual-temperature band and to the
   acquisition date is tested in run_real_tir_robust.py.

The physical gate (BT 270-330 K median, emissivity within [0.6, 1.0]) is
asserted here and again in validate_pipeline.py.
"""
from __future__ import annotations

import numpy as np
from osgeo import gdal

import common as C

gdal.UseExceptions()

DATE = "2006-10-18"
CENTRES = np.array(C.ASTER_CENTRES)
UNIT_COEF = np.array([6.822e-3, 6.780e-3, 6.590e-3, 5.693e-3, 5.225e-3])
C1 = 1.191042e8          # W um^4 m-2 sr-1
C2 = 1.4387752e4         # um K


def planck(lam_um, temp_k):
    return C1 / (lam_um ** 5 * (np.exp(C2 / (lam_um * temp_k)) - 1.0))


def bt_from_radiance(rad, lam_um):
    with np.errstate(divide="ignore", invalid="ignore"):
        return C2 / (lam_um * np.log(C1 / (lam_um ** 5 * np.maximum(rad, 1e-9)) + 1.0))


def scene_files(date):
    d = C.RAW / "aster" / date
    files = sorted(d.glob("*.TIR.tif"))
    if not files:
        raise FileNotFoundError(
            f"no ASTER scenes in {d}; run `python code/fetch_aster.py {date}` once")
    return files


def build_cube(date=DATE, eps_max=0.98, drop_band5=False):
    """Mosaic one archived ASTER date, retrieve emissivity, mask to the survey."""
    files = scene_files(date)
    kds = gdal.Open(str(C.RAW / "K.gxf"))
    kgt = kds.GetGeoTransform()
    w, h = kds.RasterXSize, kds.RasterYSize
    bounds = (kgt[0], kgt[3] + kgt[5] * h, kgt[0] + kgt[1] * w, kgt[3])

    vrt = gdal.BuildVRT("", [str(f) for f in files], srcNodata=0, VRTNodata=0)
    warped = gdal.Warp("", vrt, format="MEM", dstSRS="EPSG:32611",
                       outputBounds=bounds, xRes=50.0, yRes=50.0,
                       resampleAlg="bilinear", srcNodata=0, dstNodata=0,
                       multithread=True)

    dn = np.empty((5, h, w), dtype=np.float32)
    for i in range(5):
        buf = warped.GetRasterBand(i + 1).ReadRaster(0, 0, w, h,
                                                     buf_type=gdal.GDT_Float32)
        dn[i] = np.frombuffer(buf, dtype=np.float32).reshape(h, w)

    valid = (dn > 0) & np.isfinite(dn)
    rad = dn * UNIT_COEF[:, None, None]
    bt = np.stack([bt_from_radiance(rad[i], CENTRES[i]) for i in range(5)])
    good = valid.all(axis=0) & ((bt > 200) & (bt < 400)).all(axis=0)

    t_surf = np.nanmax(bt, axis=0)
    eps = np.stack([np.clip(rad[i] / planck(CENTRES[i], t_surf), 0.5, 1.0)
                    for i in range(5)])
    eps = eps * eps_max / np.maximum(eps.max(axis=0, keepdims=True), 1e-6)

    survey = C.load_valid_mask()
    keep = good & survey
    cube = np.where(keep[None], eps, np.nan).astype(np.float32)
    if drop_band5:
        cube = cube[:4]

    # residual temperature dependence per band (lower is better)
    b4 = eps[3][keep]
    resid = [float(np.corrcoef(eps[i][keep], t_surf[keep])[0, 1]) for i in range(5)]

    meta = {
        "source": "ASTER L1T v003 (NASA/METI), via Microsoft Planetary Computer",
        "date": date,
        "scene_files": [f.name for f in files],
        "bands_um": (CENTRES[:4] if drop_band5 else CENTRES).tolist(),
        "unit_coefficients": UNIT_COEF.tolist(),
        "eps_max_assumed": eps_max,
        "coverage_all_bands_grid": float(valid.all(axis=0).mean()),
        "coverage_of_survey": float(keep.sum() / max(survey.sum(), 1)),
        "analysis_pixels": int(keep.sum()),
        "bt_percentiles": [float(x) for x in np.nanpercentile(bt[:, good], [1, 50, 99])],
        "eps_percentiles": [float(x) for x in np.nanpercentile(eps[:, keep], [1, 50, 99])],
        "eps_band_mean": [float(x) for x in np.nanmean(eps[:, keep], axis=1)],
        "t_surface_percentiles": [float(x) for x in
                                  np.nanpercentile(t_surf[keep], [1, 50, 99])],
        "corr_eps_with_tsurf": resid,
        "corr_eps_with_band13": [float(np.corrcoef(eps[i][keep], b4)[0, 1])
                                 for i in range(5)],
    }
    return cube, keep, meta


def main():
    cube, keep, meta = build_cube(DATE)
    lo, med, hi = meta["eps_percentiles"]
    bt_med = meta["bt_percentiles"][1]
    if not (0.6 <= lo and hi <= 1.0 and 270.0 <= bt_med <= 330.0):
        raise SystemExit(f"physical gate failed: eps {lo:.3f}-{hi:.3f}, BT {bt_med:.1f} K")
    np.save(C.OUT / "tir_cube_real.npy", cube)
    np.save(C.OUT / "analysis_mask.npy", keep)
    C.save_json(C.OUT / "tir_real.json", meta)
    print("scenes          :", meta["scene_files"])
    print("BT percentiles  :", np.round(meta["bt_percentiles"], 1), "K")
    print("eps percentiles :", np.round(meta["eps_percentiles"], 3))
    print("eps band means  :", np.round(meta["eps_band_mean"], 3))
    print("corr eps~T_surf :", np.round(meta["corr_eps_with_tsurf"], 3))
    print(f"analysis mask   : {meta['analysis_pixels']:,} px "
          f"({meta['coverage_of_survey']:.1%} of the survey)")
    print("saved tir_cube_real.npy / analysis_mask.npy / tir_real.json")


if __name__ == "__main__":
    main()
