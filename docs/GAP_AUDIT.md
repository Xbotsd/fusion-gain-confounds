# Gap audit — what is done, what is missing, and where the rigor is thin

Snapshot: data chain **95/95 PASS + 19/19 cross-checks + 24/24 unit tests**,
manifest **6,701 files / 11.24 GB**. Five published-method baselines are in;
the Gnojek & Prichystal citation was corrected to 1985; every validated
artefact now has a producer in `run_all.py` (coverage check: 0 orphans).

## Rigor scorecard (against a JSTARS/C&G methods paper)

| dimension | score | why |
|---|---:|---|
| Data independence | 3/10 | target is a gamma-derived proxy; no external labels |
| Multi-modal realism | 3/10 | TIR/EM are synthetic; ASU/V2 are variants, not real data |
| Model identifiability | 4/10 | EM corrected; rest of H hand-set, column normalisation |
| Statistical inference | 6/10 | 128-px block bootstrap, BH-corrected scenario deltas, threshold sweep |
| Uncertainty | 2/10 | 68/95 % coverage 10.3/20.2 %; variance scale 17.97 |
| Reproducibility | 8/10 | hashes, manifest, fixed seeds, one-command stages |
| Manuscript completeness | 6/10 | references complete and DOI-checked; captions/statements/format open |
| Journal readiness | 6/10 | positive corrected result; TIR/EM still synthetic |

## P0 — must resolve before submission

1. **No independent alteration ground truth.** `clay_prior` is derived from the
   same K/eTh channels used by the inversion. A partial external check is now in
   place: the USGS SIM 3206 surficial map gives independent substrate groups;
   clay is highest in alluvium/felsic plutonic and lowest in carbonate
   (Kruskal p<0.001; felsic > carbonate p<0.001). This is a qualitative
   substrate check, not an alteration/deposit label.
2. **TIR and EM are synthetic.** There is no measured TIR image or EM section.
   ASU endmembers (F1 0.132) and V2 single-truth testbed (gamma-only F1 0.489 vs
   all 0.179) are negative controls, not real-data validation.
3. **H is not fully calibrated; EM is now corrected.** Raw Ω·m + five-mineral
   EM was replaced by log10(ρ) + clay-only, which raises F1 from 0.267 to 0.498.
   The rest of H remains hand-set; column normalisation is still a relative
   heuristic; structured H perturbations are now reported but no calibration.
4. **Legacy model has no accuracy advantage; corrected EM does.** Legacy block
   bootstrap: ΔF1 = −0.064 [−0.116, −0.022]. Corrected EM: F1 0.498,
   AP 0.513, ΔF1 = +0.167 [0.118, 0.216], 200/200 wins. Validation and depth
   have now been re-run with the corrected EM (overall recall 0.829 vs 0.661;
   depth clay decreases with depth), so the corrected model should become the
   main model. ablation and uncertainty calibration now also use the corrected H (_emfix outputs).
5. **Uncertainty is not usable.** 68/95 % coverage is 10.3/20.2 %; scaling by
   17.97 gives 49.1/100 %. Either recalibrate with a predictive model or remove
   uncertainty claims.
6. **Depth cube is not validated.** 40 layers come from Wisconsin AEM statistics,
   not this site; surface gamma/TIR are repeated at every layer; no borehole or
   independent 3-D check.

## P1 — rigor gaps that reviewers will notice

7. **Threshold/top-k sensitivity is now reported** (`docs/THRESHOLD_SENSITIVITY.md`):
   at `gt > 0.55`, top-2, EM-fix stays best (0.533 at clay > 0.35); absolute
   F1 varies strongly with the target definition.
8. **Generation-parameter sensitivity: done** (`generation_sensitivity.json`).
   Clay amplitude, independent-field amplitude, depth-decay length, overall
   scale and TIR noise are each swept; 16 settings give F1 0.468-0.518 against
   0.267 legacy. The overall EM scale is a no-op because channels are z-scored.
9. **Scenario-level CIs: done** (`docs/SCENARIO_CI.md`): 21 scenarios with
   128-px block-bootstrap CIs, 20 paired BH-corrected deltas vs normal, and a
   sync check tying them to `validation_emfix.json`. The document is generated
   from the artefact by `code/dev/build_scenario_ci.py`, so it cannot drift.
10. **Multiple comparisons: done.** Benjamini-Hochberg across the 20-comparison
    family is applied in `scenario_bootstrap.py`; significant results are
    labelled with BH p-values.
11. **Published-method baselines: done** (`docs/PUBLISHED_BASELINES.md`): five
    published exploration methods (IAEA ternary, F-parameter, eTh/K, SAM, EM
    conductor index). Key finding: the F-parameter (AP 0.650) and low eTh/K
    (0.572) beat the corrected fusion (0.513) on the proxy — the circularity
    caveat made quantitative; must be reported, not hidden.
12. **Single survey.** One Ivanpah survey; Wyoming/Nevada flight plans are
    unused; the real TMI is now used (granite indicator) but not in the fusion;
    no cross-site real validation.
13. **Geological plausibility is only qualitative.** SIM 3206 substrate groups
    are consistent with the clay ranking, but there is no alteration zone or
    known-deposit comparison.
