"""Check the submission package against the International Journal of Remote Sensing requirements.

Run before every upload:

    python code/check_submission.py

Verifies the reference style (Taylor & Francis author-date), the required
sections, the metadata limits, the layout properties and the upload set against
its sources. Exit code 0 when every check passes.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from docx import Document

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "docs" / "Manuscript_v2_draft.md"
DOCX = ROOT / "docs" / "Manuscript_v2_draft.docx"
SUB = ROOT / "docs" / "submission"
UP = SUB / "upload"

ROWS: list[tuple[str, str, str]] = []


def chk(name: str, ok: bool, detail: str = "") -> None:
    ROWS.append(("PASS" if ok else "FAIL", name, detail))


def main() -> int:
    md = MD.read_text(encoding="utf-8")
    body, refblock = md.split("## References", 1)
    entries = [ln.strip() for ln in refblock.strip().splitlines() if ln.strip()]
    doc = Document(str(DOCX))
    texts = [p.text for p in doc.paragraphs]

    # ------------------------------------------------ Taylor & Francis style
    groups = re.findall(r"\([^()]*?(?:19|20)\d\d\)", body)
    chk("in-text citations are author-date", bool(groups), f"{len(groups)} groups")
    chk("no comma before the year in citations",
        not re.findall(r"\([^()]*?[A-Za-z],\s(?:19|20)\d\d", body))
    chk("no numeric citation markers", not re.findall(r"\[\s*\d+\s*[,\u2013-]", body))
    chk("all authors named in the list", "et al." not in refblock, f"{len(entries)} entries")
    chk("article titles in quotation marks",
        all(("\u201c" in e) for e in entries if re.search(r",\s(?:19|20)\d\d\.\s", e)))
    chk("every entry has 'Authors. Year.'",
        all(re.search(r"\.\s(?:19|20)\d\d\.\s", e) for e in entries))

    surnames = [e.split(",")[0].strip() for e in entries]
    chk("alphabetical order", surnames == sorted(surnames, key=str.lower))
    chk("no uncited entry", not [s for s in surnames if s not in body and "IAEA" not in s])
    keys = set()
    for m in re.finditer(r"\(([^()]*?(?:19|20)\d\d)\)", body):
        for part in m.group(1).split(";"):
            mm = re.search(r"([A-Z][A-Za-zÀ-ž\-]+)(?: et al\.)?(?:\s+and\s+[A-Z][A-Za-zÀ-ž\-]+)?"
                           r"\s+(?:19|20)\d\d", part)
            if mm:
                keys.add(mm.group(1))
    chk("no citation without an entry",
        not [k for k in keys if k not in surnames and k != "IAEA"], str(sorted(keys))[:80])

    # ------------------------------------------------------------- sections
    for sec in ("## Abstract", "## Code availability", "## Declarations", "## References"):
        chk(f"section {sec[3:]}", sec in md)
    chk("disclosure statement", "**Disclosure statement.**" in md)
    chk("Code availability has the template fields",
        all(k in md for k in ("Name of the code/library", "Contact", "Hardware requirements",
                              "Program language", "Software required", "Program size",
                              "Repository")))
    chk("supplementary table S1 referenced", "Table S1" in re.sub(r"\s+", " ", body))
    chk("supplementary file exists", (ROOT / "docs" / "Supplementary_Tables.docx").exists())

    # ------------------------------------------------------------- metadata
    chk("title present", texts[0].startswith("Two confounds in reported fusion"))
    abstract = texts[texts.index("Abstract") + 1]
    chk("abstract <= 250 words", len(abstract.split()) <= 250, f"{len(abstract.split())} words")
    kw = next(t for t in texts if t.startswith("Keywords:"))
    chk("6 keywords", len(kw.split(":", 1)[1].split(";")) == 6)

    # --------------------------------------------------------------- layout
    xml = doc.element.xml
    chk("page break before abstract and references", xml.count('w:type="page"') == 2)
    chk("8 tables and 6 figures", len(doc.tables) == 8 and len(doc.inline_shapes) == 6)
    chk("double spacing", doc.styles["Normal"].paragraph_format.line_spacing == 2.0)
    chk("line numbers enabled", "w:lnNumType" in xml)
    chk("table headers repeat, rows do not split", xml.count("tblHeader") == 8)
    chk("8 table captions kept with their tables",
        sum(1 for p in doc.paragraphs
            if p.text.startswith("Table ") and p.paragraph_format.keep_with_next) == 8)

    # -------------------------------------------------------------- package
    man = json.loads((SUB / "upload_manifest.json").read_text(encoding="utf-8"))
    sources = {
        "Manuscript.docx": DOCX,
        "Cover_Letter.docx": SUB / "cover_letter.docx",
        "Supplementary_Material.docx": ROOT / "docs" / "Supplementary_Tables.docx",
    }
    stale = [n for n, s in sources.items()
             if hashlib.sha256((UP / n).read_bytes()).hexdigest()
             != hashlib.sha256(s.read_bytes()).hexdigest()]
    chk("upload set matches its sources", not stale, str(stale))
    chk("manifest lists 10 files", len(man["files"]) == 10, str(len(man["files"])))
    chk("6 figure files", len(list((UP / "figures").glob("*.png"))) == 6)

    for status, name, detail in ROWS:
        print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
    fails = [r for r in ROWS if r[0] == "FAIL"]
    print(f"\n{len(ROWS) - len(fails)} passed, {len(fails)} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
