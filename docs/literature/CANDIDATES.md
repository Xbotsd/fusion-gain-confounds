# Current-literature plan (after the CAGEO desk rejection)

The Editor-in-Chief rejected CAGEO-D-26-02178 on scope and added a second,
substantive criticism:

> "I think a journal on remote sensing specifically would be better, note however,
> that you also need to consider searching for current literature on the topic,
> this is at present completely missing."

Both points are correct as stated:

* **Scope.** C&G is a computational-geoscience methods journal; this paper is a
  remote-sensing data-fusion study. The journal's own scope statement does not
  cover it.
* **Literature.** The submitted list has 23 entries and **nothing published after
  2016**: it is a methods lineage (Kalman 1960, Telford 1990, IAEA 2003) with no
  engagement with the 2019–2026 literature on multimodal fusion, ASTER mapping,
  prospectivity uncertainty or reproducibility. That is indefensible in 2026 and
  would have been raised by any reviewer.

## 1. Where to send it instead

The editor's suggestion (a remote-sensing journal) plus the no-APC constraint
leaves these free (subscription-route) options, verified with OpenAlex on
2026-11-22:

| journal | publisher | OA status (verified) | IF approx. | fit | note |
|---|---|---|---:|---|---|
| **International Journal of Remote Sensing** | Taylor & Francis | hybrid, `is_oa=false`, no APC | 2.8–3.4 | **best** — general remote sensing, accepts methods/benchmarks | no page charges expected; confirm colour |
| Remote Sensing Applications: Society and Environment | Elsevier | hybrid, APC optional | ~5 | good if framed as an application | scope is applications, not methods |
| Journal of Applied Remote Sensing | SPIE | hybrid, `is_oa=false` | ~1.8 | safe fallback | check SPIE page charges |
| ISPRS J. Photogrammetry and Remote Sensing | Elsevier | hybrid, no APC | ~12 | too selective for a benchmark | — |

Not free any more: IEEE JSTARS (fully OA), IJAEOG (fully OA), Geocarto
International (fully OA), Canadian Journal of Remote Sensing (fully OA).

**Recommendation: International Journal of Remote Sensing.** Free subscription
route, Q2, explicitly covers remote-sensing methods and applications, and the
paper's benchmark/negative-result framing fits its readership better than C&G.

## 2. The 16 recent references to add (verified DOIs)

Grouped by the section each would strengthen. Metadata pulled from OpenAlex on
2026-11-22; author lists and pagination must be completed from Crossref when the
entries are written.

### 2.2 Multimodal fusion (methods lineage 2019–2024)

| year | reference | DOI |
|---:|---|---|
| 2019 | Ghamisi et al., *Multisource and multitemporal data fusion in remote sensing: a comprehensive review*, IEEE Geoscience and Remote Sensing Magazine | 10.1109/mgrs.2018.2890023 |
| 2020 | Du & Zare, *Multiresolution multimodal sensor fusion for remote sensing data with label uncertainty*, IEEE TGRS | 10.1109/tgrs.2019.2955320 |
| 2023 | Roy et al., *Multimodal fusion transformer for remote sensing image classification*, IEEE TGRS | 10.1109/tgrs.2023.3286826 |
| 2024 | Chen, Zhao & Bruzzone, *A novel approach to incomplete multimodal learning for remote sensing data fusion*, IEEE TGRS | 10.1109/tgrs.2024.3387837 |

### 2.1 Single-modality mapping (ASTER, gamma-ray, hyperspectral)

| year | reference | DOI |
|---:|---|---|
| 2019 | Abrams & Yamaguchi, *Twenty years of ASTER contributions to lithologic mapping and mineral exploration*, Remote Sensing | 10.3390/rs11111394 |
| 2019 | Rajendran & Nasir, *ASTER capability in mapping of mineral resources of arid region*, Ore Geology Reviews | 10.1016/j.oregeorev.2018.04.014 |
| 2021 | Peyghambari & Zhang, *Hyperspectral remote sensing in lithological mapping, mineral exploration, and environmental geology: an updated review*, J. Applied Remote Sensing | 10.1117/1.jrs.15.031501 |
| 2024 | Xi et al., *Application of airborne gamma-ray spectrometry in geological lithology mapping*, Acta Geophysica | 10.1007/s11600-024-01408-1 |
| 2026 | Weihermann, Li & Zhang, *Machine-learning-based thorium normalization in airborne gamma-ray spectrometry*, Scientific Reports | 10.1038/s41598-026-76122-7 |

### 2.3 Evaluation, uncertainty and reproducibility

| year | reference | DOI |
|---:|---|---|
| 2022 | Yang et al., *Quantification of uncertainty associated with evidence layers in mineral prospectivity mapping*, Natural Resources Research | 10.1007/s11053-022-10144-6 |
| 2023 | Kapoor & Narayanan, *Leakage and the reproducibility crisis in machine-learning-based science*, Patterns | 10.1016/j.patter.2023.100804 |
| 2024 | Zhang et al., *Workflow-induced uncertainty in data-driven mineral prospectivity mapping*, Natural Resources Research | 10.1007/s11053-024-10322-8 |

### 2.4/2.5 Fusion in mineral exploration (the gap this paper fills)

| year | reference | DOI |
|---:|---|---|
| 2021 | Shirmard et al., *A review of machine learning in processing remote sensing data for mineral exploration*, Remote Sensing of Environment | 10.1016/j.rse.2021.112750 |
| 2022 | Shabani et al., *Multi-dimensional data fusion for mineral prospectivity mapping*, Minerals | 10.3390/min12121629 |
| 2026 | Christa, Suhari & Mane, *Self-supervised multi-modal fusion for mineral prospectivity mapping*, Natural Resources Research | 10.1007/s11053-026-10771-3 |
| 2026 | Zhang, Chen & Jiang, *A causal-aware artificial-intelligence framework for mineral prospectivity mapping*, Geoscience Frontiers | 10.1016/j.gsf.2026.102248 |

## 3. How the argument changes with them

The paper's claim becomes sharper, not weaker:

* The 2019–2026 fusion literature reports gains on tasks where the target is
  derived from the inputs or where the inversion is underdetermined. That is the
  same confound, at scale — the new references let the introduction say where the
  problem bites instead of asserting it.
* Reproducibility work (Kapoor & Narayanan, 2023) and workflow-uncertainty work
  (Zhang et al., 2024) provide the vocabulary for "conditioning vs information"
  and for why our controls matter.
* ASTER and gamma-ray papers give the modality-specific state of the art, which
  the old list covered only up to 1998–2009.
* The gap statement can then be honest: no recent airborne multi-modal benchmark
  reports the rank of the inverse problem *and* a model-free information test.

## 4. Work still to do

1. Complete author lists, volume/pages and DOIs from Crossref for all 16.
2. Rewrite §1 (positioning), §2 (new structure above) and §8.1 (which now has
   contemporary evidence to cite).
3. Add the new references to the list and keep the author–date style.
4. Retarget the manuscript formatting to IJRS (Taylor & Francis style, no
   Highlights requirement, abstract ≤ 250 words, keywords).
5. Re-run `code/check_submission.py`, rebuild the package and submit.
