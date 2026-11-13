# Changelog — cleanup and corrections

## Round 17 — submission guide and paste fields (2026-11-13)

* **Step-by-step guide** `docs/submission/SUBMISSION_GUIDE.md`: official links
  (journal home, Guide for Authors, Editorial Manager `cageo`), registration,
  field-by-field entry, the upload-slot order, the PDF check before approval,
  post-submission states and the usual pitfalls.
* **`paste_fields.txt`** is generated with the package: title, authors, abstract
  (247 words), six keywords and five highlights, stripped of Markdown, ready to
  paste into the submission form.
* **Links checked as far as this machine allows:** Editorial Manager answers 200;
  ScienceDirect and Elsevier pages return 403 to scripted requests but open
  normally in a browser.
* **No scientific content changed.**

## Round 16 — upload set assembled (2026-11-13)

* **One command builds the upload set.** `code/make_submission_package.py` now
  produces `docs/submission/upload/` with the manuscript, a dated cover letter, a
  highlights file, the supplementary material, six RGB 300-dpi figures (alpha
  flattened to white) and the graphical abstract, plus
  `docs/submission/upload_manifest.json` (path, bytes, SHA-256 and the Editorial
  Manager slot of every file) and `CG_submission_package.zip` (17.8 MB). The
  `upload/` copies and the zip are git-ignored build artefacts; rerunning the
  script refreshes them from the canonical files.
* **Cover letter and highlights are stand-alone Word files** generated from the
  Markdown sources, so the letter is dated, addressed to the C&G editor and uses
  the same numbers as the manuscript.
* **The submission README lists the upload slots** (cover letter, manuscript,
  highlights, six figures, graphical abstract, supplementary material), their
  sizes and the rebuild command.
* **Manifest hygiene:** `build_manifest.py` now skips `docs/submission/upload/`
  and the submission zip, so build artefacts no longer enter the scientific
  manifest while the raw `.zip` survey files stay in it.
* **No change to scientific content.** The validator and the 36 assertions are
  untouched; the manifest stands at 6,848 files / 11.46 GB.

## Round 15 — C&G submission package completed (2026-11-12)

* **Generative-AI declaration added.** The Declarations section now states that a
  large language model (DeepSeek) was used to draft and edit text, to write and
  review code and to assist the analysis, and that the author reviewed and
  verified all content and takes responsibility for it. Elsevier requires this
  disclosure.
* **Table 8 moved to Supplementary Table S1.** The thermal-retrieval sensitivity
  table now lives in `docs/Supplementary_Tables.md` / `.docx`; §7.6 points to it
  and the main text carries 8 tables. The published-practice table is renumbered
  Table 9 → Table 8, and `validate_pipeline.py` now parses Tables 4–8.
* **Documentation synced.** The submission checklist lists the supplementary file,
  the declaration and the 8-table layout; READINESS_AUDIT, GAP_AUDIT,
  JOURNAL_SHORTLIST and SUPPLEMENTARY follow.
* **Word paragraph structure fixed.** `docs/build_draft_docx.py` had emitted one
  Word paragraph per hard-wrapped Markdown line, so every line carried its own
  paragraph spacing and the review copy was not a normal manuscript. Consecutive
  text lines are now joined into real paragraphs (176 instead of 424), while
  headings, list items, tables, captions and the 24 references stay separate.
* **No data or figure changes.** The validator still passes 53/53 artefacts and
  22/22 invariants, the 36 assertions pass, and the manifest was rebuilt.

## Round 14 — final journal choice: Computers & Geosciences (2026-11-12)

* **Target fixed on C&G.** Free subscription route (0 APC, 0 page charges), JCR Q1 /
  中科院 地球科学 2 区, and the best scope match for a benchmark + software + audit
  paper. The acceptance-first alternative (ESI: free, 3 区, higher acceptance) is
  documented as the fallback in `docs/JOURNAL_SHORTLIST.md`.
* **Package switched back.** `docs/COVER_LETTER.md` is restored to the C&G version
  (the ESI version remains in git `87e9797`); `docs/submission/README.md` targets
  Elsevier again, highlights are marked as required (5 bullets, max 77 characters)
  and the ESI-only author–year conversion is removed. References stay numeric;
  only the reference-list punctuation may need minor restyling to Elsevier
  numbered.
