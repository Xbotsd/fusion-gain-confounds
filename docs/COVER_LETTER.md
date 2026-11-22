# Cover letter — International Journal of Remote Sensing

**To:** The Editor-in-Chief, *International Journal of Remote Sensing*

**Subject:** Submission of "Two confounds in reported fusion gains for airborne
mineral exploration: target circularity and an underdetermined inversion"

Dear Editor,

We submit the manuscript above for consideration as a research paper. It asks a
question that matters to every remote-sensing fusion study: when a second or third
modality is added, does the reported improvement come from new information, or
from the way the added channels condition an underdetermined retrieval?

**The data are real where real data exist.** Airborne radiometrics (USGS Ivanpah–Clark
Mountain, 295,943 samples, 2019–2020), real ASTER L1T thermal infrared (five
emissivity bands, 2006, normalisation TES), real aeromagnetics and the USGS SIM
3206 geological map are combined on one 50 m grid. The single synthetic modality —
airborne EM, for which no measured survey exists over this footprint — is labelled
as such throughout and used as a controlled augmentation, not as evidence about
field EM.

**The result is about how fusion gains are measured.** Adding the five ASTER bands
raises proxy F1 from 0.531 to 0.652 and the AUC against independent geology from
0.387 to 0.913. But five inert channels with the same response rows recover 69–98 %
of that F1 gain and an AUC at least as high (0.919 with zeros, 0.922 with Gaussian
noise), and a block-shuffled ASTER cube does the same: most of the gain is
conditioning of a rank-3 inverse problem, not information about the surface. A test
that never uses the response matrix — a multinomial classifier over four
geologically similar substrates with spatial-block cross-validation — keeps a real
but four-times-smaller gain, +0.179 balanced accuracy (95 % CI [0.120, 0.241],
20 of 20 repeats), which collapses to +0.003 when the thermal cube is
block-shuffled. We also correct a mis-specified synthetic EM row (F1 0.168 → 0.497)
and show that it still does not beat gamma + ASTER.

**It is reproducible and open.** The pipeline is 46 scripts in nine stages; a
coverage guard, a validator over 53 artefacts and 22 invariants, 36 unit
assertions and a SHA-256 manifest accompany it. Code and derived results are
archived at https://doi.org/10.5281/zenodo.24130421 and the repository is public
under the MIT licence, with details in the section "Code availability".

**Why this journal.** The fusion literature in remote sensing is rich and growing
(Ghamisi et al. 2019; Shirmard et al. 2022), but the evaluation of a fusion gain is
usually a single score against a target. Our benchmark gives that community a
control it can apply to any multimodal product: report the rank of the inverse
problem, and report one information test that does not use the response matrix.
We believe this fits the readership of *International Journal of Remote Sensing*
better than a computational-geoscience venue, because the contribution is about
remote-sensing data fusion and its evaluation.

The manuscript is original, is not under consideration elsewhere, and the single
author approves submission.

Yours sincerely,

Yudong Xu
Heilongjiang University of Science and Technology, Harbin, China
3468858545@qq.com
