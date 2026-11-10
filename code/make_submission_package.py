"""Build the submission package: separate highlights, keywords, figure files, captions.

Elsevier asks for highlights and figures as separate files; the manuscript keeps
them inline for reading, this script produces the upload set from the same source
so the two cannot disagree.
"""
from __future__ import annotations

import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
MS = ROOT / "docs" / "Manuscript_v2_draft.md"
OUT = ROOT / "docs" / "submission"

text = MS.read_text(encoding="utf-8")

# --- keywords: Elsevier allows up to six ---------------------------------
kw_line = next(ln for ln in text.splitlines() if ln.startswith("**Keywords:**"))
kws = [k.strip().strip("*").strip() for k in kw_line.split(":", 1)[1].split(";")]
kws = [k for k in kws if k]
print("keywords found:", len(kws), kws)
keep = ["airborne mineral exploration", "gamma-ray spectrometry", "thermal infrared",
        "ASTER", "multi-modal fusion", "identifiability"]
missing = [k for k in keep if k not in kws]
assert not missing, missing
kws = keep

# --- highlights ----------------------------------------------------------
start = text.index("## Highlights")
end = text.index("## 1. Introduction")
block = text[start:end]
bullets = [" ".join(b.split()) for b in block.split("\n- ") if b.strip()]
bullets = [b.replace("## Highlights", "").strip() for b in bullets]
bullets = [b for b in bullets if b]
print("highlights:", len(bullets), [len(b) for b in bullets])
assert 3 <= len(bullets) <= 5 and all(len(b) <= 85 for b in bullets)

# --- figures + captions --------------------------------------------------
figs = re.findall(r"<!-- FIGURE:(\S+) -->", text)
caps = re.findall(r"^\*\*Figure (\d+)\.\*\* (.+)$", text, flags=re.M)
print("figures:", figs)
print("captions:", [c[0] for c in caps])
assert len(figs) == len(caps)

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "figures").mkdir(exist_ok=True)
for i, (name, (num, caption)) in enumerate(zip(figs, caps), start=1):
    src = ROOT / "processed" / name
    assert src.exists(), src
    suffix = src.suffix
    dst = OUT / "figures" / f"figure{i:02d}{suffix}"
    shutil.copy2(src, dst)
    print(f"  figure{i:02d} <- {name}")

(OUT / "highlights.txt").write_text(
    "\n".join(f"- {b}" for b in bullets) + "\n", encoding="utf-8")
(OUT / "keywords.txt").write_text("; ".join(kws) + "\n", encoding="utf-8")
(OUT / "figure_captions.txt").write_text(
    "\n\n".join(f"Figure {n}. {c}" for n, c in caps) + "\n", encoding="utf-8")
print("wrote highlights.txt, keywords.txt, figure_captions.txt, figures/")
