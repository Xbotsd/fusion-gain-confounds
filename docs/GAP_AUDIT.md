# Gap audit — what is done, what is missing, and where the rigour is thin

Snapshot 2026-11-10, real-ASTER main line: **53/53 artefacts, 20/20 invariants,
25/25 unit tests, 0 coverage orphans**, manifest 6,772 files / 11.45 GB.

## Rigour scorecard

| dimension | score | why |
|---|---:|---|
| Data reality | 8/10 | gamma, TIR, TMI and geology real; EM synthetic and labelled everywhere |
| Target independence | 8/10 | three targets including a model-free one that no response matrix can inflate |
| Identifiability | 9/10 | rank, κ, variance-gain index and a zero-filled control |
| Statistical inference | 7/10 | 128-px block bootstrap, 20-repeat CV, CIs; N_eff 110 |
| Uncertainty | 2/10 | coverage 0.13/0.26; the filter variance is not a predictive interval |
| Reproducibility | 9/10 | pinned, hashed, offline ASTER archive, coverage guard, one command |
| Manuscript completeness | 6/10 | rewritten; open items below |

## Closed in this round

* **Real ASTER thermal infrared on the main line** (5 bands, 2006-10-18, archived
  offline with STAC ids and SHA-256); synthetic TIR demoted to a control.
* **Two normalisation bugs fixed** (response-matrix columns and channel weights
  were normalised over inactive rows/channels, which inflated fusion gains).
* **The conditioning confound measured**: five channels of zeros with the ASTER H
  rows reproduce F1 0.649 vs 0.652 and AUC 0.922 vs 0.913.
* **A model-free information test**: +0.179 balanced accuracy (CI [0.120, 0.241],
  20/20), null for a block-shuffled cube.
* **Independent target wired into every experiment** (proxy F1 *and* geology AUC).
* Manuscript rewritten; abstract 249 words; 9 tables, 6 figures in order.

## Open — needs an external action

| # | item | who |
|---:|---|---|
| 1 | create the GitHub repository and push (`docs/GITHUB_SETUP.md`) | **you** — credentials |
| 2 | Zenodo DOI from that repository | **you** |
| 3 | CRediT, conflict of interest, funding, acknowledgements | me, **funding text from you** |
| 4 | target-journal two-column template and figure sizing | needs the template file |
| 5 | cover-letter reviewer suggestions | **needs real names** |
| 6 | graphical abstract | me, needs your approval of the design |

## Open — scientific, cannot be closed with public data

| # | item | why |
|---:|---|---|
| 7 | measured airborne EM | no AEM survey exists over this footprint; the delivered data are radiometric + magnetic |
| 8 | alteration / mineralisation labels, boreholes | not public for this area |
| 9 | contemporaneous thermal data | anonymous ASTER archive used here covers 2006; Landsat has only two thermal bands |
| 10 | full temperature–emissivity separation | the AST_05 product needs an Earthdata login; we use normalisation and test its sensitivity |
| 11 | single survey | no second site with the same four real layers |

## Deliberately deprecated

The synthetic-TIR experiments (ablation, validation families, advantage, EM-fix
tables, V2, ASU, scenario bootstrap) still run in the `legacy` stage, but the
manuscript no longer draws numbers from them: the real-ASTER branch supersedes
them, and keeping both in the text invited the very confusion this paper is
about.
