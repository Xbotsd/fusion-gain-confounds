"""Move table captions inline and place figures at first citation.

Before: 12 tables with captions collected in a `## Tables` list at the end, and
six figures appended after the references with no caption in the body.

After: each table carries `**Table N.** ...` immediately above it, and each
figure carries a `<!-- FIGURE:file -->` directive plus `**Figure N.** ...` right
after the paragraph that first cites it. The docx builder renders the directive
as the image and the caption as an italic centred line.
"""
import re
from pathlib import Path

P = Path(r"D:\A_MineralProspecting\docs\Manuscript_v2_draft.md")

TABLES = [
    "Data layers, sources, resolution and role in the observation vector.",
    "Metric definitions: positive rule, target, mask and aggregation.",
    "Legacy model: modality configuration, clay abundance, gradient, recall, "
    "precision and F1 on the valid mask.",
    "Legacy model: estimator comparison (clay abundance, gradient, recall, "
    "precision, F1).",
    "Legacy model: coherence comparison (average precision, matched-prevalence "
    "precision, connected components, mean patch size).",
    "Response-matrix lever: single-row perturbation and the clay-only log10 EM "
    "row.",
    "Corrected-EM model against independent inversion, GLS/Bayesian fusion and "
    "the legacy estimator.",
    "Modality ablation under the corrected model, including the independent TIR "
    "truth.",
    "Robustness scenarios under the corrected model, with 128-px block-bootstrap "
    "confidence intervals and Benjamini-Hochberg-corrected paired tests.",
    "Depth-Kalman layer means of the five minerals, legacy versus corrected EM.",
    "Uncertainty calibration: nominal versus empirical coverage and the "
    "variance-scale factor.",
    "Published single-modality and ratio methods with their references.",
]

FIGURES = [
    ("fig_data.png",
     "Real radiometric channels, the synthetic TIR and EM cubes and the "
     "clay_prior proxy on the 50 m grid."),
    ("fig_method.png",
     "Benchmark protocol and estimator chain: weighted least squares, spatial "
     "Kalman filter and depth Kalman."),
    ("fig_results.png",
     "Legacy fusion result: mineral abundance maps and posterior variance."),
    ("ablation.png",
     "Modality ablation: clay abundance, F1 and spatial gradient for the four "
     "configurations."),
    ("validation.png",
     "Robustness: scenario recall and the temperature sweep."),
    ("em_fix.png",
     "Legacy versus corrected EM: F1 and map fragmentation."),
]


def main():
    text = P.read_text(encoding="utf-8")

    # drop the trailing caption list
    if "## Tables" in text:
        text = text[:text.index("## Tables")].rstrip() + "\n"

    lines = text.split("\n")

    # ---- figures: insert after the paragraph that first cites them --------
    for n, (fname, cap) in enumerate(FIGURES, start=1):
        pat = re.compile(rf"\bFigure {n}\b")
        idx = next(i for i, l in enumerate(lines)
                   if pat.search(l) and not l.startswith("!")
                   and not l.startswith("**Figure"))
        j = idx
        while j + 1 < len(lines) and lines[j + 1].strip():
            j += 1
        block = ["", f"<!-- FIGURE:{fname} -->", f"**Figure {n}.** {cap}", ""]
        lines[j + 1:j + 1] = block

    # ---- tables: caption immediately above each table block ---------------
    out, t_i, i = [], 0, 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|"):
            t_i += 1
            out.append(f"**Table {t_i}.** {TABLES[t_i - 1]}")
            out.append("")
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                out.append(lines[i])
                i += 1
            continue
        out.append(lines[i])
        i += 1

    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    P.write_text(text, encoding="utf-8")
    print("tables captioned:", t_i, "figures inserted:", len(FIGURES))


if __name__ == "__main__":
    main()
