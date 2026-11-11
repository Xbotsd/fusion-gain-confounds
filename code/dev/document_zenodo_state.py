"""Document what the Zenodo record now contains and how to maintain it."""
import pathlib

root = pathlib.Path(__file__).resolve().parents[2]
g = root / "docs" / "GITHUB_SETUP.md"
t = g.read_text(encoding="utf-8")

anchor = "## How the push was authenticated"
addition = """## Maintaining the Zenodo record

The record is https://zenodo.org/records/24130421 (version 1.0.0, same DOI
10.5281/zenodo.24130421 after every metadata edit).

* **Metadata edits** go through the legacy deposition endpoint:
  `PUT /api/deposit/depositions/24130421` with the full metadata block, then
  `POST /api/deposit/depositions/24130421/actions/publish`. A metadata-only edit
  keeps the DOI and the version number; `PATCH /api/records/.../draft` answers
  405, so use `PUT` on the legacy endpoint.
* **Communities**: `POST /api/records/24130421/communities` with
  `{"communities": [{"id": "<community uuid>"}]}` creates an inclusion request.
  The request for `remote-sensing` was submitted on 2026-11-11 and stays open
  until a curator accepts it; the record page shows the community only after
  that.
* **No software-specific fields**: Zenodo's current schema has no
  `programming_language` or `development_status` field (checked against the live
  record: the metadata keys are title, doi, publication_date, description,
  access_right, creators, keywords, related_identifiers, version, language,
  resource_type, license, relations). Language and development status are stated
  in the description instead, and `pyproject.toml` carries them for tooling.
* **`isPublishedIn`**: to be added once the manuscript has a journal DOI, as
  `related_identifiers: [{identifier: "10.xxxx/...", relation: "isPublishedIn",
  resource_type: "publication-article"}]`.

"""
assert anchor in t
g.write_text(t.replace(anchor, addition + anchor), encoding="utf-8")
print("GITHUB_SETUP.md: Zenodo maintenance section added")

# changelog
ch = root / "docs" / "CHANGELOG.md"
c = ch.read_text(encoding="utf-8")
anchor2 = "## Round 9 — controls tightened, one bootstrap, one command (current)"
new_entry = """## Round 10 — repository and archive (current)

* **Repository renamed** to `fusion-gain-confounds`, so the name states the
  paper's thesis instead of the field area; all documents, `CITATION.cff`, the
  cover letter and the manuscript carry the new URL.
* **Licence corrected**: `LICENSE` was a pure MIT text signed "A_MineralProspecting
  authors" (a directory name); it now reads "Copyright (c) 2026 Yudong Xu" and
  GitHub detects MIT. Third-party data terms moved to `NOTICE.md`.
* **DOI issued**: Zenodo record 24130421, version DOI 10.5281/zenodo.24130421,
  concept DOI 10.5281/zenodo.24130420, archive `fusion-gain-confounds-1.0.0.zip`
  (18.7 MB, `git archive` of commit `2d194a2`). The DOI is in the manuscript's
  data-availability paragraph, `CITATION.cff`, the README badge and the cover
  letter.
* **Record description expanded** with the quantitative result, the archive
  contents and the reproduction command; a community-inclusion request for
  `remote-sensing` is pending curator acceptance.
* **Author ORCID** 0009-0002-3231-0444 on the title page, in CRediT, in
  `CITATION.cff` and in the Zenodo creator metadata.
* **State:** the paper is NOT submitted; the DOI identifies the software, not a
  publication.

"""
if "Round 10" not in c:
    ch.write_text(c.replace(anchor2, new_entry + anchor2), encoding="utf-8")
    print("CHANGELOG.md: Round 10 added")
else:
    print("CHANGELOG.md already has Round 10")
