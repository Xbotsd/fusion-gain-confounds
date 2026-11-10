# Physically structured H perturbations

Legacy H sensitivity used iid ±30 % noise, which is not physical and can average
out. `structured_perturbation.py` instead changes one physically meaningful block
at a time: modality gain, clay K/eTh signature, EM clay response, and the
log10 clay-only EM model.

## Results (main data, valid pixels, legacy reference)

| variant | clay | recall | F1 | gradient |
|---|---:|---:|---:|---:|
| baseline | 0.458 | 0.693 | 0.267 | 0.00664 |
| gamma ×0.8 | 0.461 | 0.692 | 0.261 | 0.00644 |
| gamma ×1.2 | 0.456 | 0.692 | 0.271 | 0.00684 |
| TIR ×0.8 | 0.435 | 0.642 | 0.258 | 0.00695 |
| TIR ×1.2 | 0.481 | 0.739 | 0.274 | 0.00642 |
| EM ×0.8 | 0.479 | 0.743 | 0.280 | 0.00660 |
| EM ×1.2 | 0.439 | 0.648 | 0.255 | 0.00670 |
| clay K ×0.8 | 0.460 | 0.659 | 0.252 | 0.00646 |
| clay K ×1.2 | 0.457 | 0.721 | 0.280 | 0.00684 |
| clay eTh ×0.8 | 0.459 | 0.707 | 0.271 | 0.00668 |
| clay eTh ×1.2 | 0.458 | 0.679 | 0.263 | 0.00661 |
| EM clay ×0.5 | 0.517 | 0.819 | 0.299 | 0.00635 |
| EM clay ×2.0 | 0.358 | 0.479 | 0.207 | 0.00718 |
| **EM log10 clay-only** | **0.174** | **0.858** | **0.498** | **0.00785** |

## Interpretation

- Modality gain changes F1 by about ±0.01, so the legacy model is not fragile to
  a global calibration error.
- Clay K/eTh changes F1 by ±0.015; the gamma signature matters but is not the
  dominant lever.
- EM clay weight is the dominant lever: halving it gives 0.299, doubling it
  drops to 0.207; the log10 clay-only model gives **0.498**.
- The corrected model is not a small perturbation; it is a different, physically
  motivated parameterisation. That is why it should be reported as a model
  correction, not as a robustness check.

## Caveat

The EM data are synthetic; the structured perturbations test model sensitivity,
not real sensor calibration. The EM-fix result still needs to be propagated to
validation/degradation/temperature/depth.

## Files

`processed/structured_perturbation.json/csv/png`; script
`code/structured_perturbation.py`.
