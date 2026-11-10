# Manuscript vs implementation

> **Scope.** This table audits the *original* manuscript
> (`A Unified Kalman Framework with Environment.docx`), which is why several rows
> say "does not reproduce". The current paper (`Manuscript_v2_draft.md`) is
> audited claim-by-claim in `docs/READINESS_AUDIT.md`; use that document before
> submission.

The manuscript (`A Unified Kalman Framework with Environment.docx`) is treated
as a reference.  This table records what the repository actually implements, so
that no claim is inherited without evidence.

| manuscript claim | status in this repository | evidence / note |
|---|---|---|
| Unified Kalman kernel fusing gamma, EM and TIR | **partially implemented** | WLS + forward Kalman in `run_fusion.py`, `run_depth.py`. The state is 5 abundances; there is no drift or environment state. |
| Environment-aware adaptive `R_k = diag(σ²)` with `f(T, RH, vib, EMI, SNR)` | **partially implemented** | Quality weights `W=diag(q)` in `run_validation.py` (temperature, fault factors) and `run_environment.py` (real T/RH grids). Vibration and EMI intensity are not measured; no per-channel SNR calibration. |
| Depth-Kalman 3-D inversion, 40 layers, 500–600 m | **implemented** | `run_depth.py`; 40 layers, 0–600 m. Surface gamma/TIR are repeated at every layer, so deep variation is driven mainly by EM and the F/Q prior. |
| Physics-constrained AI residual learning, 1-D CNN, INT8, <300 KB | **implemented (NumPy) and measured** | `run_edge_ai.py`: 2,717 params, 2.7 KB INT8 (budget met 111×); proxy AP 0.533→0.377 (ranking degrades), RMSE 0.351→0.106. See `docs/EDGE_MODULES.md`. |
| Offline edge deployment, Jetson Orin, <200 ms | **CPU-measured; Jetson not claimed** | 21 ms per 10k-sample tile on CPU (budget met 9.5×); no device available, INT8 simulated. See `docs/EDGE_MODULES.md`. |
| Granite interference compensation | **implemented and tested; not needed here** | `prepare_granite.py` + `run_granite_compensation.py`: local granite is not radiometrically distinct (K 3.16 vs 3.04 %) and shows no clay excess (−0.010); applying the compensation raises felsic clay 0.165→0.336 and lowers F1 0.498→0.475. |
| Three-level degradation (full → built-in → synthetic) | **not implemented as described** | The code implements quality down-weighting and channel exclusion. There is no rule engine that synthesises data when a sensor is missing. |
| Tri-modal fusion raises clay from 0.198 to 0.403 (+104 %) | **does not reproduce with one H matrix** | The draft's ablation used a different `H` from the validation. With the validation matrix, `run_ablation.py` gives different numbers; see `docs/MODEL_AUDIT.md`. |
| Overall detection rate 65.26 % | **definition changed** | The old value mixed pixel coverage and recall; the cleaned pipeline reports recall/precision/F1 on valid pixels with one definition. |
| CORAL reduces domain gap 5.22 % → 0.27 % | **recomputed** | `run_validation.py` recomputes direct transfer and CORAL with the same metric; the “gap” is the mean absolute difference of mean abundances, not a statistical distance. |
| Stable from −60 °C to +80 °C | **simulated only** | Temperature enters as noise injection plus quality weights; no climatic chamber or field test. |
| Data: USGS Colorado Mineral Belt, 2023, 28,472 line-km | **incorrect** | Actual grids/CSV are Ivanpah (NV–CA), 2019-12 → 2020-03; see `docs/DATA_PROVENANCE.md`. |
| Real gamma + physically consistent synthetic TIR/EM | **true, with a caveat** | TIR and EM were generated from *different* clay fields (correlation 0.56); see `docs/MODEL_AUDIT.md`. |
| 13 systematic experiments | **different count** | The cleaned pipeline has 8 script families: fusion, depth, ablation, validation (6 scenarios), baselines, environment, sensitivity, audit. |
| References [1]–[18] | **missing** | The docx has citation markers but no reference list. |
| Figures and tables | **missing from the docx** | Figures exist as PNG/EPS; tables are plain text lines. |

## What must change in the manuscript

1. Correct the survey name, coordinates, dates and line-km in Section 5.1.
2. Replace “detection rate” with “recall against the clay_prior alteration
   proxy” and report precision/F1 alongside it.
3. Either remove the AI-residual and edge-runtime sections or label them as
   unimplemented future work.
4. Recompute the ablation table with the single `H` used by the validation and
   update the +104 % claim.
5. State explicitly that TIR and EM are synthetic and that the target is
   gamma-derived, so the experiments validate estimator mechanics, not geology.
6. Add the reference list, embed the figures, and convert Tables I–IV to real
   tables.

