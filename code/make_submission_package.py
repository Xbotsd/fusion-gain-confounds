"""Build the Computers & Geosciences upload set from the canonical manuscript.

Outputs, all under docs/submission/:

  highlights.txt / highlights.docx     5 bullets, <= 85 characters
  keywords.txt                         the six keywords, one line
  figure_captions.txt                  the six captions, numbered
  cover_letter.docx                    docs/COVER_LETTER.md as a letter
  upload/                              ready-to-upload copies (git-ignored)
    Manuscript.docx                    docs/Manuscript_v2_draft.docx
    Cover_Letter.docx                  copy of cover_letter.docx
    Highlights.docx                    copy of highlights.docx
    Supplementary_Material.docx        docs/Supplementary_Tables.docx
    figures/figure01..06.png           RGB, 300 dpi, alpha flattened
    Graphical_Abstract.png             RGB, alpha flattened
  upload_manifest.json                 path, bytes, SHA-256 and upload slot
  CG_submission_package.zip            the whole upload/ folder (git-ignored)

The copies exist so the submission cannot drift from the sources: rerun this
script after any manuscript change. Needs python-docx and Pillow, which are
submission-time dependencies, not pipeline dependencies.
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
keep = ["airborne mineral exploration", "gamma-ray spectrometry", "thermal infrared",
        "ASTER", "multi-modal fusion", "identifiability"]
missing = [k for k in keep if k not in kws]
assert not missing, missing
kws = keep
print("keywords:", len(kws), kws)

# -------------------------------------------------------------- highlights
start = text.index("## Highlights")
end = text.index("## 1. Introduction")
block = text[start:end]
bullets = [" ".join(b.split()) for b in block.split("\n- ") if b.strip()]
bullets = [b.replace("## Highlights", "").strip() for b in bullets]
bullets = [b for b in bullets if b]
assert 3 <= len(bullets) <= 5 and all(len(b) <= 85 for b in bullets), \
    [(len(b), b) for b in bullets]
print("highlights:", len(bullets), [len(b) for b in bullets])

# --------------------------------------------------------- figures, captions
figs = re.findall(r"<!-- FIGURE:(\S+) -->", text)
caps = re.findall(r"^\*\*Figure (\d+)\.\*\* (.+)$", text, flags=re.M)
assert len(figs) == len(caps) == 6, (len(figs), len(caps))

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "figures").mkdir(exist_ok=True)
for i, (name, (num, _caption)) in enumerate(zip(figs, caps), start=1):
    src = ROOT / "processed" / name
    assert src.exists(), src
    dst = OUT / "figures" / f"figure{i:02d}{src.suffix}"
    shutil.copy2(src, dst)
    print(f"  figure{i:02d} <- {name}")

(OUT / "highlights.txt").write_text(
    "\n".join(f"- {b}" for b in bullets) + "\n", encoding="utf-8")
(OUT / "keywords.txt").write_text("; ".join(kws) + "\n", encoding="utf-8")
(OUT / "figure_captions.txt").write_text(
    "\n\n".join(f"Figure {n}. {c}" for n, c in caps) + "\n", encoding="utf-8")

# ------------------------------------------------------- copy-paste fields
title = next(ln[2:].strip() for ln in text.splitlines() if ln.startswith("# "))
authors_clean = (
    "Yudong Xu (corresponding author)\n"
    "ORCID 0009-0002-3231-0444\n"
    "Heilongjiang University of Science and Technology, Harbin, China\n"
    "3468858545@qq.com")
abstract = text.split("## Abstract", 1)[1].split("**Keywords:**", 1)[0].strip()
personal = [
    "airborne geophysics", "gamma-ray spectrometry", "thermal infrared remote sensing",
    "ASTER", "multi-modal data fusion", "inverse problems", "identifiability",
    "mineral exploration", "reproducible research", "spatial statistics",
]
paste = (
    "TITLE\n" + title + "\n\n"
    "AUTHORS\n" + authors_clean + "\n\n"
    "ABSTRACT\n" + " ".join(abstract.split()) + "\n\n"
    "KEYWORDS\n" + "\n".join(kws) + "\n\n"
    "HIGHLIGHTS\n" + "\n".join(bullets) + "\n\n"
    "PERSONAL KEYWORDS (registration, pick 5+)\n" + "\n".join(personal) + "\n")
(OUT / "paste_fields.txt").write_text(paste, encoding="utf-8")
print("wrote paste_fields.txt")


# ------------------------------------------------------------------- docx
def base_doc(margins_cm: float = 2.5, spacing: float = 1.0) -> Document:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)
    style.paragraph_format.space_after = Pt(6)
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


# cover letter: markdown -> letter
lines = LETTER_MD.read_text(encoding="utf-8").splitlines()
doc = base_doc()
i = 0
first_heading = True
while i < len(lines):
    line = lines[i].rstrip()
    if not line.strip():
        i += 1
        continue
    if line.startswith("# "):
        # letterhead: skip the document title, the letter has its own subject line
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

doc.paragraphs[0].insert_paragraph_before(
    dt.date.today().strftime("%d %B %Y"))
doc.save(OUT / "cover_letter.docx")
print("wrote cover_letter.docx")

# highlights: markdown -> docx
doc = base_doc()
doc.add_heading("Highlights", level=1)
for b in bullets:
    doc.add_paragraph(b, style="List Bullet")
doc.save(OUT / "highlights.docx")
print("wrote highlights.docx")


# ------------------------------------------------------------ upload folder
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
shutil.copy2(OUT / "highlights.docx", UPLOAD / "Highlights.docx")
shutil.copy2(ROOT / "docs" / "Supplementary_Tables.docx",
             UPLOAD / "Supplementary_Material.docx")
for i in range(1, 7):
    flatten(OUT / "figures" / f"figure{i:02d}.png",
            UPLOAD / "figures" / f"figure{i:02d}.png")
flatten(ROOT / "docs" / "graphical_abstract.png",
        UPLOAD / "Graphical_Abstract.png")

slots = {
    "Cover_Letter.docx": "Cover Letter",
    "Manuscript.docx": "Manuscript (Word)",
    "Highlights.docx": "Highlights",
    "Supplementary_Material.docx": "Supplementary Material",
    "Graphical_Abstract.png": "Graphical Abstract",
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
                "files": manifest}, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8")

zip_path = OUT / "CG_submission_package.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for p in sorted(UPLOAD.rglob("*")):
        if p.is_file():
            zf.write(p, p.relative_to(UPLOAD))

print(f"upload set: {len(manifest)} files, "
      f"{sum(m['bytes'] for m in manifest) / 1e6:.1f} MB")
for m in manifest:
    print(f"  {m['upload_slot']:22s} {m['file']:28s} {m['bytes']/1e6:6.2f} MB")
print(f"wrote {zip_path.relative_to(ROOT)} "
      f"({zip_path.stat().st_size/1e6:.1f} MB)")
