# Submission package — checks against the journal's requirements

Target: *Computers & Geosciences* (Elsevier) — final choice (2026-11-12): free
subscription route (no APC, no page charges), JCR Q1 / 中科院 地球科学 2 区, and
the best scope match for a benchmark + software + audit paper
(`../JOURNAL_SHORTLIST.md`). Earth Science Informatics is the fallback if the
C&G decision comes back negative. **Caveat:** the live C&G Guide for Authors
could not be retrieved from this machine (ScienceDirect answers HTTP 403 to
scripted requests), so the list below was checked against Elsevier's standard
article requirements, not the current journal-specific text. Re-check items
marked *(confirm)* before uploading.

## Step-by-step guide

`SUBMISSION_GUIDE.md` is the operating manual: official links (journal home,
Guide for Authors, Editorial Manager), registration, field-by-field entry of the
title/abstract/keywords/authors, the upload-slot order, the PDF check and the
usual pitfalls. `paste_fields.txt` holds the exact text to paste into the form.

## Ready-to-upload set

`python code/make_submission_package.py` rebuilds `upload/` and
`upload_manifest.json` from the canonical files every time it runs, so the upload
cannot drift from the manuscript. `CG_submission_package.zip` holds the same 12
files (git-ignored, as are the copies under `upload/`; rebuild with the script).

| Editorial Manager slot | file in `upload/` | size |
|---|---|---:|
| Cover Letter | `Cover_Letter.docx` | 40 KB |
| Manuscript (Word) | `Manuscript.docx` | 9.3 MB |
| Highlights | `Highlights.docx` | 40 KB |
| Declaration of competing interests | `Declaration_of_Competing_Interests.docx` | 40 KB |
| Figure 1–6 | `figures/figure01..06.png` | 0.1–5.0 MB each |
| Graphical Abstract | `Graphical_Abstract.png` | 0.15 MB |
| Supplementary Material | `Supplementary_Material.docx` | 40 KB |

The figures are RGB (alpha flattened to white) at 300 dpi. `upload_manifest.json`
records the byte size and SHA-256 of every file. Keywords and figure captions are
entered in the form from `keywords.txt` and `figure_captions.txt`. The manuscript
still contains the Highlights section for reading; the separate file is the one
the journal uses.

## Files in this folder

| file | what it is |
|---|---|
| `../Manuscript_v2_draft.docx` | the manuscript: title page, abstract, 6 keywords, 8 tables, 6 figures, continuous line numbers, double spacing |
| `../Supplementary_Tables.docx` | supplementary Table S1 (thermal-retrieval sensitivity), referenced from §7.6 |
| `highlights.txt` / `highlights.docx` | 5 bullets, 70-77 characters each (limit 85, up to 5) |
| `declaration_of_competing_interests.docx` | required separate Word file: no competing interests |
| `keywords.txt` | the 6 keywords, one line |
| `figure_captions.txt` | the six captions, numbered to match `figures/` |
| `figures/figure01..06.png` | the six figures as separate files, 300 dpi, RGB |
| `../COVER_LETTER.md` / `cover_letter.docx` | cover letter, dated and addressed to the C&G editor |
| `../graphical_abstract.png` | graphical abstract (optional for this journal), copied and flattened into `upload/` |
| `../CITATION.cff`, `../.zenodo.json` | archive metadata for the DOI |
| `upload/`, `upload_manifest.json`, `CG_submission_package.zip` | the ready-to-upload set and its checksums |
| `SUBMISSION_GUIDE.md` | step-by-step Editorial Manager walkthrough and links |
| `paste_fields.txt` | title, authors, abstract, keywords and highlights ready to paste |

## Checked

| requirement | state |
|---|---|
| Abstract ≤ 250 words | 247 (whitespace count) |
| Highlights: ≤ 5 bullets, ≤ 85 characters each | 5 bullets, max 77 |
| Keywords ≤ 6 | 6 |
| Double-spaced text with line numbers | yes (2.0, continuous) |
| Tables as editable text, not images | 8 native Word tables + 1 supplementary Word table |
| Figures numbered in citation order, each with a caption | 6, order verified |
| Figure resolution ≥ 300 dpi | 300 dpi; `figure04` is 5100 px wide so it stays above 300 dpi at printed width |
| References numbered, every entry cited | 24 entries, all cited; consistent numeric style (Elsevier accepts any consistent style at submission and restyles at proof) *(confirm)* |
| Title page: title, author, affiliation, corresponding e-mail | present |
| CRediT author statement | present |
| Declaration of competing interests | present |
| Funding statement | present (none) |
| Acknowledgements and data-source credits | present |
| Data availability statement | present (repository, MIT licence, Zenodo DOI 10.5281/zenodo.24130421) |
| Cover letter | present, numbers rewritten against the current results |
| Generative-AI declaration | **present** — added to the Declarations section on 2026-11-12 |

## Status and remaining items

1. **Generative-AI declaration — done (2026-11-12).** A declaration naming the
   large language model used for drafting, code and analysis, and stating that the
   author reviewed and verified all content, sits in the Declarations section.
2. **Repository DOI — done.** https://doi.org/10.5281/zenodo.24130421 (version 1.0.0), concept
   https://doi.org/10.5281/zenodo.24130420. The manuscript, `CITATION.cff` and README carry it.
3. **Software availability — done.** Named software, version, MIT licence, repository,
   archive DOI, environment and reproduction command are in the manuscript.
4. **Table S1 — moved out of the main text.** Upload `Supplementary_Tables.docx`
   with the submission; §7.6 points to it. The main text now has 8 tables.
5. **Confirm journal-specific points** on the C&G Guide for Authors: whether the
   graphical abstract is mandatory, whether a separate title page is required (this
   package keeps it inside the manuscript), and whether the Highlights file should
   be uploaded separately or pasted into the submission form.
