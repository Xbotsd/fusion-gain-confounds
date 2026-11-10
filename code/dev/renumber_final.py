"""Final numbering pass: tables 1-9 and figures 1-6 in order of appearance."""
from pathlib import Path

P = Path(r"D:\A_MineralProspecting\docs\Manuscript_v2_draft.md")
t = P.read_text(encoding="utf-8")

# --- tables: H-rows table becomes Table 3; 3..8 shift to 4..9 (descending) ---
for n in range(8, 2, -1):
    t = t.replace(f"**Table {n}.**", f"**Table {n + 1}.**")
    t = t.replace(f"Table {n}. ", f"Table {n + 1}. ")

# caption the response-matrix table (the first table block after '### 4.1')
anchor = "Quartz falls to 0.16–0.26 in the reststrahlen region"
t = t.replace(anchor, "**Table 3.** TIR rows of the response matrix: USGS splib07 "
                       "emissivity of each mineral averaged over the ASTER band "
                       "pass, not hand-set.\n\n| band (µm) | Quartz | Feldspar | "
                       "Clay | Calcite | Dolomite |\n|---:|---:|---:|---:|---:|---:|"
                       "\n| 8.291 | 0.255 | 0.765 | 0.992 | 0.814 | 0.937 |"
                       "\n| 8.634 | 0.410 | 0.712 | 0.993 | 0.811 | 0.932 |"
                       "\n| 9.075 | 0.157 | 0.789 | 0.935 | 0.756 | 0.923 |"
                       "\n| 10.657 | 0.902 | 0.847 | 0.921 | 0.756 | 0.888 |"
                       "\n| 11.289 | 0.925 | 0.872 | 0.957 | 0.857 | 0.864 |"
                       "\n\n" + anchor, 1)

# the old hand table right above the anchor must go (it is now duplicated)
old = ("| band (µm) | Quartz | Feldspar | Clay | Calcite | Dolomite |\n"
       "|---:|---:|---:|---:|---:|---:|\n"
       "| 8.291 | 0.255 | 0.765 | 0.992 | 0.814 | 0.937 |\n"
       "| 8.634 | 0.410 | 0.712 | 0.993 | 0.811 | 0.932 |\n"
       "| 9.075 | 0.157 | 0.789 | 0.935 | 0.756 | 0.923 |\n"
       "| 10.657 | 0.902 | 0.847 | 0.921 | 0.756 | 0.888 |\n"
       "| 11.289 | 0.925 | 0.872 | 0.957 | 0.857 | 0.864 |\n\n")
if t.count(old) == 2:
    t = t.replace(old, "", 1)

# --- figures: identifiability 5 -> 3, maps 3 -> 4, ablation 4 -> 5 ----------
t = t.replace("**Figure 5.** Identifiability diagnostics", "**Figure Z.** Identifiability diagnostics")
t = t.replace("**Figure 3.** Clay abundance from the real-ASTER", "**Figure Y.** Clay abundance from the real-ASTER")
t = t.replace("**Figure 4.** Ablation on both targets", "**Figure X.** Ablation on both targets")
t = t.replace("**Figure Z.**", "**Figure 3.**").replace("**Figure Y.**", "**Figure 4.**").replace("**Figure X.**", "**Figure 5.**")

# in-text references to the moved figures
t = t.replace("Table 5. The information test", "Table 6. The information test")
t = t.replace("the model-free test in Table 5", "the model-free test in Table 6")
P.write_text(t, encoding="utf-8")

import re
print("tables:", re.findall(r"^\*\*Table (\d+)\.", t, re.M))
print("figures:", re.findall(r"^\*\*Figure (\d+)\.", t, re.M))
print("table blocks:", len(re.findall(r"^\|---", t, re.M)))
