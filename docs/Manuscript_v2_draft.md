# Two confounds in reported fusion gains for airborne mineral exploration: target circularity and an underdetermined inversion

**Authors:** Yudong Xu¹  
¹ Heilongjiang University of Science and Technology, Harbin, China  
**Corresponding author:** 3468858545@qq.com

## Abstract

Reported fusion gains in airborne mineral exploration are rarely reproducible because of two confounds: the target is derived from the channels being inverted, and the inversion is underdetermined, so adding any channel changes conditioning rather than information. We separate both on a real-data benchmark over the Ivanpah-Clark Mountain area: USGS radiometrics (295,943 samples), real ASTER L1T thermal infrared (five emissivity bands), real aeromagnetics and USGS SIM 3206 geology, with one synthetic electromagnetic augmentation since no measured airborne EM exists. Three gamma channels for five minerals give rank 3, and gamma alone scores at chance against independent geology (AUC 0.387). Five ASTER bands raise proxy F1 from 0.531 to 0.652 and geological AUC to 0.913 - but five uninformative channels with the same response rows recover 69-98 % of the F1 gain and all of the AUC gain, so most of it is conditioning. A model-free test isolates the information: gamma plus ASTER classifies four similar substrates at balanced accuracy 0.529 versus 0.350 for gamma (+0.179, CI [0.120, 0.241], 20/20 repeats), while a shuffled cube gives 0.354. Correcting a mis-specified electromagnetic row raises F1 from 0.168 to 0.497 but still loses to gamma plus thermal. Effective sample size is 110, not 1.2 million pixels, and the filter variance is not a confidence interval (coverage 0.13). Fusion studies should report the rank of the inverse problem and an information test that does not use the response matrix.

**Keywords:** airborne mineral exploration; gamma-ray spectrometry; thermal infrared; ASTER; multi-modal fusion; identifiability; reproducibility; benchmark

## Highlights

- Most fusion gains stem from circular targets and underdetermined inversions
- Three gamma channels for five minerals give rank 3; AUC 0.387 on real geology
- Real ASTER TIR lifts proxy F1 to 0.652; inert channels recover 69-98 %
- Model-free gain is +0.179 balanced accuracy, lost when the cube is shuffled
- Fixing the synthetic EM row helps (+0.332 F1) but still loses to gamma+TIR

## 1. Introduction

Airborne surveys are a primary tool for mapping alteration and lithology over
large areas. Gamma-ray spectrometry measures potassium, equivalent uranium and
equivalent thorium in roughly the top 30 cm; electromagnetic (EM) induction
responds to bulk conductivity; thermal infrared (TIR) emissivity carries
mineralogical information through reststrahlen features. Each modality is
physically limited, so combining them is attractive, and the literature
repeatedly reports that fusion improves a map or a classification score [1–4,21].

The reported gains range from marginal to more than 100 %. Reproducing them is
difficult for two reasons that this paper treats as measurable quantities rather
than caveats.

**Confound 1: the target usually contains the answer.** In airborne exploration
there is rarely an independent mineral map, so the evaluation target is often an
alteration index computed from the same gamma channels the inversion uses. A
gamma ratio then tracks the target by construction, and any multimodal model is
competing against the target's own definition [4,23].

**Confound 2: the inversion is often underdetermined.** With three gamma
channels and five mineral abundances the linear mixture problem has rank 3.
Adding any channel raises the rank, which reduces the variance of every
abundance estimate — whether or not the new channel carries information about
the target. A variance-based gain index will therefore be positive almost
always, and a benchmark that reports only the fused score cannot tell
conditioning from information.

We quantify both confounds on a real-data benchmark. The radiometric survey is
real, the thermal infrared is real (ASTER L1T emissivity), the magnetics and the
geological map are real; only the EM section is synthetic, because no measured
airborne EM exists over this footprint, and it is labelled as such throughout.
All comparisons share one mask, one response-matrix construction and one metric
definition.

Our contributions are four.

(i) We show that the two confounds can be separated experimentally. Appending
channels that carry no information - all zeros, Gaussian noise, or the real cube
block-shuffled - recovers 69-98 % of that F1 gain (0.614, 0.649 and 0.634
against 0.652) and all of the geological AUC gain, which measures the
conditioning effect directly.

(ii) We provide an information test that conditioning cannot fake: a
multinomial model on the same channels with spatial-block cross-validation and
no response matrix. Gamma plus real ASTER reaches balanced accuracy 0.529 against
0.350 for gamma alone (+0.179, CI [0.120, 0.241], 20 of 20 repeats), while a
block-shuffled ASTER cube is indistinguishable from gamma (0.354).

