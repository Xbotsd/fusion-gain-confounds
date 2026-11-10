# Threshold and top-k sensitivity

The benchmark fixes `clay > 0.25`, top-2 and `clay_prior > 0.55`. This sweep
varies the clay threshold (0.15–0.45), top-k (1–3) and proxy threshold
(0.45–0.65) for four methods.

## At the default proxy threshold and top-k (`gt > 0.55`, top-2)

| method | best F1 | best clay threshold | F1 at 0.25 |
|---|---:|---:|---:|
| Independent | 0.363 | 0.30 | 0.333 |
| GLS / Bayesian | 0.332 | 0.15 | 0.326 |
| Legacy WLS + Kalman | 0.296 | 0.15 | 0.267 |
| **EM-fix Kalman** | **0.533** | 0.35 | **0.498** |

The corrected EM model remains the best at the default proxy prevalence, and its
F1 changes by less than 0.04 across the clay threshold range. The legacy model
never overtakes Independent in this setting.

## At the most permissive setting (`gt > 0.45`, top-3, threshold 0.15)

F1 rises for every method because the positive class is much larger and top-3
allows three minerals: Independent 0.658, GLS 0.745, legacy 0.832, EM-fix 0.725.
This is a prevalence/threshold effect, not evidence that the legacy model is
better; it is reported to show that absolute F1 is not comparable across
different target definitions.

## Conclusion

- The ranking at the paper's stated target (`gt > 0.55`, top-2) is stable:
  EM-fix > Independent > GLS > legacy.
- Absolute F1 is highly sensitive to the proxy threshold and top-k; the paper
  must state these values and report the sweep.
- The legacy model's apparent advantage at low thresholds is an artefact of
  predicting many positives, not a better clay estimate.

## Files

`processed/threshold_sensitivity.json/csv/png`,
`processed/threshold_summary.json`; script `code/threshold_sensitivity.py`.
