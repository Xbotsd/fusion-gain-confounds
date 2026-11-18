# Submission record — CAGEO-D-26-02178

**Journal:** Computers & Geosciences (Elsevier)
**Manuscript number:** CAGEO-D-26-02178
**Submitted:** 13 November 2026 (PDF built 2026-11-13 00:11 EST)
**Article type:** Research Paper · **Section/Category:** Remote sensing
**Corresponding author:** Yudong Xu, Heilongjiang University of Science and Technology
**Build:** `CAGEO-D-26-02178.pdf`, 39 pages — 31 pages of manuscript plus 8 attachment pages

This file is the post-submission record: what went out, what the built PDF shows,
which defects were found, and what is fixed in the repository versus what has to be
changed in Editorial Manager.

## 1. What was submitted

| Slot | File | In the built PDF |
|---|---|---|
| Manuscript | `Manuscript.docx` | pp. 6–31 |
| Cover letter | `Cover_Letter.docx` | p. 2 (body) + p. 3 (signature) |
| Declaration of competing interests | `Declaration_of_Competing_Interests.docx` | p. 4 |
| Highlights | `Highlights.docx` | p. 5 |
| figure01–06.png | `figures/` | pp. 32–37, as download links |
| Graphical_Abstract.png | `upload/` | p. 38, as a download link |
| Supplementary_Material.docx | `upload/` | p. 39, as a download link |

Metadata as registered: title, 235-word abstract, six keywords, one author with
ORCID, five highlights, data link `https://doi.org/10.5281/zenodo.24130421`,
no preprint (SSRN), no MethodsX co-submission.

## 2. Defects found in the built PDF

Severity: **A** = visible to the editor/reviewers and worth correcting now;
**B** = cosmetic but fixed in the repository for the next version;
**C** = advice only.

| # | Sev | Defect | Where | Status |
|---:|---|---|---|---|
| 1 | A | The six figures, the graphical abstract and the supplementary file were all registered with the item type **Supplementary Material**, so the built PDF lists them as download links (pp. 32–39) instead of typeset figures | Editorial Manager | **needs EM action** |
| 2 | A | Author affiliation line reads `Harbin, --- Select One --- CHINA` — the state/country selector was left unset | p. 1 | **needs EM action** |
| 3 | B | A stray bullet inside §7.3: a Markdown line starting with `-` was parsed as a list item, producing "…gives 0.354 / • no gain - and…" | p. 21 | fixed in repo |
| 4 | B | Table captions separated from their tables by a page break (Table 2 caption on p. 10, table on p. 11; Table 3 caption on p. 14, table on p. 15) | pp. 10–15 | fixed in repo |
| 5 | B | The abstract was split across pp. 6–7 | pp. 6–7 | fixed in repo |
| 6 | B | Three body paragraphs opened with "Table 4."/"Table 7."/"Table 8.", immediately before the real captions, so the PDF looked like it had two captions per table | pp. 18, 22, 24 | fixed in repo |
| 7 | B | Hyphens used as dashes ("0.913 - but", "block-shuffled - recovers") and hyphen ranges ("69-98 %") | throughout | fixed in repo |
| 8 | B | The reference note cited an internal file, "See `docs/REFERENCES_AUDIT.md`" | p. 29 | fixed in repo |
| 9 | B | The cover letter pushed its signature block onto a second page, leaving p. 3 almost blank | pp. 2–3 | fixed in repo (now 1 page) |
| 10 | C | Corresponding-author title shows "B.E. Candidate" | p. 1 | change in EM if desired |
| 11 | C | Reference list is IEEE-style; C&G sets Elsevier numbered style (year after authors) | pp. 29–31 | convert at revision |
| 12 | C | Highlights appear both as a separate file and inside the manuscript | pp. 5, 7 | optional to drop from manuscript |

## 3. What the fixes changed in the repository

* `docs/build_draft_docx.py` — a hyphen now starts a bullet only when it opens a
  list; table captions are italic, small and `keep_with_next`; table rows cannot
  break across pages and header rows repeat; figure images stay with their
  captions; a page break precedes the abstract, so the title page stands alone.
