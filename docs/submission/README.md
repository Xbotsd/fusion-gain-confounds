# Submission package — checks against the journal's requirements

Target: *Computers & Geosciences* (Elsevier), confirmed on 2026-11-12 as the
best free option (subscription route, no APC); fallbacks are Earth Science
Informatics and Journal of Applied Geophysics, see `../JOURNAL_SHORTLIST.md`.
**Caveat:** the live Guide for
Authors could not be retrieved from this machine (ScienceDirect answers HTTP 403
to scripted requests), so the list below was checked against Elsevier's standard
article requirements, not against the current journal-specific text. Re-check
items marked *(confirm)* on the Guide for Authors page before uploading.

## Files in this folder

| file | what it is |
|---|---|
| `../Manuscript_v2_draft.docx` | the manuscript: title page, abstract, 6 keywords, 9 tables, 6 figures, continuous line numbers, double spacing |
| `highlights.txt` | 5 bullets, 70-77 characters each (limit 85, up to 5) |
| `keywords.txt` | the 6 keywords, one line |
| `figure_captions.txt` | the six captions, numbered to match `figures/` |
| `figures/figure01..06.*` | the six figures as separate files, 300 dpi (except note below) |
| `../COVER_LETTER.md` | cover letter |
| `../graphical_abstract.png` | graphical abstract (optional for this journal) |
| `../CITATION.cff`, `../.zenodo.json` | archive metadata for the DOI |

## Checked

| requirement | state |
|---|---|
| Abstract ≤ 250 words | 247 (whitespace count) |
| Highlights: ≤ 5 bullets, ≤ 85 characters each | 5 bullets, max 77 |
| Keywords ≤ 6 | 6 |
| Double-spaced text with line numbers | yes (2.0, continuous) |
| Tables as editable text, not images | 9 native Word tables |
| Figures numbered in citation order, each with a caption | 6, order verified |
| Figure resolution ≥ 300 dpi | 300 dpi; `figure04` is 5100 px wide so it stays above 300 dpi at printed width |
| References numbered, every entry cited | 24 entries, all cited; IEEE numeric style *(confirm the journal still asks for numbered)* |
| Title page: title, author, affiliation, corresponding e-mail | present |
| CRediT author statement | present |
| Declaration of competing interests | present |
| Funding statement | present (none) |
| Acknowledgements and data-source credits | present |
| Data availability statement | present (repository, MIT licence, Zenodo DOI 10.5281/zenodo.24130421) |
| Cover letter | present, numbers rewritten against the current results |
| Generative-AI declaration | **not added — author decision** (Elsevier requires it when generative AI was used) |

## Still to do before upload

1. **Generative-AI declaration.** Elsevier requires a statement when generative
   AI was used in the writing process. If applicable, add a short section before
   the references, for example: "During the preparation of this work the author
   used a large language model to draft and edit text and code; the author
   reviewed and verified all content and takes full responsibility for the
   publication." Tell me and I will insert it verbatim into the manuscript and
   the `.docx`.
2. **Repository DOI — done.** https://doi.org/10.5281/zenodo.24130421 (version 1.0.0), concept
   https://doi.org/10.5281/zenodo.24130420. The manuscript, `CITATION.cff` and README carry it.
3. **Confirm three journal-specific points** on the Guide for Authors: reference
   style (numbered vs author-date), whether the graphical abstract is mandatory,
   and whether a separate title-page file is required (this package keeps the
   title page inside the manuscript).
