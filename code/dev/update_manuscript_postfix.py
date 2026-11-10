"""Post-fix manuscript updates: numbers that are now wrong + the new findings."""
from pathlib import Path

P = Path(r"D:\A_MineralProspecting\docs\Manuscript_v2_draft.md")
t = P.read_text(encoding="utf-8")
subs = []

# --- abstract: ablation numbers after the normalisation fix -----------------
subs.append((
    "gamma alone wins the ablation (F1 0.519 versus 0.498)",
    "gamma alone wins the ablation (F1 0.522 versus 0.498)"))

# --- 7.4 ablation table (corrected model) ----------------------------------
subs.append((
    "| Gamma | 0.305 | 0.957 | 0.356 | 0.519 | 0.388 | \u22120.136 |\n"
    "| Gamma + TIR | 0.079 | 0.332 | 0.704 | 0.451 | 0.242 | 0.271 |\n"
    "| Gamma + EM | 0.383 | 0.963 | 0.266 | 0.417 | 0.393 | 0.034 |\n"
    "| All (corrected) | 0.174 | 0.858 | 0.351 | 0.498 | 0.216 | 0.290 |",
    "| Gamma | 0.293 | 0.957 | 0.359 | 0.522 | 0.374 | \u22120.109 |\n"
    "| Gamma + TIR | 0.078 | 0.320 | 0.708 | 0.441 | 0.242 | 0.271 |\n"
    "| Gamma + EM | 0.360 | 0.962 | 0.264 | 0.414 | 0.359 | 0.067 |\n"
    "| All (corrected) | 0.174 | 0.858 | 0.351 | 0.498 | 0.215 | 0.290 |"))

# --- 7.4 prose --------------------------------------------------------------
subs.append((
    "Table 8 gives the corrected ablation and Figure 5 shows it. Against the\n"
    "gamma-derived proxy gamma alone reaches F1 0.519, above the full set at 0.498,\n"
    "with gamma+TIR at 0.451 and gamma+EM at 0.417. Against the synthetic TIR truth\n"
    "the ordering reverses and the full set is clearly best: RMSE 0.216 and r 0.290,\n"
    "versus RMSE 0.388 and r = \u22120.136 for gamma alone.",
    "Table 8 gives the corrected ablation and Figure 5 shows it. Against the\n"
    "gamma-derived proxy gamma alone reaches F1 0.522, above the full set at 0.498,\n"
    "with gamma+TIR at 0.441 and gamma+EM at 0.414. Against the synthetic TIR truth\n"
    "the ordering reverses and the full set is clearly best: RMSE 0.215 and r 0.290,\n"
    "versus RMSE 0.374 and r = \u22120.109 for gamma alone."))

# --- 5.4: sign agreement is now 0/6, gains recomputed ----------------------
subs.append((
    "**Every added modality lowers the analytic variance.** `G` is positive in all\n"
    "six cases: `+TIR` 0.734, `+EM` 0.804 and `+TIR+EM` 0.917 under the legacy\n"
    "matrix, and 0.419, 0.596 and 0.692 under the corrected one.",
    "**Every added modality lowers the analytic variance.** `G` is positive in all\n"
    "six cases: `+TIR` 0.409, `+EM` 0.411 and `+TIR+EM` 0.750 under the legacy\n"
    "matrix, and 0.409, 0.570 and 0.673 under the corrected one."))

subs.append((
    "The sign of `G` agrees with the sign\n"
    "of the observed change in F1 in only **one of six** additions. The legacy `+EM`\n"
    "case is decisive: it has the largest predicted gain (0.804), reduces the\n"
    "estimator variance, and produces the worst F1 change (\u22120.133).",
    "The sign of `G` agrees with the sign\n"
    "of the observed change in F1 in **none of six** additions. The legacy `+EM`\n"
    "case is decisive: it lowers the estimator variance (G = 0.411) and produces the\n"
    "worst F1 change (\u22120.330)."))

subs.append((
    "the legacy matrix the EM block carries\n"
    "**98.2 %** of the squared norm of the clay column (gamma 1.5 %, TIR 0.3 %), so a",
    "the legacy matrix the EM block carries\n"
    "**98.2 %** of the squared norm of the clay column (gamma 1.5 %, TIR 0.3 %), so a"))

# --- 8.1: the gain-index sentence ------------------------------------------
subs.append((
    "in this study the largest variance gain (0.804, legacy `+EM`) coincided with the worst accuracy change",
    "in this study a positive variance gain (0.411, legacy `+EM`) came with the worst accuracy change"))

for a, b in subs:
    n = t.count(a)
    if n != 1:
        print("MISS", n, a[:60].replace("\n", " "))
    t = t.replace(a, b)

P.write_text(t, encoding="utf-8")
print("manuscript updated")
