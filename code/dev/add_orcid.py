"""Add the author's ORCID to the manuscript, CITATION.cff and .zenodo.json."""
import json
import pathlib

root = pathlib.Path(__file__).resolve().parents[2]
ORCID = "0009-0002-3231-0444"

# ---- manuscript title page ----------------------------------------------
ms = root / "docs" / "Manuscript_v2_draft.md"
t = ms.read_text(encoding="utf-8")
old = "**Authors:** Yudong Xu\u00b9  "
new = (f"**Authors:** Yudong Xu\u00b9 (ORCID {ORCID})  ")
assert t.count(old) == 1, "title block not found"
t = t.replace(old, new)

# CRediT line: name the identifier once, in the standard place
old_credit = "**CRediT author statement.** Yudong Xu: conceptualisation,"
new_credit = (f"**CRediT author statement.** Yudong Xu (ORCID {ORCID}): "
              "conceptualisation,")
assert t.count(old_credit) == 1, "CRediT block not found"
t = t.replace(old_credit, new_credit)
ms.write_text(t, encoding="utf-8")
print("manuscript: ORCID on the title page and in the CRediT statement")

# ---- CITATION.cff -------------------------------------------------------
cff = root / "CITATION.cff"
c = cff.read_text(encoding="utf-8")
old_c = ('    family-names: Xu\n'
         '    given-names: Yudong\n'
         '    affiliation: "Heilongjiang University of Science and Technology, Harbin, China"\n'
         '    email: 3468858545@qq.com')
new_c = ('    family-names: Xu\n'
         '    given-names: Yudong\n'
         '    affiliation: "Heilongjiang University of Science and Technology, Harbin, China"\n'
         '    email: 3468858545@qq.com\n'
         f'    orcid: "https://orcid.org/{ORCID}"')
assert c.count(old_c) == 1, "CITATION.cff author block not found"
cff.write_text(c.replace(old_c, new_c), encoding="utf-8")
print("CITATION.cff: orcid field added")

# ---- .zenodo.json -------------------------------------------------------
zen = root / ".zenodo.json"
d = json.loads(zen.read_text(encoding="utf-8"))
creator = d["creators"][0]
creator["orcid"] = ORCID
zen.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("zenodo: creator orcid =", creator["orcid"])
