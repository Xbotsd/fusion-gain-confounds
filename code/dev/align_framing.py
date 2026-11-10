"""Align abstract / highlights / contributions / conclusion with Section 7."""
import re
from pathlib import Path

P = Path(r"D:\A_MineralProspecting\docs\Manuscript_v2_draft.md")
t = P.read_text(encoding="utf-8")

ABS = """Multi-modal fusion is widely proposed to improve airborne mineral exploration, yet reported gains are rarely comparable because studies use different response matrices, synthetic augmentation recipes and metric definitions. We present a reproducible benchmark on the real USGS airborne radiometric survey of the Ivanpah–Clark Mountain area (Nevada–California, 2019–2020), with documented synthetic thermal-infrared (TIR) and electromagnetic (EM) modalities. The benchmark fixes one response matrix, one valid-pixel mask and one contingency-table metric, and varies modality set, sensor degradation, temperature, domain shift, response-matrix perturbation, resolution and seed. We first show that the legacy fusion model has no gain, and we diagnose the cause: its EM row uses raw resistivity with five mineral responses, so after column normalisation the EM field is attributed to the wrong minerals. Expressing EM as log10 resistivity with a clay-only response raises proxy F1 from 0.267 to 0.498 and average precision from 0.126 to 0.513, above every generic baseline, with a 128-px block-bootstrap gain of +0.167 [0.118, 0.216] over independent inversion and a ten-run F1 of 0.49816 ± 0.00005. The corrected model is also far more robust: temperature-family recall rises from 0.476 to 0.912, and depth clay now decreases rather than increases with depth. We then show the limit of the exercise. Because the evaluation target is a gamma-derived index, two published gamma ratios beat the fusion on it (F-parameter AP 0.650, low eTh/K 0.572), gamma alone beats the full set in ablation (F1 0.519 versus 0.498), and losing both auxiliary modalities is statistically indistinguishable from normal (BH p = 0.90); on an independent synthetic TIR truth the ordering reverses and fusion is best. Reporting a fusion gain therefore requires stating the target, and a gamma-derived target cannot demonstrate multimodal superiority. We release the code, recipes, audit scripts and a coverage guard, and recommend that fusion studies report recall, precision and F1 with published single-modality baselines, spatial-autocorrelation-corrected uncertainty (effective sample size here is ~110-175, not 1.27 million) and an explicit statement of what the target actually measures."""

t = re.sub(r"(## Abstract\n\n).*?(\n\n\*\*Keywords)", lambda m: m.group(1) + ABS + m.group(2),
           t, count=1, flags=re.S)

HL = """## Highlights

- Legacy fusion has no gain; the cause is a raw-resistivity, five-mineral EM row.
- Log10 clay-only EM raises F1 from 0.267 to 0.498 and AP from 0.126 to 0.513.
- The gain survives 128-px block bootstrap (+0.167 [0.118, 0.216]) and ten repeats.
- Published gamma ratios still beat fusion on a gamma-derived target (AP 0.650).
- Effective sample size is ~110-175, not 1.27 million pixels; all CIs are block-level.
- The +104 % claim is a matrix artefact; a coverage guard prevents missing scripts."""

t = re.sub(r"## Highlights\n\n(?:- .*\n)+", HL + "\n", t, count=1)

CONTRIB = """Our contributions are five. (i) We build a reproducible benchmark with one response matrix, one valid-pixel mask and one metric definition, together with a coverage guard that fails if any validated artefact lacks a producing script. (ii) We derive a fusion gain index from the clay-estimate variance and show that it predicts the sign of the observed modality effect. (iii) We diagnose a specific and common mis-specification — raw-resistivity, multi-mineral EM — and show that correcting it to a log10 clay-only response raises proxy F1 from 0.267 to 0.498. (iv) We quantify the limit of the exercise: on a gamma-derived target, published gamma ratios and gamma alone beat the fusion, so a fusion gain reported against such a target cannot demonstrate multimodal superiority. (v) We give a protocol that makes multi-modal evaluation comparable, including block-bootstrap uncertainty at the measured spatial integral scale and a check that the effective sample size is reported."""

t = re.sub(r"Our contributions are four\..*?future multi-modal studies\.",
           CONTRIB, t, count=1, flags=re.S)

CONC = """## 9. Conclusion

Under one response matrix, one mask and one metric, the legacy tri-modal fusion does not improve agreement with the gamma-derived alteration proxy, and the widely quoted +104 % gain is a matrix artefact. The failure is diagnosable: a raw-resistivity EM row with five mineral responses misassigns the EM field, and expressing EM as log10 resistivity with a clay-only response raises proxy F1 from 0.267 to 0.498 and average precision from 0.126 to 0.513, significantly above independent inversion and GLS, and stable across ten repeats and a 128-px block bootstrap.

The same benchmark also bounds the claim. Because the target is a gamma-derived index, gamma alone wins the ablation and two published gamma ratios (F-parameter AP 0.650, low eTh/K 0.572) outperform the fusion; losing both auxiliary modalities is statistically indistinguishable from normal. On an independent synthetic TIR truth the ordering reverses and the fused estimate is best. A fusion gain is therefore meaningful only relative to a stated target, and a gamma-derived target cannot demonstrate multimodal superiority. We recommend that multi-modal studies report recall, precision and F1 against published single-modality baselines, correct for spatial autocorrelation, and state what their target measures."""

t = re.sub(r"## 9\. Conclusion\n\n.*?(?=\n## )", CONC + "\n\n", t, count=1, flags=re.S)

P.write_text(t, encoding="utf-8")
print("abstract/highlights/contributions/conclusion updated; chars:", len(t))
