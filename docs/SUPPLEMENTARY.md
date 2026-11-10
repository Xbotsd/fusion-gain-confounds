# Supplementary material inventory

## S1. Code

| script | role |
|---|---|
| `prepare_gamma.py` | real gamma cube, clay_prior, TIR truth, valid mask |
| `prepare_tir.py` | USGS splib07 TIR cube |
| `prepare_em.py` | synthetic EM cube |
| `run_fusion.py` | WLS + spatial Kalman, main maps |
| `run_depth.py` | 40-layer depth Kalman |
| `run_ablation.py` | modality ablation |
| `run_validation.py` | degradation, temperature, domain, H, leave-channel-out |
| `run_baselines.py` | independent, average, fixed weight, PCA, GLS, ours |
| `run_environment.py` | real T/RH quality weights |
| `run_sensitivity.py` | 20 seeds, resolution, weighting diagnostic |
| `run_repeats.py` | 10-run average and pixel-wise std |
| `run_advantage.py` | ablation, AP/coherence comparison, Q/R sweep, noise |
| `block_bootstrap.py` | 128×128 (6.4 km) spatial block bootstrap for F1 |
| `autocorr_sample_size.py` | integral scale, design effect, N_eff, per-block AP |
| `run_em_fix.py` | corrected log10/clay-only EM model |
| `run_em_fix_repeats.py` | 10-run average for corrected EM |
| `run_ablation_emfix.py` | corrected-EM ablation |
| `run_calibration_emfix.py` | corrected-EM uncertainty calibration |
| `test_core.py` | unit tests (24 checks, runs in the audit stage) |
| `run_validation_emfix.py` | corrected-EM validation suite |
| `run_depth_emfix.py` | corrected-EM 40-layer depth Kalman |
| `prepare_tmi.py` | resample the real TMI grid to the analysis grid |
| `prepare_granite.py` | granite indicator + physical properties (gamma/TMI/NGU) |
| `run_granite_compensation.py` | granite interference compensation experiment |
| `run_edge_ai.py` | NumPy 1-D CNN residual learner, INT8, latency |
| `structured_perturbation.py` | physically structured H perturbations |
| `threshold_sensitivity.py` | clay/top-k/proxy threshold sweep |
| `scenario_bootstrap.py` | per-scenario 128-px CIs + BH-corrected deltas |
| `run_published_baselines.py` | five published exploration-method baselines |
| `independent_validation.py` | USGS SIM 3206 substrate comparison |
| `fetch_asu_spectra.py` | ASU guest export |
| `run_asu_variant.py` | ASU endmember sensitivity |
| `validate_pipeline.py` | 90-artefact integrity, 15 cross-checks |
| `build_manifest.py` | SHA-256/schema manifest |
| `make_figures.py` | data/method/results figures |
| `run_em_beta_sensitivity.py` | EM depth-profile (beta) sensitivity |
| `run_identifiability.py` | condition number, clay variance and gain index |
| `run_generation_sensitivity.py` | sweep of the synthetic-generation parameters |
| `report_large_files.py` | large-intermediate inventory and storage policy |
| `verify_references.py` | Crossref check of the candidate list (network) |
| `audit_data.py` | provenance and H audit |

## S2. Data

| item | location | note |
|---|---|---|
| real gamma | `raw/K.gxf`, `eU.gxf`, `eTh.gxf` | USGS Ivanpah, 50 m |
| radiometric CSV | `Radiometric_Data.csv` | 295,943 samples, 1 Hz |
| TIR (USGS) | `processed/tir_cube.npy` | synthetic splib07 |
| TIR (ASU) | `processed/tir_cube_asu.npy` | synthetic ASU, sensitivity only |
| EM | `processed/em_cube.npy` | synthetic AEM statistics |
| geology | `processed/geology_substrate.npy` | real USGS SIM 3206 substrate |
| corrected EM | `processed/em_fix.json` | log10 + clay-only result |
| pseudo-replication | `processed/autocorr.json` | τ, DE, N_eff, block checks |
| main abundance | `processed/kf_mineral_abundance.npy` | 5 × 1772 × 1075 |
| depth cube | `processed/depth_kalman_3d.npy` | 40 × 5 × 1772 × 1075 |
| metrics | `processed/*.json|csv` | fusion, ablation, validation, baselines, environment, sensitivity, repeats |
| manifest | `processed/data_manifest.json` | SHA-256 inventory |

## S3. Figures

