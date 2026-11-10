# Published-method baselines

`run_published_baselines.py` replaces the "generic baselines only" gap (GAP
item 11) with five methods actually published and used in airborne mineral
exploration. All are evaluated with the same protocol (AP and
matched-prevalence F1 against `clay_prior > 0.55` on valid pixels).

| method | reference | AP | matched F1 |
|---|---|---:|---:|
| Ternary K-dominance | IAEA 2003 (TECDOC-1363 practice) | 0.344 | 0.393 |
| **F-parameter K·eU/eTh** | **Gnojek & Prichystal 1985, Geoexploration 23, 491-502, DOI 10.1016/0016-7142(85)90076-6** | **0.650** | **0.617** |
| **Low eTh/K** | **Dickson & Scott 1997, AGSO J. 17(2)** | **0.572** | **0.569** |
| Spectral Angle Mapper (TIR) | Kruse et al. 1993, Remote Sens. Environ. 44 | 0.091 | 0.000 |
| EM conductor index | Fountain 1998 / Siemon 2009 context | 0.090 | 0.014 |
| [ref] Independent inversion | — | 0.173 | 0.049 |
| [ref] GLS / Bayesian | — | 0.245 | 0.292 |
| [ref] EM-fix Kalman fusion | this work | 0.513 | 0.386 |

## The main finding (must be reported honestly)

**Two published gamma-only ratio indices beat the entire fusion machinery on
the proxy target**: the F-parameter reaches AP 0.650 / matched F1 0.617 versus
0.513 / 0.386 for the corrected fusion. This is not a failure of the fusion
model — it is the circularity of a gamma-derived target made quantitative:
`clay_prior` is a monotone function of K and eTh, and any index that increases
with K and decreases with eTh (exactly what F = K·eU/eTh and low eTh/K do)
will track it. **No multimodal method can beat a gamma ratio on a gamma-index
target.** This is the strongest single piece of evidence for the paper's
central caveat, and it complements the ablation (gamma-only F1 0.519) and the
EMI+TIR-failure result (BH p = 0.91).

## Secondary findings

- **SAM on TIR fails (AP 0.091)**: spectral angle measures mineral identity in
  the synthetic TIR bands, which are generated from a *different* clay field
  than the proxy. Single-modality published methods on TIR/EM cannot track the
  proxy because the synthetic channels do not encode it.
- **EM conductor index fails (AP 0.090)**: the synthetic EM recipe makes clay
  *increase* resistivity (documented inconsistency), so the standard
  "low-resistivity conductor" practice inverts on this dataset.
- **Ternary K-dominance (AP 0.344)** is comparable to the independent
  inversion: a visualisation-derived index, not a quantitatively tuned one.

## How to use these baselines in the paper

1. Present the table above alongside the generic baselines.
2. State explicitly that on a gamma-derived proxy, published gamma ratios are
   unbeatable by construction; the benchmark's role is to expose this rather
   than to claim fusion superiority.
3. Against the synthetic TIR truth the ordering reverses: the corrected fusion
   gives RMSE 0.216 / r 0.290 versus gamma-only r = −0.136, so the choice of
   evaluation target decides the ranking — the paper's core message.

## Caveats

- The five methods are quantitative adaptations of published practice (ratios,
  ternary dominance, spectral angle, conductor index); they are not reproductions
  of any specific software.
- SAM uses the same USGS endmembers as the forward model — a mild inverse-crime
  component, but it fails on the proxy anyway.
- Matched F1 uses the prevalence quantile (9.5 % positive rate).

## Files

`processed/published_baselines.json/csv/png`; script
`code/run_published_baselines.py` (runs in the `variants` stage).

