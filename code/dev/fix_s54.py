"""Update Section 5.4 with the post-normalisation-fix numbers."""
from pathlib import Path

P = Path(r"D:\A_MineralProspecting\docs\Manuscript_v2_draft.md")
t = P.read_text(encoding="utf-8")

PAIRS = [
    ("`+TIR` 0.734, `+EM` 0.804 and `+TIR+EM` 0.917 under the legacy matrix, "
     "and 0.419, 0.596 and 0.692 under the corrected one.",
     "`+TIR` 0.409, `+EM` 0.411 and `+TIR+EM` 0.750 under the legacy matrix, "
     "and 0.409, 0.570 and 0.673 under the corrected one."),
    ("Magnitudes differ by up to 0.61 in `G`: legacy `+EM` is predicted at 0.804 "
     "and measured at 0.197,",
     "Magnitudes differ in `G`: legacy `+TIR` is predicted at 0.409 and measured "
     "at 0.765,"),
    ("in only **one of six** additions. The legacy `+EM` case is decisive: it has "
     "the largest predicted gain (0.804), reduces the estimator variance, and "
     "produces the worst F1 change (\u22120.133).",
     "in **none of six** additions. The legacy `+EM` case is decisive: it lowers "
     "the estimator variance (G = 0.411) and produces the worst F1 change "
     "(\u22120.330)."),
]

for a, b in PAIRS:
    n = t.count(a)
    print(n, a[:50])
    t = t.replace(a, b)

P.write_text(t, encoding="utf-8")
print("done")
