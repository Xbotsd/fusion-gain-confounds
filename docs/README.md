# Airborne multi-modal mineral exploration — reproducible benchmark

A real-data benchmark that asks when adding a modality to airborne mineral
exploration actually helps, and separates the two reasons a reported gain can be
spurious: a **circular target** and an **underdetermined inversion**.

## Data

| layer | status | source |
|---|---|---|
| K, eU, eTh | **real** | USGS airborne radiometric survey, Ivanpah–Clark Mountain NV–CA, 2019–2020, 295,943 samples |
| thermal infrared ×5 | **real** | ASTER L1T v003, 2006-10-18, emissivity via normalisation TES, 90 m → 50 m |
| aeromagnetics | **real** | USGS TMI grid (used in the edge experiment only) |
| geology | **real** | USGS SIM 3206 surficial map, DOI 10.3133/sim3206 (independent target) |
| EM ×3 layers | **synthetic** | no measured AEM exists over this footprint; documented recipe, seed 12345 |

Every EM result in the paper and in the artefacts is labelled synthetic.

## The central result

With three gamma channels and five mineral unknowns the inverse problem has
**rank 3**, and gamma alone scores at chance against independent geology
(AUC 0.387). Adding the five ASTER bands raises proxy F1 0.531 → 0.652 and the
geological AUC to 0.913 — but appending five channels of **zeros** with the same
response rows reproduces F1 0.649 and AUC 0.922. Almost all of that gain is
conditioning, not information.

A model-free test (multinomial logistic, 128-px block CV, no response matrix)
isolates the real information: gamma + ASTER reaches balanced accuracy 0.529
versus 0.350 for gamma alone (+0.179, 95 % CI [0.120, 0.241], 20/20 repeats),
while a block-shuffled ASTER cube gives 0.354 — no gain.

## Quick start

```powershell
.\run.bat                      # prepare → main → controls → aux → figures → audit
.\run.bat main                 # only the paper's experiments
D:\miniconda3\envs\geo\python.exe code\test_core.py    # unit tests
```

The launcher auto-selects an interpreter with numpy/scipy/GDAL (env
`AMPYTHON` overrides). The ASTER scenes are archived under `raw/aster/` with
their STAC ids and SHA-256, so `prepare` runs offline; to re-download them run
`python code/fetch_aster.py`.

## Pipeline

| stage | scripts | produces |
|---|---|---|
| prepare | gamma, synthetic TIR, EM, **real ASTER TIR**, geology | cubes + analysis mask |
| main | `run_main.py` | ablation, baselines, bootstrap, repeats, calibration |
| controls | `run_tir_controls`, `run_tir_information`, `run_geology_multiclass`, `run_identifiability`, `run_real_tir_robust` | conditioning and information tests |
| aux | depth, published baselines, calibration, autocorr, edge | supporting experiments |
| legacy | synthetic-TIR reference branch | the comparison table |
| audit | unit tests, coverage guard, validator, manifest | PASS/FAIL + SHA-256 |

`code/validate_pipeline.py` checks 53 artefacts and 22 invariants, including the
zero-filled and shuffled controls, so a regression cannot silently restore a
spurious gain.

## Documentation

`docs/RESULTS.md` (numbers), `docs/DATA_PROVENANCE.md` (sources and recipes),
`docs/READINESS_AUDIT.md` (publication readiness), `docs/GAP_AUDIT.md` (what is
missing and why), `docs/MODEL_AUDIT.md` (model caveats),
`docs/NORMALISATION_AUDIT.md` (the two switch-off bugs and their fix),
`docs/REFERENCES_AUDIT.md` (bibliography state), `docs/CHANGELOG.md`.

Older round notes are in `docs/archive/`; they are historical and their numbers
are superseded — see `docs/archive/README.md`.

## Licence

MIT (`LICENSE`), with USGS / NASA-METI / NGU data-source notices.
