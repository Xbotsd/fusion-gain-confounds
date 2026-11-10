# Results — real ASTER main line

Every number comes from `processed/main_results.json` and the artefacts listed
below. Mask: radiometric survey ∩ full ASTER coverage, **1,237,644
pixels** (65.0% of the grid).

## 1. Ablation

| EM model | configuration | F1 | AP | recall | precision | geology AUC |
|---|---|---:|---:|---:|---:|---:|
| corrected | gamma | 0.531 | 0.393 | 0.965 | 0.367 | 0.387 |
| corrected | gamma+tir | 0.652 | 0.624 | 0.814 | 0.543 | 0.913 |
| corrected | gamma+em | 0.418 | 0.456 | 0.964 | 0.267 | 0.724 |
| corrected | all | 0.497 | 0.577 | 0.934 | 0.338 | 0.912 |
| legacy | gamma | 0.531 | 0.393 | 0.965 | 0.367 | 0.387 |
| legacy | gamma+tir | 0.652 | 0.624 | 0.814 | 0.543 | 0.913 |
| legacy | gamma+em | 0.192 | 0.128 | 0.391 | 0.128 | 0.898 |
| legacy | all | 0.168 | 0.123 | 0.331 | 0.113 | 0.826 |

## 2. The central result: conditioning versus information

| configuration | F1 | geology AUC | 4-class balanced accuracy |
|---|---:|---:|---:|
| gamma | 0.531 | 0.387 | 0.350 |
| gamma + real ASTER | 0.652 | 0.913 | 0.529 |
| gamma + block-shuffled ASTER | 0.634 | 0.913 | 0.354 |
| gamma + five noise channels | 0.649 | 0.922 | — |
| gamma + synthetic TIR | 0.597 | 0.905 | 0.389 |

Inside the estimator, noise-filled and shuffled copies score like the real cube:
the gain is conditioning. Without a response matrix the information gain is
+0.179 balanced accuracy
(95 % CI +0.120 to
+0.241, improving in
20/20 repeats), and it disappears for
a shuffled cube (+0.003).

## 3. Identifiability

| model | subset | equations | rank | κ | clay variance |
|---|---|---:|---:|---:|---:|
| legacy | gamma | 3 | 3 | 7.2 | 1.18e-03 |
| legacy | gamma+TIR | 8 | 5 | 15.8 | 1.39e-03 |
| corrected | all | 11 | 5 | 15.6 | 1.03e-03 |

The variance gain index is positive for every addition and agrees with the F1 sign
in 1/6 cases:
it cannot be used as evidence that fusion helps.

## 4. Estimator comparison (real ASTER, corrected EM)

| method | F1 | AP | geology AUC | components |
|---|---:|---:|---:|---:|
| GLS / Bayesian | 0.560 | 0.495 | 0.661 | 7,949 |
| Simple average | 0.506 | 0.480 | 0.838 | 3,514 |
| WLS only | 0.497 | 0.548 | 0.873 | 1,630 |
| WLS + Kalman | 0.497 | 0.577 | 0.912 | 919 |
| Fixed weight | 0.433 | 0.541 | 0.863 | 833 |
| PCA (3 comp.) | 0.425 | 0.387 | 0.857 | 1,678 |
| Independent | 0.355 | 0.456 | 0.697 | 4,786 |
| WLS + Kalman (legacy EM) | 0.168 | 0.123 | 0.826 | 1,695 |

## 5. Bootstrap contrasts

| contrast | Δ | 95 % CI | P(better) |
|---|---:|---|---:|
| F1 corrected_vs_legacy_EM (real, all) | +0.332 | [+0.244, +0.430] | 1.00 |
| F1 corrected_vs_independent (real) | +0.143 | [+0.106, +0.182] | 1.00 |
| F1 gamma+TIR_vs_gamma (real) | +0.119 | [+0.067, +0.167] | 1.00 |
| F1 real_vs_synthetic gamma+TIR | +0.055 | [-0.015, +0.122] | 0.94 |
| F1 real_vs_synthetic all | -0.003 | [-0.025, +0.024] | 0.42 |
| AUC gamma+TIR_vs_gamma (real) | +0.457 | [+0.123, +0.697] | — |
| AUC all_vs_gamma (real) | +0.458 | [+0.149, +0.691] | — |
| AUC real_vs_synthetic gamma+TIR | +0.012 | [+0.000, +0.025] | — |

## 6. Stability and uncertainty

Ten repeats with 1 % channel noise: F1 0.49669 ±
0.00003; geology AUC
0.9117 ±
0.0001.

Calibration: 68 %/95 % coverage 0.129/
0.258, variance scale
13.5. The filter variance is **not** a
confidence interval.

Pseudo-replication: integral scale 50 px
(2508 m), design effect
10168, **N_eff 122**
from 1,237,644 pixels.

## Files

`main_results.json`, `main_ablation.csv`, `main_baselines.csv`,
`tir_controls.json`, `tir_information.json`, `geology_multiclass.json`,
`identifiability.json`, `real_tir_robust.json`, `independent_validation.json`,
`published_baselines.json`, `depth.json`, `calibration.json`, `autocorr.json`.
