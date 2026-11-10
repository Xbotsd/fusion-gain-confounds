# Publication readiness — real-ASTER main line

Date: 2026-11-10. Every number below is from a command, not recall.

## Verdict

| layer | verdict |
|---|---|
| Framework | **complete** — 53 artefacts, 18 invariants, 0 coverage orphans, 25 unit tests |
| Functional coverage | **complete for the manuscript**; the legacy synthetic branch is labelled and optional |
| Data reality | gamma, ASTER TIR, TMI and geology are real; **EM is synthetic and cannot be otherwise** |
| Manuscript | rewritten around the new evidence, 9 tables, 6 figures, IEEE-style references |

## What changed and why it matters

The thermal infrared is now **real ASTER data on the main line** (5 bands, 90 m,
2006-10-18, archived offline with SHA-256). The synthetic splib07 cube survives
only as a control. That alone removes the largest reviewer objection.

More importantly, two controls changed the paper's claim:

1. **Conditioning control.** Appending five channels of *zeros* with the ASTER
   rows of `H` reproduces almost the whole fused gain (F1 0.649 vs 0.652;
   geological AUC 0.922 vs 0.913). Gamma alone has rank 3 of 5, so the inversion
   is underdetermined and any channel helps by regularising it.
2. **Information control.** A model-free multinomial test (no response matrix)
   shows a real but four-times-smaller gain: gamma + ASTER = 0.529 balanced
   accuracy versus 0.350 for gamma (+0.179, CI [0.120, 0.241], 20/20 repeats),
   and a block-shuffled cube gives 0.354.

The manuscript now reports both, which is a stronger and more defensible
contribution than the previous "fusion works / does not work" framing.

## Framework evidence

| item | value |
|---|---|
| stages | prepare, main, controls, aux, legacy, figures, audit (+ asu, refs network) |
| artefacts validated | **53/53** |
| cross-artefact invariants | **18/18** |
| unit tests | **25/25** |
| coverage orphans | **0** |
| manifest | 6,772 files / 11.45 GB with SHA-256 |
| raw ASTER archived | 7 scenes + XML, `raw/aster/<date>/manifest.json` |

## Still open (needs an external action)

| item | who |
|---|---|
| push to GitHub (credentials) | **you** — see `docs/GITHUB_SETUP.md` |
| Zenodo DOI (after the push) | **you** |
| JSTARS/C&G two-column template | needs the official template file |
| CRediT / conflict of interest / funding text | me, but **funding text from you** |
| measured AEM section | does not exist at this site — stated in the paper |

## Scientific limits, stated in the paper

One survey; ASTER is 2006 against radiometrics of 2019–2020; emissivity from a
normalisation TES rather than a full temperature–emissivity separation; the
geological target is substrate, not alteration or mineralisation; the EM section
is synthetic; the information test uses a linear classifier on raw channels.
