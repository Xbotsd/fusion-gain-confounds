"""Build the supplementary-tables Word file from docs/Supplementary_Tables.md."""
from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "Supplementary_Tables.md"
OUT = ROOT / "docs" / "Supplementary_Tables.docx"


def add_runs(p, text: str) -> None:
    for part in re.split(r"(\*\*.*?\*\*|`.*?`)", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            p.add_run(part[2:-2]).bold = True
        elif part.startswith("`") and part.endswith("`"):
            r = p.add_run(part[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(9)
        else:
            p.add_run(part)


def add_table(doc, rows: list[list[str]]) -> None:
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = "Table Grid"
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for i, row in enumerate(rows):
        for j, cell in enumerate(row):
            run = table.cell(i, j).paragraphs[0].add_run(cell)
            run.bold = i == 0
            if j:
                table.cell(i, j).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT


def main() -> None:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)
    style.paragraph_format.space_after = Pt(6)

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            i += 1
            continue
        if line.startswith("## "):
            doc.add_heading(line[3:], level=1)
            i += 1
            continue
        if line.startswith("# "):
            doc.add_heading(line[2:], level=0)
            i += 1
            continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not set("".join(cells)) <= set("-: "):
                    rows.append(cells)
                i += 1
            add_table(doc, rows)
            doc.add_paragraph()
            continue
        parts = [line]
        j = i + 1
        while j < len(lines):
            nxt = lines[j].rstrip()
            if not nxt.strip() or nxt.startswith(("|", "#")):
                break
            parts.append(nxt.strip())
            j += 1
        p = doc.add_paragraph()
        add_runs(p, " ".join(parts))
        i = j

    doc.save(OUT)
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()
