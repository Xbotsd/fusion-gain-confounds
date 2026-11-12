# Publication readiness — real-ASTER main line

Date: 2026-11-10; maintenance pass 2026-11-12. Every number below is from a command, not recall.

## Verdict

| layer | verdict |
|---|---|
| Framework | **complete** — 53 artefacts, 22 invariants, 0 coverage orphans, 36 unit assertions (9 test groups) |
| Functional coverage | **complete for the manuscript**; the legacy synthetic branch is labelled and optional |
| Data reality | gamma, ASTER TIR, TMI and geology are real; **EM is synthetic and cannot be otherwise** |
| Manuscript | rewritten around the new evidence, 9 tables, 6 figures, IEEE-style references |
| Archive | **published** — Zenodo 10.5281/zenodo.24130421, version 1.0.0; file checksum and contents re-verified 2026-11-12 |

## What changed and why it matters

The thermal infrared is now **real ASTER data on the main line** (5 bands, 90 m,
2006-10-18, archived offline with SHA-256). The synthetic splib07 cube survives
only as a control. That alone removes the largest reviewer objection.

More importantly, two controls changed the paper's claim:

1. **Conditioning control.** Appending five inert channels with the ASTER rows of
   `H` recovers 69-98 % of the fused F1 gain (0.614 for all-zero channels, 0.649
   for Gaussian noise, 0.652 for the real cube) and a geological AUC at least as
   high (0.919 and 0.922 against 0.913). Gamma alone has rank 3 of 5, so the
   inversion is underdetermined and any channel helps by regularising it.
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
| cross-artefact invariants | **22/22** |
| unit assertions | **36/36 in 9 test groups** |
| coverage orphans | **0** |
| manifest | **6,842 files / 11.46 GB**, SHA-256 for every file (`processed/data_manifest.json`) |
| raw ASTER archived | 7 scenes + XML, `raw/aster/<date>/manifest.json` |

## Still open (needs an external action)

| item | state |
|---|---|
| push to GitHub | **done** 2026-11-10 — see `docs/GITHUB_SETUP.md` |
| Zenodo DOI | **done** 2026-11-11 — version 1.0.0; checksum verified 2026-11-12 |
| `remote-sensing` community inclusion | request open since 2026-11-11; the record shows the community only after a curator accepts |
| ESI/Springer template | needs the official template file; the double-spaced review copy is ready |
| generative-AI declaration | **author decision** — Elsevier requires it when generative AI was used |
| journal submission | **not submitted**; the DOI identifies the software, not a publication |

## Scientific limits, stated in the paper

One survey; ASTER is 2006 against radiometrics of 2019–2020; emissivity from a
normalisation TES rather than a full temperature–emissivity separation; the
geological target is substrate, not alteration or mineralisation; the EM section
is synthetic; the information test uses a linear classifier on raw channels.