* **Manuscript, data and artefacts unchanged.** The software-availability
  paragraph, the numeric citations, the 9 tables and 6 figures all stay as they
  are; nothing in `processed/` was regenerated for this decision.

## Round 13 — acceptance-first journal target (2026-11-12)

* **Target changed to _Earth Science Informatics_ (Springer).** Under the stated
  constraint — no page charges and the highest realistic acceptance — ESI is the
  best free option: subscription route with no APC and no page charges, a scope
  built around geoscience data, computational workflows and reproducibility, and
  a review culture more receptive to a benchmark with a partly negative result
  than C&G. The acceptance ordering and its caveats are in
  `docs/JOURNAL_SHORTLIST.md`.
* **C&G is kept as the Q1 alternative.** It remains free (subscription route) and
  is the only free Q1 / 中科院 2 区 option in this list, but its acceptance rate is
  lower; the choice is now explicit rather than implicit.
* **Package updated for ESI.** `docs/COVER_LETTER.md` is rewritten for *Earth
  Science Informatics*; `docs/submission/README.md` now targets Springer, marks
  highlights as optional and records the one real reformatting task: the
  manuscript still uses IEEE numeric citations and must be converted to Springer
  Basic (author–year) before an ESI upload. JAG and C&G use numeric styles and
  would not need that step. The C&G letter and the numeric manuscript remain in
  git (`d1a4cea`).
* **Manuscript text, numbers and docx unchanged.** This round changes only the
  venue-facing documents; the validator, artefacts and figures are untouched.

## Round 12 — system check and journal choice (2026-11-12)

* **End-to-end rerun from the committed tree.** `python code/run_all.py all`
  exited 0: every stage ran, and the headline numbers reproduced exactly —
  gamma F1 0.5314, gamma+TIR 0.6519, all 0.4967; zero channels 0.6144, noise
  0.6490, block-shuffled 0.6341; model-free 0.3503 → 0.5290 (+0.1787, CI
  [0.1198, 0.2412]); ΔF1 +0.1195 [0.0674, 0.1668]. The validator passed 53/53
  artefacts and 22/22 invariants, `test_core.py` 36/36, and the manifest was
  rebuilt (6,843 files / 11.46 GB). A field-by-field comparison with HEAD shows
  no scientific value changed: only `generated_at`/`runtime_s` fields, file
  sizes that differ by the one digit of a timestamp, and the measured
  `edge_ai` latency moved.
* **`DATA_STRUCTURE.md` rewritten for the real-ASTER line.** The old file still
  described the 10-channel synthetic v2 chain and `run_fusion.py` as the fusion
  stage. It is archived as `docs/archive/DATA_STRUCTURE_V2.md`, and the new file
  documents the 11 channels, the two masks, the response matrix, the current
  array/JSON schemas and the 22 invariants.
* **Standalone and legacy scripts documented** (SUPPLEMENTARY §S6):
  `run_fusion`, `block_bootstrap`, `run_independent_target`, `run_real_tir`,
  `run_em_fix_repeats`, the three `*_emfix` wrappers and the packaging/network
  helpers. They run but are deliberately outside `run_all.py`, and none of their
  outputs is one of the 53 validated artefacts.
* **Journal re-evaluated against live metadata.** OpenAlex and Crossref checks on
  2026-11-12 show that **IEEE JSTARS and IJAEOG are now fully open access**
  (CC BY articles, mandatory APC ~$1,800 and ~$3,550) and must leave the free
  list; C&G, ESI, JAG, Mathematical Geosciences, Geophysical Prospecting,
  Exploration Geophysics and IJRS remain hybrid with a subscription route.
  `JOURNAL_SHORTLIST.md` is rewritten around that evidence and confirms **C&G as
  the target** (free subscription route, Q1/2 区), with ESI then JAG as
  fallbacks. JSTARS and IJAEOG were previously recommended as free; they are not.
