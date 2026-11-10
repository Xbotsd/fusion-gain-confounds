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

* The ablation rows `gamma` (0.325 legacy / 0.519 corrected) are **not
  comparable across matrices**; the +0.19 difference in that row is a
  normalisation artefact, not an EM effect.
* Any statement of the form "correcting EM changes the gamma-only result" is
  invalid. Statements about the **full** model are still meaningful, because
  there every channel is active, but part of the 0.267 → 0.498 gain may be
  renormalisation rather than physics.
* The real-ASTER-TIR comparison inherits the same artefact and must be rerun
  after the fix.

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

* Fix designed, not yet applied (it invalidates every number in `docs/`).
* Experiments 2–4 of the rigor plan (bootstrap CI, TES sensitivity, second date)
  should run **after** the fix, otherwise they inherit the artefact.
* Experiment 1's geology-target results are recorded in
  `processed/independent_target.json` but are marked provisional for the same
  reason.
