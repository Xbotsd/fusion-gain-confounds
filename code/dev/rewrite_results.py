"""Rewrite Section 7 as one coherent corrected-EM narrative with strict table order.

Table plan (sequential, each shown once):
  T1  data layers             (3.1, unchanged)
  T2  metric definitions      (3.6, unchanged)
  T3  legacy ablation         (7.1)
  T4  generic baselines       (7.1)
  T5  coherence metrics       (7.1)
  T6  structured H variants   (7.2)
  T7  corrected main result   (7.3)
  T8  corrected ablation      (7.4)
  T9  corrected depth profile (7.5)
  T10 corrected scenarios+CI  (7.5)
  T11 calibration both models (7.6)
  T12 published baselines     (7.10)
"""
from pathlib import Path

P = Path(r"D:\A_MineralProspecting\docs\Manuscript_v2_draft.md")
text = P.read_text(encoding="utf-8")
start = text.index("## 7. Results")
end = text.index("## 8. Discussion")

NEW = """## 7. Results

The section follows one model. Section 7.1 reports the legacy estimator, which
shows no fusion gain. Section 7.2 diagnoses why. Section 7.3 introduces the
corrected response matrix, which is the model used everywhere afterwards.
Sections 7.4-7.8 characterise it, and Sections 7.9-7.12 place it against
independent geology, published methods and edge deployment.

### 7.1 The legacy estimator shows no fusion gain

At the normal operating point the legacy fused map (Figure 3) has mean clay
0.458 on valid pixels, a spatial gradient of 0.00664 and a mean posterior
variance of 0.0080; the proxy metrics are recall 0.6933, precision 0.1654,
F1 0.2671 and IoU 0.1541. The low precision is expected: the target occupies
9.5 % of the valid pixels while the estimator labels about 60 % positive. The
earlier “65.26 %” figure was recall alone.

Table 3 reports the legacy ablation. Gamma alone gives clay 0.342 and F1 0.325;
adding TIR raises F1 to 0.339; adding EM lowers it to 0.191; the full set gives
clay 0.458 but F1 0.267. The widely quoted +104 % gain (0.198 → 0.403) does not
reproduce: it was produced by an ablation matrix whose clay signature is K-poor
and Th-rich, opposite to the validation matrix. The +104 % is therefore a
matrix artefact, not a modality effect.

| Configuration | Clay | Gradient | Recall | Precision | F1 |
|---|---:|---:|---:|---:|---:|
| Gamma | 0.342 | 0.00673 | 0.773 | 0.205 | 0.325 |
| Gamma + TIR | 0.392 | 0.00406 | 0.973 | 0.205 | 0.339 |
| Gamma + EM | 0.351 | 0.00779 | 0.392 | 0.127 | 0.191 |
| All | 0.458 | 0.00664 | 0.693 | 0.165 | 0.267 |

Table 4 compares six generic baselines. The independent per-modality inversion
has the best proxy F1 (0.333), followed by GLS/Bayesian (0.326), fixed weight
(0.179), simple average (0.066) and PCA (0.026). The legacy estimator has the
highest clay abundance and the smoothest map but its F1 is 0.267. Under ±30 %
H perturbation recall is 0.659 ± 0.228: the mean is stable but the spread grows
quickly.

| Method | Clay | Gradient | Recall | F1 |
|---|---:|---:|---:|---:|
| Independent | 0.235 | 0.01604 | 0.701 | 0.333 |
| Simple average | 0.028 | 0.01625 | 0.036 | 0.066 |
| Fixed weight | 0.353 | 0.00923 | 0.383 | 0.179 |
| PCA (3 comp.) | 0.020 | 0.00805 | 0.013 | 0.026 |
| GLS / Bayesian | 0.315 | 0.01821 | 0.673 | 0.326 |
| WLS + Kalman (legacy) | 0.458 | 0.00664 | 0.693 | 0.267 |

Table 5 adds coherence metrics. On the legacy matrix the estimator's advantage
is interpretability, not accuracy: 223 connected components versus 5,375 for
the independent inversion, mean patch 3,407 versus 108 px, and 240 isolated
false-positive components versus 5,038. A 128 × 128-px (6.4 km) block bootstrap
with 200 replicates confirms the accuracy deficit is significant: ΔF1 = −0.064
[−0.116, −0.022], with the legacy estimator never winning in 200 resamples.

| Method | AP | matched precision | components | mean patch (px) |
|---|---:|---:|---:|---:|
| Independent | 0.173 | 0.124 | 5,375 | 108 |
| Simple average | 0.266 | 0.143 | 8,179 | 2 |
| Fixed weight | 0.122 | 0.037 | 465 | 1,283 |
| PCA (3 comp.) | 0.266 | 0.143 | 1,721 | 2 |
| GLS / Bayesian | 0.245 | 0.292 | 2,291 | 247 |
| WLS + Kalman (legacy) | 0.126 | 0.040 | 223 | 3,407 |

### 7.2 Diagnosis: the EM row is mis-specified

The fusion gain index of Section 5.3 predicts the legacy ablation before it is
run: under the raw-resistivity matrix TIR has a positive gain, EM a negative
one, and the full set is worse than gamma+TIR. The mechanism is visible in the
matrix. The legacy EM row assigns 20, 15 and 25 Ω·m to clay and much higher
resistivities to the other four minerals; after column normalisation clay
receives a small EM weight while the other minerals dominate, so the EM field is
attributed to quartz, feldspar, calcite and dolomite instead of clay. Table 6
quantifies the lever: halving the EM clay weight raises F1 to 0.299, doubling it
drops F1 to 0.207, and expressing EM as log10 resistivity with a clay-only row
raises F1 to 0.498. The legacy failure is a model-specification error, not
evidence against fusion.

| Variant | Clay | Recall | F1 |
|---|---:|---:|---:|
| baseline (legacy) | 0.458 | 0.693 | 0.267 |
| gamma ×0.8 / ×1.2 | 0.461 / 0.456 | 0.692 / 0.692 | 0.261 / 0.271 |
| TIR ×0.8 / ×1.2 | 0.435 / 0.481 | 0.642 / 0.739 | 0.258 / 0.274 |
| EM ×0.8 / ×1.2 | 0.479 / 0.439 | 0.743 / 0.648 | 0.280 / 0.255 |
| clay K ×0.8 / ×1.2 | 0.460 / 0.457 | 0.659 / 0.721 | 0.252 / 0.280 |
| clay eTh ×0.8 / ×1.2 | 0.459 / 0.458 | 0.707 / 0.679 | 0.271 / 0.263 |
| EM clay ×0.5 / ×2.0 | 0.517 / 0.358 | 0.819 / 0.479 | 0.299 / 0.207 |
| EM log10, clay-only | 0.174 | 0.858 | 0.498 |

### 7.3 Correcting the EM response: the main result

Two physically motivated changes are made and nothing else: the EM channels are
expressed as log10 ρ, and the three EM rows of `H` become clay-only with
β = [0.90, 0.86, 0.36] (Section 4.8). Data, mask, metric and the gamma/TIR rows
are unchanged. Figure 6 compares the two models and Table 7 gives the metrics.

| method | F1 | AP | recall | precision | components |
|---|---:|---:|---:|---:|---:|
| Independent | 0.333 | 0.173 | 0.701 | 0.218 | 5,375 |
| GLS / Bayesian | 0.326 | 0.245 | 0.673 | 0.215 | 2,291 |
| Legacy WLS + Kalman | 0.267 | 0.126 | 0.693 | 0.165 | 223 |
| EM-fix WLS | 0.496 | 0.499 | 0.852 | 0.350 | 1,009 |
| **EM-fix Kalman** | **0.498** | **0.513** | **0.858** | **0.351** | **765** |

The corrected model raises F1 from 0.267 to 0.498 and AP from 0.126 to 0.513,
above every generic baseline, while fragmenting far less than the independent
inversion (765 versus 5,375 components). A 128 × 128-px block bootstrap gives
ΔF1 = +0.167 [0.118, 0.216] against the independent inversion, winning 200 of
200 replicates. Ten runs with 1 % channel noise give F1 0.49816 ± 0.00005,
recall 0.85749 ± 0.00012, precision 0.35105 ± 0.00003 and clay
0.17393 ± 0.000001: the estimator is numerically stable.

Because the fields are spatially autocorrelated the effective sample size is
only about 110-175 independent samples (Section 7.7), so all uncertainty in this
paper is reported at the 128-px block scale rather than at the pixel scale.

### 7.4 Ablation under the corrected model

Table 8 gives the corrected ablation. Against the gamma-derived proxy gamma
alone reaches F1 0.519, above the full set at 0.498, with gamma+TIR at 0.451 and
gamma+EM at 0.417. Against the synthetic TIR truth the ordering reverses and
the full set is clearly best: RMSE 0.216 and r 0.290, versus RMSE 0.388 and
r = −0.136 for gamma alone. The disagreement is expected because the proxy is a
gamma index: on a gamma-derived target a gamma-only estimator is favoured by
construction, while on an independent mineral target the fused estimate wins.
This is the central caveat of the benchmark, quantified rather than argued.

| Configuration | Clay | Recall | Precision | F1 | RMSE (TIR truth) | r (TIR truth) |
|---|---:|---:|---:|---:|---:|---:|
| Gamma | 0.305 | 0.957 | 0.356 | 0.519 | 0.388 | −0.136 |
| Gamma + TIR | 0.079 | 0.332 | 0.704 | 0.451 | 0.242 | 0.271 |
| Gamma + EM | 0.383 | 0.963 | 0.266 | 0.417 | 0.393 | 0.034 |
| All (corrected) | 0.174 | 0.858 | 0.351 | 0.498 | 0.216 | 0.290 |

### 7.5 Robustness: degradation, temperature, domain shift and depth

Figure 5 shows the scenario recalls and the temperature sweep. Table 10 lists
them with 128-px block-bootstrap confidence intervals and
Benjamini-Hochberg-corrected paired tests against the normal scenario.

| Scenario | Recall | Precision | F1 | Recall 95 % CI |
|---|---:|---:|---:|---|
| Normal | 0.858 | 0.351 | 0.498 | [0.789, 0.912] |
| EMI degraded ×5 | 0.494 | 0.639 | 0.557 | [0.421, 0.567] |
| EMI failed ×20 | 0.338 | 0.702 | 0.456 | [0.265, 0.432] |
| TIR degraded ×5 | 0.949 | 0.299 | 0.454 | [0.862, 0.986] |
| Gamma degraded ×5 | 0.860 | 0.255 | 0.393 | [0.779, 0.915] |
| EMI + TIR failed | 0.952 | 0.421 | 0.584 | [0.900, 0.979] |
| T = −60 °C | 0.957 | — | 0.417 | [0.892, 0.992] |
| T = +80 °C | 0.918 | — | 0.430 | [0.850, 0.962] |
| Direct transfer | 0.858 | — | 0.499 | [0.788, 0.914] |
| CORAL | 0.799 | — | 0.472 | [0.727, 0.880] |

Four results are statistically significant and physically consistent. First,
EM is the load-bearing modality: EMI failure costs −0.187 recall
[−0.246, −0.142] and EMI degradation −0.129 [−0.168, −0.087]. Second, TIR is
redundant for the proxy: TIR degradation raises recall by +0.028
[+0.013, +0.045]. Third, losing both EM and TIR is indistinguishable from normal
(−0.003, BH p = 0.90) because gamma alone then carries the proxy, the same
circularity as Section 7.4. Fourth, CORAL significantly hurts
(−0.015 [−0.022, −0.009]); the synthetic shift is a per-channel scaling that
z-scoring already removes, so the experiment does not test CORAL on a real
covariance change.

Temperature is the largest change relative to the legacy model: mean recall
rises from 0.476 to 0.912 and F1 from 0.253 to 0.480. Recall increases away from
25 °C (+0.030 at −60 °C) while F1 falls (0.490 → 0.417), so more positives are
flagged but less precisely; recall must not be reported alone.

The depth Kalman also changes qualitatively. The legacy profile rises from clay
0.276 at 0.1 m to 0.444 at 500 m, which is physically unlikely. With the
corrected EM response, clay decreases from 0.276 to 0.179 while dolomite
increases from 0.121 to 0.278 (Table 9). The depth section remains a synthetic
extrapolation from surface gamma/TIR and AEM layer statistics, not a
borehole-validated 3-D model.

| Depth | Quartz | Feldspar | Clay | Calcite | Dolomite |
|---:|---:|---:|---:|---:|---:|
| 0.1 m | 0.129 | 0.211 | 0.276 | 0.181 | 0.121 |
| 1.9 m | 0.123 | 0.145 | 0.247 | 0.197 | 0.224 |
| 5.6 m | 0.115 | 0.137 | 0.224 | 0.188 | 0.272 |
| 28 m | 0.112 | 0.131 | 0.202 | 0.176 | 0.315 |
| 120 m | 0.118 | 0.135 | 0.192 | 0.179 | 0.312 |
| 500 m | 0.137 | 0.148 | 0.179 | 0.193 | 0.278 |

### 7.6 Uncertainty calibration

The forward-filter variance is not a calibrated interval (Table 11). Under the
legacy model the empirical 68 % and 95 % coverage are 10.3 % and 20.2 % with a
variance-scale factor of 17.97, which raises them only to 49.1 % and 100 %.
Under the corrected model the coverage is 9.5 % and 21.0 % with a scale factor
of 15.15, giving 49.9 % and 100 % after rescaling. The bias grows to −0.315 in
the corrected model because the clay estimate is systematically lower than the
proxy. `P` is a filter variance, not a posterior predictive interval, and the
uncertainty maps must not be quoted as confidence intervals.

| Model | Coverage 68 % | Coverage 95 % | Scale factor | Scaled 68 % | Scaled 95 % |
|---|---:|---:|---:|---:|---:|
| Legacy | 10.3 % | 20.2 % | 17.97 | 49.1 % | 100 % |
| Corrected EM | 9.5 % | 21.0 % | 15.15 | 49.9 % | 100 % |

### 7.7 Spatial autocorrelation and effective sample size

The 1,265,683 valid pixels are not independent samples. The measured integral
scale is 53 px (2.7 km) for the proxy and 42 px (2.1 km) for the corrected clay
estimate, giving design effects of 11,482 and 7,250 and effective sample sizes
of about 110 and 175. Pixel-level standard errors are therefore understated by
two orders of magnitude, and the original 32-px bootstrap blocks were shorter
than the correlation length. All bootstraps here use 128-px (6.4 km) blocks, and
`pipeline_validation.json` enforces the rule that the block length is at least
twice the integral scale. The per-64-px-block average precision of the estimator
on held-out blocks is 0.438 ± 0.296 across 19 blocks, which is the honest
uncertainty scale for a pixel-level metric in this dataset.

### 7.8 Resolution and random seed

Striding the grid from 50 to 800 m raises legacy proxy recall from 0.693 to
0.759 and changes clay from 0.458 to 0.449, while runtime falls from 7.68 to
0.04 s. Coarser grids smooth the proxy agreement upward; this is an aggregation
effect, not better physics. Twenty noise realisations and ten repeated 1 % noise
runs reproduce the corrected F1 to five decimals, so the estimator is
numerically stable; that stability is not sampling uncertainty (Section 7.7).

### 7.9 Independent geological check

As a check that does not use the gamma channels, the USGS SIM 3206 surficial
geologic map (DOI 10.3133/sim3206) was rasterised to the 50 m grid. Clay is
highest in alluvium (0.487), felsic plutonic (0.426) and volcanic (0.417)
substrates and lowest in sedimentary (0.020) and carbonate (0.011) substrates;
Kruskal-Wallis p < 0.001 and felsic > carbonate p < 0.001. The ranking is
directionally consistent with the geology. The map describes surficial
substrate, not alteration assemblages, so this is a qualitative consistency
check, not an accuracy validation.

### 7.10 Published-method baselines

Table 12 places the corrected model against five published exploration methods.
This comparison changes the paper's conclusion, so it is stated plainly: on the
proxy target the F-parameter K·eU/eTh (Gnojek & Prichystal 1985) reaches AP
0.650 and matched-prevalence F1 0.617, and low eTh/K (Dickson & Scott 1997)
reaches 0.572 and 0.569 — both gamma-only indices beat the corrected fusion
(0.513 and 0.386). Spectral angle mapping on TIR (0.091) and an EM conductor
index (0.090) fail because the synthetic TIR and EM channels do not encode the
proxy field.

The explanation is structural rather than a defect of the estimator: the proxy
is a monotone function of K and eTh, and any index that increases with K and
decreases with eTh tracks it by construction, so no multimodal method can beat a
gamma ratio on a gamma-index target. Together with Section 7.4 (gamma-only best
on the proxy) and Section 7.5 (EMI + TIR failure indistinguishable from normal)
this gives three independent lines of evidence for the same caveat. The
corollary is equally important: on the independent synthetic TIR truth the
ordering reverses and the fused estimate is best.

| Method | Reference | AP | matched F1 |
|---|---|---:|---:|
| Ternary K-dominance | IAEA 2003 | 0.344 | 0.393 |
| F-parameter K·eU/eTh | Gnojek & Prichystal 1985 | **0.650** | **0.617** |
| Low eTh/K | Dickson & Scott 1997 | 0.572 | 0.569 |
| Spectral angle mapper (TIR) | Kruse et al. 1993 | 0.091 | 0.000 |
| EM conductor index | Fountain 1998 | 0.090 | 0.014 |
| EM-fix Kalman (this work) | — | 0.513 | 0.386 |

### 7.11 Independent testbed and endmember sensitivity

Two further controls bound the result. A second testbed (V2) removes the two
data inconsistencies: clay is set to `clay_prior`, TIR and EM are generated from
that single field, and EM uses log10 resistivity with a clay-only response.
Gamma alone still gives the best proxy F1 (0.489), while gamma+TIR (0.219),
gamma+EM (0.299) and the full set (0.179) are lower, confirming that the
bottleneck is the target definition and not only the synthetic recipes. The ASU
measured endmembers strengthen the TIR contrast and lower proxy F1 from 0.267 to
0.132 under the legacy matrix, the expected consequence of a TIR field driven by
a different clay truth; it is reported as a sensitivity analysis, not as a
replacement for the USGS library.

### 7.12 Edge deployment modules

Three modules proposed in early drafts were implemented in software and tested.
Granite interference compensation uses the real TMI grid, real NGU airborne
FDEM resistivity statistics (103,484 measured values, median 1,856 Ω·m) and the
SIM 3206 felsic-plutonic map. The local granite is not radiometrically distinct
(K 3.16 versus 3.04 %) and shows no clay excess (−0.010) under the corrected
model; applying the compensation raises felsic clay from 0.165 to 0.336 and
lowers F1 from 0.498 to 0.475, so it is unnecessary and harmful at this site. A
1-D CNN residual learner (pure NumPy, 2,717 parameters, 2.7 KB in INT8) reduces
proxy RMSE from 0.350 to 0.102 but lowers average precision from 0.533 to 0.377:
it demonstrates the deployment path, not an accuracy gain. Latency is 21-30 ms
per 10,000-sample tile on CPU, meeting the 200 ms budget with a nine-fold
margin; no edge hardware was available, so no Jetson claim is made.

"""
text = text[:start] + NEW + text[end:]
P.write_text(text, encoding="utf-8")
print("rewritten; chars:", len(text))
