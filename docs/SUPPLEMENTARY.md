# Supplementary material inventory

## S1. Code — main line

| script | role |
|---|---|
| `fetch_aster.py` | archive the raw ASTER L1T scenes with STAC ids and SHA-256 (network, once) |
| `prepare_gamma.py` | real gamma cube, clay proxy, control truth, survey mask |
| `prepare_tir_real.py` | ASTER emissivity cube (mosaic, radiance, brightness temperature, normalisation TES) and the analysis mask |
| `prepare_geology.py` | SIM 3206 substrate raster and class counts |
| `prepare_tir.py`, `prepare_em.py` | synthetic controls (splib07 TIR, EM section) |
| `run_main.py` | ablation, baselines, block bootstrap, repeats, calibration, autocorrelation |
| `run_tir_controls.py` | all-zero, Gaussian-noise, block- and pixel-shuffled, ridge controls |
| `run_tir_information.py` | cross-validated information test against geology and the proxy |
| `run_geology_multiclass.py` | model-free 4-class test, 20 repeats |
| `run_identifiability.py` | rank, condition number, variance-gain index |
| `run_real_tir_robust.py` | TES and acquisition-date sensitivity |
| `run_depth.py`, `run_depth_emfix.py` | 40-layer depth Kalman |
| `run_published_baselines.py` | five published single-modality indices |
| `independent_validation.py` | clay by substrate, Kruskal-Wallis, AUC |
| `uncertainty_calibration.py` | coverage and reliability of the filter variance |
| `autocorr_sample_size.py` | integral scale, design effect, N_eff |
| `run_edge_ai.py`, `prepare_granite.py`, `run_granite_compensation.py` | edge-deployment modules |
| `test_core.py` | 36 assertions in 9 test groups, including the two switch-off invariances |
| `check_coverage.py` | fails if any validated artefact has no producer |
| `validate_pipeline.py` | 53 artefacts, 22 invariants |
| `make_figures.py`, `make_graphical_abstract.py` | paper figures and the graphical abstract |
| `build_manifest.py` | SHA-256 inventory |

## S2. Data

| item | location | note |
|---|---|---|
| radiometrics | `raw/K.gxf`, `eU.gxf`, `eTh.gxf` + line CSV | real USGS, 2019–2020 |
| ASTER TIR | `raw/aster/2006-10-18/`, `2006-09-25/` | real, 7 scenes, STAC ids + SHA-256 in `manifest.json` |
| magnetics | `raw/TMI.gxf` | real |
| geology | `processed/geology_substrate.npy` + `geology_groups.json` | real SIM 3206 |
| EM | `processed/em_cube.npy` | **synthetic**, seed 12345 |
| emissivity cube | `processed/tir_cube_real.npy` | derived from ASTER by the pipeline |
| analysis mask | `processed/analysis_mask.npy` | survey ∩ ASTER, 1,237,644 px |

## S3. Figures

| figure | file | content |
|---|---|---|
| F1 | `fig_data.png` | real layers, ASTER bands, synthetic EM, clay proxy |
| F2 | `fig_method.png` | protocol and estimator chain |
| F3 | `identifiability.png` | variance gain, observed F1 and AUC changes |
| F4 | `main_maps.png` | clay: real ASTER, synthetic control, proxy |
| F5 | `main_ablation.png` | ablation on both targets |
| F6 | `published_baselines.png` | published indices vs the fusion |

## S4. Tables

| table | source |
|---|---|
| T1 data layers | `docs/DATA_PROVENANCE.md` |
| T2 targets and metrics | `main_results.json` definition block |
| T3 thermal rows of H | `main_results.json` → `H_tir_real` |
| T4 ablation | `main_ablation.csv` |
| T5 conditioning controls | `tir_controls.json` |
| T6 model-free information | `geology_multiclass.json` |
| T7 estimator comparison | `main_baselines.csv` |
| T8 retrieval sensitivity | `real_tir_robust.json` |
| T9 published practice | `published_baselines.json` |

## S5. Reproduction

```powershell
.\run.bat all                     # prepare → main → controls → aux → figures → audit
.\run.bat legacy                  # synthetic-TIR reference branch (optional)
D:\miniconda3\envs\geo\python.exe code\test_core.py
```

## S6. Standalone and legacy scripts

These run, but are deliberately not in `run_all.py`; they are kept for the record
or for one-off use. None of their outputs is among the 53 validated artefacts.

| script | status | output |
|---|---|---|
| `run_fusion.py` | legacy: the v2 Kalman fusion stage (10-channel `load_cubes`) | `kf_mineral_abundance.npy`, `fusion.json` |
| `block_bootstrap.py` | legacy: pixel-block bootstrap of the v2 method comparison | `bootstrap.json/csv` |
| `run_independent_target.py` | legacy: first independent-target experiment | `independent_target.*` |
| `run_real_tir.py` | legacy: first real-ASTER ablation branch | `real_tir.*` |
| `run_em_fix_repeats.py` | legacy: 10-run average for the corrected-EM model | `em_fix_repeats.json/csv` |
| `run_ablation_emfix.py`, `run_calibration_emfix.py`, `run_validation_emfix.py` | thin wrappers that append `--emfix` and call the corresponding `run_*` module | the `*_emfix` artefacts |
| `make_submission_package.py` | packaging helper: copies figures and writes captions/keywords | `docs/submission/` |
| `fetch_aster.py` | network: archives the raw ASTER scenes once | `raw/aster/` |
| `maintain.py` | read-only repository/archive health check | printed report, exit code |
| `common.py`, `run_all.py` | shared code and the launcher | — |

`run_all.py legacy` covers the synthetic-TIR reference branch only (ablation,
validation, baselines, advantage, EM fix, repeats, sensitivity, environment,
threshold, perturbation, scenarios, beta/generation sensitivity, V2).

## S7. Pre-emptive reviewer questions

1. **Is the thermal data real?** Yes, ASTER L1T v003, five bands, archived with
   STAC ids and hashes; the synthetic splib07 cube is a control only.
2. **Why is EM synthetic?** No airborne EM exists over this footprint; the
   delivered survey is radiometric and magnetic. Every EM result is labelled.
3. **Is the fusion gain genuine?** Partly. The inversion-side gain is mostly
   conditioning (69-98 % of the F1 gain is reproduced by inert channels); the model-free information gain is +0.179
   balanced accuracy and is null for a shuffled cube.
4. **Why does gamma fail on geology?** Three equations for five unknowns: rank 3.
   K alone separates the substrates at AUC 0.986, so the loss is in the
   inversion, not the data.
5. **Is the uncertainty usable?** No. Coverage is 0.13/0.26; we report it as a
   filter variance and never as a confidence interval.
6. **How many independent samples?** 110 effective samples from 1.24 M pixels (173 for the inverted clay map);
   all contrasts use 128-px block bootstrap.
