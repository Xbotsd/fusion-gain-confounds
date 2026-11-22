"""Build the upload set for the current target journal.

Target: Natural Resources Research (Springer, hybrid). Submission is through
Editorial Manager; the journal asks for a Word manuscript with line numbers and
page numbers, a separate cover letter, figures, and supplementary material.

    python code/make_submission_package.py
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MS = ROOT / "docs" / "Manuscript_v2_draft.docx"
MS_MD = ROOT / "docs" / "Manuscript_v2_draft.md"
OUT = ROOT / "docs" / "submission"
UPLOAD = OUT / "upload"
LETTER_MD = ROOT / "docs" / "COVER_LETTER.md"

text = MS_MD.read_text(encoding="utf-8")

# ---------------------------------------------------------------- keywords
kw_line = next(ln for ln in text.splitlines() if ln.startswith("**Keywords:**"))
kws = [k.strip().strip("*").strip() for k in kw_line.split(":", 1)[1].split(";")]
kws = [k for k in kws if k]
assert 4 <= len(kws) <= 6, kws
print("keywords:", kws)

# --------------------------------------------------------- figures, captions
figs = re.findall(r"<!-- FIGURE:(\S+) -->", text)
caps = re.findall(r"^\*\*Figure (\d+)\.\*\* (.+)$", text, flags=re.M)
assert len(figs) == len(caps) == 6, (len(figs), len(caps))

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "figures").mkdir(exist_ok=True)
for i, (name, (_num, _caption)) in enumerate(zip(figs, caps), start=1):
    src = ROOT / "processed" / name
    assert src.exists(), src
    shutil.copy2(src, OUT / "figures" / f"figure{i:02d}{src.suffix}")
    print(f"  figure{i:02d} <- {name}")

(OUT / "keywords.txt").write_text("; ".join(kws) + "\n", encoding="utf-8")
(OUT / "figure_captions.txt").write_text(
    "\n\n".join(f"Figure {n}. {c}" for n, c in caps) + "\n", encoding="utf-8")


def base_doc(margins_cm: float = 2.2, spacing: float = 1.0) -> Document:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)
    style.paragraph_format.space_after = Pt(4)
    style.paragraph_format.line_spacing = spacing
    for section in doc.sections:
        section.top_margin = Cm(margins_cm)
        section.bottom_margin = Cm(margins_cm)
        section.left_margin = Cm(margins_cm)
        section.right_margin = Cm(margins_cm)
    return doc


def add_runs(p, s: str) -> None:
    for part in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)", s):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            p.add_run(part[2:-2]).bold = True
        elif part.startswith("*") and part.endswith("*"):
            p.add_run(part[1:-1]).italic = True
        elif part.startswith("`") and part.endswith("`"):
            r = p.add_run(part[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(9)
        else:
            p.add_run(part)


# --------------------------------------------------------------- cover letter
lines = LETTER_MD.read_text(encoding="utf-8").splitlines()
doc = base_doc()
i = 0
while i < len(lines):
    line = lines[i].rstrip()
    if not line.strip() or line.startswith("# "):
        i += 1
        continue
    parts = [line.strip()]
    j = i + 1
    while j < len(lines):
        nxt = lines[j].rstrip()
        if not nxt.strip() or nxt.startswith("#"):
            break
        parts.append(nxt.strip())
        j += 1
    p = doc.add_paragraph()
    add_runs(p, " ".join(parts))
    i = j
doc.paragraphs[0].insert_paragraph_before(dt.date.today().strftime("%d %B %Y"))
doc.save(OUT / "cover_letter.docx")
print("wrote cover_letter.docx")


# ------------------------------------------------------------- upload folder
def flatten(src: Path, dst: Path) -> None:
    im = Image.open(src).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    im = Image.alpha_composite(bg, im).convert("RGB")
    im.save(dst, "PNG", dpi=(300, 300))


if UPLOAD.exists():
    shutil.rmtree(UPLOAD)
(UPLOAD / "figures").mkdir(parents=True)

shutil.copy2(MS, UPLOAD / "Manuscript.docx")
shutil.copy2(OUT / "cover_letter.docx", UPLOAD / "Cover_Letter.docx")
shutil.copy2(ROOT / "docs" / "Supplementary_Tables.docx",
             UPLOAD / "Supplementary_Material.docx")
shutil.copy2(OUT / "Data_Deposition.docx", UPLOAD / "Data_Deposition.docx")
for i in range(1, 7):
    flatten(OUT / "figures" / f"figure{i:02d}.png",
            UPLOAD / "figures" / f"figure{i:02d}.png")
flatten(ROOT / "docs" / "graphical_abstract.png", UPLOAD / "Graphical_Abstract.png")

slots = {
    "Cover_Letter.docx": "Cover letter",
    "Manuscript.docx": "Manuscript",
    "Supplementary_Material.docx": "Supplementary material",
    "Data_Deposition.docx": "Data deposition information",
    "Graphical_Abstract.png": "Graphical abstract (optional)",
}
for i in range(1, 7):
    slots[f"figures/figure{i:02d}.png"] = f"Figure {i}"

manifest = []
for rel, slot in slots.items():
    p = UPLOAD / rel
    manifest.append({
        "file": rel,
        "upload_slot": slot,
        "bytes": p.stat().st_size,
        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
    })
(OUT / "upload_manifest.json").write_text(
    json.dumps({"generated": dt.datetime.now().isoformat(timespec="seconds"),
                "target": "Natural Resources Research",
                "files": manifest}, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8")

zip_path = OUT / "NRR_submission_package.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for p in sorted(UPLOAD.rglob("*")):
        if p.is_file():
            zf.write(p, p.relative_to(UPLOAD))

print(f"upload set: {len(manifest)} files, "
      f"{sum(m['bytes'] for m in manifest) / 1e6:.1f} MB")
for m in manifest:
    print(f"  {m['upload_slot']:32s} {m['file']:28s} {m['bytes']/1e6:6.2f} MB")
print(f"wrote {zip_path.relative_to(ROOT)} ({zip_path.stat().st_size/1e6:.1f} MB)")
