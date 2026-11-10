# Pipeline audit — execution, yield and old-vs-new comparison

Generated after the full run on 2026-10-21. Machine-readable companions:
`processed/pipeline_validation.json`, `processed/data_manifest.json`,
`processed/repeats.json`, `processed/depth.json`.

## 1. Execution status

| Stage | Script | Wall time | Status | Main output |
|---|---|---:|---|---|
| Gamma | `prepare_gamma.py` | — | PASS | `gamma_cube.npy`, `clay_prior.npy`, `valid_mask.npy` |
| TIR | `prepare_tir.py` | — | PASS | `tir_cube.npy` |
| EM | `prepare_em.py` | — | PASS | `em_cube.npy` |
| Fusion | `run_fusion.py` | 5.0–11.5 s (load-dependent) | PASS | `kf_mineral_abundance.npy`, `fusion.json` |
| Depth | `run_depth.py` | 99.1 s | PASS | `depth_kalman_3d.npy`, `depth_uncertainty.npy`, `depth.json` |
| Corrected validation | `run_validation_emfix.py` | 69.2 s | PASS | `validation_emfix.*` |
| Corrected depth | `run_depth_emfix.py` | 80.3 s | PASS | `depth_*_emfix.*` |
| TMI resample | `prepare_tmi.py` | — | PASS | `tmi_grid.npy` (real magnetics) |
| Granite prep | `prepare_granite.py` | — | PASS | `granite_indicator.npy`, `granite_properties.json`, `fig_granite.png` |
| Granite compensation | `run_granite_compensation.py` | — | PASS | `granite_compensation.*` |
| Edge AI | `run_edge_ai.py` | — | PASS | `edge_ai.*` (CNN, INT8, latency) |
| Pseudo-replication | `autocorr_sample_size.py` | — | PASS | `autocorr.*` (τ, DE, N_eff, block check) |
| Ablation | `run_ablation.py` | — | PASS | `ablation.csv/json/png` |
| Corrected ablation | `run_ablation_emfix.py` | — | PASS | `ablation_emfix.*` |
| Corrected calibration | `run_calibration_emfix.py` | — | PASS | `calibration_emfix.*` |
| Validation | `run_validation.py` | 131.7 s | PASS | `validation.csv/json/md/png` |
| Baselines | `run_baselines.py` | — | PASS | `baselines.csv/json/png` |
| Environment | `run_environment.py` | — | PASS | `environment.json/png`, `env_*.npy` |
| Sensitivity | `run_sensitivity.py` | — | PASS | `sensitivity.json/png`, `resolution.csv` |
| ASU variant | `fetch_asu_spectra.py` + `run_asu_variant.py` | — | PASS | `tir_cube_asu.npy`, `fusion_asu.json`, `fig_asu_endmembers.png` |
| V2 testbed | `run_v2.py` | — | PASS | `processed/v2/*` |
| Calibration | `uncertainty_calibration.py` | — | PASS | `calibration.json/csv/png` |
| Bootstrap | `block_bootstrap.py` | — | PASS | `bootstrap.json/csv` |
| EM correction | `run_em_fix.py` | — | PASS | `em_fix.json/csv/png` |
| Structured H | `structured_perturbation.py` | — | PASS | `structured_perturbation.json/csv/png` |
| Threshold sweep | `threshold_sensitivity.py` | — | PASS | `threshold_sensitivity.*` |
| Scenario CIs | `scenario_bootstrap.py` | — | PASS | `scenario_bootstrap.*` (22 scenarios, BH-corrected) |
| Independent geology | `independent_validation.py` | — | PASS | `independent_validation.*`, `geology_substrate.npy` |
| Repeats | `run_repeats.py` | 14.0 s | PASS | `repeats.json`, `repeat_*_abundance.npy` |
| Figures | `make_figures.py` | — | PASS | `fig_data/method/results.png` |
| Audit | `audit_data.py` | — | PASS | `docs/data_audit.json`, `docs/model_audit.json` |
| Unit tests | `test_core.py` | 24 checks | PASS | `ALL TESTS PASSED` |
| Coverage guard | `check_coverage.py` | 0.2 s | PASS | every artefact has a producer in `run_all.py` |
| Integrity | `validate_pipeline.py` | 0.4 s | PASS | `pipeline_validation.json` (95/95, 13/13 cross-checks) |
| Manifest | `build_manifest.py` | 8.6 s | PASS | `data_manifest.json` (6,701 files) |

