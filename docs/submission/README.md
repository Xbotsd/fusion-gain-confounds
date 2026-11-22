# Submission package — Natural Resources Research

Target: ***Natural Resources Research*** (Springer, official journal of the
International Association for Mathematical Geosciences). Hybrid journal: the
subscription route carries **no APC**. Chosen after *Computers & Geosciences*
rejected the paper on scope (2026-11-22) and after a check of the metrics showed
*International Journal of Remote Sensing* to be a weaker venue than expected.

Submission is through Springer's **Editorial Manager**:
https://www.editorialmanager.com/narr/default.aspx

## Ready-to-upload set

`python code/make_submission_package.py` rebuilds `upload/` and
`upload_manifest.json` from the canonical sources; `NRR_submission_package.zip`
is a convenience copy (both are git-ignored).

| slot | file | size |
|---|---|---:|
| Cover letter | `Cover_Letter.docx` | 38 KB |
| Manuscript | `Manuscript.docx` | 9.3 MB |
| Supplementary material | `Supplementary_Material.docx` | 37 KB |
| Graphical abstract (optional) | `Graphical_Abstract.png` | 149 KB |
| Figure 1–6 | `figures/figure01..06.png` | 0.1–5.0 MB each |

Keywords and figure captions are entered in the form from `keywords.txt` and
`figure_captions.txt`.

## Checked

`python code/check_submission.py` → **28 checks, 0 failed**:

| requirement | state |
|---|---|
| APA 7 in-text citations (Author, Year) | 36 citation groups |
| Reference list | 39 entries, alphabetical, year in parentheses after authors, `&` before the last author, 30 DOIs as full links |
| Every reference cited, every citation referenced | no orphan either way |
| Abstract 150–250 words | 249 |
| Keywords 4–6 | 6 |
| Statements and Declarations | Competing Interests, Data Availability, Funding, CRediT, generative-AI declaration |
| Code availability | seven fields, repository and archived DOI |
| Layout | line numbers, page numbers in the footer, 8 tables, 6 figures, double spacing |
| Package | 10 files, hashes match the sources |

## What changed for this venue

* **Reframed as mineral prospectivity research.** The abstract opens on
  prospectivity mapping and the introduction positions the work inside that
  literature; the benchmark is presented as a control for multimodal
  prospectivity maps, which is what NRR publishes.
* **APA 7 references** (39 entries, 16 of them 2019–2026), journal names
  italicised, DOIs as full links.
* **Statements and Declarations** section in Springer's form, with a Data
  Availability statement added.
* **Page numbers** added to the footer (Springer requires them alongside the line
  numbers).
* Cover letter rewritten for the NRR readership.

## Status and remaining items

1. Create the account at the Editorial Manager link above (ORCID
   0009-0002-3231-0444), choose the research-paper article type.
2. Upload the set; the manuscript already carries line numbers and page numbers.
3. Complete the declarations in the system exactly as in the manuscript.
4. **No fee**: do not select Open Choice.
5. Confirm the current Guide for Authors for anything the system requires beyond
   this set.