* **Software availability paragraph added** to the manuscript (name, version,
  licence, repository, DOI, environment, reproduction command) and the `.docx`
  rebuilt (419 paragraphs, 9 tables, 6 figures). This is what the C&G Guide for
  Authors asks for, and it was impossible before the DOI existed.
* **Static check:** pyflakes over `code/*.py` reports only unused imports and
  unused local variables — no undefined names and no syntax errors; CI's
  `compileall` stays green.
* **No Zenodo edit.** Version 1.0.0 remains the archived snapshot; this round
  changes docs and tooling only, so no new version is published.

## Round 11 — maintenance (2026-11-12)

* **State re-verified from the artefacts, not from memory.** Working tree clean at
  `36f1836`, in sync with `origin/main`; CI run
  [43023376520](https://github.com/Xbotsd/fusion-gain-confounds/actions/runs/43023376520)
  green; this round re-ran `test_core.py` (36/36 assertions) and
  `validate_pipeline.py` (PASS, 53/53 artefacts, 22/22 invariants), which refreshed
  `processed/pipeline_validation.json` with the same values. The last full
  `run_all.py all` (2026-11-10) had exited 0.
* **The archive was checked, not assumed.** The Zenodo file
  `fusion-gain-confounds-1.0.0.zip` was downloaded: its MD5
  `5a9ee01403f63109bd0076c436093323` equals the record's checksum, its 270 entries
  equal `git ls-tree -r 2d194a2`, and the DOI resolves to record 24130421.
* **Metadata aligned with that snapshot.** `pyproject.toml` still named the old
  repository (`ivanpah-fusion-benchmark`, version 0.1.0); it is now
  `fusion-gain-confounds` 1.0.0 with repository and DOI URLs. `.zenodo.json` moved
  to version 1.0.0 and now carries the published description, the `eng` language
  and the GitHub `isSupplementTo` relation alongside the SIM 3206 citation.
* **Tag and release added.** `v1.0.0` is an annotated tag on `2d194a2`, the archived
  commit, and the GitHub release points at the DOI. Until now the only release
  (`v0.1.0`) was unrelated to the DOI, which made the archive untraceable from
  GitHub; it is now marked superseded.
* **Documentation corrected where it contradicted the artefacts.** The "25 unit
  tests" in the README, SUPPLEMENTARY, READINESS_AUDIT and the cover letter are 36
  assertions in 9 test groups; the cover letter's "19 invariants" is 22; the
  submission checklist's abstract count (236) is 247 and its data-availability row
  still said "DOI on acceptance"; READINESS_AUDIT and GAP_AUDIT still listed the
  GitHub push and the DOI as open; NORMALISATION_AUDIT still said the fix was
  "designed, not yet applied" although Round 7 applied it.
* **Maintenance made repeatable.** `code/maintain.py` is a read-only health check
  (git state, version strings, DOI strings, Zenodo record, GitHub release,
  placeholder/encoding scan, last validator run) and `docs/MAINTENANCE.md` states
  what may change and how a new version is published.
* **Zenodo was not edited.** Record 24130421 stays at version 1.0.0, the
  `remote-sensing` inclusion request is still open, and there is no newer upload of
  this project to maintain. DOI 10.5281/zenodo.24130421 is a *version* DOI: a new
  version gets a new version DOI, while the concept DOI 10.5281/zenodo.24130420
  stays fixed.

## Removed

All versioned duplicates and the pre-translation backup were deleted from
`code/`:

* `ablation.py`, `ablation_v2.py` (kept the v3 logic, rewritten as `run_ablation.py`)
* `degradation_test.py`, `_v2`, `_v3` (rewritten as `run_validation.py`)
* `kf_fusion.py`, `_v2`, `_v3`, `_v4`, `_final` (rewritten as `run_fusion.py`)
* `generate_em_cube.py`, `_v2`, `_v3`, `_final` (rewritten as `prepare_em.py`)
* `generate_tir_cube.py` (rewritten as `prepare_tir.py`)
* `depth_kalman_v2.py` (rewritten as `run_depth.py`)
* `final_gt.py`, `final_validation_v2.py` (rewritten as `run_validation.py`)
* `baseline_comparison.py` (rewritten as `run_baselines.py`)
* `cross_domain.py`, `H_sensitivity.py`, `multi_seed.py`, `resolution.py`,
  `temperature_advanced.py`, `temperature_test.py` (merged into
  `run_validation.py` / `run_sensitivity.py` / `run_environment.py`)
* `stack_cube.py`, `config_H.py`, `extract_tir_spectra*.py`,
  `extract_em_stats.py`, `read_*.py`, `convert_grd.py`, `diag_nc.py`,
  `EDI_RUN.PY`, `S.PY`, `test_grd.py`, `viz_aem.py`, `TIR_spectra_preview.py`,
  `statistical_test.py`, `generate_fig1.py`, `generate_fig2.py`,
  `translate_code.py`
* `code_backup_20261016_193309/`

Stale result files from the removed versions were deleted from `processed/`
(`ablation_*_v2`, `degradation_*_v2..v4`, `exp10..exp14`, old `Fig1/Fig2`,
`kf_fusion_result*`, `temperature_*`, `final_validation*`, previews).

## Final code

`common.py`, `prepare_gamma.py`, `prepare_tir.py`, `prepare_em.py`,
`run_fusion.py`, `run_depth.py`, `run_ablation.py`, `run_validation.py`,
`run_baselines.py`, `run_environment.py`, `run_sensitivity.py`,
`make_figures.py`, `audit_data.py`, `run_all.py`, `requirements.txt`.

## Fixed

1. **Metric bug.** `detection_metrics` originally cast the continuous
   `clay_prior` to boolean, which made every pixel “truth” and precision
   identically 1.0.  It now thresholds at 0.55 explicitly.
2. **Valid mask.** Metrics were computed over the whole grid, including 33.6 %
   NoData cells filled with constants.  All metrics now use the 66.4 % valid
   survey footprint.
3. **Per-pixel solve.** `wls_pixel` reshaped a `(5,5,H,W)` array with the wrong
   axis order, producing singular systems; it now transposes to `(H,W,5,5)` and
   uses float64.
4. **Baseline dispatch.** The independent baseline applied a 5×3 operator to a
   10-row observation; it now passes the matching modality rows.
5. **Adaptive weight direction.** Scenario scripts now use explicit quality
   multipliers `W = diag(q)` (higher quality = more weight); the old code used a
   noise estimate directly as a weight and plotted its inverse.
6. **One H matrix.** The ablation and validation now share `H_MATRIX`; the old
   ablation used a different clay signature.  See `docs/MODEL_AUDIT.md`.
7. **Provenance.** Docs and scripts now state the real survey (Ivanpah, NV–CA,
   2019-12 → 2020-03) instead of the manuscript’s Colorado label.
8. **Figures.** Redrawn without the unimplemented AI-residual and edge-runtime
   modules.

## Data unchanged

`prepare_*.py` reproduce the original cubes:

* gamma: bit-identical;
* TIR: max abs difference `3.4e-6` (float32 rounding);
* EM: max abs difference `5.4e-3` Ω·m (float32 rounding).

No synthetic value was silently regenerated or rescaled.

## Results that changed

* ablation: `0.198 → 0.403 (+104 %)` does not reproduce; with one H the
  gamma+TIR configuration is best on F1 (0.339), EM lowers it (0.191).
* “detection rate 65.26 %” → mean proxy recall **0.6594**, mean F1 **0.2533**;
  precision 0.165 at the normal operating point.
* EMI failure *increases* proxy recall (0.693 → 0.976), the opposite of the
  draft’s graceful-degradation narrative.
* CORAL gap: 0.08 % direct vs 0.17 % CORAL (not 5.22 % → 0.27 %).
* Overall ordering of baselines changes: the independent inversion has the best
  F1 (0.333) under the legacy H; GLS has the best matched-prevalence precision
  (0.292); the proposed estimator has the highest clay abundance, the smoothest
  map and the most coherent components (223 vs 5,375).
* Corrected EM (log10 resistivity + clay-only) raises F1 from 0.267 to **0.498**
  and AP from 0.126 to **0.513**; the legacy negative result is a
  model-specification artefact, not a verdict on fusion.

## Round 3 — diagnosis hardened, framing aligned

* **A sharper diagnosis.** The legacy EM row is now described by what the code
  and data actually show, not by an asserted mechanism. Measured: the EM-only
  clay estimate under the legacy rows is **anti-correlated** with the proxy
  (r = −0.469, F1 0.06), because the row gives clay the *lowest* resistivity
  while the documented synthetic field places clay at *higher* log10 ρ. The raw
  Ω·m scale also presses the TIR mineral contrast from 0.21–0.26 down to 0.024
  and raises κ(H) from 48.5 to 1156. The earlier draft text (“clay receives a
  small EM weight”) was wrong and is corrected in the manuscript (§5.2, §7.2,
  §8.1, §8.2, abstract).
* **New experiment: β sensitivity.** `run_em_beta_sensitivity.py` →
  `em_beta_sensitivity_emfix.json/csv` sweeps four depth profiles. F1 is
  0.498 (production β, the recipe's `exp(−d/250)` decay rounded), 0.490 (exact
  recipe decay), 0.483 (reversed) and 0.459 (uniform), against 0.267 legacy. β
  is therefore not a tuned parameter. Added to the `eval_emfix` stage, to
  `validate_pipeline.EXPECTED_JSON`, and to two new cross-checks
  (`em_beta_matches_recipe`, `em_beta_robust`).
* **Duplicate scenario removed downstream.** `validation.json` was regenerated
  after the earlier dedup fix: 27 scenarios, overall recall **0.6609**, F1
  **0.2537**, sensor-degradation family **0.746** (it had been 0.738 while the
  duplicated `normal` row was inside the family mean).
* **Every reported CI now comes from the current artefact.** The scenario CIs in
  the manuscript and in `SCENARIO_CI.md` were stale; `SCENARIO_CI.md` is now
  generated from `scenario_bootstrap.json` by `code/dev/build_scenario_ci.py`,
  so it cannot drift. ΔF1 upper bound corrected 0.217 → **0.216** everywhere;
  EMI+TIR-failure BH p corrected 0.90 → **0.91**.
* **Manuscript restructure completed.** New **§4.8** defines the corrected EM
  model (transform, attribution, sign, β provenance, sensitivity). Abstract,
  highlights, contributions, conclusion and §8 were rewritten to lead with the
  corrected model and to state the gamma-ratio limit explicitly. Table citations
  now run 1–12 in order (Table 9 = scenarios, Table 10 = depth) and the `##
  Tables` caption list was rebuilt to match the 12 body tables.
* **Documentation regenerated** with post-dedup numbers: `RESULTS.md` (now
  corrected-EM first), `EM_FIX.md`, `EM_FIX_VALIDATION.md`, `ADVANTAGE.md`,
  `SCENARIO_CI.md`, `PUBLISHED_BASELINES.md`. `published_baselines.json` was
  regenerated to fix the stale `Gnojek 1995` label (correct year 1985).
* **State:** 90/90 artefacts, 15/15 cross-checks, 24/24 unit tests, 0 coverage
  orphans, manifest 6,685 files / 12.77 GB.

## Round 10 — repository and archive (current)

* **Repository renamed** to `fusion-gain-confounds`, so the name states the
  paper's thesis instead of the field area; all documents, `CITATION.cff`, the
  cover letter and the manuscript carry the new URL.
* **Licence corrected**: `LICENSE` was a pure MIT text signed "A_MineralProspecting
  authors" (a directory name); it now reads "Copyright (c) 2026 Yudong Xu" and
  GitHub detects MIT. Third-party data terms moved to `NOTICE.md`.
* **DOI issued**: Zenodo record 24130421, version DOI 10.5281/zenodo.24130421,
  concept DOI 10.5281/zenodo.24130420, archive `fusion-gain-confounds-1.0.0.zip`
  (18.7 MB, `git archive` of commit `2d194a2`). The DOI is in the manuscript's
  data-availability paragraph, `CITATION.cff`, the README badge and the cover
  letter.
* **Record description expanded** with the quantitative result, the archive
  contents and the reproduction command; a community-inclusion request for
  `remote-sensing` is pending curator acceptance.
* **Author ORCID** 0009-0002-3231-0444 on the title page, in CRediT, in
  `CITATION.cff` and in the Zenodo creator metadata.
* **State:** the paper is NOT submitted; the DOI identifies the software, not a
  publication.

## Round 9 — controls tightened, one bootstrap, one command (current)

* **The zero-channel control is now literally zeros.** `run_tir_controls.py`
  gained `gamma + 5 zero channels` alongside the Gaussian-noise block. The
  literal zeros are the *weaker* control: they recover 69 % of the F1 gain
  (0.614) while noise recovers 98 % (0.649) and the block-shuffled cube 85 %
  (0.634), against 0.652 for real ASTER and 0.531 for gamma. On the independent
  geological target every inert control scores at least as high as the real cube
  (0.919 and 0.922 against 0.913), so that gain is conditioning in full. The
  manuscript, abstract, highlights and conclusion now state the range instead of
  the single noise figure they previously attributed to zeros.
* **One block bootstrap.** `paired_bootstrap`, `block_ids` and `pred_of` moved
  into `common.py`; `run_main.py` and `run_real_tir_robust.py` both call it, so
  the robustness table and the main table can no longer quote different
  intervals for the same contrast (they did: `[0.082, 0.157]` versus
  `[0.067, 0.167]`). A new validator invariant fails if they diverge again.
* **The manuscript's tables are validated, not typed.** `validate_pipeline.py`
  parses Tables 4–7 and 9 out of `Manuscript_v2_draft.md` and fails if any cell
  differs from the artefact it came from; the check was verified by perturbing a
  cell. Invariants went 18 → 22.
* **One autocorrelation estimate.** `main_results.json` keeps a clearly labelled
  in-run sanity value; the quoted integral scales, design effect (11,262) and
  N_eff (110 for the proxy, 173 for the clay map) come only from
  `autocorr.json`.
* **Submission back-matter.** CRediT statement, competing interests, funding and
  acknowledgements added; highlights cut to ≤ 77 characters; a graphical
  abstract (`docs/graphical_abstract.png`, produced by
  `make_graphical_abstract.py` in the `figures` stage) reads its numbers from the
  artefacts.
* **Repository tidy.** Twenty-one superseded round notes moved to `docs/archive/`
  with a README explaining why their numbers are stale; the cover letter rewritten
  against the current results.
* **State:** `python code/run_all.py all` exits 0; 53/53 artefacts, 22/22
  invariants, 25/25 unit tests, 0 coverage orphans, manifest 6,791 files /
  11.45 GB. A second full run reproduced every scientific value bit-for-bit; only
  `runtime_s` differed.

## Round 8 — real ASTER promoted to the main line

* **The thermal infrared is now real data.** `prepare_tir_real.py` builds the
  five-band ASTER L1T emissivity cube offline from `raw/aster/` (4 scenes,
  2006-10-18, archived by `fetch_aster.py` with STAC ids and SHA-256), and the
  observation becomes 3 gamma + 5 ASTER TIR + 3 EM = **11 channels**. The TIR
  rows of `H` are sampled from USGS splib07 over each ASTER band pass instead of
  being hand-set. The synthetic splib07 cube survives only as a control.
* **Two implementation bugs fixed, both of which inflated fusion gains.**
  Response-matrix columns were normalised over *all* rows (including modalities
  switched off) and channel weights over *all* channels, so "gamma only" gave
  F1 0.325 under one matrix and 0.519 under another for identical data. Both now
  normalise over the active set only, and `test_core.py` asserts the two
  invariances.
* **The paper's central claim changed, because the data said so.**
  `run_tir_controls.py` appends five channels of *zeros* with the ASTER rows of
  `H` and reproduces almost the entire gain (F1 0.649 vs 0.652; geological AUC
  0.922 vs 0.913): inside an underdetermined inversion the gain is
  **conditioning**, not information. Gamma alone has rank 3 of 5.
* **A model-free information test** (`run_geology_multiclass.py`) removes the
  response matrix entirely: multinomial logistic, 128-px block CV, four
  geologically similar substrates, 20 repeats. Gamma + real ASTER = 0.529
  balanced accuracy vs 0.350 for gamma (+0.179, CI [0.120, 0.241], 20/20), and a
  block-shuffled cube gives 0.354. This is the paper's real positive result and
  it is ~4x smaller than the inversion implied.
* **Independent target added throughout** (`run_tir_information.py`,
  `run_geology_multiclass.py`, `geology_auc` in `run_main.py`): every
  configuration now reports proxy F1 *and* geological AUC.
* **Pipeline restructured** into prepare / main / controls / aux / legacy /
  figures / audit; `validate_pipeline.py` rewritten around 53 artefacts and 18
  invariants, three of which are the new controls.
* **Manuscript rewritten** (title, abstract, Sections 3–9, 8 tables) so that
  every number comes from the regenerated artefacts and the EM modality is
  labelled synthetic everywhere.
* **Repository prepared**: `git init`, `.gitignore` (raw data and multi-GB cubes
  excluded, 10.3 MB tracked), `CITATION.cff`, `.zenodo.json`.


* **Found and fixed a normalisation artefact.** `normalize_H` scaled each mineral
  column over all ten rows, including modalities that were switched off, so
  "gamma only" gave F1 0.3246 under the legacy matrix and 0.5190 under the
  corrected one for identical data. `fuse` now normalises over the active rows,
  a unit test asserts the invariance, and the whole pipeline was re-run.
* **The headline claim survives and is cleaner.** Full-model F1 is unchanged
  (0.2671 legacy, 0.4982 corrected) and the two matrices now agree exactly
  wherever EM is inactive, so the entire gain comes from the EM rows.
  Ablation numbers did change: gamma 0.5217, gamma+TIR 0.4410, gamma+EM 0.1912 /
  0.4142, all 0.2671 / 0.4982.
* **New independent-target experiment** (`run_independent_target.py`). Scored
  against USGS SIM 3206 substrate classes, with labels that never see gamma or
  TIR: gamma alone sits at chance (AUC 0.476), gamma+TIR reaches 0.905 with the
  real ASTER cube and 0.895 with the synthetic one, the full set 0.909. The raw
  channels separate the same substrates almost perfectly (K alone 0.986), so the
  loss is caused by the inversion being underdetermined with three channels, not
  by missing information.
* **Real-TIR robustness (experiments 2-4).** Bootstrap of the gamma+TIR gain:
  +0.119 [0.080, 0.169], 200/200 wins. Insensitive to the TES assumption
  (eps_max 0.95/0.98/1.00 give 0.6400/0.6401/0.6403), to dropping the band with
  the residual temperature correlation (0.5856), and to the acquisition date
  (2006-09-25 gives 0.6410).
* Experiment 1 also made the section 5 result sharper: the variance-gain index
  now agrees with the F1 sign in **0 of 6** additions.
* **State:** 97/97 artefacts, 21/21 cross-checks.

## Round 6 — real ASTER TIR branch

* **Real thermal infrared acquired and processed**: prepare_tir_real.py pulls
  four ASTER L1T scenes (2006-10-18, 100 % footprint coverage, 90 m, 5 bands)
  anonymously from the Planetary Computer, mosaics them with GDAL onto the 50 m
  analysis grid, converts DN to radiance with the ASTER unit-conversion
  coefficients, retrieves brightness temperature and separates emissivity by
  normalisation. Physical gate: BT 282-298 K, emissivity 0.89-1.00, residual
  temperature correlation 0.03-0.21 in bands 1-3.
* **Ablation rerun on real data** (
un_real_tir.py → 
eal_tir.json/csv/png)
  with three branches so that data and model construction are separated:
  published pipeline, synthetic data with library-sampled H, and real ASTER.
  Reference branch reproduces em_fix.json exactly (F1 0.4982), and a new
  cross-check asserts it.
* **The central ablation conclusion changes**: with real ASTER emissivity,
  gamma + TIR reaches F1 **0.644** against 0.521 for gamma alone (+0.12), where
  the synthetic cube gave -0.07. TIR, not EM, is the load-bearing modality once
  the TIR data are real. The legacy matrix still suppresses TIR (0.315), which
  confirms the conditioning argument.
* EM remains synthetic: no measured AEM exists at this site, documented in
  docs/REAL_DATA_FEASIBILITY.md.
* **State:** 97/97 artefacts, 21/21 cross-checks.

## Round 5 — P0 and P3 closed

* **§5 identifiability implemented** (`run_identifiability.py` → `identifiability.json/csv/png`,
  `eval_emfix` stage, two new cross-checks). The computation contradicted the
  manuscript's original claim: the variance gain index is **positive for every
  added modality** (six of six) and agrees with the observed F1 sign in only
  **one of six** cases. The legacy `+EM` configuration has the largest predicted
  gain (0.804) and the worst F1 change (−0.133), because the EM block carries
  98.2 % of the clay column's squared norm while being mis-signed. §5.4,
  contribution (ii) and §8.1 were rewritten to state this honestly: a variance
  index is necessary but not sufficient.
* **Abstract cut to 248 words** (was 359; journal limit 250), with the κ detail
  and the ten-run precision figures dropped and the gamma-ratio caveat kept.
* **Captions and figures moved inline**: 12 table captions now sit above their
  tables, and the six figures carry `<!-- FIGURE:… -->` + `**Figure N.**` right
  after the paragraph that first cites them. Figures were renumbered by citation
  order (EM comparison is now Figure 4, ablation 5, robustness 6). The trailing
  `## Tables` list and the figure appendix after the references are gone.
* **Continuous line numbers** added to the docx (`w:lnNumType`), as the journal
  requires for review.
* **Generation-parameter sensitivity** (P3): `run_generation_sensitivity.py` →
  `generation_sensitivity.json/csv/png`. It regenerates the EM cube through the
  `prepare_em.py` code path (bit-identical: max |diff| 0.0 Ω·m) and sweeps clay
  amplitude, independent-field amplitude, depth decay, overall scale and TIR
  noise. Sixteen settings give F1 0.468–0.518 against 0.267 legacy. Two
  findings: the overall EM scale has *no* effect (channels are z-scored, so an
  amplitude error is unobservable), and clay-vs-independent amplitude act in
  opposite directions as expected.
* **Large-file policy** (P3): `report_large_files.py` → `large_files.json`,
  documented in `DATA_STRUCTURE.md §5.1`. Seven derived cubes above 200 MB
  (7.8 GB) are kept locally, never uploaded, and verified by the manifest. A
  stale 1.45 GB duplicate (`depth_kalman_3d.npy_emfix.npy`, produced by an old
  naming bug, referenced nowhere) was deleted.
* **State:** 95/95 artefacts, 19/19 cross-checks, 24/24 unit tests, 0 coverage
  orphans.

## Round 4 — bibliography executed

* **Removed two unverifiable references**: Macnae 2016 (ASEG extended abstract)
  and Bedini 2009 (unindexed journal, no Crossref record after repeated title and
  author queries). Neither was cited in the body, so no sentence changed; the
  list went from 25 to 24 entries and stays contiguous 1–24.
* **Added the missing SAM citation**: Kruse et al. 1993, *Remote Sensing of
  Environment* 44(2–3), 145–163, DOI 10.1016/0034-4257(93)90013-N
  (Crossref-verified). The manuscript cited "Kruse et al. 1993" in §7.10 and
  Table 12 without listing it — an orphan citation.
* **Citation coverage fixed**: 19 of 24 entries were never cited. IEEE-style
  numeric markers were inserted where the corresponding technique is named —
  [1–4,21] gamma ratios, [5–7,20,21] EM, [8–10,22] TIR, [11–14] fusion,
  [18] metrics, [19] aeromagnetic/TMI, [23] F-parameter, [24] SAM, [4] low
  eTh/K, and [15] moved from the fusion paragraph to the CORAL sentence in §6
  where it belongs. Verified programmatically: **no missing and no orphan
  markers over 1–24**.
* **`code/verify_references.py`** candidate list updated to match (Macnae/Bedini
  out, Kruse in), so a future Crossref run checks the list that is actually
  submitted.
* `docs/REFERENCES_AUDIT.md` rewritten as an executed record: 24 entries, 11
  DOI-verified, 5 books with DOI, 8 MANUAL with stable bibliographic details,
  plus a citation-coverage table.