(iii) We fix two implementation errors that bias fusion benchmarks in the same
direction: response-matrix columns normalised over inactive rows, and channel
weights normalised over inactive channels. Both make "switching a modality off"
depend on the rows that are multiplied by zero. Unit tests now assert both
invariances.

(iv) We report an EM model correction honestly, including that it does not win:
correcting a raw-resistivity, five-mineral EM row to log10 resistivity with a
clay-only row raises proxy F1 from 0.168 to 0.497 (ΔF1 +0.332, CI [0.244, 0.430])
but leaves it below gamma+TIR at 0.652.

## 2. Related work

### 2.1 Single-modality mineral exploration

Gamma-ray spectrometry is routinely used for mapping and alteration detection,
with ternary images and ratios such as K/eTh as alteration indices [1–4,21]. It
is sensitive to the top 30 cm only and is affected by soil moisture and
vegetation. Airborne EM provides conductivity to tens or hundreds of metres and
is non-unique in inversion [5–7,20]. TIR spectroscopy identifies rock-forming
minerals through 8–14 µm emissivity features [8–10,22]; quantitative abundance
requires temperature–emissivity separation and is sensitive to particle size and
atmospheric correction.

### 2.2 Multi-modal fusion

Fusion has been approached with Bayesian updating, weighted least squares, Kalman
filters, principal components and, recently, learned models [11–14]. Most studies
report an improved map or score; few analyse when an improvement is expected. In
a linear mixture model the benefit of a channel depends on the conditioning of
the response matrix, on the noise of the new channel and on the target
definition. If the target is a function of the existing channels, the last two
cannot be separated without an external check.

### 2.3 Evaluation and reproducibility

Reproducibility requires fixed data, code, parameters and metric definitions
[16,17]. Benchmark studies in geoscience repeatedly show that gains shrink when
splits and metrics are standardised. A specific hazard for spatial data is
pseudo-replication: neighbouring pixels are not independent, so a metric computed
per pixel has an effective sample size orders of magnitude below the pixel count.

### 2.4 Gap

There is no airborne multi-modal benchmark that (a) uses real data for the
modalities that exist, (b) reports the rank of the inverse problem, and (c)
includes a target-independent information test. This paper supplies all three and
shows that omitting (b) and (c) is enough to manufacture an apparent fusion gain.

## 3. Data

**Table 1.** Data layers, provenance, native resolution and role.

| layer | source | resolution | role |
|---|---|---|---|
| K, eU, eTh | USGS airborne radiometrics, Ivanpah–Clark Mtn, 2019–2020 | 50 m | real observation |
| ASTER TIR ×5 | ASTER L1T v003, 2006-10-18, emissivity normalisation | 90 m → 50 m | real observation |
| EM ×3 layers | synthetic (Wisconsin AEM statistics, seed 12345) | 50 m | documented augmentation |
| TMI | USGS aeromagnetics | 50 m | edge experiment only |
| substrate | USGS SIM 3206 geologic map (DOI 10.3133/sim3206) | 50 m | independent target |
| clay_prior | derived from K and eTh | 50 m | circular proxy target |

**Table 2.** The three targets used in this paper and why each is needed.

| target | definition | what it can show |
|---|---|---|
| Gamma proxy | `clay_prior > 0.55`, computed from K and eTh | comparability with the literature; circular for gamma |
| Geology, inversion | AUC, clay-bearing vs clay-poor substrates, estimated clay | end-to-end behaviour of the model |
| Geology, model-free | balanced accuracy, 4 substrate classes, raw channels, block CV | information that conditioning cannot fake |


<!-- FIGURE:fig_data.png -->
**Figure 1.** The real observation layers: K, eU and eTh on the 50 m grid, the five ASTER emissivity bands (2006-10-18), the synthetic EM shallow layer and the derived clay_prior proxy. The study area spans 53.8 x 88.6 km; the analysis mask is the intersection of the radiometric footprint and full ASTER coverage.

### 3.1 Real airborne radiometrics

The USGS survey of the Ivanpah–Clark Mountain area (Nevada–California) provides
295,943 samples at 1 Hz over 631 lines, 47 flights and 34 survey days between
13 December 2019 and 21 March 2020. Corrected K (%), eU (ppm) and eTh (ppm) were
gridded to 50 m on 1772 × 1075 pixels in NAD83 / UTM 11N; the irregular footprint
leaves 66.4 % of the grid valid. Median values are K 3.24 %, eU 6.69 ppm and eTh
5.81 ppm.

