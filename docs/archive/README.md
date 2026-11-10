# Archive — superseded round notes

Everything in this folder was written while the benchmark was being built and is
kept only as a record of how the conclusions were reached. **None of it is part
of the submission, and none of its numbers should be quoted.**

The documents that are current are, in reading order:

| file | what it is |
|---|---|
| `../README.md` | orientation and the one-command reproduction |
| `../RESULTS.md` | every headline number, with its artefact |
| `../SUPPLEMENTARY.md` | script inventory and the full results tables |
| `../DATA_PROVENANCE.md` | sources, licences, processing recipes |
| `../READINESS_AUDIT.md` | what is done, what is not, and the evidence |
| `../GAP_AUDIT.md` | known gaps and why they are not closed |
| `../MODEL_AUDIT.md` | model caveats |
| `../NORMALISATION_AUDIT.md` | the two normalisation bugs and their fix |
| `../REFERENCES_AUDIT.md` | bibliography state |
| `../CHANGELOG.md` | round-by-round history |
| `../JOURNAL_SHORTLIST.md`, `../COVER_LETTER.md`, `../GITHUB_SETUP.md` | submission logistics |
| `../Manuscript_v2_draft.md` / `.docx` | the manuscript |

Why the archived notes are stale, concretely:

* They predate the promotion of real ASTER thermal infrared to the main line, so
  they quote the synthetic-library branch (gamma+TIR F1 0.597, geological AUC
  0.905) instead of the real one (0.652 and 0.913).
* They predate the fix of the two normalisation bugs, so their fused scores for
  the same data differ by up to 0.2 F1.
* They predate the conditioning controls (zeros, noise, block-shuffled), the
  model-free multi-class test and the single shared block bootstrap, so they
  present fusion gains without the decomposition that the paper is about.
* `Manuscript_v2_draft.md.bak` is a snapshot before the structural rewrite.

Two of them are still useful as narrative rather than as numbers:
`PIPELINE_AUDIT.md` for the timing/throughput measurements and
`PAPER_VS_IMPLEMENTATION.md` for the list of claims that were removed because the
code did not support them.