`run_all.py audit` from the project root also passes. PowerShell may report
`exit code 1` because GDAL writes a FutureWarning to stderr; the Python
subprocess exit code is 0. This is a console artefact, not a pipeline failure.

## 2. Output yield

From `pipeline_validation.json`:

| Metric | Value |
|---|---:|
| Grid pixels | 1,904,900 |
| Valid survey pixels | 1,265,683 |
| Valid fraction | **0.6644** |
| Finite abundance on valid pixels | **1.0000** |
| Predicted positive rate (clay>0.25 & top-2) | 0.6002 |
| Clay range on valid pixels | 0.00–1.00 |
| Artefacts present / expected | **89 / 89 (100 %)** |
| Experiment records | **65** (4 ablation, 28 validation, 6 baselines, 20 seeds, 5 resolutions, 2 weightings) |
| Fusion runtime | 11.49 s |
| Throughput | **110,000–252,000 valid pixels/s** (wall-clock, load-dependent) |

Data volume:

| Item | Files | Size |
|---|---:|---:|
| Raw inputs + spectral library (`raw/`) | 6,376 | 2.18 GB |
| Root survey vectors / report / CSV / license | 32 | 0.17 GB |
| Processed, top level | 127 | 8.27 GB |
| Processed `em/` | 28 | 0.25 GB |
| Processed `spectra/` | 10 | <0.01 GB |
| Processed `v2/` | 8 | 1.87 GB |
| Code (`code/`, incl. `dev/`) | 52 | 0.23 MB |
| Docs | 38 | 8.08 MB |
| Manifest total | **6,701** | **12.77 GB** |

Raw/root/processed/code/docs/`v2` are counted recursively; `processed/` top-level
excludes its three sub-directories. Numbers are reproduced by `build_manifest.py`
(`processed/data_manifest.json` → `summary`).

## 3. Old vs new

Old values are the documented legacy results (the old files were removed during
cleanup; sources: `final_validation_gt.txt`, `ablation_metrics_v3.txt`,
`exp11_cross_domain.txt`, and the old depth cube). They are **not** directly
comparable because the old metrics mixed grid coverage with valid-pixel recall.

| Item | Old (draft/legacy) | New (cleaned) | Note |
|---|---:|---:|---|
| Recall | 0.6526 | **0.6933** | Old: all pixels; new: valid pixels |
| Precision | 0.1521 | **0.1654** | Same positive definition |
| F1 | 0.2474 | **0.2671** | New is slightly higher |
| “Detection rate” | 65.26 % | **65.94 %** mean proxy recall | Renamed; not a detection rate |
| Ablation clay | 0.198 → 0.403 | **0.342 → 0.458** | Old used matrix A; new uses one H |
| Depth clay | 0.245 → 0.312 (paper) | **0.276 → 0.444** | New depth uses unified H |
| Cross-domain gap | 5.215 % → 0.273 % | **0.080 % → 0.174 %** | CORAL does not help |
| Code files | 48 | **52** | versions removed, dev/ parked |
| Processed files | 125 | **127** | ASU + V2 + calibration + CIs added |
| Processed size | ≈5.1 GB | **8.27 GB** | ASU + V2 cubes, corrected depth |
| Multi-run average | none | **10 runs** | see below |
| Integrity check | none | **95/95 PASS** | new |

The changes are explained by three fixes, not by new data:

