# Methods (as implemented)

## 1. Observation vector

Each 50 m pixel has ten channels:

| index | channel | unit | source |
|---:|---|---|---|
| 0 | K | % | real gamma |
| 1 | eU | ppm | real gamma |
| 2 | eTh | ppm | real gamma |
| 3–6 | TIR emissivity at 8.6, 9.6, 11.3, 12.5 µm | – | synthetic |
| 7–9 | EM apparent resistivity, layers 0, 15, 35 (≈0, 12, 227 m) | Ω·m | synthetic |

`z = [z_0 … z_9]^T`.

## 2. Response matrix

`H` is 10 × 5; columns are Quartz, Feldspar, Clay, Calcite, Dolomite.

| row | Qz | Fsp | Clay | Cal | Dol |
|---|---:|---:|---:|---:|---:|
| K | 0.5 | 1.5 | **4.0** | 0.3 | 0.3 |
| eU | 2.0 | 1.0 | 1.5 | 2.0 | 1.0 |
| eTh | 1.0 | 1.5 | **1.0** | 1.0 | 0.5 |
| TIR 8.6 | 0.92 | 0.85 | 0.88 | 0.80 | 0.82 |
| TIR 9.6 | 0.95 | 0.92 | 0.90 | 0.90 | 0.88 |
| TIR 11.3 | 0.85 | 0.90 | 0.92 | 0.95 | 0.93 |
| TIR 12.5 | 0.90 | 0.88 | 0.90 | 0.92 | 0.94 |
| EM 0 m | 100 | 200 | **20** | 500 | 400 |
| EM 12 m | 80 | 150 | **15** | 600 | 500 |
| EM 227 m | 120 | 180 | **25** | 800 | 700 |

Clay is deliberately K-rich, Th-poor and conductive — the hydrothermal illite
signature.  `H` is a relative signature matrix, not a set of measured
concentrations.

## 3. Standardisation and weighted least squares

Each channel is z-scored over the valid survey pixels and clipped at ±3.  Each
mineral column of `H` is normalised to unit L2 norm.  The estimate solves

```
x^ = argmin  (z - H x)^T W (z - H x) + lambda ||x||^2
     x >= 0,  sum(x) = 1

x^ = (H^T W H + lambda I)^-1 H^T W z
```

with `lambda = 0.1`, `W = diag(w)`.  The solution is projected onto the
non-negative unit simplex after every update.

**Caveat.**  Z-scoring `z` and column-normalising `H` are not the same change of
variables; the pair is a *relative-signature* matching scheme, not an absolute
concentration inversion.  This is the model that produced the reported maps and
is retained for reproducibility.  `docs/MODEL_AUDIT.md` records the consequence.

## 4. Spatial Kalman filter

The WLS estimate at column `j` is treated as the observation of a random-walk
state along the survey direction:

```
x^- = x ,        P^- = P + Q
K   = P^- / (P^- + R_obs)
x   = x^- + K (z_wls - x^-)
P   = (1 - K) P^- + 0.05 * mean(innovation^2)
```

`Q = 0.005`, `R_obs = 0.02`.  The filter is causal (forward only); `P` is a
forward-filter variance, not a calibrated confidence interval.

## 5. Depth Kalman

The 40 EM layers are treated as a sequence along depth (`k = 0 … 39`,
0–600 m):

```
F = 0.85 I + 0.15/5
Q = 0.03
H_k : rows 0–6 as above; EM row scaled by 1 + 0.2 * depth_factor * [1, .5, -.8, 1.2, 1]
R_k : gamma/TIR rows 1 + 5 * depth_factor; EM row 1
```

Surface gamma and TIR are repeated at every layer as anchors.  Consequently the
deep abundance variation is driven mainly by EM and by the `F/Q` prior; this is
a structural limitation of the current depth model.

## 6. Quality weights (the adaptive part)

The production run uses uniform weights.  Scenario experiments replace them by
explicit quality multipliers `q_i` (`W = diag(q)`; higher `q` = more weight):

* fault/degradation: `q_i = 1/factor` for the degraded modality, plus noise
  injection;
* temperature: `gq = 1/(1 + 0.1 sqrt(DCR))`, `DCR = 2^((T-25)/8)`;
  `tq = tir_factor(T)/(1 + 0.02|T-25|)`; `eq` from a linear EM drift;
* measured environment: per-pixel
  `q_gamma = exp(-0.006 max(RH-20,0))`,
  `q_TIR = exp(-0.015 max(RH-20,0))`,
  `q_EM = exp(-0.004 |T-20|)`.

These are empirical, monotone quality factors, not instrument transfer models.

## 7. Metrics

* predicted positive: `clay > 0.25` **and** clay in the top-2 minerals;
* target: `clay_prior > 0.55`;
* valid pixels only (66.4 % of the grid);
* recall, precision, F1, IoU from the same contingency table;
* “overall” = mean of six scenario means; never called a detection rate.

## 8. What the experiments can and cannot show

They can show that the estimator is stable under channel loss, noise,
temperature-dependent quality changes, domain shift and H perturbation.  They
cannot show geological accuracy, because both the target (`clay_prior`) and the
synthetic modalities are derived from the same real gamma channels.
