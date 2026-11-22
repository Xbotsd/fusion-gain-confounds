# Cover letter — Natural Resources Research

**To:** The Editor-in-Chief, *Natural Resources Research*

**Subject:** Submission of "Two confounds in reported fusion gains for airborne
mineral exploration: target circularity and an underdetermined inversion"

Dear Editor,

We submit the manuscript above for consideration as a research paper. It asks a
question that is central to prospectivity mapping: when remote sensing,
geophysics and geology are combined into a mineral prospectivity map, does the
reported improvement come from new information about the subsurface, or from the
way the added layers condition an underdetermined inversion?

**A real-data benchmark.** The study area is the Ivanpah–Clark Mountain block
(Nevada–California). The layers that exist as real measurements are used as such:
USGS airborne radiometrics (295,943 samples, 2019–2020), real ASTER L1T thermal
infrared (five emissivity bands, 2006, normalisation TES), real aeromagnetics and
the USGS SIM 3206 geological map, all on one 50 m grid. Airborne EM is synthetic —
no measured survey exists over this footprint — and is labelled as such
throughout, used as a controlled augmentation rather than as evidence about field
EM.

**The result is about how fusion gains are measured.** Adding the five ASTER
bands raises proxy F1 from 0.531 to 0.652 and the AUC against independent geology
from 0.387 to 0.913. Five inert channels with the same response rows recover
69–98 % of that F1 gain and an AUC at least as high (0.919 with zeros, 0.922 with
Gaussian noise); a block-shuffled ASTER cube does the same. Most of the gain is
conditioning of a rank-3 inverse problem, not information about the surface. A
test that never uses the response matrix — a multinomial classifier over four
geologically similar substrates with spatial-block cross-validation — keeps a
real but four-times-smaller gain, +0.179 balanced accuracy (95 % CI
[0.120, 0.241], 20 of 20 repeats), which collapses to +0.003 when the thermal
cube is block-shuffled. Correcting a mis-specified synthetic EM row (F1 0.168 →
0.497) still does not beat gamma + ASTER.

**Why this journal.** Prospectivity studies increasingly rely on data fusion and
on machine-learning workflows, and the literature now documents how strongly the
product depends on the workflow and on the uncertainty in the evidence layers
(Zhang et al., 2024; Yang et al., 2022). Our benchmark gives that community a
control it can apply to any multimodal prospectivity map: report the rank of the
inverse problem, and report one information test that does not use the response
matrix.

**It is reproducible.** Forty-six scripts in nine stages, a coverage guard, a
validator over 53 artefacts and 22 invariants, 36 unit assertions, a SHA-256
manifest, and an open repository archived at
https://doi.org/10.5281/zenodo.24130421 (MIT licence), described in the Code
availability section.

The manuscript is original, is not under consideration elsewhere, and the single
author approves submission.

Yours sincerely,

Yudong Xu
Heilongjiang University of Science and Technology, Harbin, China
3468858545@qq.com
