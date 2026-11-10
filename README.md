# Airborne multi-modal mineral exploration — reproducible benchmark

Real-data benchmark that asks **when adding a modality to airborne mineral
exploration actually helps**, and separates the two reasons a reported gain can
be spurious: a circular target and an underdetermined inversion.

| layer | status | source |
|---|---|---|
| K, eU, eTh | **real** | USGS airborne radiometrics, Ivanpah–Clark Mountain NV–CA, 2019–2020 (295,943 samples) |
| thermal infrared ×5 | **real** | ASTER L1T v003, 2006-10-18, emissivity by normalisation TES, 90 m → 50 m |
| aeromagnetics | **real** | USGS TMI grid (edge experiment) |
| geology | **real** | USGS SIM 3206 surficial map, DOI 10.3133/sim3206 (independent target) |
| EM ×3 layers | **synthetic** | no measured airborne EM exists over this footprint; recipe and seed documented |

## Headline result

Three gamma channels for five mineral unknowns give **rank 3**, and gamma alone
scores at chance against independent geology (AUC 0.387). Adding the five ASTER
bands raises proxy F1 0.531 → 0.652 and the geological AUC to 0.913 — but five
channels that carry no information - all zeros, Gaussian noise, or the
block-shuffled cube - recover 69-98 % of that F1 gain and all of
the AUC gain, so most of it is **conditioning**.

A model-free test that has no response matrix isolates the real information:
gamma + ASTER reaches balanced accuracy 0.529 versus 0.350 for gamma
(+0.179, 95 % CI [0.120, 0.241], 20/20 repeats), while a block-shuffled ASTER
cube gives 0.354.

## Reproduce

```powershell
.\run.bat                  # prepare → main → controls → aux → figures → audit
.\run.bat legacy           # synthetic-TIR reference branch (optional)
```

Measured: 53 artefacts, 22 invariants, 25 unit tests, 0 coverage orphans.

## Layout

```
code/       pipeline (see docs/SUPPLEMENTARY.md for the script inventory)
docs/       manuscript, results, provenance, audits
processed/  JSON/CSV artefacts and figures (cubes are regenerated, not tracked)
raw/        delivered survey + archived ASTER scenes (not tracked; see docs/DATA_PROVENANCE.md)
```

Start with `docs/README.md`, then `docs/RESULTS.md` and
`docs/READINESS_AUDIT.md`. Licence: MIT, with USGS / NASA-METI data notices.
