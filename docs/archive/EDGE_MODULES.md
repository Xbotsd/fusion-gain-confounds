# Edge modules: granite compensation, 1-D CNN residual learner, runtime

These are the three modules that the original proposal listed but the repository
never implemented. They are now implemented **in software form** and tested; the
results are reported honestly, including where they are negative.

| module | status | result |
|---|---|---|
| Granite interference compensation | **implemented, tested** | no interference found at this site; applying the compensation hurts |
| MCU-style 1-D CNN residual learner | **implemented (NumPy), INT8** | meets size/latency budgets; detection ranking degrades |
| <200 ms runtime | **measured on CPU** | 21 ms / 10k samples (9.5× margin); no Jetson available |

## 1. Granite interference compensation

### Data found and used (all real)

| property | source | value |
|---|---|---|
| Granite map | USGS SIM 3206 `felsic plutonic` polygons (DOI 10.3133/sim3206) | 105,249 valid pixels |
| Gamma signature | real K/eU/eTh grids, same survey | K 3.16 % (felsic) vs 3.04 % (other); eTh 5.96 vs 6.10 ppm |
| Magnetic | real TMI grid (`raw/TMI.gxf`, resampled to the 50 m grid) | felsic anomaly p90 131 nT; background −63 nT |
| Conductivity | real NGU airborne FDEM databases (Sulitjelma 2025, Røros 2020; 10 grids) | 103,484 measured apparent resistivities: p10 2.0, p50 1,856, p90 954,532 Ω·m |
| Literature granite range | published values | resistivity 1e3–1e5 Ω·m; susceptibility 1e-4–5e-2 SI |

### Findings

1. **The local granite is not radiometrically distinct.** K 3.16 vs 3.04 %,
   eTh 5.96 vs 6.10 ppm, eU 6.56 vs 6.78 ppm — a gamma-based granite detector
   does not separate felsic plutonic terrain at Ivanpah (logistic indicator:
   felsic 0.089 vs other 0.086, i.e. no separation). Granite detection requires
   the geologic map and/or magnetics.
2. **There is no measurable granite gamma interference to compensate.** With the
   corrected-EM fusion, clay on felsic terrain is 0.165 vs 0.175 elsewhere
   (excess −0.010). The gamma-derived proxy itself shows only +0.019 excess and
   a *lower* positive rate in granite (5.0 % vs 15.2 %).
3. **The geology-primary indicator works.** SIM 3206 polygons + magnetic
   smoothness give G = 0.748 on felsic vs 0.018 elsewhere.

### Compensation experiment (blend toward a gamma-free TIR+EM fusion)

| estimator | F1 | clay | clay on felsic | felsic excess | Kruskal H |
|---|---:|---:|---:|---:|---:|
| gamma+TIR+EM (corrected) | 0.498 | 0.174 | 0.165 | −0.010 | 71,591 |
| TIR+EM only | 0.361 | 0.375 | 0.395 | +0.022 | — |
| granite compensated | 0.475 | 0.192 | 0.336 | **+0.157** | 57,820 |

Applying the compensation **hurts**: F1 drops 0.023, felsic clay rises from
0.165 to 0.336 (because the TIR+EM estimator overestimates clay), and the
substrate discrimination weakens (felsic becomes the top-clay substrate, rank
1/8 vs 4/8). **The module is implemented and tested, and the honest conclusion
is that granite interference compensation is unnecessary and harmful on this
dataset.** The original proposal's assumption (granite inflates the clay
estimate) does not hold at Ivanpah with the corrected-EM model.

Files: `prepare_granite.py`, `run_granite_compensation.py`,
`granite_indicator.npy`, `granite_properties.json`,
`granite_compensation.json/csv/png`, `fig_granite.png`, `tmi_grid.npy`.

## 2. MCU-style 1-D CNN residual learner (INT8, <300 KB)

Pure-NumPy implementation (no torch/tf/onnx): `Conv1D(16,k3) → Conv1D(12,k3) →
Dense(24) → Dense(1)` over the 10-channel observation plus the physics clay
estimate; residual learning `prediction = physics_clay + CNN(features)`; trained
20 epochs (SGD with decay) on 120 k pixels from even 64-px blocks, tested on
200 k pixels from odd blocks.

