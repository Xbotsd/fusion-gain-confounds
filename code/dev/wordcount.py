"""Word counts for the JSTARS length check."""
import re
from pathlib import Path

t = Path(r"D:\A_MineralProspecting\docs\Manuscript_v2_draft.md").read_text(encoding="utf-8")
TOK = re.compile(r"[A-Za-z0-9\u00c0-\u024f'\-]+")


def words(s):
    return len(TOK.findall(s))


ab = t[t.index("## Abstract"):t.index("**Keywords")]
body = t[:t.index("## References")]
no_tables = re.sub(r"^\|.*$", "", body, flags=re.M)
print("abstract words      :", words(ab))
print("abstract chars      :", len(ab))
print("body words (all)    :", words(body))
print("body words (no tab) :", words(no_tables))
print("highlights bullets  :", t[t.index("## Highlights"):t.index("## 1. Introduction")].count("\n- "))
print("tables              :", len(re.findall(r"^\|---", body, re.M)))
