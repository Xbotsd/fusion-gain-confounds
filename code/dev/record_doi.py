"""Write the issued DOI into the manuscript and every supporting file."""
import pathlib

root = pathlib.Path(__file__).resolve().parents[2]
DOI = "10.5281/zenodo.24130421"
CONCEPT = "10.5281/zenodo.24130420"
URL = "https://doi.org/" + DOI
REPO = "https://github.com/Xbotsd/fusion-gain-confounds"

# ---- manuscript ----------------------------------------------------------
ms = root / "docs" / "Manuscript_v2_draft.md"
t = ms.read_text(encoding="utf-8")
old = ("and a snapshot will be archived on Zenodo with a DOI on acceptance.")
new = (f"The code and the derived results are archived at {URL}\n"
       f"(all versions: https://doi.org/{CONCEPT}).")
assert t.count(old) == 1, "availability tail not found"
ms.write_text(t.replace(old, new), encoding="utf-8")
print("manuscript: DOI added")

# ---- CITATION.cff --------------------------------------------------------
cff = root / "CITATION.cff"
c = cff.read_text(encoding="utf-8")
if "doi:" not in c:
    c = c.replace('license: MIT',
                  f'doi: "{DOI}"\nlicense: MIT', 1)
# version + release date so the CFF points at this archived snapshot
if "version:" not in c:
    c = c.replace('doi: "', 'version: "1.0.0"\ndate-released: "2026-11-11"\ndoi: "', 1)
cff.write_text(c, encoding="utf-8")
print("CITATION.cff: doi/version added")

# ---- README --------------------------------------------------------------
r = root / "README.md"
s = r.read_text(encoding="utf-8")
badge = f"[![DOI](https://zenodo.org/badge/DOI/{DOI}.svg)]({URL})"
if badge not in s:
    lines = s.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith("**Repository:**"):
            lines.insert(i + 1, "")
            lines.insert(i + 2, badge)
            break
    r.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("README: DOI badge added")

# ---- GITHUB_SETUP.md: replace the pending-DOI section --------------------
g = root / "docs" / "GITHUB_SETUP.md"
s = g.read_text(encoding="utf-8")
start = s.index("## Remaining: the Zenodo DOI")
end = s.index("## How the push was authenticated")
new_section = f"""## DOI (issued)

Zenodo record: https://zenodo.org/records/24130421

* version DOI (cite this for the archived snapshot): **{DOI}**
* concept DOI (always resolves to the latest version): **{CONCEPT}**
* archived file: `fusion-gain-confounds-1.0.0.zip`, 18.7 MB, the `git archive`
  of commit `2d194a2`
* the record carries the MIT licence, ORCID 0009-0002-3231-0444, the seven
  keywords and a relation to the GitHub repository

The record was created through the Zenodo API (`POST /api/deposit/depositions`,
bucket upload, then `actions/publish`), not through the GitHub webhook, so the
GitHub release `v0.1.0` is unrelated to the DOI. A later version is published the
same way, or by linking the repository in Zenodo and cutting a new release.

"""
g.write_text(s[:start] + new_section + s[end:], encoding="utf-8")
print("GITHUB_SETUP.md: DOI section replaced")

# ---- submission checklist -----------------------------------------------
p = root / "docs" / "submission" / "README.md"
t = p.read_text(encoding="utf-8")
old = (f"2. **Repository DOI.** The repository is public at {REPO}; link it to Zenodo,\n"
       '   mint the DOI, then replace every "DOI to be inserted on acceptance"\n'
       "   placeholder.")
new = (f"2. **Repository DOI — done.** {URL} (version 1.0.0), concept\n"
       f"   https://doi.org/{CONCEPT}. The manuscript, `CITATION.cff` and README carry it.")
if old in t:
    p.write_text(t.replace(old, new), encoding="utf-8")
    print("submission/README.md: DOI marked done")
else:
    print("!! submission checklist text not found")

# ---- cover letter --------------------------------------------------------
cl = root / "docs" / "COVER_LETTER.md"
t = cl.read_text(encoding="utf-8")
old = (f"The code is public at {REPO} and a snapshot will be archived\n"
       "with a DOI on acceptance; the layout, licence and one-command reproduction\n"
       "are described in the data-availability section.")
new = (f"The code is public at {REPO} and archived at {URL};\n"
       "the layout, licence and one-command reproduction are described in the\n"
       "data-availability section.")
if old in t:
    cl.write_text(t.replace(old, new), encoding="utf-8")
    print("COVER_LETTER.md: DOI added")
else:
    print("!! cover letter text not found")
