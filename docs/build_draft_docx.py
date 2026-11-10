"""Convert docs/Manuscript_v2_draft.md to a Word draft with tables and figures."""
from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "Manuscript_v2_draft.md"
OUT = ROOT / "docs" / "Manuscript_v2_draft.docx"
BLUE = RGBColor(0x1F, 0x4E, 0x79)


def set_base(doc):
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "SimSun")
    st.paragraph_format.line_spacing = 2.0  # double-spaced review copy (Elsevier)
    st.paragraph_format.space_after = Pt(5)


def add_line_numbers(doc):
    """Continuous line numbers (review requirement of the journal)."""
    for section in doc.sections:
        sectPr = section._sectPr
        ln = sectPr.find(qn("w:lnNumType"))
        if ln is None:
            ln = sectPr.makeelement(qn("w:lnNumType"), {})
            sectPr.append(ln)
        ln.set(qn("w:countBy"), "1")
        ln.set(qn("w:restart"), "continuous")
        ln.set(qn("w:distance"), "360")


def add_runs(p, text):
    parts = re.split(r"(\*\*.*?\*\*|`.*?`)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            r = p.add_run(part[2:-2])
            r.bold = True
        elif part.startswith("`") and part.endswith("`"):
            r = p.add_run(part[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(9.5)
        else:
            p.add_run(part)


def add_table(doc, rows):
    if not rows:
        return
    header = rows[0]
    body = rows[1:]
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        cell = t.rows[0].cells[i]
        cell.text = ""
        para = cell.paragraphs[0]
        add_runs(para, h.strip().replace("*", ""))
        for run in para.runs:
            run.bold = True
            run.font.size = Pt(8.5)
    for row in body:
        cells = t.add_row().cells
        for i, val in enumerate(row[: len(header)]):
            cells[i].text = ""
            para = cells[i].paragraphs[0]
            add_runs(para, val.strip())
            for run in para.runs:
                run.font.size = Pt(8.5)
    doc.add_paragraph()


def main():
    doc = Document()
    set_base(doc)
    lines = SRC.read_text(encoding="utf-8").splitlines()
    i = 0
    in_refs = False
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue

        # table block
        if line.lstrip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                raw = lines[i].strip().strip("|")
                cells = [c.strip() for c in raw.split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            add_table(doc, rows)
            continue

        # figure directive
        m = re.match(r"<!--\s*FIGURE:([^ ]+)\s*-->", line.strip())
        if m:
            path = ROOT / "processed" / m.group(1)
            if path.exists():
                doc.add_picture(str(path), width=Cm(15.5))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            i += 1
            continue

        # figure caption
        if re.match(r"^\*\*Figure \d+\.\*\*", line.strip()):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_runs(p, line.strip())
            for r in p.runs:
                r.italic = True
                r.font.size = Pt(9)
            doc.add_paragraph()
            i += 1
            continue

        if line.startswith("### "):
            doc.add_heading(line[4:].strip(), level=3)
        elif line.startswith("## "):
            title = line[3:].strip()
            if title.lower().startswith("references") and not in_refs:
                doc.add_page_break()
                in_refs = True
            doc.add_heading(title, level=2)
        elif line.startswith("# "):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(line[2:].strip())
            r.bold = True
            r.font.size = Pt(16)
            r.font.color.rgb = BLUE
        elif line.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            add_runs(p, line[2:].strip())
        elif line.startswith("**Authors:**") or line.startswith("**Corresponding"):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_runs(p, line)
        else:
            p = doc.add_paragraph()
            add_runs(p, line.strip())
        i += 1

    # figures are placed inline at their first citation
    add_line_numbers(doc)
    doc.save(OUT)
    print(f"saved {OUT}")
    print(f"paragraphs {len(doc.paragraphs)} tables {len(doc.tables)} "
          f"figures {len(doc.inline_shapes)}")


if __name__ == "__main__":
    main()
