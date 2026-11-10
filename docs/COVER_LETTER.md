# Cover letter — Computers & Geosciences

**To:** Editor-in-Chief, *Computers & Geosciences*

**Subject:** Submission of "When does multi-modal fusion improve airborne mineral
exploration? An identifiability analysis and reproducible benchmark"

Dear Editor,

We submit the manuscript above for consideration as a research paper. It asks a
question that is usually assumed rather than tested: when does adding a second or
third geophysical modality actually improve an airborne mineral-exploration map,
and how would one know?

The paper is built for this journal's readership in three ways.

**It is a benchmark, not a case study.** One response matrix, one valid-pixel
mask and one contingency-table metric are fixed before any comparison, and the
protocol is released. The real radiometric survey (USGS Ivanpah–Clark Mountain,
Nevada–California, 2019–2020, 295,943 samples) is combined with real ASTER
thermal-infrared data and real geological mapping; the one synthetic modality
(airborne EM, for which no measured survey exists at this site) is labelled as
such throughout and is used as a controlled augmentation, not as evidence about
field EM.

**It is reproducible in a checkable sense.** The pipeline is 40 scripts in ten
stages. A coverage guard fails if any validated artefact lacks a producing
script; a validator checks 97 artefacts and 21 cross-artefact invariants; unit
tests cover the estimator's algebraic properties; every file carries a SHA-256 in
a manifest; dependencies are pinned. A single command rebuilds every number in
the paper.

**It reports what did not work.** The widely quoted +104 % fusion gain does not
reproduce and is shown to be a response-matrix artefact. Two published
gamma-ratio indices beat the fusion on the gamma-derived target, and that target
circularity is quantified rather than hidden. A variance-based gain index is
shown to be necessary but not sufficient: it agrees with the observed F1 change
in none of six cases, because a mis-specified channel can dominate the clay
column (98 % of its weight) and lower the estimator variance while making the map
worse.

The positive result is falsifiable: correcting the EM response to log10
resistivity with a clay-only row raises proxy F1 from 0.267 to 0.498 and average
precision from 0.126 to 0.513, with a 128-px block-bootstrap gain of
+0.167 [0.118, 0.216] over independent inversion. On an independent geological
target, gamma alone sits at chance (AUC 0.476) because three channels cannot
determine five abundances, while gamma plus real ASTER TIR reaches 0.905.

We believe the combination of a released benchmark, an audit of a widely used
modelling shortcut, and an honest negative result fits *Computers & Geosciences*
better than a remote-sensing venue, where the contribution would read as an
application rather than as a method.

The manuscript is original, is not under consideration elsewhere, and all authors
approve submission. The code and derived data will be archived with a DOI on
acceptance; the repository layout, licence and one-command reproduction are
described in the data-availability section.

Yours sincerely,

Yudong Xu
Heilongjiang University of Science and Technology, Harbin, China
3468858545@qq.com
