# Cover letter — Computers & Geosciences

**To:** Editor-in-Chief, *Computers & Geosciences*

**Subject:** Submission of "Two confounds in reported fusion gains for airborne
mineral exploration: target circularity and an underdetermined inversion"

Dear Editor,

We submit the manuscript above for consideration as a research paper. It asks a
question that is usually assumed rather than tested: when does adding a second or
third geophysical modality actually improve an airborne mineral-exploration map,
and how would one know?

The paper is built for this journal's readership in three ways.

**It is a benchmark, not a case study.** One response matrix, one valid-pixel
mask and one contingency-table metric are fixed before any comparison, and the
protocol is released. The real radiometric survey (USGS Ivanpah–Clark Mountain,
Nevada–California, 2019–2020, 295,943 samples) is combined with real ASTER L1T
thermal infrared (five emissivity bands, 2006), real aeromagnetics and USGS
SIM 3206 geological mapping; the one synthetic modality (airborne EM, for which
no measured survey exists at this site) is labelled as such throughout and is
used as a controlled augmentation, not as evidence about field EM.

**It is reproducible in a checkable sense.** The pipeline is 40 scripts in eight
stages. A coverage guard fails if any validated artefact lacks a producing
script; a validator checks 53 artefacts and 19 cross-artefact invariants; 25 unit
tests cover the estimator's algebraic properties, including the two switch-off
invariances; every file carries a SHA-256 in a manifest; dependencies are pinned.
A single command rebuilds every number in the paper.

**It reports what did not work, and isolates what did.** Adding the five ASTER
bands raises the clay-proxy F1 from 0.531 to 0.652 and the AUC against independent
geology from 0.387 to 0.913. Five inert channels with the same response rows
recover 69-98 % of that F1 gain and an AUC at least as high (0.919
with all-zero channels, 0.922 with Gaussian noise), and a block-shuffled cube
does the same: most of the gain is conditioning of a rank-3 inverse problem,
not mineralogical information. A test that never touches the response matrix — a multinomial
classifier over four geologically similar substrates — keeps a real but much
smaller gain, +0.179 balanced accuracy (95 % CI [0.120, 0.241], 20 of 20
repeats), which collapses to +0.003 when the thermal cube is block-shuffled.
Correcting a mis-specified EM row to log10 resistivity with a clay-only row raises
proxy F1 from 0.168 to 0.497 (+0.332, CI [0.244, 0.430]) and still loses to
gamma+TIR; the fusion also beats the strongest published gamma-ratio index
(0.497 versus 0.365).

Two methodological consequences are stated as requirements rather than
suggestions: report the rank of the inverse problem, and report an information
test that does not use the response matrix. We also show that the spatial
effective sample size of this survey is 110–173, not 1.24 million pixels, and
that the filter variance is not a confidence interval (empirical 68 % coverage
0.13), so every contrast is given with a 128-px block bootstrap.

We believe the combination of a released benchmark, an audit of a widely used
modelling shortcut, and an honest negative result fits *Computers & Geosciences*
better than a remote-sensing venue, where the contribution would read as an
application rather than as a method.

The manuscript is original, is not under consideration elsewhere, and the single
author approves submission. The code is public at https://github.com/Xbotsd/fusion-gain-confounds and a snapshot will be archived
with a DOI on acceptance; the layout, licence and one-command reproduction
are described in the data-availability section.

Yours sincerely,

Yudong Xu
Heilongjiang University of Science and Technology, Harbin, China
3468858545@qq.com
