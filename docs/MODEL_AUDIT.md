# Model audit

This document records the irregularities found while cleaning the repository.
They are reproducible from `docs/model_audit.json` (written by
`code/audit_data.py`) and from the scripts named below.

## 1. The draft used two different response matrices

`ablation_v3.py` (which produced the +104 % claim) used matrix **A**; the
validation scripts (`final_gt.py`, `final_validation_v2.py`) used matrix **B**.
The clay signatures are opposite:

| | K | eU | eTh | EM clay |
|---|---:|---:|---:|---:|
| A (ablation) | 1.0 | 3.0 | **4.0** | 20 Ω·m |
| B (validation, now used everywhere) | **4.0** | 1.5 | **1.0** | 20 Ω·m |

Matrix A makes clay Th-rich, which contradicts the K/eTh alteration proxy used
as the evaluation target.  Consequence (decimated grid, same metric):

| matrix | configuration | clay mean | recall | F1 |
|---|---|---:|---:|---:|
| A | gamma only | 0.321 | 0.191 | 0.090 |
| A | all | 0.435 | 0.258 | 0.110 |
| B | gamma only | 0.343 | 0.791 | 0.330 |
| B | all | 0.457 | 0.706 | 0.270 |

The original ablation numbers (0.198 → 0.403, +104 %) come from matrix A and a
different grid/mask convention; they do not reproduce under the cleaned
pipeline, and the two matrices do not even agree on the sign of the clay–Th
relationship.  The +104 % is therefore **not a modality effect**.  The pipeline
now uses matrix B only.  `docs/RESULTS.md` reports the corrected ablation.

## 2. Two different synthetic clay truths

| field | used by | mean | corr with `clay_prior` |
|---|---|---:|---:|
| TIR truth (`0.3K + 0.3eTh`) | `prepare_tir.py` | 0.30 | **0.57** |
| EM truth (`clay_prior`) | `prepare_em.py` | 0.46 (0.49 on valid pixels) | 1.00 |

TIR and EM encode *different* clay patterns.  Fusing them cannot consistently
improve a single target, and the ablation results depend on which target is
chosen.  This is the deepest limitation of the current dataset and cannot be
fixed without regenerating both cubes from one truth field.

## 3. The adaptive noise matrix was inert in the main results

`final_gt.py` and `final_validation_v2.py` computed

```
snr = rms(z_norm) / rms(z_norm - mean)
R   = clip(1/(snr + 0.1), 0.1, 10)
```

on z-scored data, where `snr ≈ 1` for every channel.  Recomputed on the actual
cubes: **R = 0.909 for all ten channels**.  The main results therefore used
uniform weights, not environment-aware weights.

## 4. The adaptive direction was inverted in the scenario scripts

`degradation_test_v4.py` estimated `R = noise / mean(noise)` and then used `R`
directly as the WLS weight:

```
HtWH = H^T (H * R)          # larger R -> larger weight
```

so the noisiest channel received the **largest** weight, while the diagnostic
figure plotted `1/R` as the “adaptive weight”.  `temperature_advanced.py` had
the same inversion (`R = 1/w` used as a weight).  The cleaned code uses explicit
quality multipliers `W = diag(q)` with higher `q` = more weight.

## 5. Metric definitions were mixed

| script | quantity | value |
|---|---|---:|
| `final_validation_v2.py` | fraction of pixels with clay > 0.25 and top-2 | 0.4282 |
| `final_gt.py` | recall against `clay_prior > 0.55` | 0.6526 |
| `final_validation_gt.txt` | precision / F1 at that point | 0.152 / 0.247 |

The manuscript quotes 0.6526 as “detection rate” but does not report precision
or F1.  The cleaned pipeline uses one contingency table and reports all four
metrics on valid pixels.

## 6. The current EM response hurts the proxy target

With the raw-resistivity matrix B, down-weighting or removing EM **increases**
recall against `clay_prior`:

| scenario | recall |
|---|---:|
| normal | 0.693 |
| EMI failed (×20, weight 1/20) | **0.976** |
| TIR degraded | 0.433 |
| gamma degraded | 0.602 |

This is the opposite of the draft's “graceful degradation” story. The reason is
mechanical and measurable. The EM columns give clay the *lowest* resistivity of
the five minerals while the synthetic field places clay at *higher* log10 ρ, so
the row pulls the clay estimate the wrong way: an EM-only fit under the legacy
rows is anti-correlated with the proxy (r = −0.469, F1 0.06). The raw Ω·m scale
also dominates the column norms, pressing the TIR mineral contrast from 0.21–0.26
to 0.024 and raising the condition number of the normalised matrix from 48.5 to
1156. A physically consistent EM row is **clay-only in log10(Ω·m)**, with
`z_EM = log10(rho)`. That correction was subsequently adopted as the main model
(manuscript §7.5): F1 rises from 0.168 to 0.497 and AP from 0.123 to 0.577, and
all validation, degradation, temperature and depth experiments were re-run with
it. See `docs/EM_FIX.md` and `docs/EM_FIX_VALIDATION.md`.

## 7. Depth model

`depth_kalman_v2.py` repeats surface gamma and TIR at all 40 layers.  The deep
abundance variation is therefore driven by EM plus the `F/Q` prior, not by
depth-sensitive gamma/TIR.  The 3-D cube should be read as a smooth interpolation
constrained by EM, not as an independent deep measurement.

## 8. What was fixed in this repository

* one `H` matrix for every experiment;
* one metric definition, valid-pixel mask, precision/F1 alongside recall;
* explicit quality weights with the correct direction;
* provenance corrected to the Ivanpah survey;
* versioned duplicates and the pre-translation backup removed;
* figures redrawn without unimplemented modules;
* `docs/PAPER_VS_IMPLEMENTATION.md` lists every claim that is not supported.