### 3.2 Real ASTER thermal infrared

Thermal infrared is the real ASTER L1T product (v003, NASA/METI), five bands at
8.29, 8.63, 9.08, 10.66 and 11.29 µm, 90 m, from the 2006-10-18 acquisition; four
scenes mosaic to full coverage of the study area. Processing is: mosaic and
resample to the 50 m grid, DN to at-sensor radiance with the ASTER
unit-conversion coefficients, brightness temperature by inverting the Planck
function at each band centre, and emissivity by normalisation [24] with an
assumed maximum of 0.98. The retrieved brightness temperature is 282–298 K
(median 291 K) and emissivity 0.87–0.98, with band means
0.895 / 0.913 / 0.918 / 0.977 / 0.979. The short-wavelength bands show the
expected reststrahlen depression. Pixels with all five bands cover 97.8 % of the
radiometric survey.

### 3.3 Synthetic electromagnetic section

No measured airborne EM exists over this footprint: the delivered survey contains
only the radiometric and magnetic grids. The EM cube is therefore a controlled
synthetic field with 40 layers from 0 to 600 m, layer statistics from the
Wisconsin AEM survey, a clay-linked component decaying as exp(−d/250) and
independent and noise fields, seed 12345. Three layers (0, 15 and 35) are used as
observation channels. Every EM result in this paper is labelled synthetic.

### 3.4 Real aeromagnetics and geology

The total magnetic intensity grid is real and resampled to the analysis grid; it
enters only the edge-deployment experiment. The USGS SIM 3206 surficial geologic
map (DOI 10.3133/sim3206) is rasterised to the same grid into eight substrate
classes. It is the only target in this paper that is not derived from any of the
observed modalities, and it is used as the independent reference.

### 3.5 Analysis mask and channel layout

All results are computed on the intersection of the radiometric footprint and
full five-band ASTER coverage: 1,237,644 pixels (65.0 % of the grid, 97.8 % of the
survey). The observation vector has eleven channels: three gamma, five ASTER
emissivity and three synthetic EM (Table 1). Every metric is defined in Table 2.

## 4. Methods

<!-- FIGURE:fig_method.png -->
**Figure 2.** Benchmark protocol and estimator chain. Three targets are scored for every configuration: the circular gamma proxy, an inversion-side geological AUC, and a model-free four-class test that has no response matrix.

### 4.1 Response matrix

The gamma rows are the relative signatures used throughout (K, eU, eTh per
mineral). The TIR rows are **not hand-set**: for each mineral the USGS splib07
emissivity spectrum is averaged over each ASTER band pass, giving the five rows

**Table 3.** TIR rows of the response matrix: USGS splib07 emissivity of each mineral averaged over the ASTER band pass, not hand-set.

| band (µm) | Quartz | Feldspar | Clay | Calcite | Dolomite |
|---:|---:|---:|---:|---:|---:|
| 8.291 | 0.255 | 0.765 | 0.992 | 0.814 | 0.937 |
| 8.634 | 0.410 | 0.712 | 0.993 | 0.811 | 0.932 |
| 9.075 | 0.157 | 0.789 | 0.935 | 0.756 | 0.923 |
| 10.657 | 0.902 | 0.847 | 0.921 | 0.756 | 0.888 |
| 11.289 | 0.925 | 0.872 | 0.957 | 0.857 | 0.864 |

Quartz falls to 0.16–0.26 in the reststrahlen region and returns to 0.90–0.93
beyond 10 µm, which is a check that the band-pass sampling is correct.

### 4.2 Estimator

Weighted least squares on standardised channels with a column-normalised
response matrix, followed by a forward Kalman recursion along the image axis
(λ = 0.1, Q = 0.005, R = 0.02) and projection to the simplex. The estimator is
applied unchanged to every subset; a subset is selected by zero weights.

Two invariances are enforced and unit-tested:

* response-matrix columns are normalised over the **active rows only**;
* channel weights are normalised over the **active channels only**.

Without them, switching a modality off changes the answer through the rows and
weights that are multiplied by zero — a bias that inflates apparent fusion gains
and that we found in our own earlier implementation.

### 4.3 Identifiability diagnostics

For each modality subset we report the number of equations and the numerical
rank of the normalised active matrix, its condition number, and the clay-variance
gain index `G = 1 − Var(S∪m)/Var(S)` computed from
`Cov = G (HᵀWH+λI)⁻¹ HᵀWΣW H (HᵀWH+λI)⁻¹` with Σ the robust per-channel noise.

### 4.4 Targets and metrics

