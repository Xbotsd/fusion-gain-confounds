# Real-data feasibility (checked 2026-11-07)

Question: can the synthetic modalities be replaced with measured data, so that
every number in the paper comes from real sensors?

## Verdict per modality

| modality | current | real data available? | verdict |
|---|---|---|---|
| Gamma (K, eU, eTh) | real USGS survey | yes, in hand | already real |
| Magnetics (TMI) | real USGS grid | yes, in hand | already real |
| Geology | real USGS SIM 3206 | yes, in hand | already real |
| TIR | synthetic splib07 | **done** — real ASTER L1T cube built (2006-10-18, 5 bands, 50 m) | see docs/REAL_DATA_RESULTS.md; synthetic kept as the reference branch |
| EM / resistivity | synthetic AEM statistics | **no** | no measured AEM exists at this site |

## Evidence for TIR

Queried the Microsoft Planetary Computer STAC API (`aster-l1t`) for the survey
footprint (UTM 11N 626275–680025 E, 3868325–3956925 N, 53.8 × 88.6 km):

* 20 ASTER L1T scenes overlap the footprint in 2006;
* **two acquisition dates give 100 % coverage with four scenes each**
  (2006-10-18 and 2006-09-25); 2006-08-01 gives 97.1 %;
* each scene carries a 5-band TIR raster (`*.TIR.tif`), 90 m, UTM 11N,
  950 × 847 px, dtype uint16, plus an XML granule record;
* anonymous access works: the SAS token endpoint
  `/api/sas/v1/token/aster-l1t` issues a token and GDAL can open the asset
  through `/vsicurl/` and read windows (verified: bands 1/4/5 return DN
  0–1983).

## Why it is not a drop-in replacement

1. **The stored values are not emissivity.** ASTER L1T delivers at-sensor
   radiance; the emissivity that the forward model needs comes from the AST_05
   TES product, which lives on LP DAAC behind an Earthdata login and is not on
   Planetary Computer.
2. **The DN→radiance coefficients are not in the accessible metadata.** The XML
   asset is granule metadata (band availability, sun angles), not the
   radiometric calibration table. Recovering radiance therefore needs the HDF
   attributes, which are not served by this mirror.
3. **Temperature dominates the signal.** The footprint spans roughly 700–2000 m
   of relief, so a raw TIR radiance channel is mostly a topographic temperature
   map. Feeding it to a linear mineral model without TES would produce a map of
   elevation, not of clay.
4. **Band coverage differs.** ASTER TIR is 8.29, 8.63, 9.08, 10.66 and
   11.29 µm; the current model uses 8.6, 9.6, 11.3 and 12.5 µm. A real-TIR
   rebuild must resample the spectral library at the ASTER band centres and
   rebuild the TIR rows of `H`, i.e. it is a model change, not a data swap.

## Evidence for EM

* The delivered survey (`raw/`) contains exactly four grids: `K.gxf`,
  `eU.gxf`, `eTh.gxf`, `TMI.gxf`, plus line-level radiometric CSV and the flight
  plans. There is no EM product.
* The USGS airborne survey over Ivanpah–Clark Mountain was radiometric and
  magnetic; no public airborne EM survey covers this footprint.
* Consequence: a "real EM" version of this paper cannot be built from public
  data. Options are (a) keep the synthetic EM as a documented controlled
  augmentation, (b) drop EM and lose the paper's central experiment, or
  (c) acquire/commission an AEM survey (hardware and budget).

## What a real-TIR rebuild would involve

1. `prepare_tir_real.py`: fetch four ASTER scenes per date, window-read the TIR
   raster, mosaic on the 90 m UTM grid, resample to 50 m, mask to the survey
   footprint.
2. Radiometric calibration: obtain the TIR unit-conversion coefficients (ASTER
   L1T HDF attribute table) — requires either the HDF granule or an Earthdata
   login to LP DAAC.
3. Temperature–emissivity separation: alpha-residual method (Kealy & Hook 1990)
   or the ASTER TES; validate that retrieved emissivity stays in [0.6, 1.0] and
   brightness temperature in 270–330 K.
4. Rebuild the TIR rows of `H` from USGS splib07 averaged over the ASTER band
   passes (5 rows instead of 4).
5. Rerun `fusion`, `ablation`, `validation`, `depth`, `emfix` and every
   downstream artefact; every number in the manuscript and in `docs/` changes.

Steps 1 and 4 are straightforward. Steps 2–3 are the risk: an unvalidated TES
would silently corrupt every downstream result, which is worse than a clearly
labelled synthetic modality.

## Recommendation

* **TIR**: do it, but as a new variant with its own validation gate (emissivity
  range, temperature range, comparison against the synthetic cube), not as a
  silent replacement. Use the 2006-10-18 mosaic (100 % coverage).
* **EM**: state plainly in the paper that no measured AEM exists at this site,
  cite the survey inventory as evidence, and keep the synthetic EM labelled as
  a controlled augmentation. This is already the honest position of §3.3.
* **Epoch**: ASTER 2006 is 14 years before the radiometric survey. For
  contemporaneity, Landsat 8/9 C2 L2 (2019–2020, 100 m) is available on the
  same anonymous endpoint but provides only two thermal bands (10.6–11.2 and
  11.5–12.5 µm), so it cannot feed the four-band emissivity model without a
  further reduction in spectral constraint.
