# V2 controlled testbed

## What it is

The main dataset has two clay truths: TIR is generated from `0.3K + 0.3eTh`
(mean 0.30) and EM from `clay_prior` (mean 0.46), correlated at 0.57. The V2
variant removes that inconsistency:

* clay = `clay_prior` (the evaluation target);
* the other four minerals fill `1 - clay` with the gamma-derived pattern;
* TIR is generated from the USGS endmembers plus 0.005 emissivity noise;
* EM is generated from clay only, in `log10(Ω·m)`, with
  `beta(depth) = 0.90 exp(-depth/250)`, an independent field, noise and a
  quadratic model-mismatch term;
* the inversion uses `log10` EM and clay-only EM rows in `H`.

This is a controlled testbed, not a real dataset. It is an inverse crime by
construction: the same truth field generates the data and is used as the target.
It is reported because it isolates the effect of the two data inconsistencies.

## Results

| configuration | clay | recall | precision | F1 |
|---|---:|---:|---:|---:|
| gamma | 0.335 | 0.969 | 0.327 | 0.489 |
| gamma + TIR | 0.132 | 0.225 | 0.213 | 0.219 |
| gamma + EM | 0.279 | 0.568 | 0.203 | 0.299 |
| all | 0.162 | 0.268 | 0.135 | 0.179 |

Even with one truth field and a physically plausible log10 EM row, gamma alone
remains the best configuration on the proxy target. The reason is structural:
the target is a gamma-derived index, so gamma is close to the data-generating
process; TIR and EM add information about the other minerals, which perturbs the
clay estimate. Fusion can only help when the target contains information that
gamma does not already have (for example, an independent alteration or deposit
map), or when the inversion is reformulated so that adding a channel cannot
rotate the clay estimate away from the target.

## What this means for the paper

Do not replace the main results with V2. Use V2 as a second negative control:

1. the main dataset shows that the legacy TIR/EM truths are inconsistent;
2. V2 shows that even a consistent synthetic truth does not create a fusion gain
   when the target is gamma-derived;
3. therefore the paper's claim must be about *when* fusion helps, not that it
   always helps.

## Files

`processed/v2/` contains `truth_abundance_v2.npy`, `tir_cube_v2.npy`,
`em_cube_v2.npy`, `H_v2.npy`, `ablation_v2.csv/json` and `fig_v2.png`.
The script is `code/run_v2.py`.