Three targets are used, deliberately:

1. **Gamma proxy** — `clay_prior > 0.55`, an alteration index computed from K and
   eTh. Circular for gamma; reported because the literature uses such targets.
   Metrics: recall, precision, F1 at clay > 0.25 with clay in the top two
   minerals, and average precision.
2. **Independent geology, inversion** — AUC of the estimated clay between
   clay-bearing substrates (alluvium, felsic plutonic) and clay-poor ones
   (carbonate, sedimentary).
3. **Independent geology, model-free** — balanced accuracy of a multinomial
   logistic model on the raw channels for four radiometrically similar
   substrates (felsic plutonic, volcanic, metasedimentary, alluvium), with
   128-px spatial-block cross-validation. This test has no response matrix, so
   conditioning cannot inflate it.

### 4.5 Uncertainty

All contrasts use a 128-px block bootstrap (200 replicates), the block length
being at least twice the measured integral scale. The effective sample size is
derived from the integral scale of the clay field.

## 5. Identifiability

With three gamma channels and five abundances the active matrix has rank 3; the
ridge solution is a minimum-norm compromise, not a clay map. This is visible in
the estimator's own diagnostics: κ = 7.2 and rank 3 from 3 equations. Adding the
five ASTER bands gives 8 equations, rank 5 and κ = 15.8, so the estimate becomes
identifiable.

The clay-variance gain index is positive for every addition, and it does not
predict accuracy: the sign of `G` agrees with the sign of the observed F1 change
in 1 of 6 additions and with the geological AUC change in 3 of 6. A variance
argument is therefore necessary but not sufficient, and in an underdetermined
problem it is guaranteed to be positive — which is precisely why it cannot be
used as evidence that fusion helps.

<!-- FIGURE:identifiability.png -->
**Figure 3.** Identifiability diagnostics: predicted clay-variance gain (a), observed change in proxy F1 (b) and in geological AUC (c). The variance index is positive for every addition and does not track either observed change.

## 6. Experiments

Ablation over four modality subsets; generic baselines; a conditioning control
(zero-filled channels with the real ASTER rows); a geographic-shuffle control;
the model-free multi-class geology test with 20 repeats; a TES and
acquisition-date sensitivity of the real TIR retrieval; ten repeats with 1 %
channel noise; a 40-layer depth Kalman; uncertainty calibration; pseudo-
replication; five published single-modality indices.

## 7. Results

All electromagnetic results in this section are computed on the synthetic
section of Section 3.3; they constrain the response model, not field EM.

### 7.1 The gamma proxy rewards gamma, and TIR helps on it

Table 4. With the corrected EM model, gamma alone reaches F1 0.531; adding the
five ASTER bands raises it to **0.652** (AP 0.393 → 0.624, precision 0.367 →
0.544). Adding the synthetic EM instead gives 0.418, and the full set 0.497. On
this circular target the best configuration is gamma+TIR, and the synthetic EM
is a liability.

**Table 4.** Modality ablation on the real-ASTER layout, both EM models (1,237,644 analysis pixels).

| EM model / configuration | clay mean | recall | precision | F1 | AP | geology AUC |
|---|---:|---:|---:|---:|---:|---:|
| legacy / gamma | 0.299 | 0.965 | 0.367 | 0.531 | 0.393 | 0.387 |
| legacy / gamma+tir | 0.150 | 0.814 | 0.543 | 0.652 | 0.624 | 0.913 |
| legacy / gamma+em | 0.344 | 0.391 | 0.128 | 0.192 | 0.128 | 0.898 |
| legacy / all | 0.328 | 0.331 | 0.113 | 0.168 | 0.123 | 0.826 |
| corrected / gamma | 0.299 | 0.965 | 0.367 | 0.531 | 0.393 | 0.387 |
| corrected / gamma+tir | 0.150 | 0.814 | 0.543 | 0.652 | 0.624 | 0.913 |
| corrected / gamma+em | 0.377 | 0.964 | 0.267 | 0.418 | 0.456 | 0.724 |
| corrected / all | 0.236 | 0.934 | 0.338 | 0.497 | 0.577 | 0.912 |

<!-- FIGURE:main_maps.png -->
**Figure 4.** Clay abundance from the real-ASTER main line (left), from the synthetic-TIR control (centre), and the gamma-derived clay_prior (right). The synthetic cube reproduces the proxy field by construction; the real ASTER map does not, which is why the two score differently against independent geology.

### 7.2 Against independent geology the underdetermined model fails

