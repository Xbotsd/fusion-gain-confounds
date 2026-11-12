# Column-normalisation audit (found 2026-11-07)

## What was being tested

Experiment 1 of the rigor plan: score every configuration against an
**independent** target — the USGS SIM 3206 substrate classes — instead of the
gamma-derived `clay_prior`, to see whether fusion helps when the target does not
already contain the modality's information.

## What it exposed

The "gamma-only" row of the ablation is **not** the same configuration under the
two response matrices. `common.normalize_H` divides each mineral column by its
norm over **all ten rows**, including the rows of modalities that are switched
off. Changing the EM rows therefore rescales the gamma and TIR columns, and the
estimator's solution changes even when EM is inactive.

Measured, with identical input data and identical active channels:

| matrix | gamma-only F1 (project normalisation) | gamma-only F1 (active-only normalisation) |
|---|---:|---:|
| legacy `H` | 0.3246 | **0.5511** |
| corrected `H` | 0.5190 | **0.5511** |

The same three channels, the same z-scored data, the same mask: 0.325 versus
0.519 depending only on the values in the inactive EM rows. Under a normalisation
that ignores inactive rows the two matrices agree exactly, as they must.

## Consequences for the current numbers

Both bugs are fixed (§*The fix*) and the whole benchmark was re-run. What the
fix changed, stated against the numbers in `main_results.json` at the time
(2026-11-08; the real-ASTER main line came later):

* The gamma-only row no longer depends on which EM matrix is used: it is 0.531
  under the legacy and the corrected model alike. Before the fix the same row
  read 0.325 under one matrix and 0.519 under the other, purely because the
  column normalisation summed over inactive rows.
* The corrected-EM result therefore survives as a **model** statement, not a
  normalisation artefact: F1 0.168 → 0.497, AP 0.123 → 0.577, with every channel
  active in both branches.
* The real-ASTER thermal result was re-run after the fix, and its control
  (identical H rows, zero-valued channels) is what showed the gain to be mostly
  conditioning. That control would have been impossible to interpret before the
  fix, because switching channels off itself changed the score.

## The fix

Normalise `H` on the rows that are active in the experiment:

```
Hn = normalize_H(H[active_rows])          # instead of normalize_H(H)[active_rows]
```

This makes the estimator invariant to channels that carry no weight, which is
what "switching a modality off" is supposed to mean. It changes every ablation
number and therefore every downstream table.

## Why this matters for the paper

A reviewer who re-runs the ablation will find that the gamma-only baseline moves
by 0.19 F1 depending on a matrix row that is multiplied by zero. That is a
fatal-looking inconsistency unless it is fixed and reported. It also affects the
interpretation of the central claim: how much of the corrected-EM gain survives
once the normalisation is made neutral is now an open, answerable question.

## Status

* **Applied** (Round 7, 2026-11-08). `common.normalize_H` divides each mineral
  column by its norm over the rows that are *active* in the experiment, and
  `test_core.py` asserts both switch-off invariances ("inactive rows do not change
  the estimate" and "switching channels off equals deleting them").
* Every artefact was regenerated after the fix. The numbers quoted above are the
  state measured on 2026-11-07 and are kept only as the audit trail; the current
  numbers are in `docs/RESULTS.md`.
* Experiments 2–4 of the rigor plan (bootstrap CI, TES sensitivity, second
  acquisition date) ran **after** the fix, so they do not inherit the artefact.
* The pre-fix geology-target run in `processed/independent_target.json` is
  superseded by the main-line `geology_multiclass.json` and `tir_information.json`.
