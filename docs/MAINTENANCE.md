# Maintenance

Two artefacts are maintained from this workspace, and they must agree:

* the GitHub repository **https://github.com/Xbotsd/fusion-gain-confounds**
* the Zenodo record **https://zenodo.org/records/24130421** — version DOI
  `10.5281/zenodo.24130421`, concept DOI `10.5281/zenodo.24130420`

The Zenodo scope is this record only. Other records in the account belong to
other projects and are not edited from here. **The record is left untouched until
there is something to archive** — a new upload, or an explicit request to version
the record. The procedures for metadata edits and community requests are in
`docs/GITHUB_SETUP.md`.

## Routine check

```powershell
python code/maintain.py            # git, versions, DOI strings, Zenodo, GitHub, validator
python code/maintain.py --offline  # same, without the two network calls
```

It is read-only and needs no credentials; a healthy tree prints `0 failed`. The
heavier checks are the pipeline's own:

```powershell
python code/test_core.py            # 36 assertions in 9 groups
python code/validate_pipeline.py    # 53 artefacts, 22 invariants
python code/check_coverage.py       # every validated artefact has a producer
python code/build_manifest.py       # re-hash after any tracked file changes
```

Run `build_manifest.py` **last**: it hashes the tracked files, so any edit after
it makes the manifest stale.

## Invariants

* The Zenodo archive is a `git archive` of the commit named by the version tag.
  `v1.0.0` is `2d194a2`; the zip has 270 entries and MD5
  `5a9ee01403f63109bd0076c436093323`, both re-checked against the live record on
  2026-11-12.
* `pyproject.toml`, `CITATION.cff` and `.zenodo.json` carry the same version;
  the Zenodo record carries that version too.
* The version DOI appears in the README, `CITATION.cff`, the manuscript and
  `docs/GITHUB_SETUP.md`; the concept DOI at least in `GITHUB_SETUP.md` and the
  manuscript.
* `docs/Manuscript_v2_draft.md` is the source of the submitted manuscript. The
  `.docx` is generated from it with `docs/build_draft_docx.py` (needs
  `pip install python-docx`, not a pipeline dependency) and must be rebuilt
  after any text edit.
* The archive is never re-uploaded under the same version. A new version gets a
  new version DOI; the concept DOI stays fixed.

## What may change

Docs and code may change when the artefacts support the change. Result JSON/CSV
files are written by the scripts and never edited by hand; if a script changes,
rerun it and let the validator decide. Raw third-party data and the derived cubes
stay out of the repository (`docs/DATA_PROVENANCE.md`).

## Publishing a new version

Only when a new upload exists:

1. finish the work; run `python code/run_all.py all`, `test_core.py` and
   `validate_pipeline.py`; rebuild the manifest;
2. commit, tag the archived commit (`git tag -a vX.Y.Z <commit>`) and push both;
3. `git archive --format=zip --prefix=fusion-gain-confounds-X.Y.Z/ -o
   fusion-gain-confounds-X.Y.Z.zip vX.Y.Z`;
4. `POST /api/deposit/depositions/24130421/actions/newversion`, copy
   `.zenodo.json` into the new draft's metadata, upload the zip to its bucket and
   `POST .../actions/publish`;
5. update the version DOI strings (README, `CITATION.cff`, manuscript,
   `GITHUB_SETUP.md`, `.zenodo.json`), rebuild the `.docx`, and record the DOI in
   `docs/CHANGELOG.md`;
6. create the GitHub release for the tag, pointing at the new DOI, and mark the
   previous release superseded;
7. `python code/maintain.py` until it reports `0 failed`.

The DOI cannot be written into the files before it exists, so step 5 lands in a
metadata-only commit **after** the tag — as it did for 1.0.0. That is expected;
the tag still identifies the archived bytes, and the follow-up commit changes
only DOI strings and notes.

The API token is never stored in the repository. The helper scripts under
`code/dev/` read it from `$env:TEMP\zenodo_token.txt`; a token placed there, or
in `$env:ZENODO_TOKEN`, must never be committed.
