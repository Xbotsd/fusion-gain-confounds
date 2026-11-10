# Reference audit

The automatic Crossref query (`code/verify_references.py`) is **not reliable
enough for final citations**: several queries matched unrelated papers or book
chapters. The raw auto-match table was therefore discarded; this file is the
manual audit to use before submission.

Status legend: **OK** = DOI/title checked; **BOOK** = book DOI, check edition;
**MANUAL** = no reliable DOI, verify volume/pages in the publisher or library.

| # | citation | status | note |
|---:|---|---|---|
| 1 | IAEA, Guidelines for radioelement mapping using gamma ray spectrometry data, IAEA-TECDOC-1363, 2003 | MANUAL | IAEA reports usually have no DOI; verify TECDOC number |
| 2 | Minty, Fundamentals of airborne gamma-ray spectrometry, AGSO J. 17(2), 1997 | MANUAL | AGSO journal, no DOI |
| 3 | Wilford et al., AGSO J. 17(2), 1997 | MANUAL | same issue as [2] |
| 4 | Dickson & Scott, AGSO J. 17(2), 1997 | MANUAL | same issue as [2] |
| 5 | Fountain, Exploration Geophysics 29, 1998 | OK | DOI 10.1071/EG998001 |
| 6 | Siemon et al., J. Appl. Geophys. 67, 2009 | OK | DOI 10.1016/j.jappgeo.2007.11.003 |
| 7 | Dentith & Mudge, Geophysics for the Mineral Exploration Geoscientist, CUP 2014 | BOOK | DOI 10.1017/CBO9781139024358 |
| 8 | Christensen et al., JGR Planets 105, 2000 | OK | DOI 10.1029/1998JE000624 |
| 9 | Salisbury et al., Infrared Spectra of Minerals, 1991 | BOOK | DOI 10.1180/mono-4 |
| 10 | Ramsey & Christensen, JGR Solid Earth 103, 1998 | OK | DOI 10.1029/97JB02784 |
| 11 | Kalman, J. Basic Eng. 82, 1960 | OK | DOI 10.1115/1.3662552 |
| 12 | Maybeck, Stochastic Models, Estimation and Control, 1979 | MANUAL | book, ISBN; no DOI |
| 13 | Bar-Shalom et al., Estimation with Applications..., Wiley 2001 | BOOK | DOI 10.1002/0471221279 |
| 14 | Julier & Uhlmann, ACC 1997 | OK | DOI 10.1109/ACC.1997.609105 |
| 15 | Sun et al., AAAI 2016 | OK | DOI 10.1609/aaai.v30i1.10306 |
| 16 | Wilkinson et al., Scientific Data 3, 2016 | OK | DOI 10.1038/sdata.2016.18 |
| 17 | Peng, Science 334, 2011 | OK | DOI 10.1126/science.1213847 |
| 18 | Powers, J. Machine Learning Technologies 2(1), 2011 | MANUAL | journal; check pages 37–63 |
| 19 | Reeves, Aeromagnetic Surveys, Geosoft 2005 | MANUAL | technical book, no DOI |
| 20 | Nabighian (ed.), Electromagnetic Methods in Applied Geophysics, SEG 1988 | BOOK | DOI 10.1190/1.9781560802631 |
| 21 | Telford et al., Applied Geophysics, CUP 1990 | BOOK | DOI 10.1017/CBO9781139167932 |
| 22 | Hook et al., in Remote Sensing for the Earth Sciences, 1999 | MANUAL | chapter; verify pages |
| 23 | Gnojek & Prichystal, Geoexploration 23, 491–502, 1985 | **OK** | DOI 10.1016/0016-7142(85)90076-6 (Crossref-verified 2026-11-07). The draft's "1995, 33(1–3), 99–113" was wrong — year, volume and pages corrected |
| 24 | Kruse et al., Remote Sens. Environ. 44, 145–163, 1993 | **OK** | DOI 10.1016/0034-4257(93)90013-N (Crossref-verified 2026-11-07). Added because §7.10 and Table 12 cite SAM on TIR and the work was missing from the list |

## Verification trail (2026-11-07, Crossref + publisher pages)

