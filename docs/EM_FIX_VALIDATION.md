# Corrected-EM validation and depth

The corrected EM model (log10 resistivity + clay-only response) was propagated to
the validation suite and the 40-layer depth Kalman. Legacy results are kept for
comparison; corrected outputs use the `_emfix` suffix.

## Family means

| family | legacy recall | EM-fix recall |
|---|---:|---:|
| normal | 0.693 | **0.858** |
| leave-2-channels-out | 0.674 | **0.825** |
| sensor degradation | 0.746 | **0.719** |
| temperature | 0.476 | **0.912** |
| cross-domain CORAL | 0.689 | **0.799** |
| H sensitivity | 0.687 | **0.861** |
| **overall recall** | **0.661** | **0.829** |
| overall F1 | 0.254 | **0.480** |

## Degradation

| scenario | legacy recall | EM-fix recall |
|---|---:|---:|
| normal | 0.693 | 0.858 |
| EMI degraded ×5 | 0.952 | 0.494 |
| EMI failed ×20 | 0.976 | 0.338 |
| TIR degraded ×5 | 0.433 | 0.949 |
| gamma degraded ×5 | 0.602 | 0.860 |
| EMI + TIR failed | 0.770 | 0.952 |

After correction, **EMI failure hurts** (as it should, because EM is now useful),
and **TIR failure helps** (TIR is largely redundant for the clay proxy). The
legacy pattern was the opposite, which was a symptom of EM mis-specification.
The corrected degradation family mean (0.719) is *below* the legacy one (0.746)
precisely because the corrected model depends on EM; degrading a modality that
carries information must cost recall, and degrading one that does not must not.

## Temperature

| T (°C) | legacy recall | EM-fix recall | EM-fix F1 |
|---:|---:|---:|---:|
| −60 | 0.352 | 0.957 | 0.417 |
| −40 | 0.388 | 0.949 | 0.437 |
| −25 | 0.477 | 0.923 | 0.470 |
| 0 | 0.603 | 0.885 | 0.491 |
| 25 | 0.690 | 0.857 | 0.490 |
| 50 | 0.570 | 0.884 | 0.477 |
| 70 | 0.382 | 0.926 | 0.442 |
| 80 | 0.348 | 0.918 | 0.430 |

The corrected model is far less temperature-sensitive in recall, although F1
still drops at temperature extremes (0.430–0.417 at ±60–80 °C vs 0.490 at 25 °C).

## H sensitivity

| perturbation | legacy recall | EM-fix recall |
|---|---:|---:|
| ±0 % | 0.693 | 0.858 |
| ±5 % | 0.705 | 0.860 |
| ±10 % | 0.703 | 0.862 |
| ±15 % | 0.691 | 0.863 |
| ±20 % | 0.665 | 0.864 |
| ±30 % | 0.659 | 0.859 |

The corrected model is stable in the mean; the trial-to-trial standard deviation
grows from 0.000 to 0.057 at ±30 %.

## Depth

| quantity | legacy | EM-fix |
|---|---:|---:|
| clay at layer 0 (0.1 m) | 0.276 | 0.276 |
| clay at layer 39 (500 m) | **0.444** | **0.179** |
| runtime | 38.7 s | 39.2 s |

The legacy depth model drove clay upward with depth, which is physically
unlikely; the corrected model decreases clay with depth. The depth section is
still a synthetic extrapolation from surface gamma/TIR and Wisconsin AEM layer
statistics, not a site-specific 3-D validation.

## Cross-domain

Direct transfer recall is 0.858; CORAL reduces it to 0.799. CORAL is therefore
not beneficial for this corrected model, unlike the legacy result. This should
be reported as a negative CORAL result.

## Caveats

- Validation and depth still use synthetic TIR/EM, gamma-derived target and
  hand-set H; the correction removes one clear mis-specification, not all
  calibration uncertainty.
- The posterior variance is **not** a predictive interval under either model:
  empirical 68/95 % coverage is 9.5 %/21.0 % for the corrected model (legacy
  10.3 %/20.2 %), with a variance-scale factor of 15.15. See
  `docs/EM_FIX.md` and `calibration_emfix.json`.
- The depth cube is 40 layers from AEM statistics, not borehole-validated.
- Scenario point estimates here are given without CIs; the 128-px block
  bootstrap and BH-corrected paired tests are in `docs/SCENARIO_CI.md`.

## Files

`processed/validation_emfix.json/csv/md/png`,
`processed/depth_emfix.json`, `depth_kalman_3d_emfix.npy`,
`depth_uncertainty_emfix.npy`, `depth_*_emfix.png`;
scripts `code/run_validation_emfix.py`, `code/run_depth_emfix.py`.