14. **Corrected-EM model fully propagated.** Ablation, validation, degradation,
    temperature, depth and uncertainty calibration all have `_emfix` outputs;
    the legacy tables remain for comparison. The gamma-only ablation result
    (F1 0.519 > all 0.498 on the proxy) must be reported as the circularity
    caveat, not hidden.
21. **Edge modules implemented with negative results.** Granite compensation
    (no interference at this site; harmful if applied) and the 1-D CNN residual
    learner (AP 0.533→0.377) are implemented and documented in
    `docs/EDGE_MODULES.md`; they must not be claimed as accuracy improvements.
22. **Edge hardware still absent.** INT8 is simulated and latency is CPU-only;
    no Jetson/MCU, no power measurement.
23. **Pseudo-replication quantified.** N_eff ≈ 110–175 (not 1.27 M pixels);
    bootstrap blocks enlarged to 128 px (≥2τ); block-level AP uncertainty
    ±0.296. Pixel-level standard errors must not be reported anywhere.

## P2 — engineering and manuscript completeness

15. **References: done.** 24 contiguous entries, 11 DOI-verified (Gnojek
    corrected to 1985; Kruse 1993 added for the SAM citation), 8 MANUAL entries
    with full volume/issue/pages. Macnae 2016 and Bedini 2009 were removed as
    unverifiable. Every entry is cited in the body and no marker is orphaned
    (checked programmatically). See `docs/REFERENCES_AUDIT.md`.
16. **Manuscript mechanics: partially done.** Fixed: the table caption list
    matches the 12 body tables; table and figure citations run in order
    (1–12 / 1–6); bold markup renders correctly in docx cells. Still open:
    captions are not inline with the tables, figures are appended after the
    references instead of at first citation, no line numbers, no JSTARS
    template, no author-contributions / conflict-of-interest / funding
    statements, no graphical abstract, and the cover-letter reviewer
    suggestions are placeholders.
17. **Open science: mostly done.** MIT `LICENSE` (with data-source notices),
    `requirements-lock.txt` (pinned), `test_core.py` (unit tests, 24 checks,
    runs in the audit stage). Still missing: a public repository DOI/Zenodo
    and CI.
18. **Figure quality: done.** All pipeline figures are 300 dpi; the manuscript
    figures were regenerated. (No CI to keep them that way automatically.)
19. **ECOSTRESS script parked.** Moved to `code/dev/` with a README; not in
    the pipeline.
20. **Large intermediates: policy defined.** Seven files above 200 MB
    (7.8 GB, all derived `.npy` cubes); `report_large_files.py` records them and
    the rule is: keep locally, never upload, regenerated by `run_all.py` and
    verified by the manifest. A stale 1.45 GB duplicate file was removed.

## What can be fixed without new data

- generation-parameter sensitivity (TIR noise, EM correlation, depth decay);
- figure/table captions inline, JSTARS template, line numbers;
- author-contributions / conflict-of-interest / funding statements;
- graphical abstract;
- large-intermediate compression policy.

## What requires new data or hardware

- real TIR/EM imagery;
- independent alteration/deposit labels;
- field or climate-chamber validation;
- site-specific 3-D/borehole validation;
- edge hardware (Jetson/MCU) and power measurement.

## What requires a model redesign

- calibrating H / row scaling with intercept instead of column normalisation;
- log10 EM with clay-only response (done);
- predictive uncertainty (not forward-filter variance);
- target definition that is not a gamma-derived proxy.

## Open items as of 2026-11-07

| # | item | size | who |
|---:|---|---|---|
| 1 | move the 12 table captions inline, above each table (they are currently one list at the end) | small, mechanical | me |
| 2 | place the 6 figures at first citation with inline captions instead of appending them after the references | small, mechanical | me |
| 3 | add continuous line numbers to the docx (JSTARS review requirement) | small | me |
| 4 | add Author Contributions (CRediT), Conflict of Interest, Funding and Acknowledgements sections | small, text only | me, but **funding text must come from you** |
| 5 | build a graphical abstract from the existing figures | medium | me, needs your approval of the design |
| 6 | generation-parameter sensitivity: sweep TIR noise, EM correlation weight, depth decay and independent-field weight through the corrected model | medium, ~30 min compute | me |
| 7 | large intermediates: 8 files > 200 MB (three depth cubes, three TIR cubes, two EM cubes); add a compression/cleanup policy and document it | small | me |
| 8 | JSTARS two-column template and final figure sizing | medium | needs the official template file |
| 9 | public repository + Zenodo DOI + CI workflow | medium | **needs your GitHub/Zenodo account** |
| 10 | cover-letter reviewer suggestions | small | **needs real names (cannot invent)** |
| 11 | real TIR/EM data, independent labels, borehole check, edge hardware | large | out of scope by design |

Items 1–7 and 9's CI workflow can be done in this workspace; 8 and 10 need an
external artefact or decision; 11 is the honest limit of the study.

## Closed since the last snapshot

- corrected-EM model propagated to ablation, validation, degradation,
  temperature, depth and calibration;
- threshold/top-k sweep and scenario-level block bootstrap with BH correction;
- published-method baselines;
- reference list (24 entries, all cited, DOI-checked, two unverifiable entries
  removed);
- β (EM depth profile) sensitivity experiment and two new cross-checks;
- stale figures and captions realigned, docx table markup fixed.








