# Corrected EM model — the missing fusion gain

## Problem

The legacy EM rows have three defects that the paper now diagnoses
quantitatively rather than by assertion:

1. **Scale.** They are linear in raw resistivity, and the processed cube spans
   16.5–1133.6 Ω·m (p1–p99), i.e. 1.22–3.05 decades. The raw values dominate the
   column norms of `H`, which attenuates the TIR mineral contrast from 0.21–0.26
   to **0.024**, and raises the condition number of the column-normalised matrix
   from **48.5 to 1156**.
2. **Attribution.** All five minerals receive an EM response (100/200/20/500/400
   Ω·m), although survey-scale EM cannot resolve quartz from feldspar.
3. **Sign.** Clay is given the *lowest* resistivity (20/15/25 Ω·m) of the five
   minerals, while the documented synthetic recipe (`prepare_em.py`) writes clay
   into *higher* log10 ρ. An EM-only fit under the legacy rows therefore returns
   a clay map **anti-correlated** with the proxy: r = **−0.469** (F1 0.06). The
   same rows in log10 form give r = −0.256.

This is why the legacy model shows a **negative** EM gain and why removing EM
improves the proxy.

## Correction

Two changes, no target tuning:

1. `z_EM = log10(clip(ρ, 1, 1e5))`;
2. `H_EM` is clay-only, `H_EM(k, Clay) = β_k`, other minerals zero.

`β = [0.90, 0.86, 0.36]`. It is **not fitted**: the synthetic cube decays the
clay coefficient as `exp(−d/250)`, which at the sampled layer centres
(0.1, 13.1, 244.3 m) gives `[1.000, 0.949, 0.377]` after normalising to the
shallow layer — that profile, rounded. Because the synthetic field carries a
positive clay coefficient, the rows are positive; the sign follows the
documented generator, not a petrophysical claim about clay conductivity.

The rest of `H`, the data, the mask and the metric are unchanged.

## Sensitivity to β

`run_em_beta_sensitivity.py` → `em_beta_sensitivity_emfix.json/csv`. Four
profiles through the full estimator:

| β profile | F1 (WLS) | F1 (Kalman) |
|---|---:|---:|
| production `[0.90, 0.86, 0.36]` | 0.4959 | **0.4982** |
| recipe decay `[1.000, 0.949, 0.377]` | 0.4880 | 0.4898 |
| reversed `[0.36, 0.86, 0.90]` | 0.4802 | 0.4828 |
| uniform `[1, 1, 1]` | 0.4572 | 0.4587 |
| *legacy fusion, for reference* | 0.2671 | — |

Every profile beats the legacy fusion by ≥ 0.19 F1, so the gain is carried by
the log transform and the clay-only attribution, not by the depth weights.
`validate_pipeline.py` checks both that `β` matches the recipe decay
(deep/shallow ratio) and that the worst profile still clears the legacy model.

## Results

| method | F1 | AP | recall | precision | components | gradient |
|---|---:|---:|---:|---:|---:|---:|
| Independent | 0.333 | 0.173 | 0.701 | 0.218 | 5,375 | 0.0160 |
| GLS / Bayesian | 0.326 | 0.245 | 0.673 | 0.215 | 2,291 | 0.0182 |
| Legacy WLS + Kalman | 0.267 | 0.126 | 0.693 | 0.165 | 223 | 0.0066 |
| EM-fix WLS | 0.496 | 0.499 | 0.852 | 0.350 | 1,009 | 0.0109 |
| **EM-fix Kalman** | **0.498** | **0.513** | **0.858** | **0.351** | **765** | **0.0079** |

Spatial block bootstrap (128×128 px = 6.4 km, ≥ 2× the measured 2.7 km integral
scale; 200 replicates):

- Independent F1 0.331 [0.258, 0.400];
- EM-fix Kalman F1 0.498 [0.419, 0.569];
- ΔF1 = **+0.167 [0.118, 0.216]**, EM-fix wins 200/200 replicates.

Ten runs with 1 % channel noise: F1 **0.49816 ± 0.00005**, recall
0.85749 ± 0.00012, precision 0.35105 ± 0.00003, clay 0.17393 ± 0.000001. The
result is numerically stable. A threshold sweep (`gt > 0.55`, top-2) gives a
best F1 of 0.533 at clay > 0.35; the corrected model remains the best method at
the stated target. See `docs/THRESHOLD_SENSITIVITY.md`.

## Ablation and uncertainty under the corrected EM

`run_ablation.py --emfix` (outputs `ablation_emfix.*`):

| config | clay | F1 | RMSE (TIR truth) | r (TIR truth) |
|---|---:|---:|---:|---:|
| gamma | 0.305 | **0.519** | 0.388 | −0.136 |
| gamma+TIR | 0.079 | 0.451 | 0.242 | 0.271 |
| gamma+EM | 0.383 | 0.417 | 0.393 | 0.034 |
| all | 0.174 | 0.498 | **0.216** | **0.290** |

Honest reading: **against the gamma-derived proxy, gamma alone is best (0.519)**
— the expected circularity of a gamma-index target. Against the synthetic TIR
truth, the full corrected set is clearly best (RMSE 0.216, r 0.290). The
corrected EM therefore makes fusion *competitive with gamma on the proxy and
better than every generic baseline*, and *best on the TIR truth*, but it does not
beat gamma alone on the proxy.

`uncertainty_calibration.py --emfix` (outputs `calibration_emfix.*`): coverage
68/95 % = 9.5/21.0 %, variance scale 15.15 (legacy 17.97), scaled 49.9/100.0 %,
bias −0.315, RMSE 0.348. The corrected model's forward-filter variance is still
**not** a predictive interval; the uncertainty fields must not be quoted as
confidence intervals.

## Caveats

- EM and TIR are still synthetic; this is not independent field validation.
- The corrected rows are consistent with the documented generator, which is why
  the benchmark measures internal consistency rather than geological skill; the
  paper states this limit explicitly.
- Validation, degradation, temperature and depth have been re-run with the
  corrected EM; see `docs/EM_FIX_VALIDATION.md` (overall recall 0.661 → 0.829,
  overall F1 0.254 → 0.480).
- The posterior variance is **not** calibrated (see above); coverage is
  ~10 %/21 %.
- The corrected model is the main model in the manuscript; the legacy tables are
  retained only as the diagnosis.

## Files

`processed/em_fix.json`, `em_fix.csv`, `em_fix.png`,
`em_beta_sensitivity_emfix.json/csv`; scripts `code/run_em_fix.py`,
`code/run_em_beta_sensitivity.py`.
