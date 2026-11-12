# Cover letter — Earth Science Informatics

**To:** Editor-in-Chief, *Earth Science Informatics*

**Subject:** Submission of "Two confounds in reported fusion gains for airborne
mineral exploration: target circularity and an underdetermined inversion"

Dear Editor,

We submit the manuscript above for consideration as a research paper. It addresses
a problem that every multi-source geoscience data product faces: when a new layer
is added to an inversion or a classifier, does the reported improvement come from
new information, or from the way the added channels condition an underdetermined
problem?

The paper is built for this journal's readership in four ways.

**It is a data-informatics benchmark, not a case study.** One response matrix, one
analysis mask and one contingency-table metric are fixed before any comparison,
and the whole workflow is released. The real layers are a USGS airborne
radiometric survey (Ivanpah–Clark Mountain, Nevada–California, 2019–2020,
295,943 samples), real ASTER L1T thermal infrared (five emissivity bands, 2006),
real aeromagnetics and the USGS SIM 3206 geologic map; the one synthetic modality
(airborne EM, for which no measured survey exists at this site) is labelled as
such throughout and is used as a controlled augmentation, not as evidence about
field EM.

**The data chain is open and checkable.** The pipeline is 40 scripts in eight
stages. A coverage guard fails if any validated artefact lacks a producing script;
a validator checks 53 artefacts and 22 invariants, including the zero, noise and
shuffled controls; 36 assertions cover the estimator's algebraic properties and
the two switch-off invariances; every file carries a SHA-256 in a manifest;
dependencies are pinned; one command rebuilds every number. The raw ASTER scenes
are archived with their STAC identifiers and hashes so the thermal cube can be
rebuilt offline. Code and results are archived at
https://doi.org/10.5281/zenodo.24130421 and the repository is public under the MIT
licence.

**It separates the two reasons a reported fusion gain can be spurious.** Adding
the five ASTER bands raises the clay-proxy F1 from 0.531 to 0.652 and the AUC
against independent geology from 0.387 to 0.913. But five inert channels with the
same response rows recover 69–98 % of that F1 gain and an AUC at least as high
(0.919 with all-zero channels, 0.922 with Gaussian noise), and a block-shuffled
cube does the same: most of the gain is conditioning of a rank-3 inverse problem,
not mineralogical information. A test that never touches the response matrix — a
multinomial classifier over four geologically similar substrates — keeps a real
but much smaller gain, +0.179 balanced accuracy (95 % CI [0.120, 0.241], 20 of 20
repeats), which collapses to +0.003 when the thermal cube is block-shuffled.
Correcting a mis-specified EM row to log10 resistivity with a clay-only row raises
proxy F1 from 0.168 to 0.497 and still loses to gamma+TIR.

**It reports what did not work.** The spatial effective sample size of this survey
is 110–173, not 1.24 million pixels, and the filter variance is not a confidence
interval (empirical 68 % coverage 0.13); every contrast is therefore given with a
128-px block bootstrap. We state these limits rather than hiding them, because
they change how such benchmarks should be read.

We believe this combination — a released, reproducible fusion workflow, an audit
of a widely used evaluation shortcut, and an honest negative result — fits *Earth
Science Informatics*, whose readers build and reuse exactly such data-processing
chains. The manuscript is original, is not under consideration elsewhere, and the
single author approves submission.

Yours sincerely,

Yudong Xu
Heilongjiang University of Science and Technology, Harbin, China
3468858545@qq.com
