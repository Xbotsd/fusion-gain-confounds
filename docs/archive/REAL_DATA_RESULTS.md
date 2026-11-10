# Real ASTER TIR: results and comparison with the synthetic data

Date: 2026-11-07. All numbers from `processed/real_tir.json` and
`processed/tir_real.json`.

## What was built

`prepare_tir_real.py` assembles a **real** thermal-infrared cube from ASTER L1T:

| item | value |
|---|---|
| scenes | 4 × ASTER L1T, 2006-10-18 (100 % coverage of the footprint) |
| native grid | 90 m, UTM 11N, 5 TIR bands |
| delivered grid | 50 m, 1772 × 1075, masked to the radiometric survey footprint |
| bands | 8.291, 8.634, 9.075, 10.657, 11.289 µm |
| calibration | ASTER L1 unit-conversion coefficients → at-sensor radiance |
| temperature | inverse Planck at the band centres |
| emissivity | emissivity normalisation (Realmuto 1990), ε_max = 0.98 |
| pixels with all bands | 85.7 % (60.0 % after the survey mask) |

Physical validation (recorded in `tir_real.json`):

* brightness temperature 282–298 K (median 291 K) — plausible for an October
  late-morning desert scene at 1,000–1,700 m;
* emissivity 0.89–1.00, per-band means
  **0.914 / 0.931 / 0.936 / 0.997 / 0.999**;
* the short-wavelength bands show the expected reststrahlen depression, and the
  residual correlation with the 10.657 µm band is only 0.03–0.21, i.e. the
  temperature has been largely removed. (Band 5 still correlates at 0.81, which
  is the known weakness of a normalisation TES and is stated as a limitation.)

`run_real_tir.py` rebuilds the TIR rows of `H` from USGS splib07 sampled over
the ASTER band passes — nothing about the real TIR block is hand-set:

| band (µm) | Quartz | Feldspar | Clay | Calcite | Dolomite |
|---:|---:|---:|---:|---:|---:|
| 8.291 | 0.255 | 0.765 | 0.992 | 0.814 | 0.937 |
| 8.634 | 0.410 | 0.712 | 0.993 | 0.811 | 0.932 |
| 9.075 | 0.157 | 0.789 | 0.935 | 0.756 | 0.923 |
| 10.657 | 0.902 | 0.847 | 0.921 | 0.756 | 0.888 |
| 11.289 | 0.925 | 0.872 | 0.957 | 0.857 | 0.864 |

Quartz drops to 0.16–0.26 in the reststrahlen region and returns to 0.90–0.93
beyond 10 µm, which is the textbook behaviour and a check that the sampling is
correct.

## Ablation: real vs synthetic, same pipeline and mask

F1 on the clay proxy. Three branches: the published pipeline (synthetic data,
hand-set `H`), a control with synthetic data but library-sampled `H`, and the
real ASTER branch.

### Corrected EM matrix

| configuration | synthetic, hand-set H | synthetic, library H | **real ASTER** |
|---|---:|---:|---:|
| gamma | 0.519 | 0.520 | 0.521 |
| gamma + TIR | 0.451 | 0.570 | **0.644** |
| gamma + EM | 0.417 | 0.416 | 0.417 |
| all | 0.498 | 0.494 | 0.482 |

### Legacy EM matrix

| configuration | synthetic, hand-set H | synthetic, library H | **real ASTER** |
|---|---:|---:|---:|
| gamma | 0.325 | 0.325 | 0.325 |
| gamma + TIR | 0.339 | 0.336 | 0.315 |
| gamma + EM | 0.191 | 0.191 | 0.191 |
| all | 0.267 | 0.270 | 0.283 |

Average precision, corrected matrix, for reference: gamma 0.393 / 0.398 / 0.403;
gamma+TIR 0.655 / 0.697 / **0.636**; all 0.513 / 0.555 / 0.480.

## What this changes

1. **The "TIR is redundant" conclusion was an artefact of the synthetic TIR
   field.** The synthetic cube is generated from a clay field proportional to
   `0.3K + 0.3eTh`, i.e. from the same gamma channels used to build the
   evaluation proxy, so it can only re-state the proxy. With real ASTER
   emissivity, gamma + TIR reaches **F1 0.644** against 0.521 for gamma alone —
   a +0.12 gain instead of the −0.07 seen with the synthetic cube.
2. **TIR becomes the load-bearing modality, not EM.** In the real branch the
   best configuration is gamma + TIR; adding the synthetic EM lowers F1 to
   0.482. This is consistent with the physics: EM here is still a synthetic
   field built from the same clay proxy, whereas the ASTER emissivity carries
   independent mineralogical information.
3. **The reference row reproduces exactly.** The `synthetic-handset` branch gives
   F1 0.4982, AP 0.5134, R 0.8575, P 0.3511 — identical to `em_fix.json`. The
   comparison is therefore on the same pipeline, mask and metric, not across two
   different implementations.
4. **Under the legacy matrix the real TIR does not help** (0.315 vs 0.339). The
   legacy matrix's ill-conditioning (κ = 1156) still suppresses the TIR
   contrast, which is exactly the mechanism described in §4.8: real data cannot
   rescue a mis-specified response matrix.

## Limitations to state

* ASTER 2006 is 14 years earlier than the radiometric survey (2019–2020). The
  land surface in this desert is stable at the mapping scale, but the epoch
  difference must be reported.
* Emissivity normalisation is a simplification of the full ASTER TES. Bands 1–3
  are usable; band 5 retains a residual temperature correlation of 0.81.
* EM remains synthetic. No measured AEM exists at this site (see
  `docs/REAL_DATA_FEASIBILITY.md`).
* One date, four scenes, 85.7 % band coverage before the survey mask.

## Files

`processed/tir_cube_real.npy`, `tir_real.json`, `real_tir.json/csv/png`;
scripts `code/prepare_tir_real.py`, `code/run_real_tir.py` (network stage
`real`, run explicitly with `python code/run_all.py real`).
