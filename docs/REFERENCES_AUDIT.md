# Reference audit

The automatic Crossref query (`code/verify_references.py`) is **not reliable
enough for final citations**: several queries matched unrelated papers or book
chapters. The raw auto-match table was therefore discarded; this file is the
manual audit to use before submission.

**Style (changed 2026-11-18).** *Computers & Geosciences* requires author–date
citations and rejects numeric ones at pre-review; the list below was rebuilt in
the style of the journal's Word template
(`Author, A.A., Author, B.B., Year. Title. Journal Volume, pages.`). Every entry
names **all** authors and gives **full** journal titles. Do not reintroduce
numeric markers.

Status legend: **OK** = DOI/title checked; **BOOK** = book DOI, check edition;
**MANUAL** = no reliable DOI, verify volume/pages in the publisher or library.

## Current list: 23 entries, alphabetical

| entry | year | status | DOI |
|---|---:|---|---|
| Bar-Shalom, Li, Kirubarajan — Estimation with applications to tracking and navigation | 2001 | BOOK | 10.1002/0471221279 |
| Christensen et al. (8 authors) — thermal emission spectral library | 2000 | OK | 10.1029/1998JE000624 |
| Dentith & Mudge — Geophysics for the mineral exploration geoscientist | 2014 | BOOK | 10.1017/CBO9781139024358 |
| Dickson & Scott — aerial gamma-ray surveys | 1997 | MANUAL | — (AGSO Journal 17(2), unindexed) |
| Fountain — airborne EM systems, 50 years | 1998 | OK | 10.1071/EG998001 |
| Gnojek & Přichystal — zinc mineralisation, northern Moravia | 1985 | OK | 10.1016/0016-7142(85)90076-6 |
| Hook et al. (5 authors) — multispectral TIR in geological studies | 1999 | MANUAL | — (book chapter; page range 59–110 from the standard citation, not independently verified) |
| IAEA — guidelines for radioelement mapping (TECDOC-1363) | 2003 | MANUAL | — (agency report) |
| Julier & Uhlmann — non-divergent estimation | 1997 | OK | 10.1109/ACC.1997.609105 |
| Kalman — linear filtering and prediction | 1960 | OK | 10.1115/1.3662552 |
| Kruse et al. (7 authors) — SIPS | 1993 | OK | 10.1016/0034-4257(93)90013-N |
| Maybeck — Stochastic models, estimation, and control | 1979 | MANUAL | — (book) |
| Minty — airborne gamma-ray spectrometry | 1997 | MANUAL | — (AGSO Journal 17(2), unindexed) |
| Nabighian (Ed.) — Electromagnetic methods in applied geophysics | 1988 | BOOK | 10.1190/1.9781560802631 |
| Peng — reproducible research | 2011 | OK | 10.1126/science.1213847 |
| Powers — precision, recall, F-measure, ROC | 2011 | MANUAL | — (journal not in Crossref) |
| Ramsey & Christensen — mineral abundance determination | 1998 | OK | 10.1029/97JB02784 |
| Reeves — Aeromagnetic surveys | 2005 | MANUAL | — (technical book) |
| Salisbury et al. (4 authors) — infrared spectra of minerals | 1991 | MANUAL | — (book; the Mineralogical Society DOI belongs to a different 1974 volume) |
| Siemon, Auken & Christiansen — laterally constrained inversion | 2009 | OK | 10.1016/j.jappgeo.2007.11.003 |
| Telford, Geldart & Sheriff — Applied geophysics | 1990 | BOOK | 10.1017/CBO9781139167932 |
| Wilford, Bierwirth & Craig — gamma-ray spectrometry in regolith mapping | 1997 | MANUAL | — (AGSO Journal 17(2), unindexed) |
| Wilkinson et al. (53 authors) — FAIR guiding principles | 2016 | OK | 10.1038/sdata.2016.18 |

Counts: **23 entries**, **14 with a DOI**, **9 without** (three books, one chapter,
one agency report, three AGSO Journal 1997 papers, one unindexed journal).

## Changes made on 2026-11-18 (pre-review return)

* **Numeric → author–date.** All eight in-text marker groups were rewritten, e.g.
  `[1–4,21]` became `(Dickson and Scott, 1997; IAEA, 2003; Minty, 1997; Telford et
  al., 1990; Wilford et al., 1997)`.
* **Table 8's reference column** now reads `IAEA (2003)`, `Gnojek and Přichystal
  (1985)` and so on.
* **All authors named.** `et al.` was removed from the list itself: Christensen
  (8 names), Hook (5), Kruse (7), Wilkinson (53), Salisbury (4), Siemon (3),
  Telford (3), Wilford (3), Bar-Shalom (3).
* **Full journal titles.** `AGSO J.` → *AGSO Journal of Australian Geology and
  Geophysics*; `JGR` → *Journal of Geophysical Research: Planets* / *: Solid
  Earth*; `Remote Sens. Environ.` → *Remote Sensing of Environment*.
* **Two DOIs corrected.** Fountain 1998 is `10.1071/EG998001` (the audit's
  `EG980001` resolved to an unrelated 1980 paper); the Salisbury 1991 book has no
  DOI (the `10.1180/mono-4` DOI belongs to *The Infrared Spectra of Minerals*,
  Mineralogical Society, 1974, edited by Farmer).
* **One entry removed, two newly cited.** Sun et al. (2016) was in the list but
  cited nowhere after the manuscript rewrite; it was dropped. Powers (2011) and
  Reeves (2005) were also uncited and are now cited where they belong (metric
  definitions in §4.4; the TMI grid in §3.4).
* **Result:** 23 entries, 23 in-text keys, no uncited entry, no dangling citation.

## Verification trail (2026-11-07, Crossref + publisher pages)

- **Gnojek & Přichystal 1985** — Crossref returns 10.1016/0016-7142(85)90076-6,
  *Geoexploration* **23, 491–502**, December 1985. The draft had cited
  1995/33(1)/99–113; all three fields were wrong and are fixed.
- **AGSO Journal 17(2) 1997 special issue** (Minty; Wilford et al.; Dickson &
  Scott): not indexed in Crossref, no DOI exists. Pages were confirmed against
  the standard citations and stay MANUAL.
- **Bedini 2009** and **Macnae 2016**: unverifiable (conference abstract /
  unindexed journal) and uncited; removed on 2026-11-07.
- **Kruse et al. 1993** — added to support the SAM citation, Crossref-verified.
- **IAEA TECDOC-1363 (2003)** — agency reports carry no DOI; cite as
  *IAEA-TECDOC-1363, Vienna*.
- **Powers 2011** — *Journal of Machine Learning Technologies* 2(1) is not in
  Crossref; the citation (37–63) stays MANUAL.

## What to do at proof stage

1. For **OK/BOOK** entries, check the DOI resolves and the edition/year matches.
2. For **MANUAL** entries, use the publisher or library record; never invent a DOI.
3. If a reference cannot be verified, remove it rather than risk a wrong citation.
