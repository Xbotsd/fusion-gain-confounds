# Supplementary tables

## Table S1. Sensitivity of the thermal result to the retrieval and the acquisition

Main-text §7.6 refers to this table. Values are proxy F1 on the clay-proxy target
over the analysis mask; the gamma-only row is invariant to the thermal variant by
construction. The bootstrap of the gamma+TIR gain is +0.119, 95 % CI
[+0.067, +0.167] (200 replicates, 128-px blocks), computed on the baseline row.

| variant | gamma F1 | gamma+TIR F1 |
|---|---:|---:|
| baseline 2006-10-18 (5 bands) | 0.531 | 0.652 |
| eps_max 0.95 | 0.531 | 0.652 |
| eps_max 1.00 | 0.531 | 0.652 |
| no 11.29 um band (4 bands) | 0.531 | 0.640 |
| second date 2006-09-25 | 0.531 | 0.651 |

Source: `processed/real_tir_robust.json`, produced by `code/run_real_tir_robust.py`.
The main-text result is unchanged by any of these variants: the conclusion does not
depend on the assumed maximum emissivity, on the band with the largest residual
temperature correlation, or on the acquisition date.
