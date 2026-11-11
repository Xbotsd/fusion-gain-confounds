"""Repair the data-availability paragraph: keep the URL intact and current."""
import pathlib

root = pathlib.Path(__file__).resolve().parents[2]
URL = "https://github.com/Xbotsd/fusion-gain-confounds"

ms = root / "docs" / "Manuscript_v2_draft.md"
t = ms.read_text(encoding="utf-8")
start = t.index("## Reproducibility and data availability")
end = t.index("## Declarations")

para = """The pipeline is 40 scripts in eight stages. A coverage guard fails if any
validated artefact lacks a producing script; a validator checks 53 artefacts and
22 invariants (including the zero, noise and shuffled controls); unit tests
assert the two switch-off invariances and the spectral-library construction of
the thermal rows; every file carries a SHA-256 in a manifest; dependencies are
pinned; one command rebuilds every number. The raw ASTER scenes are archived with
their STAC identifiers and hashes so the thermal cube can be rebuilt offline.
The repository is public under the MIT licence at

""" + URL + """

and a snapshot will be archived on Zenodo with a DOI on acceptance.
"""
t = t[:start] + "## Reproducibility and data availability\n\n" + para + "\n" + t[end:]
ms.write_text(t, encoding="utf-8")
print("manuscript paragraph rebuilt; URL intact:", URL in t)

# directory name in the clone instructions
g = root / "docs" / "GITHUB_SETUP.md"
s = g.read_text(encoding="utf-8")
s = s.replace("cd ivanpah-fusion-benchmark", "cd fusion-gain-confounds")
g.write_text(s, encoding="utf-8")
print("GITHUB_SETUP.md clone path updated")

# one-off helper scripts: keep them pointing at the live name
for name in ("gh_create_repo.ps1", "gh_credential_probe.ps1", "gh_set_topics.ps1",
             "gh_set_topics2.ps1", "gh_verify_repo.ps1"):
    p = root / "code" / "dev" / name
    if p.exists():
        s = p.read_text(encoding="utf-8")
        if "ivanpah-fusion-benchmark" in s:
            p.write_text(s.replace("ivanpah-fusion-benchmark",
                                   "fusion-gain-confounds"), encoding="utf-8")
            print(f"{name}: updated")

p = root / "code" / "dev" / "record_repo_url.py"
if p.exists():
    s = p.read_text(encoding="utf-8")
    p.write_text(s.replace("ivanpah-fusion-benchmark", "fusion-gain-confounds"),
                 encoding="utf-8")
    print("record_repo_url.py: updated")
