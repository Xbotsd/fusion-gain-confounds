# Submission package — International Journal of Remote Sensing

Target: ***International Journal of Remote Sensing*** (Taylor & Francis) — the
chosen venue after *Computers & Geosciences* rejected the paper on scope
(2026-11-22). IJRS is hybrid: the subscription route carries **no APC and no page
charges**, and the journal explicitly covers remote-sensing methods and
applications.

The previous C&G submission (manuscript CAGEO-D-26-02178) and its two returns are
documented in [SUBMISSION_RECORD.md](SUBMISSION_RECORD.md); the C&G-specific
walkthrough and checklist are kept as historical files.

## Ready-to-upload set

`python code/make_submission_package.py` rebuilds `upload/` and
`upload_manifest.json` from the canonical sources; `IJRS_submission_package.zip`
is a convenience copy (both are git-ignored).

| slot | file | size |
|---|---|---:|
| Cover letter | `Cover_Letter.docx` | 38 KB |
| Main document | `Manuscript.docx` | 9.3 MB |
| Supplementary material | `Supplementary_Material.docx` | 37 KB |
| Graphical abstract (optional) | `Graphical_Abstract.png` | 149 KB |
| Figure 1–6 | `figures/figure01..06.png` | 0.1–5.0 MB each |

No highlights file is required by IJRS. Keywords and figure captions are entered
in the form from `keywords.txt` and `figure_captions.txt`.

## Checked

`python code/check_submission.py` → **29 checks, 0 failed**:

| requirement | state |
|---|---|
| In-text citations author–date, no comma before year | 35 citation groups |
| Reference list | 39 entries, alphabetical, all authors named, article titles quoted, full journal titles |
| Every reference cited, every citation referenced | no orphan either way |
| Abstract ≤ 250 words | 235 |
| Keywords | 6 |
| Sections | Abstract, Code availability, Declarations, References; Disclosure statement present |
| Layout | 8 tables, 6 figures, double spacing, continuous line numbers, table rows and captions kept together |
| Package | 10 files, hashes match the sources |

## What changed for this venue

* **New references.** 39 entries, of which **16 are 2019–2026** works on multimodal
  fusion, ASTER and hyperspectral mapping, prospectivity uncertainty and
  reproducibility. The previous list stopped at 2016 — the C&G editor called the
  current literature "completely missing", and that criticism was fair.
* **§2 rewritten** around that literature: single-modality state of the art,
  fusion methods (2019–2024), evaluation/uncertainty/reproducibility, and the gap
  the paper fills.
* **Taylor & Francis style**: `(Author Year)` in text and
  `Surname, I. N., and I. N. Surname. Year. “Title.” Journal Vol (Issue): pages.`
  in the list.
* **Highlights removed** (not used by IJRS); **Competing interests** renamed
  **Disclosure statement**, as T&F requires.
* Cover letter rewritten for the IJRS readership.

## Status and remaining items

1. **Portal.** IJRS uses ScholarOne, not Editorial Manager: create the account at
   the journal's "Submit an article" link, then upload the set above.
2. **ORCID** 0009-0002-3231-0444 and affiliation go in the author step.
3. **Data availability.** The manuscript carries the Zenodo DOI and the repository
   link; if ScholarOne asks for a statement, paste the same text.
4. **No fee.** Choose the subscription route; do not select Open Select / OA.
5. **Confirm** the journal's current Guide for Authors for anything ScholarOne
   requires beyond this set (e.g. a separate title page).