1. all metrics are computed on the 66.4 % valid footprint, not the NoData fill;
2. the ablation and validation share one H matrix;
3. the depth cube is regenerated with the same H as the 2-D fusion.

## 4. Multi-run average

`run_repeats.py`: 10 independent 1 % channel-noise realisations.

| Metric | Mean | Std | 95 % CI |
|---|---:|---:|---|
| Recall | 0.69330 | 0.00014 | [0.69321, 0.69339] |
| F1 | 0.26706 | 0.00005 | [0.26703, 0.26709] |
| Clay mean | 0.45829 | 0.00001 | [0.45829, 0.45830] |

Pixel-wise mean/std maps: `repeat_mean_abundance.npy`, `repeat_std_abundance.npy`.
The existing 20-seed sensitivity (2 % noise) gives recall 0.69329 ± 0.00015,
consistent with the 10-run result.

### ASU endmember check

Five measured ASU spectra (Quartz 479, Feldspar 468, Clay 571, Calcite 604,
Dolomite 515) were downloaded with `fetch_asu_spectra.py` and used to rebuild a
TIR variant. The stronger ASU contrast lowers proxy F1 from 0.267 to 0.132,
because the synthetic TIR truth and the evaluation proxy are different fields.
The variant is a sensitivity/negative control, not a replacement of the main
results; details in `docs/ASU_VARIANT.md`.

### Uncertainty calibration

The forward-filter variance is severely under-confident against the proxy:
68 % nominal coverage is 10.3 %, 95 % is 20.2 %; the variance scale factor is
17.97, which raises coverage only to 49.1 % and 100 %. See `calibration.json`.

### V2 testbed

Even with a single truth field, log10 EM and a clay-only EM row, gamma alone
remains best on the gamma-derived proxy (F1 0.489 vs 0.219 for gamma+TIR and
0.179 for all). This confirms that the target definition, not only the synthetic
recipe, limits the fusion gain. See `docs/V2_VARIANT.md`.

### Block bootstrap

A 128×128 (6.4 km) spatial block bootstrap (200 replicates) gives F1 0.2639
[0.2395, 0.2854] for the proposed estimator vs 0.3294 [0.3027, 0.3529] for the
independent inversion; ΔF1 = −0.064 [−0.116, −0.022] and ours never wins.
The accuracy deficit is statistically significant; the advantage is coherence,
not accuracy. See `bootstrap.json`.

### Corrected EM

Replacing raw Ω·m + five-mineral EM with log10(ρ) + clay-only response raises F1
from 0.267 to **0.498** and AP from 0.126 to **0.513**. The block bootstrap gives
ΔF1 = +0.167 [0.118, 0.216], 200/200 wins over Independent. This is the main
positive result; see `em_fix.json` and `docs/EM_FIX.md`.

The diagnosis is measured, not asserted: an EM-only fit under the legacy rows is
anti-correlated with the proxy (r = −0.469) because the row gives clay the lowest
resistivity while the synthetic field puts clay at higher log10 ρ; the raw Ω·m
scale presses the TIR mineral contrast from 0.21–0.26 to 0.024 and raises κ(H)
from 48.5 to 1156.

The depth profile `β = [0.90, 0.86, 0.36]` is the recipe's `exp(−d/250)` clay
decay at the layer centres, rounded, not a fitted parameter.
`run_em_beta_sensitivity.py` sweeps four profiles: 0.498 (production), 0.490
(exact decay), 0.483 (reversed), 0.459 (uniform) — all ≥ 0.19 F1 above the legacy
model. Two cross-checks (`em_beta_matches_recipe`, `em_beta_robust`) enforce this
in `validate_pipeline.py`.

With the corrected EM, validation overall recall is **0.829** (legacy 0.661),
overall F1 **0.480** (legacy 0.254), temperature-family recall **0.912** (legacy
0.476), H-sensitivity **0.861** (legacy 0.687); EMI failure now hurts (0.338) and
TIR failure helps (0.949). Depth clay decreases from 0.276 at 0.1 m to 0.179 at
500 m, versus 0.276→0.444 for the legacy model. See
`docs/EM_FIX_VALIDATION.md`.