The same clay maps scored against SIM 3206 give AUC 0.387 for gamma alone — at
chance — and 0.913 once TIR is added. The raw channels explain this: K alone
separates the same substrates at AUC 0.986, so the information is present and the
inversion destroys it. Three equations cannot determine five abundances; adding
TIR makes the problem overdetermined and the geological contrast reappears. The
paired block bootstrap gives ΔAUC +0.457 [0.123, 0.697] and ΔF1 +0.120
[0.067, 0.167].

<!-- FIGURE:main_ablation.png -->
**Figure 5.** Ablation on both targets: proxy F1 (a) and independent geological AUC (b) for the three data branches. Adding any channel improves both scores inside the inversion; the model-free test in Table 6 separates conditioning from information.

### 7.3 Most of that gain is conditioning, not information

Replacing the real ASTER cube with channels that carry no information, while
keeping the same response rows, recovers most of the effect. The share depends
on which inert control is used, so Table 5 reports three:

**Table 5.** Conditioning controls. The zero and noise blocks use the real ASTER
rows of `H` with data that carry no information; the block-shuffled cube keeps
the ASTER marginals and destroys geographic registration. Columns are proxy F1,
average precision, geological AUC and the model-free balanced accuracy.

| configuration | F1 | AP | geology AUC | 4-class balanced accuracy |
|---|---:|---:|---:|---:|
| gamma | 0.531 | 0.393 | 0.387 | 0.350 |
| gamma + real ASTER | 0.652 | 0.624 | 0.913 | 0.529 |
| gamma + block-shuffled ASTER | 0.634 | 0.635 | 0.913 | 0.354 |
| gamma + five zero channels | 0.614 | 0.774 | 0.919 | — |
| gamma + five noise channels | 0.649 | 0.687 | 0.922 | — |
| gamma + synthetic TIR | 0.597 | 0.706 | 0.905 | 0.389 |

**Table 6.** Model-free information test: balanced accuracy for four geologically similar substrates, 128-px block cross-validation, 15,000 pixels per class, 20 repeats, chance 0.25.

| features | balanced accuracy | gain vs gamma [95 % CI] | repeats improved |
|---|---:|---|---:|
| gamma | 0.350 ± 0.055 | +0.000 [+0.000, +0.000] | 0/20 |
| real ASTER | 0.410 ± 0.024 | +0.060 [-0.035, +0.146] | 18/20 |
| gamma + real ASTER | 0.529 ± 0.034 | +0.179 [+0.120, +0.241] | 20/20 |
| gamma + block-shuffled ASTER | 0.354 ± 0.047 | +0.003 [-0.050, +0.061] | 9/20 |
| gamma + synthetic TIR | 0.389 ± 0.046 | +0.039 [+0.008, +0.100] | 20/20 |
| gamma + TMI | 0.349 ± 0.056 | -0.001 [-0.021, +0.022] | 9/20 |
| gamma + real ASTER + TMI | 0.521 ± 0.036 | +0.170 [+0.109, +0.235] | 20/20 |