* `docs/Manuscript_v2_draft.md` — dashes corrected to en dashes, `69–98 %`
  ranges, the three "Table N." paragraph openings reworded, the internal
  `REFERENCES_AUDIT.md` pointer removed. No number, table or figure changed:
  the validator still reports 53/53 artefacts and 22/22 invariants, including
  "tables 4-8 equal the artefacts".
* `code/make_submission_package.py` — the cover letter is built with 2.2 cm
  margins and 4 pt paragraph spacing, so it fits one page (581 words, 1 page).
* Rebuilt `docs/Manuscript_v2_draft.docx`: 26 pages, 8 tables, 6 figures, 175
  paragraphs (the previous build had 424 one-line paragraphs).

## 4. Editorial Manager actions

1. **Author details** — `Edit Author Details` for Yudong Xu: set the state/country
   (`China`) so the `--- Select One ---` placeholder disappears, and change the
   title from "B.E. Candidate" to blank or a preferred title.
2. **File types** — if the submission still offers `Edit Submission`, change the
   item type of `figure01`–`figure06` to **Figure**, `Graphical_Abstract.png` to
   **Graphical Abstract** and keep only `Supplementary_Material.docx` as
   Supplementary Material.
3. If the submission is locked (With Editor / Under Review), send one short note
   to the editorial office listing the two items and asking them to update the
   record; include the manuscript number.

## 5. Pre-review return (2026-11-18)

The journal returned the submission **before review**, flagging one breach and
warning that a second failure means desk rejection:

> Reference Format — the reference list must be consistent, must name all
> authors, must not abbreviate journal titles, and in-text citations must be
> author–date (APSA/APA).

The repository requirement in the same notice (a functional repository with README
and documentation) was already met.

What was changed in response (Round 21 in `docs/CHANGELOG.md`):

| item | before | after |
|---|---|---|
| in-text citations | `[1–4,21]`, `[16,17]`, … | `(Dickson and Scott, 1997; IAEA, 2003; …)` |
| list style | IEEE numeric, year at the end | `Author, A.A., Author, B.B., Year. Title. Journal Volume, pages.` |
| authors | `Christensen, P.R., … et al.` | all named (Wilkinson 53, Christensen 8, Kruse 7, …) |
| journal titles | `AGSO J.`, `JGR` | full titles |
| table 8 references | `IAEA 2003` | `IAEA (2003)` |
| code | software paragraph inside Reproducibility | dedicated **Code availability** section with the template's fields |
| cover letter | repository mentioned | "details listed in the section *Code availability*" |

23 entries, 23 in-text keys, no orphan on either side. Two DOIs were corrected
(Fountain `10.1071/EG998001`; the Salisbury book has none) and one uncited entry
(Sun et al., 2016) was removed.

## 6. Resubmission (2026-11-18)

The corrected package was uploaded again and approved by the author on
**18 November 2026** under the same manuscript number, **CAGEO-D-26-02178**.

Uploaded: `Manuscript.docx` (author–date references, Code availability section,
46 scripts / nine stages), `Cover_Letter.docx` (cites the Code availability
section), `Highlights.docx`, `Declaration_of_Competing_Interests.docx`,
`figure01..06.png` as **Figure**, `Graphical_Abstract.png` as **Graphical
Abstract**, `Supplementary_Material.docx` as **Supplementary Material**.

Metadata fixed in Editorial Manager: author country set to China (the
`--- Select One ---` placeholder is gone); data-availability statement set to
"Other" with the Zenodo DOI and the GitHub repository; preprint service declined;
section/category *Remote sensing* with the method and remote-sensing
classifications.

A note to the publication office lists the three corrections and states that all
reported results and numeric values are unchanged (verified: all 223 numeric
values of the first submission are still present).

## 7. Status and next step

* The PDF states `--Manuscript Draft--`: the first submission was returned at
  pre-review on 2026-11-18; the corrected files in `upload/` are the resubmission. Nothing in the repository changes the submitted record by itself.
* Everything in §3 is staged for the **revision** (or for a fresh submission if
  the paper is declined). Before any resubmission: rebuild with
  `python code/make_submission_package.py`, re-render, and check pagination again
  with `docs/submission/SUBMISSION_GUIDE.md` §6.
* The scientific content is unchanged between the submitted files and the
  repository HEAD except for the typographic fixes listed above.