| figure | file | content |
|---|---|---|
| F1 | `fig_data.png` | real gamma, synthetic TIR/EM, clay_prior |
| F2 | `fig_method.png` | WLS + Kalman pipeline |
| F3 | `fig_results.png` | clay map and uncertainty |
| F4 | `ablation.png` | ablation bars |
| F5 | `validation.png` | scenario recall and temperature |
| F6 | `fig_asu_endmembers.png` | ASU endmember sensitivity |
| F7 | `calibration.png` | uncertainty coverage and reliability |
| F8 | `v2/fig_v2.png` | V2 controlled testbed |
| F9 | `advantage.png` | PR curves and accuracy/smoothness |
| F10 | `em_fix.png` | legacy vs corrected EM |
| F11 | `independent_validation.png` | clay by geological substrate |
| F12 | `structured_perturbation.png` | structured H sensitivity |
| F13 | `threshold_sensitivity.png` | clay/top-k threshold sweep |
| F14 | `validation_emfix.png` | corrected-EM validation |
| F15 | `depth_profiles_emfix.png` | corrected-EM depth profile |
| F16 | `autocorr.png` | autocorrelation, N vs N_eff, block AP |
| F17 | `scenario_bootstrap.png` | scenario recall with 95 % CIs |

## S4. Tables

| table | source |
|---|---|
| T1 data layers | `docs/DATA_STRUCTURE.md` |
| T2 metrics | `docs/METHODS.md` |
| T3 experiment matrix | `docs/PIPELINE_AUDIT.md` |
| T4 ablation | `processed/ablation.csv` |
| T5 degradation/temperature | `processed/validation.csv` |
| T6 baselines | `processed/baselines.csv` |
| T7 calibration | `processed/calibration.csv` |
| T8 ASU sensitivity | `processed/ablation_asu.csv`, `fusion_asu.json` |
| T9 V2 testbed | `processed/v2/ablation_v2.csv` |
| T10 advantage | `processed/advantage.csv` |
| T11 bootstrap | `processed/bootstrap.csv` |
| T12 corrected EM | `processed/em_fix.csv` |
| T13 independent geology | `processed/independent_validation.csv` |
| T14 structured H | `processed/structured_perturbation.csv` |
| T15 corrected EM repeats | `processed/em_fix_repeats.csv` |
| T16 threshold sweep | `processed/threshold_sensitivity.csv` |
| T17 corrected validation | `processed/validation_emfix.csv` |
| T18 corrected depth | `processed/depth_emfix.json` |
| T19 granite | `processed/granite_compensation.csv` |
| T20 edge AI | `processed/edge_ai.csv` |
| T21 pseudo-replication | `processed/autocorr.csv` |
| T22 scenario CIs | `processed/scenario_bootstrap.csv` |

## S5. Reproduction

```powershell
.\run.bat all                        # 8 stages / 40 scripts incl. unit tests + audit
D:\miniconda3\envs\geo\python.exe code\test_core.py   # unit tests only
```

The launcher auto-selects an interpreter with numpy/scipy/GDAL (the `geo`
conda env). Figures are 300 dpi. License: MIT (`LICENSE`), with USGS/NGU/ASU
data-source notices.

## S6. Pre-emptive reviewer questions

1. **Why is the target gamma-derived?** Because no independent geological label
   exists for this survey; the paper states this and reports the model-fit
   residual in addition to the proxy metric.
2. **Why are TIR and EM synthetic?** Controlled modalities isolate the fusion
   mechanics; the recipes and code are released so the experiment can be
   repeated with real data.
3. **Why did the legacy EM hurt, and what changed?** The legacy row is linear in
   raw Ω·m, gives all five minerals a response, and assigns clay the *lowest*
   resistivity while the synthetic field places clay at higher log10 ρ. An
   EM-only fit under those rows is anti-correlated with the proxy (r = −0.469).
   Expressing EM as log10 ρ with a clay-only response fixes the sign and the
   scale (κ 1156 → 48.5) and raises F1 from 0.267 to 0.498. See §4.8 and
   `docs/EM_FIX.md`.
4. **Why is the +104 % claim withdrawn?** It comes from a different H matrix
   used only by the old ablation; the validation matrix gives different numbers.
5. **Why is the posterior variance not calibrated?** It is a forward-filter
   variance; the paper reports coverage and calibration error and does not
   claim a confidence interval.
6. **Why ASU endmembers lower F1?** They amplify TIR, and TIR encodes a
   different clay field from the evaluation proxy; this is a negative control
   for synthetic circularity, not a rejection of ASU data.