| model | params | INT8 size | matched F1 | AP | RMSE |
|---|---:|---:|---:|---:|---:|
| physics (corrected-EM fusion) | — | — | 0.525 | **0.533** | 0.350 |
| CNN float | 2,717 | — | 0.418 | 0.377 | **0.102** |
| CNN INT8 | 2,717 | **2.7 KB** | 0.419 | 0.377 | 0.102 |

- **Size budget met**: 2.7 KB INT8 vs the 300 KB budget (111× margin).
- **Regression improves**: RMSE 0.350 → 0.102 (−70 %).
- **Detection ranking degrades**: AP 0.533 → 0.377 (−29 %). The per-pixel CNN
  regresses toward the local mean; it learns the smooth part of the proxy but
  loses the sharp contrasts that rank proxy positives.
- **INT8 quantization is essentially free** (AP 0.344 → 0.360, within noise).

The module therefore demonstrates the deployment path (train → quantize →
size/latency) but **cannot be claimed as an accuracy improvement**; it would be
used for its speed, not its accuracy.

Caveat: the training target is the gamma-derived clay proxy, so even a perfect
CNN would only reproduce the proxy, not geological truth.

Files: `run_edge_ai.py`, `edge_ai.json/csv/png`.

## 3. Runtime (<200 ms)

Measured on CPU (no Jetson/MCU device available; INT8 is simulated — quantized
weights, float arithmetic):

| workload | latency |
|---|---:|
| 10,000-sample tile, float CNN | 20.1 ms |
| 10,000-sample tile, INT8-sim CNN | 21.0 ms |
| per sample | 2.1 µs |
| **budget** | **<200 ms → met with 9.5× margin** |

A 1-km² tile at 50 m is 20×20 = 400 samples → ~0.9 ms. Even a 25 km² block
(1,000,000 pixels) stays near 2 s single-threaded on this CPU. The 200 ms budget
is a CPU measurement; Jetson Orin numbers are **not** claimed because no device
was available.

## 4. Pseudo-replication warning (data reliability)

The 1,265,683 valid pixels are a 50 m grid of a spatially autocorrelated field.
Measured integral scales (`autocorr_sample_size.py`): clay proxy τ ≈ 53 px
(2.7 km), corrected-EM clay τ ≈ 42 px (2.1 km). Design effects are 11,482 and
7,250, so the **effective sample sizes are only ~110 and ~175**, not 1.27 M.
Consequences:

- every pixel-level standard error is understated by ~2 orders of magnitude;
- the original 32-px bootstrap blocks were *smaller* than the correlation
  length and have been replaced by 128-px (6.4 km) blocks in
  `block_bootstrap.py` and `run_em_fix.py`;
- the corrected-EM ΔF1 becomes +0.167 [0.118, 0.216] (still 200/200 wins);
- per-64-px-block AP of the physics estimator on the CNN test blocks is
  0.438 ± 0.296 over 19 blocks — the honest uncertainty scale for any
  pixel-level metric is ±0.3, not the nominal pixel-count standard error.

The 10-run "±0.00005" repeatability numbers measure numerical stability under
noise re-seeding, **not** sampling uncertainty. `pipeline_validation.json`
now carries cross-checks that the bootstrap block size exceeds 2× the integral
scale and that N_eff is reported.

## 5. What changed in the project's claim table

- "1-D CNN, INT8, <300 KB" — was *not implemented* → now **implemented and
  measured** (2.7 KB, AP negative).
- "Jetson/<200 ms" — was *not measured* → now **CPU-measured, budget met**;
  Jetson still not claimed.
- "Granite interference compensation" — was *zero traces* → now **implemented
  and tested; no interference at this site; compensation harmful**.
- The magnetic (TMI) and NGU conductivity data are now part of the data
  inventory with real measured values.


- "1-D CNN, INT8, <300 KB" — was *not implemented* → now **implemented and
  measured** (2.7 KB, AP negative).
- "Jetson/<200 ms" — was *not measured* → now **CPU-measured, budget met**;
  Jetson still not claimed.
- "Granite interference compensation" — was *zero traces* → now **implemented
  and tested; no interference at this site; compensation harmful**.
- The magnetic (TMI) and NGU conductivity data are now part of the data
  inventory with real measured values.


