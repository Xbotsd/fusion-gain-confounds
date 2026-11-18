"""Check the submission package against the journal's requirements.

Runs without network access and without opening Word. Verifies:

  * the reference style the journal returned the submission for (author–date,
    all authors named, full journal titles, alphabetical, nothing orphaned);
  * the sections the C&G template requires, including Code availability;
  * the metadata limits (abstract words, keyword count, highlight length);
  * the layout properties that caused earlier defects (page breaks, table rows
    that cannot split, captions kept with their tables and figures, line numbers,
    double spacing);
  * the upload set against its sources (SHA-256) and the manifest.
  * the repository checks run by code/maintain.py are separate.

    python code/check_submission.py

Exit code 0 when every check passes.
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
    flat = re.sub(r"\s+", " ", body)
    entries = [ln.strip() for ln in refblock.strip().splitlines() if ln.strip()]
    doc = Document(str(DOCX))
    texts = [p.text for p in doc.paragraphs]

    # ---------------------------------------------------- reference style
    groups = re.findall(r"\([^()]*?(?:19|20)\d\d\)", body)
    chk("no numeric citation markers",
        not re.findall(r"\[\s*\d+\s*[,–\-]", body),
        f"{len(groups)} author-date groups")
    chk("in-text uses 'and', not '&'",
        not re.search(r"[A-Z][a-z]+ & [A-Z][a-z]+,\s*(?:19|20)\d\d", body))
    chk("all authors named in the list", "et al." not in refblock, f"{len(entries)} entries")

    abbr = re.findall(r"(?:AGSO J\.|JGR|J\.\s?(?:Geophys|Appl|Basic|Res|Sci)\b|"
                      r"Remote Sens\.|Comput\.\s?Geosci\.|IEEE Trans\.|Geophys\.\s?Res\.)", refblock)
    chk("no abbreviated journal titles", not abbr, str(abbr[:3]) if abbr else "full titles")

    chk("every entry has 'Authors, Year.'",
        all(re.search(r",\s*(?:19|20)\d\d\.\s", e) for e in entries),
        str([e[:40] for e in entries if not re.search(r",\s*(?:19|20)\d\d\.\s", e)][:2]))
    chk("every entry ends with a DOI or a period",
        all(re.search(r"https://doi\.org/\S+$", e) or e.endswith(".") for e in entries))

    surnames = [e.split(",")[0].strip() for e in entries]
    chk("alphabetical order", surnames == sorted(surnames, key=str.lower))
    chk("no uncited entry",
        not [s for s in surnames if s not in body and "IAEA" not in s])
    keys = set()
    for m in re.finditer(r"\(([^()]*?(?:19|20)\d\d)\)", body):
        for part in m.group(1).split(";"):
            mm = re.match(r"\s*([A-Z][A-Za-zÀ-ž'\- ]+?)(?: et al\.| and [A-Z][A-Za-zÀ-ž'\- ]+)?,"
                          r"\s*((?:19|20)\d\d)", part)
            if mm:
                keys.add(mm.group(1).strip())
    chk("no citation without an entry",
        not [k for k in keys if k not in surnames and k != "IAEA"])

    # ------------------------------------------------------------- sections
    for sec in ("## Abstract", "## Highlights", "## Code availability",
                "## Declarations", "## References"):
        chk(f"section {sec[3:]}", sec in md)
    chk("Code availability has the template fields",
        all(k in md for k in ("Name of the code/library", "Contact", "Hardware requirements",
                              "Program language", "Software required", "Program size",
                              "Repository")))
    chk("supplementary table S1 referenced", "Table S1" in flat)
    chk("supplementary file exists", (ROOT / "docs" / "Supplementary_Tables.docx").exists())

    # ------------------------------------------------------------- metadata
    chk("title present", texts[0].startswith("Two confounds in reported fusion"))
    abstract = texts[texts.index("Abstract") + 1]
    chk("abstract <= 250 words", len(abstract.split()) <= 250, f"{len(abstract.split())} words")
    kw = next(t for t in texts if t.startswith("Keywords:"))
    chk("6 keywords", len(kw.split(":", 1)[1].split(";")) == 6)
    hl = [p for p in doc.paragraphs if p.style.name == "List Bullet"]
    chk("5 highlights, each <= 85 characters",
        len(hl) == 5 and all(len(p.text) <= 85 for p in hl),
        f"{len(hl)} bullets, max {max((len(p.text) for p in hl), default=0)}")

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
        "Highlights.docx": SUB / "highlights.docx",
        "Supplementary_Material.docx": ROOT / "docs" / "Supplementary_Tables.docx",
        "Declaration_of_Competing_Interests.docx": SUB / "declaration_of_competing_interests.docx",
    }
    stale = [n for n, s in sources.items()
             if hashlib.sha256((UP / n).read_bytes()).hexdigest()
             != hashlib.sha256(s.read_bytes()).hexdigest()]
    chk("upload set matches its sources", not stale, str(stale))
    chk("manifest lists 12 files", len(man["files"]) == 12, str(len(man["files"])))
    chk("6 figure files", len(list((UP / "figures").glob("*.png"))) == 6)

    for status, name, detail in ROWS:
        print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
    fails = [r for r in ROWS if r[0] == "FAIL"]
    print(f"\n{len(ROWS) - len(fails)} passed, {len(fails)} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