Inside the estimator, zeros, noise and shuffled copies all score close to the real
cube (69-98 % of the F1 gain, and a geological AUC at or above the real cube's),
because the extra rows regularise a rank-3 problem. The model-free column of
Table 5 (expanded in Table 6) does not use the response matrix: there gamma+ASTER
reaches 0.529 against 0.350 for gamma (+0.179), a block-shuffled cube gives 0.354
- no gain - and the synthetic TIR cube gives 0.389, a much smaller real gain
(+0.039).

The honest reading is that real ASTER TIR does carry information about substrate
that gamma does not (20 of 20 repeats, CI [0.120, 0.241]), but the +0.12 F1 and
+0.53 AUC reported by the inversion overstate it: for the AUC there is no
information left at all once conditioning is controlled, and for F1 the true
share is roughly a third.

### 7.4 Estimator comparison

Table 7. On the proxy, GLS reaches the highest F1 (0.560), the proposed
WLS+Kalman 0.497 with the highest AP (0.577) and the highest geological AUC
(0.912), and the fewest components among the accurate methods (919 against 4,786
for the independent inversion and 7,949 for GLS). The Kalman stage therefore buys
coherence and geological agreement rather than proxy F1.

**Table 7.** Estimator comparison on the same mask and metric (real ASTER, corrected EM).

| method | F1 | AP | precision | geology AUC | components |
|---|---:|---:|---:|---:|---:|
| GLS / Bayesian | 0.560 | 0.495 | 0.447 | 0.661 | 7,949 |
| Simple average | 0.506 | 0.480 | 0.375 | 0.838 | 3,514 |
| WLS only | 0.497 | 0.548 | 0.340 | 0.873 | 1,630 |
| WLS + Kalman | 0.497 | 0.577 | 0.338 | 0.912 | 919 |
| Fixed weight | 0.433 | 0.541 | 0.282 | 0.863 | 833 |
| PCA (3 comp.) | 0.425 | 0.387 | 0.308 | 0.857 | 1,678 |
| Independent | 0.355 | 0.456 | 0.216 | 0.697 | 4,786 |
| WLS + Kalman (legacy EM) | 0.168 | 0.123 | 0.113 | 0.826 | 1,695 |

### 7.5 The EM correction is real but does not win

Correcting the raw-resistivity, five-mineral EM row to log10 resistivity with a
clay-only row (still on the synthetic section) raises proxy F1 from 0.168 to 0.497 (ΔF1 +0.332 [0.244, 0.430],
200/200 replicates). The legacy row is anti-correlated with the clay proxy, which
is why it is catastrophic when fused. But the corrected EM still lowers the score
relative to gamma+TIR (0.497 versus 0.652), and it reduces the geological AUC
from 0.913 to 0.912 while lowering it to 0.724 when used without TIR. Since the
EM section is synthetic, this is a statement about the model, not about field EM.

### 7.6 The thermal result does not depend on the retrieval choices

Varying the assumed maximum emissivity from 0.95 to 1.00 changes gamma+TIR F1 by
less than 0.001; dropping the band with the largest residual temperature
correlation (11.29 µm) leaves 0.640; repeating with the second acquisition date
(2006-09-25) gives 0.651 against 0.652. Ten repeats with 1 % channel noise give
F1 0.4967 ± 0.00003. The conclusion is not an artefact of the TES simplification
or of one scene.

**Table 8.** Sensitivity of the thermal result to the retrieval and the acquisition. Bootstrap of the gamma+TIR gain: +0.119 [+0.067, +0.167].

| variant | gamma F1 | gamma+TIR F1 |
|---|---:|---:|
| baseline 2006-10-18 (5 bands) | 0.531 | 0.652 |
| eps_max 0.95 | 0.531 | 0.652 |
| eps_max 1.00 | 0.531 | 0.652 |
| no 11.29 um band (4 bands) | 0.531 | 0.640 |
| second date 2006-09-25 | 0.531 | 0.651 |

### 7.7 Depth

The 40-layer Kalman recursion, using the real surface gamma and ASTER TIR as
anchors and one synthetic EM layer as the depth-varying channel, gives clay
0.281 at the surface rising to 0.360 at 500 m without the EM correction, and
0.281 → 0.342 (13 m) → 0.323 (500 m) with the clay-only EM row. The depth cube
remains a synthetic extrapolation: surface channels are repeated at every layer
and the only depth-varying information is the synthetic EM section.

<!-- FIGURE:published_baselines.png -->
**Figure 6.** Published single-modality indices against the fusion on the matched-prevalence rule. Ranking depends on the target: ternary K-dominance is the best geological discriminator and one of the weakest proxy detectors.

### 7.8 Published single-modality practice

Table 9. On the matched-prevalence rule the strongest published index is low
eTh/K (F1 0.365), followed by the F-parameter (0.284) and ternary K-dominance
(0.150); spectral angle mapping on the real ASTER bands and an EM conductor index
give 0.071 and 0.016. The fusion reaches 0.497. On independent geology the
ordering changes: ternary K-dominance separates substrates best (AUC 0.986)
because it is essentially a potassium map, the fusion 0.912, low eTh/K 0.217
(inverted). Which index "wins" is a property of the target, not of the data.

**Table 9.** Published single-modality practice versus the fusion, on the same mask and with the matched-prevalence rule.

| method | reference | matched F1 | geology AUC |
|---|---|---:|---:|
| Ternary K-dominance | IAEA 2003 | 0.150 | 0.986 |
| F-parameter K*eU/eTh | Gnojek & Prichystal 1985 | 0.284 | 0.923 |
| Low eTh/K | Dickson & Scott 1997 | 0.365 | 0.217 |
| SAM on real ASTER TIR | Kruse et al. 1993 | 0.071 | 0.083 |
| EM conductor index | Fountain 1998 | 0.016 | 0.087 |
| Independent inversion | this work | 0.355 | 0.697 |
| WLS + Kalman (ours) | this work | 0.497 | 0.912 |

### 7.9 Uncertainty and pseudo-replication

The forward-filter variance is not a confidence interval: empirical 68 % and 95 %
coverage are 0.129 and 0.258, with a variance-scale factor of 13.5 that raises
them only to 0.517 and 1.00. The clay field has an integral scale of about 50 px (2.5 km), a design effect of
11,262 and an effective sample size of 110 from 1,237,644 pixels; the inverted
clay map, being smoother, gives 173. Every contrast in this paper is therefore
reported with a 128-px block bootstrap.

### 7.10 What this bounds

The benchmark is one survey; the EM section is synthetic; ASTER is from 2006
while the radiometrics are from 2019–2020; the geological target is substrate, not
alteration or mineralisation; and no borehole or field validation is available.
The information test uses a linear classifier on raw channels, so it measures
separable information rather than the best achievable map.

## 8. Discussion

### 8.1 Why the two confounds matter

The literature's fusion gains are usually reported as an improvement in a score
against a target built from the same data. Under that design a positive gain is
not evidence that a modality adds information: a rank-deficient inversion will
improve when any channel is added, and our zero-filled control shows the effect
is large enough to consume the entire reported gain. The two controls we propose
are cheap: report the rank of the active matrix, and report one information test
computed without the response matrix.

### 8.2 Why EM hurt, and what correcting it bought

The legacy EM row was linear in raw resistivity, gave all five minerals a
response and assigned clay the lowest resistivity, which inverts the sign of its
contribution. Correcting it to log10 resistivity with a clay-only row is the
right model and raises the fused score fourfold, but because the section is
synthetic the result says nothing about field EM. It does say something about
benchmarks: a mis-specified row can make a modality look useless, and the same
row, corrected, can still be inferior to a simpler two-modality model.

### 8.3 Metric implications

Proxy F1, geological AUC and balanced accuracy rank the configurations
differently. Gamma is best on nothing except recall; gamma+TIR is best on the
proxy and on the inversion-side geology; gamma+ASTER is best on the model-free
information test but not on the proxy. Reporting a single number is therefore not
enough, and reporting the proxy alone is actively misleading for a multimodal
study.

### 8.4 Limitations

The EM modality is synthetic. The TIR is real but from a different epoch, at
90 m, five bands, and retrieved with a normalisation TES rather than a full
temperature–emissivity separation. There is one survey and no independent
alteration or deposit label. The estimator is linear with a hand-set gamma block;
only the thermal rows are derived from a spectral library.

## 9. Conclusion

On a real-data airborne benchmark, the apparent gain from adding real thermal
infrared to gamma-ray data is mostly an artefact of an underdetermined inversion:
five uninformative channels with the same response rows recover 69-98 % of the
F1 gain (0.614 for zeros, 0.649 for noise, 0.652 for the real cube) and a
geological AUC at least as high (0.919 and 0.922 against 0.913). What survives a
model-free test is a real but much smaller information gain, +0.179 balanced
accuracy across four geologically similar substrates, which vanishes when the
thermal cube is block-shuffled. Correcting a mis-specified EM row raises the fused score from
0.168 to 0.497 but still does not beat gamma+TIR. We recommend that fusion
studies report the rank of the inverse problem, an information test that does not
use the response matrix, and the spatial effective sample size; without the first
two, a reported fusion gain cannot be distinguished from conditioning.

## Reproducibility and data availability

The pipeline is 40 scripts in eight stages. A coverage guard fails if any
validated artefact lacks a producing script; a validator checks 53 artefacts and
22 invariants (including the zero, noise and shuffled controls); unit tests
assert the two switch-off invariances and the spectral-library construction of
the thermal rows; every file carries a SHA-256 in a manifest; dependencies are
pinned; one command rebuilds every number. The raw ASTER scenes are archived with their STAC identifiers and hashes so the
thermal cube can be rebuilt offline. The repository is released under the MIT
licence; the reference copy is archived on Zenodo (DOI to be inserted on
acceptance) and the benchmark is built so that one command regenerates every
table and figure in this paper.

## Declarations

**CRediT author statement.** Yudong Xu: conceptualisation, methodology,
software, validation, formal analysis, investigation, data curation, writing —
original draft, writing — review and editing, visualisation.

**Competing interests.** The author declares no competing financial or
non-financial interests.

**Funding.** This research received no specific grant from any funding agency in
the public, commercial, or not-for-profit sectors.

**Acknowledgements.** The airborne radiometric, magnetic and geological data are
courtesy of the U.S. Geological Survey; the thermal data are courtesy of NASA,
JAXA and METI through the ASTER instrument on Terra. Radiometric and magnetic
processing followed the USGS surveys cited in Section 3; responsibility for the
analysis and for the conclusions drawn from these public data rests with the
author.

## References

Numbers follow the IEEE style used in the text. Entries 1–24 are contiguous;
every entry is cited in the body. DOIs were checked against Crossref (11
entries). Eight entries carry no DOI (IAEA TECDOC; the AGSO Journal 17(2) 1997
special issue, which is unindexed; and four books or chapters). See
`docs/REFERENCES_AUDIT.md`.

1. IAEA. Guidelines for radioelement mapping using gamma ray spectrometry data. IAEA-TECDOC-1363, 2003.
2. Minty, B.R.S. Fundamentals of airborne gamma-ray spectrometry. AGSO Journal of Australian Geology and Geophysics, 17(2), 39–50, 1997.
3. Wilford, J.R., Bierwirth, P.N., Craig, M.A. Application of airborne gamma-ray spectrometry in soil/regolith mapping and applied geomorphology. AGSO Journal, 17(2), 201–216, 1997.
4. Dickson, B.L., Scott, K.M. Interpretation of aerial gamma-ray surveys—adding the geochemical factors. AGSO Journal, 17(2), 187–200, 1997.
5. Fountain, D. Airborne electromagnetic systems—50 years of development. Exploration Geophysics, 29(1–2), 1–11, 1998.
6. Siemon, B., Auken, E., Christiansen, A.V. Laterally constrained inversion of helicopter-borne frequency-domain electromagnetic data. Journal of Applied Geophysics, 67(3), 259–268, 2009.
7. Dentith, M., Mudge, S.T. Geophysics for the Mineral Exploration Geoscientist. Cambridge University Press, 2014.
8. Christensen, P.R., Bandfield, J.L., Hamilton, V.E., et al. A thermal emission spectral library of rock-forming minerals. Journal of Geophysical Research: Planets, 105(E4), 9735–9739, 2000.
9. Salisbury, J.W., Walter, L.S., Vergo, N., D'Aria, D.M. Infrared (2.1–25 μm) Spectra of Minerals. Johns Hopkins University Press, 1991.
10. Ramsey, M.S., Christensen, P.R. Mineral abundance determination: Quantitative deconvolution of thermal emission spectra. Journal of Geophysical Research: Solid Earth, 103(B1), 577–596, 1998.
11. Kalman, R.E. A new approach to linear filtering and prediction problems. Journal of Basic Engineering, 82(1), 35–45, 1960.
12. Maybeck, P.S. Stochastic Models, Estimation, and Control. Academic Press, 1979.
13. Bar-Shalom, Y., Li, X.R., Kirubarajan, T. Estimation with Applications to Tracking and Navigation. Wiley, 2001.
14. Julier, S.J., Uhlmann, J.K. A non-divergent estimation algorithm in the presence of correlations. American Control Conference, 1997.
15. Sun, B., Feng, J., Saenko, K. Return of frustratingly easy domain adaptation. AAAI, 2016.
16. Wilkinson, M.D., et al. The FAIR Guiding Principles for scientific data management and stewardship. Scientific Data, 3, 160018, 2016.
17. Peng, R.D. Reproducible research in computational science. Science, 334(6060), 1226–1227, 2011.
18. Powers, D.M.W. Evaluation: from precision, recall and F-measure to ROC, informedness, markedness and correlation. Journal of Machine Learning Technologies, 2(1), 37–63, 2011.
19. Reeves, C.V. Aeromagnetic Surveys: Principles, Practice and Interpretation. Geosoft, 2005.
20. Nabighian, M.N. Electromagnetic Methods in Applied Geophysics. Society of Exploration Geophysicists, 1988.
21. Telford, W.M., Geldart, L.P., Sheriff, R.E. Applied Geophysics. Cambridge University Press, 1990.
22. Hook, S.J., Abbott, E.A., Grove, C., Kahle, A.B., Palluconi, F.D. Use of multispectral thermal infrared data in geological studies. In Remote Sensing for the Earth Sciences, 1999.
23. Gnojek, I., Prichystal, A. A new zinc mineralization detected by airborne gamma-ray spectrometry in northern Moravia (Czechoslovakia). Geoexploration, 23, 491–502, 1985. doi:10.1016/0016-7142(85)90076-6.
24. Kruse, F.A., Lefkoff, A.B., Boardman, J.W., Heidebrecht, K.B., Shapiro, A.T., Barloon, P.J., Goetz, A.F.H. The spectral image processing system (SIPS)—interactive visualization and analysis of imaging spectrometer data. Remote Sensing of Environment, 44(2–3), 145–163, 1993. doi:10.1016/0034-4257(93)90013-N.
