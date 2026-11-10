# Data provenance

## Real data

| layer | source | identifier | native |
|---|---|---|---|
| K, eU, eTh | USGS airborne radiometric survey, Ivanpah–Clark Mountain NV–CA | delivered `raw/K.gxf`, `eU.gxf`, `eTh.gxf` + line CSV | 50 m, 295,943 samples at 1 Hz, 2019-12-13 → 2020-03-21 |
| ASTER TIR ×5 | ASTER L1T v003 (NASA/METI), via Microsoft Planetary Computer | 4 scenes of 2006-10-18 (+3 of 2006-09-25), archived under `raw/aster/` with STAC ids and SHA-256 | 90 m, 5 bands 8.29–11.29 µm |
| TMI | USGS aeromagnetics, same survey block | `raw/TMI.gxf` | 50 m |
| geology | USGS SIM 3206 surficial geologic map | DOI 10.3133/sim3206, `raw/sim3206_database/` | polygons → 50 m |

The ASTER scenes are downloaded once by `code/fetch_aster.py`, which writes
`raw/aster/<date>/manifest.json` (STAC item id, source URL without the SAS token,
bytes, SHA-256). `code/prepare_tir_real.py` then works **offline** from that
archive, so the thermal cube is reproducible without network access.

## Synthetic data

| layer | recipe | why synthetic |
|---|---|---|
| EM, 40 layers 0–600 m | Wisconsin AEM layer statistics + clay-linked field decaying as exp(−d/250) + independent and noise fields, seed 12345 | no measured airborne EM exists over this footprint; the delivered survey contains only radiometric and magnetic grids |

Every EM result in the manuscript and in `processed/*.json` is labelled
synthetic. No claim is made about field EM behaviour.

## Derived targets

| target | construction | status |
|---|---|---|
| `clay_prior` | 0.5·K + 0.3·(1−eTh) + 0.2·|eU−eTh| on p2–p98 normalised channels, smoothed σ = 15 px | gamma-derived, **circular** for gamma |
| `truth_abundance` | 0.4K+0.2eU etc., renormalised | only used to synthesise the control TIR cube |
| substrate labels | SIM 3206 classes rasterised to the grid | independent of all observed modalities |

## Corrections recorded

* the draft's "Colorado Mineral Belt 2023, 28,472 line-km" description was wrong;
  the grids are Ivanpah 2019–2020;
* ASTER replaces the synthetic splib07 TIR cube as the **main line**; the
  synthetic cube is now an explicit control;
* the analysis mask is the intersection of the radiometric survey and the ASTER
  coverage (97.8 % of the survey), so real and synthetic branches are compared on
  identical pixels.