- **Gnojek & Prichystal — CORRECTED**: Crossref returns 10.1016/0016-7142(85)90076-6,
  Geoexploration **23, 491–502, December 1985** ("northern Moravia
  (Czechoslovakia)"). The draft cited 1995/33(1–3)/99–113 — all three fields
  wrong. Fixed in the draft and in `PUBLISHED_BASELINES.md`.
- **AGSO Journal 17(2) 1997 special issue** (Minty; Wilford et al.; Dickson &
  Scott): queried Crossref by full title — **not indexed, no DOI exists**.
  The papers are standard literature; pages must be confirmed in a library
  (Geoscience Australia holds the series). Status stays MANUAL.
- **Bedini 2009** and **Macnae 2016 (ASEG abstract)**: not found in Crossref
  by title/author queries after repeated attempts, and both are poorly
  documented (conference abstract / unindexed journal). **Both were removed from
  the reference list on 2026-11-07**, and neither is cited in the body, so no
  in-text change was needed. The list went from 25 to 24 entries, with Kruse et
  al. 1993 added to fill the SAM citation that §7.10 and Table 12 make.
- **Kruse et al. 1993 — ADDED**: `Remote Sensing of Environment` 44(2–3),
  145–163, DOI 10.1016/0034-4257(93)90013-N, Crossref-verified. The draft cited
  "Kruse et al. 1993" for the Spectral Angle Mapper without listing it.
- **IAEA TECDOC-1363 (2003)**: IAEA reports carry no DOIs; the document is a
  standard reference (catalogue under TECDOC series). Cite as
  *IAEA-TECDOC-1363, Vienna, 2003*; no further verification possible online.
- **Powers 2011**: *Journal of Machine Learning Technologies* 2(1) is not in
  Crossref; the citation (37–63) circulates consistently but stays MANUAL.
- **Maybeck 1979 / Reeves 2005 / Hook 1999**: books/chapters without DOIs for
  these editions; keep MANUAL with ISBN/publisher.

## Updated counts

- Total entries in the reference list: **24**
- DOI-verified: **11** (9 previous + Gnojek corrected + Kruse added)
- Books with DOI: 5
- MANUAL: **8** entries — IAEA 2003, Minty 1997, Wilford 1997, Dickson & Scott
  1997, Maybeck 1979, Powers 2011, Reeves 2005, Hook 1999. All are standard,
  widely cited sources with stable bibliographic details; none is a conference
  abstract. Three of them share one AGSO Journal 17(2) 1997 special issue that
  is confirmed to be unindexed (no DOI exists for the issue).
- Removed as unverifiable: **Bedini 2009, Macnae 2016** (executed 2026-11-07;
  neither was cited in the body, so the text is unchanged).

## What to do

1. For **OK/BOOK** entries, copy the DOI into the reference list and check the
   edition/year.
2. For **MANUAL** entries, use the publisher/library record; do not invent a DOI.
3. Replace the draft's candidate list with the checked entries before
   submission.
4. If a reference cannot be verified, remove it rather than risk a wrong
   citation. **Done for Bedini 2009 and Macnae 2016.**

## Citation coverage (executed 2026-11-07)

The body uses IEEE-style numeric markers. Before this pass, 19 of the 25 entries
were never cited and one cited work (Kruse et al. 1993) was not in the list.
Both problems are fixed; every entry 1–24 now has at least one marker, and no
marker lacks an entry:

| body citation | marker | list entry | status |
|---|---|---|---|
| gamma ratios as alteration indices | [1–4,21] | 1–4, 21 | IAEA / AGSO / Telford |
| EM systems and inversion | [5–7,20,21] | 5–7, 20, 21 | Fountain, Siemon, Nabighian, Telford |
| TIR spectroscopy | [8–10,22] | 8–10, 22 | Christensen, Salisbury, Ramsey, Hook |
| fusion approaches | [11–14] | 11–14 | Kalman, Maybeck, Bar-Shalom, Julier |
| domain adaptation (CORAL) | [15] | 15 | Sun et al. |
| reproducibility | [16,17] | 16, 17 | Wilkinson (FAIR), Peng |
| metric definitions | [18] | 18 | Powers |
| aeromagnetic/TMI grid | [19] | 19 | Reeves |
| SAM on TIR | [24] | 24 | Kruse et al. |
| F-parameter | [23] | 23 | Gnojek & Prichystal |
| low eTh/K | [4] | 4 | Dickson & Scott |
| triad / IAEA practice | [1] | 1 | IAEA |

The bibliography was renumbered accordingly: Macnae 2016 and Bedini 2009 were
removed (see above), Kruse et al. 1993 took slot 24, and the list is contiguous
1–24 with no gaps.

## Why the automatic table is not used

Crossref's `query.bibliographic` returned, for example, a 2012 Resource Geology
paper for the IAEA TECDOC and a 1979 GSC report for Minty 1997. Those matches are
wrong. The script is useful for finding candidate DOIs, not for verification.
