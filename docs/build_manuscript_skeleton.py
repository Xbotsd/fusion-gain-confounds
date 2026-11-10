"""Build the v2 manuscript skeleton (DOCX) from docs/PAPER_STRUCTURE_V2.md."""
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "Manuscript_v2_skeleton.docx"

GRAY = RGBColor(0x66, 0x66, 0x66)
BLUE = RGBColor(0x1F, 0x4E, 0x79)


def set_normal(doc):
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), "SimSun")
    pf = style.paragraph_format
    pf.line_spacing = 1.5
    pf.space_after = Pt(6)


def note(doc, text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.italic = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = GRAY
    p.paragraph_format.space_after = Pt(4)
    return p


def bullets(doc, items):
    for item in items:
        p = doc.add_paragraph(item, style="List Bullet")
        p.paragraph_format.space_after = Pt(2)


def table(doc, caption, headers, rows, widths=None):
    cap = doc.add_paragraph()
    r = cap.add_run(caption)
    r.bold = True
    r.font.size = Pt(9.5)
    cap.paragraph_format.space_before = Pt(8)
    cap.paragraph_format.space_after = Pt(3)
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(9)
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            run = cells[i].paragraphs[0].add_run(str(val))
            run.font.size = Pt(9)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = w
    return t


def main():
    doc = Document()
    set_normal(doc)

    # ------------------------------------------------------------------ title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(
        "When does multi-modal fusion improve airborne mineral exploration? "
        "An identifiability analysis and reproducible benchmark"
    )
    run.bold = True
    run.font.size = Pt(16)
    run.font.color.rgb = BLUE

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run("Structural skeleton v2  |  target: IEEE JSTARS (primary), "
                    "Computers & Geosciences (fallback)")
    r.italic = True
    r.font.size = Pt(10)
    r.font.color.rgb = GRAY

    doc.add_paragraph()
    meta = table(
        doc,
        "Manuscript metadata",
        ["Item", "Value"],
        [
            ["Article type", "Paper (original research)"],
            ["Word budget", "9,000–10,000 words (excluding references)"],
            ["Figures / tables", "8–9 figures, 6–7 tables"],
            ["Data", "Real USGS gamma (Ivanpah, NV–CA, 2019–2020) + documented synthetic TIR/EM"],
            ["Code", "code/ (14 scripts, run_all.py), processed/ (results)"],
            ["Novelty", "Fusion gain index + reproducible benchmark + method audit"],
        ],
        widths=None,
    )
    doc.add_paragraph()
    note(doc, "HOW TO USE — Keep the section order. Each [P#] is one paragraph; "
              "replace the prompt with prose. Do not reintroduce the AI-residual, "
              "Jetson or +104% claims. Numbers in brackets are the cleaned values "
              "from processed/*.json; re-run before submission.")

    # --------------------------------------------------------------- abstract
    doc.add_heading("Abstract", level=1)
    abstract = (
        "Multi-modal fusion is widely proposed to improve airborne mineral "
        "exploration, yet reported gains are rarely comparable because studies use "
        "different response matrices, synthetic augmentation recipes and metric "
        "definitions. We present a reproducible benchmark built on the real USGS "
        "airborne radiometric survey of the Ivanpah–Clark Mountain area "
        "(Nevada–California, 2019–2020), with physically informed synthetic "
        "thermal-infrared and electromagnetic modalities generated from documented "
        "endmembers and AEM statistics. The benchmark fixes one response matrix, one "
        "valid-pixel mask and one contingency-table metric, and then varies modality "
        "set, sensor degradation, temperature, domain shift, response-matrix "
        "perturbation, resolution and random seed. We derive a fusion gain index from "
        "the clay-estimate variance and show that it predicts when adding a modality "
        "helps. Across the experiments, tri-modal fusion does not improve agreement "
        "with the gamma-derived alteration proxy over gamma+TIR; the electromagnetic "
        "modality produces a negative gain because its response is mis-specified; and "
        "the widely quoted +104 % fusion gain is reproduced only by mixing two "
        "incompatible response matrices. We release the code, data recipe and audit "
        "scripts, and recommend reporting recall, precision and F1 together with an "
        "explicit statement of the evaluation target."
    )
    doc.add_paragraph(abstract)
    note(doc, "[TODO: 200–250 words; add one sentence on the application relevance "
              "and one on the released artefacts. Do not claim a mineral discovery.]")

    doc.add_heading("Highlights", level=1)
    bullets(doc, [
        "One response matrix, one mask and one metric across all fusion experiments.",
        "A fusion gain index predicts when adding a modality improves clay estimability.",
        "Tri-modal fusion does not beat gamma+TIR on a gamma-derived proxy.",
        "EM mis-specification produces negative gain; the +104 % claim is a matrix artefact.",
        "Code, synthetic recipes and audit scripts are released for reuse.",
    ])

    # ------------------------------------------------------------ 1 introduction
    doc.add_heading("1. Introduction", level=1)
    note(doc, "Target: 1,300 words. End with a clear gap statement, not with a system pitch.")
    doc.add_heading("1.1 Context and single-modality limits", level=2)
    note(doc, "[P1] Airborne gamma-ray spectrometry, EM induction and TIR are routine in "
              "mineral exploration. State the physical limit of each (gamma ~30 cm; EM "
              "non-uniqueness and conductive overburden; TIR sensitivity to moisture and "
              "dust). Cite 3–5 representative studies.")
    note(doc, "[P2] Multi-modal fusion is proposed as the remedy. Reported gains range "
              "from marginal to >100 %, but the experimental settings are not comparable.")
    doc.add_heading("1.2 Three failure modes in the literature", level=2)
    note(doc, "[P3] (i) Response-matrix inconsistency: ablation and validation use "
              "different H. (ii) Synthetic circularity: TIR/EM are generated from "
              "gamma-derived fields and then evaluated against another gamma-derived "
              "target. (iii) Metric inflation: pixel coverage and recall are both called "
              "'detection rate'.")
    doc.add_heading("1.3 Research questions", level=2)
    note(doc, "[P4] RQ1: under what conditions does adding a modality reduce the clay "
              "estimate variance? RQ2: why are reported fusion gains hard to reproduce? "
              "RQ3: what benchmark protocol makes the comparison reproducible?")
    doc.add_heading("1.4 Contributions", level=2)
    bullets(doc, [
        "A unified benchmark: real gamma + documented synthetic TIR/EM, one H, one mask, one metric.",
        "A fusion gain index derived from the clay-estimate variance.",
        "A quantitative audit of the three failure modes; the +104 % gain is a matrix artefact.",
        "Open code, recipes and audit scripts, with recommendations for future studies.",
    ])
    note(doc, "[P6] One paragraph of paper organisation.")

    # ------------------------------------------------------------ 2 related work
    doc.add_heading("2. Related work", level=1)
    note(doc, "Target: 1,000 words. End each subsection with 'therefore ...'.")
    for sub, prompt in [
        ("2.1 Single-modality mineral exploration",
         "Gamma (K/eU/eTh, alteration indices), EM (conductivity, non-uniqueness), TIR "
         "(Reststrahlen bands). 3–5 references each."),
        ("2.2 Multi-modal fusion",
         "Bayesian, WLS, Kalman, PCA and deep fusion; most report 'fusion is better' "
         "without an identifiability analysis."),
        ("2.3 Evaluation and reproducibility",
         "Benchmarks, metric definitions, synthetic-data circularity and negative results "
         "in geoscience/remote sensing."),
        ("2.4 Gap",
         "No common H/mask/metric benchmark; no 'when does fusion help' criterion; no "
         "quantification of synthetic circularity."),
    ]:
        doc.add_heading(sub, level=2)
        note(doc, prompt)

    # ------------------------------------------------------ 3 data and benchmark
    doc.add_heading("3. Data and benchmark design", level=1)
    note(doc, "Target: 1,600 words. This section must make the real/synthetic boundary "
              "unambiguous.")
    doc.add_heading("3.1 Real airborne radiometrics", level=2)
    note(doc, "[P1] USGS Ivanpah–Clark Mountain survey, 2019-12-13 to 2020-03-21, "
              "295,943 samples at 1 Hz, 631 lines, 47 flights, 50 m grid, 1772×1075, "
              "66.4 % valid pixels. State the projection and the K/eU/eTh medians.")
    note(doc, "[P2] The corrected CSV channels and the three GXF grids agree to three "
              "decimals; give the numbers. Explain the valid mask.")
    doc.add_heading("3.2 Synthetic TIR", level=2)
    note(doc, "[P3] 8–14 µm, 200 bands, splib07 endmembers, TIR = sum_m a_m (1 - R_m); "
              "no sensor noise in the final recipe; list the four bands used.")
    doc.add_heading("3.3 Synthetic EM", level=2)
    note(doc, "[P4] 40 layers, 0–600 m, Wisconsin AEM layer statistics, seed 12345, "
              "controlled correlated field; state the correlation with clay_prior.")
    doc.add_heading("3.4 Two clay truths", level=2)
    note(doc, "[P5] TIR truth (0.3K + 0.3Th; mean 0.30) vs EM truth (clay_prior; mean "
              "0.46 full, 0.49 valid); correlation 0.57. This is the structural problem "
              "the benchmark audits; do not hide it.")
    doc.add_heading("3.5 Benchmark protocol", level=2)
    note(doc, "[P6] One H, one valid mask, one metric, fixed seeds. No train/test split "
              "(unsupervised inversion); use leave-channel-out and modality ablation "
              "instead. State that all metrics are computed on valid pixels only.")
    doc.add_heading("3.6 Metric definitions", level=2)
    note(doc, "[P7] Positive = clay > 0.25 and clay in the top-2 minerals; target = "
              "clay_prior > 0.55; report recall, precision, F1, IoU; never call it a "
              "'detection rate'.")

    table(
        doc,
        "Table 1. Data layers and their role in the benchmark.",
        ["Layer", "Source", "Extent / resolution", "Role"],
        [
            ["Gamma K/eU/eTh", "Real USGS Ivanpah", "1772×1075, 50 m", "Only real modality"],
            ["TIR", "Synthetic splib07", "200 bands, 50 m", "Controlled augmentation"],
            ["EM", "Synthetic AEM stats", "40 layers, 50 m", "Controlled augmentation"],
            ["clay_prior", "Derived from gamma", "50 m", "Evaluation proxy"],
            ["TIR truth", "Derived from gamma", "50 m", "Synthetic TIR target"],
        ],
    )
    table(
        doc,
        "Table 2. Metric definitions used in every experiment.",
        ["Term", "Definition"],
        [
            ["Positive pixel", "clay > 0.25 AND clay in top-2 minerals"],
            ["Target", "clay_prior > 0.55"],
            ["Recall", "TP / (TP + FN)"],
            ["Precision", "TP / (TP + FP)"],
            ["F1", "2PR / (P + R)"],
            ["IoU", "TP / (TP + FP + FN)"],
            ["Mask", "Valid survey pixels only (66.4 %)"],
        ],
    )

    # ---------------------------------------------------------------- 4 methods
    doc.add_heading("4. Methods", level=1)
    note(doc, "Target: 1,600 words. Keep equations minimal; put derivations in Section 5.")
    for sub, prompt in [
        ("4.1 Observation model and response matrix",
         "z (10×1), H (10×5), a (5×1); one table of H; state that H is a relative "
         "signature matrix, not absolute concentration."),
        ("4.2 Weighted least squares",
         "x = (H^T W H + λI)^-1 H^T W z; λ = 0.1; non-negative + closure; note the "
         "column-normalisation caveat."),
        ("4.3 Spatial Kalman",
         "F = I, Q = 0.005, R_obs = 0.02; forward filter only; P is a filter variance, "
         "not a calibrated interval."),
        ("4.4 Depth Kalman",
         "40 layers, F = 0.85I + 0.15/N, Q = 0.03, depth-dependent H/R; state that "
         "surface gamma/TIR are repeated at every layer."),
        ("4.5 Quality weights",
         "W = diag(q), higher q = more weight; q(T, RH, fault); uniform in the main "
         "run, quality weights in the scenario experiments."),
        ("4.6 Baselines",
         "Independent, simple average, fixed weight, PCA, GLS/Bayesian, ours."),
        ("4.7 Uncertainty calibration",
         "Coverage, reliability diagram and a simple rescaling; report in 7.7."),
    ]:
        doc.add_heading(sub, level=2)
        note(doc, prompt)

    # ------------------------------------------------------ 5 identifiability
    doc.add_heading("5. Identifiability and fusion gain", level=1)
    note(doc, "Target: 1,200 words. This is the theoretical contribution; do not skip it.")
    for sub, prompt in [
        ("5.1 Variance of the clay estimate",
         "Derive Var(x_clay) from the WLS estimator, including H, W and the channel "
         "noise covariance Sigma."),
        ("5.2 Condition number and weight sensitivity",
         "Define kappa(H) and show how EM rows with low clay resistivity but high "
         "resistivity for the other minerals create a negative gain."),
        ("5.3 Fusion gain index",
         "G = 1 - Var_clay(S ∪ m) / Var_clay(S); G > 0 means the modality helps."),
        ("5.4 Predicted vs observed gain",
         "Compare the sign/ranking of G with the ablation results; Figure 4."),
    ]:
        doc.add_heading(sub, level=2)
        note(doc, prompt)

    # ------------------------------------------------------------- 6 experiments
    doc.add_heading("6. Experiments", level=1)
    note(doc, "Target: 900 words. Describe the design, not the numbers.")
    table(
        doc,
        "Table 3. Experiment matrix.",
        ["ID", "Question", "Variable", "Metric", "Repeats"],
        [
            ["E1", "Does each modality help?", "Modality set", "Recall/P/R/F1, gain", "1"],
            ["E2", "Fault tolerance", "Noise + quality weight", "Recall/P/F1", "1"],
            ["E3", "Temperature", "−60…+80 °C", "Recall/P/F1", "1"],
            ["E4", "Domain shift", "Target transform, CORAL", "Recall/F1/gap", "1"],
            ["E5", "H robustness", "±5…30 %", "Recall mean/std", "5"],
            ["E6", "Resolution", "50…800 m", "Recall/time", "1"],
            ["E7", "Random seed", "20 realisations", "Mean/std/CI", "20"],
            ["E8", "Baselines", "6 methods", "Clay/gradient/F1", "1"],
        ],
    )

    # ---------------------------------------------------------------- 7 results
    doc.add_heading("7. Results", level=1)
    note(doc, "Target: 2,200 words. Every subsection: question → setup → numbers → "
              "interpretation → limitation.")
    results = [
        ("7.1 Main fusion and uncertainty",
         "[P1] Normal operation: clay 0.458, recall 0.693, precision 0.165, F1 0.267, "
         "mean variance 0.008. Figure 5."),
        ("7.2 Ablation and fusion gain",
         "[P2] Gamma 0.342/0.325, gamma+TIR 0.392/0.339, gamma+EM 0.351/0.191, all "
         "0.458/0.267. The +104 % claim does not reproduce; Table 4, Figure 6."),
        ("7.3 Sensor degradation",
         "[P3] Normal 0.693, EMI failed 0.976, TIR degraded 0.433, gamma degraded 0.602. "
         "EM produces negative gain; this is not graceful degradation."),
        ("7.4 Temperature",
         "[P4] −60 °C 0.352, 25 °C 0.690, +80 °C 0.348; temperature is the dominant "
         "degradation axis. Figure 7."),
        ("7.5 Cross-domain",
         "[P5] Direct 0.692, CORAL 0.689; gap 0.08 % to 0.17 %. CORAL does not help "
         "because the synthetic shift is a per-channel scaling removed by z-scoring."),
        ("7.6 H robustness and baselines",
         "[P6] ±30 %: 0.659 ± 0.228. Ours has the highest clay and smoothest map, but "
         "independent inversion has the best F1. Table 6."),
        ("7.7 Uncertainty calibration",
         "[P7] Report 68/95 % coverage, reliability diagram, calibration error before/"
         "after rescaling. Table 7, Figure 8."),
        ("7.8 Resolution and seed",
         "[P8] 50→800 m: recall 0.693→0.759; 20 seeds: 0.6933 ± 0.0001. Coarser grids "
         "smooth the proxy upward; this is an aggregation effect. Figure 9."),
    ]
    for sub, prompt in results:
        doc.add_heading(sub, level=2)
        note(doc, prompt)

    table(
        doc,
        "Table 4. Ablation (one H, valid pixels).",
        ["Configuration", "Clay", "Gradient", "Recall", "Precision", "F1", "Gain"],
        [
            ["Gamma", "0.342", "0.00673", "0.773", "0.205", "0.325", "—"],
            ["Gamma + TIR", "0.392", "0.00406", "0.973", "0.205", "0.339", "TODO"],
            ["Gamma + EM", "0.351", "0.00779", "0.392", "0.127", "0.191", "TODO"],
            ["All", "0.458", "0.00664", "0.693", "0.165", "0.267", "TODO"],
        ],
    )
    table(
        doc,
        "Table 5. Degradation and temperature.",
        ["Scenario", "Recall", "Precision", "F1", "Weight shift"],
        [
            ["Normal", "0.693", "0.165", "0.267", "—"],
            ["EMI failed ×20", "0.976", "0.202", "0.334", "EM down"],
            ["TIR degraded ×5", "0.433", "0.134", "0.204", "TIR down"],
            ["Gamma degraded ×5", "0.602", "0.109", "0.184", "Gamma down"],
            ["T = −60 °C", "0.352", "0.116", "0.175", "TIR down"],
            ["T = +80 °C", "0.348", "0.109", "0.167", "TIR down"],
        ],
    )
    table(
        doc,
        "Table 6. Baseline comparison.",
        ["Method", "Clay", "Gradient", "Recall", "F1", "Runtime (s)"],
        [
            ["Independent", "0.221", "0.01535", "0.701", "0.360", "TODO"],
            ["Simple average", "0.028", "0.01625", "0.036", "0.066", "TODO"],
            ["Fixed weight", "0.353", "0.00923", "0.383", "0.179", "TODO"],
            ["PCA (3 comp.)", "0.020", "0.00805", "0.013", "0.026", "TODO"],
            ["GLS / Bayesian", "0.315", "0.01821", "0.673", "0.326", "TODO"],
            ["WLS + Kalman", "0.458", "0.00664", "0.693", "0.267", "TODO"],
        ],
    )
    table(
        doc,
        "Table 7. Uncertainty calibration.",
        ["Nominal coverage", "Empirical coverage", "Calibration error", "After rescaling"],
        [
            ["68 %", "TODO", "TODO", "TODO"],
            ["95 %", "TODO", "TODO", "TODO"],
        ],
    )

    # -------------------------------------------------------------- 8 discussion
    doc.add_heading("8. Discussion", level=1)
    note(doc, "Target: 1,300 words. Separate 'what we found' from 'what it means'.")
    for sub, prompt in [
        ("8.1 When fusion helps",
         "G > 0 conditions; H conditioning, modality noise, target definition."),
        ("8.2 Why the EM response is mis-specified",
         "Raw ohm.m linear mixing plus five-mineral response; clay is attributed to the "
         "wrong minerals. Recommended fix: log10(rho) + clay-only row."),
        ("8.3 Metric and benchmark implications",
         "Proxy recall is not geological accuracy; report precision/F1; coverage is not "
         "detection rate; synthetic recipes must be released."),
        ("8.4 Limitations",
         "Synthetic TIR/EM, two clay truths, no independent ground truth, no hardware, "
         "depth model repeats surface modalities."),
        ("8.5 Recommendations",
         "Single truth field, log-EM, uncertainty calibration, real multi-modal data, "
         "pre-registered benchmark protocols."),
    ]:
        doc.add_heading(sub, level=2)
        note(doc, prompt)

    # -------------------------------------------------------------- 9 conclusion
    doc.add_heading("9. Conclusion", level=1)
    note(doc, "[P1] Under one H and one metric, tri-modal fusion does not beat gamma+TIR "
              "on the gamma-derived proxy. [P2] The +104 % claim is a matrix artefact. "
              "[P3] The fusion gain index predicts when a modality helps. [P4] Report "
              "recall, precision and F1 with an explicit target, and release recipes.")

    # ------------------------------------------------------- reproducibility
    doc.add_heading("Reproducibility and data availability", level=1)
    note(doc, "Code: 14 scripts under code/, one-command run_all.py. Data: real gamma "
              "source/DOI [TODO]; synthetic recipes and seeds in docs/DATA_PROVENANCE.md. "
              "Environment: Python 3.10, GDAL, scipy. Runtime: main fusion ~10 s on CPU; "
              "depth ~[TODO] min. Raw CSV may be subject to USGS terms; derived grids and "
              "scripts are released.")

    doc.add_heading("References", level=1)
    note(doc, "[TODO: 35–45 references. Suggested blocks: gamma spectrometry (5–7), EM "
              "(5–7), TIR (5–7), fusion/Kalman (8–10), evaluation/reproducibility (5–7), "
              "USGS/AEM data (3–5). Use the target journal style.]")

    # ------------------------------------------------------------- figure list
    doc.add_heading("Figure captions (to be placed after first citation)", level=1)
    figs = [
        ("Figure 1.", "Real gamma, synthetic TIR/EM and the clay_prior proxy."),
        ("Figure 2.", "Benchmark protocol: one H, one mask, one metric, fixed seeds."),
        ("Figure 3.", "WLS + spatial Kalman + depth Kalman pipeline."),
        ("Figure 4.", "Fusion gain index: predicted vs observed."),
        ("Figure 5.", "Main result: five minerals and posterior variance."),
        ("Figure 6.", "Ablation: clay, F1 and gain."),
        ("Figure 7.", "Degradation and temperature."),
        ("Figure 8.", "Uncertainty calibration: coverage and reliability."),
        ("Figure 9.", "Resolution, seed and H robustness."),
    ]
    for tag, cap in figs:
        p = doc.add_paragraph()
        r = p.add_run(tag + " ")
        r.bold = True
        p.add_run(cap)

    # --------------------------------------------------------- author note
    doc.add_page_break()
    doc.add_heading("Author note — not part of the manuscript", level=1)
    note(doc, "Cut from the old draft: Section 4 (AI residual), 2.2 three-level "
              "degradation, 2.3 Jetson/<200 ms, drift/env state, +104 %, 65.26 % as "
              "detection rate, CORAL 5.22→0.27 %, 'Colorado Mineral Belt'.")
    note(doc, "Add before submission: Related Work (35–45 refs), fusion gain derivation, "
              "uncertainty calibration, gamma-only real-data experiment, statistical "
              "tests, figures, tables, Code/Data statement.")
    note(doc, "Every number in this skeleton comes from processed/*.json after the "
              "cleaned run; re-run code/run_all.py before submission.")

    doc.save(OUT)
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()