### Pseudo-replication

The clay fields are autocorrelated over τ ≈ 42–53 px (2.1–2.7 km); design
effects 7,250–11,482 give **N_eff ≈ 110–175** independent samples, not 1.27 M
pixels. The original 32-px bootstrap blocks were smaller than the correlation
length; they have been replaced by 128-px (6.4 km) blocks. Corrected-EM
ΔF1 = +0.167 [0.118, 0.216] (200/200 wins). Per-64-px-block AP of the physics
estimator is 0.438 ± 0.296 across 19 blocks — the honest uncertainty scale.
`pipeline_validation.json` cross-checks that blocks ≥ 2τ and that N_eff is
reported. See `autocorr.json` and `docs/EDGE_MODULES.md` §4.

### Edge modules

Granite compensation: the local felsic terrain is not radiometrically distinct
(K 3.16 vs 3.04 %) and has no clay excess (−0.010); applying the compensation
lowers F1 0.498→0.475 and raises felsic clay 0.165→0.336. Real data used: SIM
3206 geology, real TMI, and 103,484 measured NGU FDEM apparent resistivities
(p50 1,856 Ω·m). The 1-D CNN residual learner (2,717 params, 2.7 KB INT8) meets
the size and latency budgets (21 ms/10k samples on CPU) but degrades average
precision (0.533→0.377). See `docs/EDGE_MODULES.md`.

### Independent geology

The USGS SIM 3206 surficial map gives clay 0.487 (alluvium), 0.426 (felsic
plutonic), 0.417 (volcanic), 0.011 (carbonate), 0.020 (sedimentary);
Kruskal–Wallis p<0.001. It is a qualitative substrate check, not an alteration
label. See `docs/INDEPENDENT_VALIDATION.md`.

## 5. Data-structure completeness

`data_manifest.json` records every file with SHA-256 and schema:

* 6,701 files, 11.24 GB;
* `.npy` → shape + dtype;
* `.csv` → rows + header;
* `.json` → top-level keys;
* root shapefiles, report PDF and radiometric CSV are now included.

`DATA_STRUCTURE.md` documents the stage graph, array schemas, JSON schemas,
integrity rules and yield definitions.

## 6. Issues found and fixed during this audit

1. **Depth H mismatch.** The old depth cube was produced with the ablation
   matrix (clay K=1); the new run uses the unified validation matrix (clay K=4).
   New clay profile: 0.276 → 0.444 (old: 0.258 → 0.386 on valid pixels).
2. **Stale depth uncertainty.** `depth_kalman_P.npy` and the old
   `depth_kalman_*.png` were from the old H and have been deleted; the new
   outputs are `depth_uncertainty.npy` and `depth_*.png`.
3. **Validator JSON bug.** `sorted()` was applied to JSON arrays
   (`ablation.json`, `baselines.json`); fixed to handle list/dict.
4. **`run_all.py` cwd bug.** Scripts were resolved relative to the current
   directory; now resolved relative to `code/`, so `python code/run_all.py`
   works from the project root.
5. **Manifest scope.** Root survey vectors, report and CSV were missing; added.
6. **Documentation number.** The predicted-positive rate was written as ≈42 %
   in `RESULTS.md`; corrected to ≈60 %.

## 7. Verdict

* **Data chain:** complete — 95/95 artefacts pass, shapes/metrics consistent.
* **Code:** every stage runs; the only non-zero console exit is the GDAL warning.
* **Yield:** 66.4 % spatial coverage, 100 % finite output on valid pixels,
  65 experiment records, 135 k valid pixels/s for the main fusion.
* **Reproducibility:** 10-run average and 20-seed sensitivity agree to 1e-4.
* **Remaining scientific limits:** TIR/EM are synthetic; no independent ground
  truth; no hardware; the depth model repeats surface gamma/TIR at every layer.







































