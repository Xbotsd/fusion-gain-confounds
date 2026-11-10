"""Finish the ORCID insertion (manuscript already done; CITATION and Zenodo left)."""
import json
import pathlib

root = pathlib.Path(__file__).resolve().parents[2]
ORCID = "0009-0002-3231-0444"

cff = root / "CITATION.cff"
c = cff.read_text(encoding="utf-8")
if ORCID in c:
    print("CITATION.cff: already present")
else:
    old = "    email: 3468858545@qq.com\nlicense: MIT"
    new = (f"    email: 3468858545@qq.com\n"
           f"    orcid: \"https://orcid.org/{ORCID}\"\n"
           f"license: MIT")
    assert c.count(old) == 1, "CITATION.cff email/licence block not found"
    cff.write_text(c.replace(old, new), encoding="utf-8")
    print("CITATION.cff: orcid field added")

zen = root / ".zenodo.json"
d = json.loads(zen.read_text(encoding="utf-8"))
d["creators"][0]["orcid"] = ORCID
zen.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("zenodo: creator orcid =", d["creators"][0]["orcid"])

# verify every place
ms = (root / "docs" / "Manuscript_v2_draft.md").read_text(encoding="utf-8")
print("manuscript occurrences:", ms.count(ORCID))
print("citation occurrences:", (root / "CITATION.cff").read_text(encoding="utf-8").count(ORCID))
