"""Read-only maintenance check for the repository and its Zenodo archive.

The project has two maintained objects and they must stay consistent:

  * the GitHub repository https://github.com/Xbotsd/fusion-gain-confounds
  * the Zenodo record https://zenodo.org/records/24130421 (version 1.0.0)

This script checks the things that can silently drift: the version strings, the
DOI strings, the tag that the archive was made from, the record's metadata and
checksum, the GitHub release, stale placeholders, encoding damage, and the last
validator run. It modifies nothing and needs no credentials.

    python code/maintain.py            # everything
    python code/maintain.py --offline  # skip the two network checks

Exit code 0 when nothing failed (warnings are allowed), 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = "Xbotsd/fusion-gain-confounds"
RECORD = "24130421"
DOI = "10.5281/zenodo.24130421"
CONCEPT_DOI = "10.5281/zenodo.24130420"
ARCHIVED_COMMIT = "2d194a2"
VERSION_TAG = "v1.0.0"

RESULTS: list[tuple[str, str, str]] = []  # (status, name, detail)


def add(status: str, name: str, detail: str = "") -> None:
    RESULTS.append((status, name, detail))


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, encoding="utf-8").stdout.strip()


def get_json(url: str, timeout: int = 25):
    req = urllib.request.Request(
        url, headers={"User-Agent": "fusion-gain-confounds-maintain",
                      "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def check_git() -> None:
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    head = git("rev-parse", "--short", "HEAD")
    dirty = git("status", "--porcelain")
    add("WARN" if dirty else "PASS", "git tree",
        f"{len(dirty.splitlines())} modified path(s)" if dirty
        else f"clean at {head} on {branch}")

    ahead = int(git("rev-list", "--count", "origin/main..HEAD") or 0)
    behind = int(git("rev-list", "--count", "HEAD..origin/main") or 0)
    if ahead and behind:
        add("FAIL", "git sync", f"{ahead} ahead, {behind} behind origin/main")
    elif ahead:
        add("WARN", "git sync", f"{ahead} commit(s) not pushed")
    elif behind:
        add("WARN", "git sync", f"{behind} commit(s) behind origin/main")
    else:
        add("PASS", "git sync", "equal to origin/main")

    tagged = git("rev-parse", "--verify", f"{VERSION_TAG}^{{}}")
    target = git("rev-parse", "--verify", ARCHIVED_COMMIT)
    if not tagged:
        add("FAIL", "version tag", f"{VERSION_TAG} is missing")
    elif target and tagged == target:
        add("PASS", "version tag", f"{VERSION_TAG} -> {ARCHIVED_COMMIT} (archived commit)")
    else:
        add("WARN", "version tag",
            f"{VERSION_TAG} -> {tagged[:7]}, archive is {ARCHIVED_COMMIT}")


def local_versions() -> dict[str, str]:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    zen = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    return {
        "pyproject.toml": re.search(r'^version = "([^"]+)"', pyproject, re.M).group(1),
        "CITATION.cff": re.search(r'^version: "([^"]+)"', cff, re.M).group(1),
        ".zenodo.json": zen["version"],
    }


def check_versions(record_version: str | None) -> None:
    versions = local_versions()
    if len(set(versions.values())) == 1:
        add("PASS", "version strings", " = ".join(f"{k} {v}" for k, v in versions.items()))
    else:
        add("FAIL", "version strings", json.dumps(versions))
    if record_version is not None:
        if record_version == versions[".zenodo.json"]:
            add("PASS", "record version", record_version)
        else:
            add("FAIL", "record version",
                f"Zenodo {record_version} != .zenodo.json {versions['.zenodo.json']}")


def check_dois() -> None:
    wanted = {
        "README.md": DOI,
        "CITATION.cff": DOI,
        "docs/GITHUB_SETUP.md": DOI,
        "docs/Manuscript_v2_draft.md": DOI,
    }
    missing = [f for f, doi in wanted.items()
               if doi not in (ROOT / f).read_text(encoding="utf-8")]
    add("FAIL" if missing else "PASS", "DOI strings",
        f"missing in {missing}" if missing else f"{DOI} in the four expected files")

    setup = (ROOT / "docs/GITHUB_SETUP.md").read_text(encoding="utf-8")
    add("PASS" if CONCEPT_DOI in setup else "FAIL", "concept DOI",
        CONCEPT_DOI if CONCEPT_DOI in setup else f"{CONCEPT_DOI} not in GITHUB_SETUP.md")


CURRENT_DOCS = ["README.md", "CITATION.cff", "docs/Manuscript_v2_draft.md",
                "docs/READINESS_AUDIT.md", "docs/GAP_AUDIT.md",
                "docs/SUPPLEMENTARY.md", "docs/GITHUB_SETUP.md",
                "docs/COVER_LETTER.md", "docs/submission/README.md"]


def check_text() -> None:
    placeholders = ["on acceptance", "to be inserted", "will be archived with a DOI",
                    "DOI TBD"]
    bad_encoding, stale = [], []
    for rel in CURRENT_DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        if "\ufffd" in text:
            bad_encoding.append(rel)
        for marker in placeholders:
            if marker in text:
                stale.append(f"{rel}: {marker!r}")
    add("FAIL" if bad_encoding else "PASS", "encoding",
        f"U+FFFD in {bad_encoding}" if bad_encoding else f"{len(CURRENT_DOCS)} current docs clean")
    add("FAIL" if stale else "PASS", "placeholders",
        "; ".join(stale) if stale else "none in the current docs")


def check_zenodo() -> str | None:
    try:
        rec = get_json(f"https://zenodo.org/api/records/{RECORD}")
    except Exception as exc:  # noqa: BLE001
        add("FAIL", "zenodo record", f"{type(exc).__name__}: {exc}")
        return None
    md = rec.get("metadata", {})
    version = md.get("version")
    status = rec.get("status", "?")
    files = rec.get("files", [])
    if status == "published" and files:
        add("PASS", "zenodo record", f"{status}, version {version}, {len(files)} file(s)")
    else:
        add("FAIL", "zenodo record", f"status {status}, {len(files)} file(s)")

    if files:
        chk = files[0].get("checksum", "")
        add("PASS" if chk.startswith("md5:") else "WARN", "zenodo checksum",
            f"{files[0].get('key')} {chk}")

    local = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    if md.get("title") != local["title"]:
        add("FAIL", "record title", "differs from .zenodo.json")
    else:
        add("PASS", "record title", "matches .zenodo.json")
    if md.get("description", "").replace("&amp;", "&") != local["description"]:
        add("WARN", "record description", "differs from .zenodo.json (metadata drift)")
    else:
        add("PASS", "record description", "matches .zenodo.json")
    return version


def check_github() -> None:
    try:
        repo = get_json(f"https://api.github.com/repos/{REPO}")
        add("PASS" if not repo.get("private") else "FAIL", "github repo",
            f"{repo.get('full_name')} public={not repo.get('private')} "
            f"branch={repo.get('default_branch')}")
    except Exception as exc:  # noqa: BLE001
        add("FAIL", "github repo", f"{type(exc).__name__}: {exc}")
        return

    try:
        rel = get_json(f"https://api.github.com/repos/{REPO}/releases/tags/{VERSION_TAG}")
        add("PASS", "github release", f"{rel.get('tag_name')} ({rel.get('html_url')})")
    except urllib.error.HTTPError as exc:
        add("FAIL", "github release", f"{VERSION_TAG} not found (HTTP {exc.code})")
    except Exception as exc:  # noqa: BLE001
        add("FAIL", "github release", f"{type(exc).__name__}: {exc}")

    try:
        runs = get_json(f"https://api.github.com/repos/{REPO}/actions/runs?per_page=5")
        run = runs.get("workflow_runs", [{}])[0]
        ok = run.get("conclusion") == "success"
        add("PASS" if ok else "WARN", "github CI",
            f"{run.get('name')} {run.get('conclusion')} {run.get('created_at')} "
            f"{run.get('html_url')}")
    except Exception as exc:  # noqa: BLE001
        add("WARN", "github CI", f"{type(exc).__name__}: {exc}")


def check_validator() -> None:
    path = ROOT / "processed" / "pipeline_validation.json"
    if not path.is_file():
        add("WARN", "validator", "no processed/pipeline_validation.json")
        return
    v = json.loads(path.read_text(encoding="utf-8"))
    checks = v.get("cross_checks", [])
    failed = [c["check"] for c in checks if not c.get("ok")]
    yield_ = v.get("yield", {})
    artefacts = f"{yield_.get('artifacts_present')}/{yield_.get('artifacts_expected')}"
    ok = v.get("status") == "PASS" and not failed
    add("PASS" if ok else "FAIL", "validator",
        f"{v.get('status')} {artefacts} artefacts, "
        f"{len(checks) - len(failed)}/{len(checks)} invariants, "
        f"run {v.get('generated_at')}")
    if failed:
        add("FAIL", "validator failures", ", ".join(failed))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--offline", action="store_true", help="skip network checks")
    args = ap.parse_args()

    print(f"maintain: {REPO}  (record {RECORD})")
    check_git()
    record_version = None if args.offline else check_zenodo()
    if args.offline:
        add("WARN", "zenodo record", "skipped (--offline)")
    check_versions(record_version)
    check_dois()
    check_text()
    if args.offline:
        add("WARN", "github", "skipped (--offline)")
    else:
        check_github()
    check_validator()

    print()
    for status, name, detail in RESULTS:
        print(f"[{status}] {name}: {detail}")
    counts = {s: sum(1 for r in RESULTS if r[0] == s) for s in ("PASS", "WARN", "FAIL")}
    print(f"\n{counts['PASS']} passed, {counts['WARN']} warnings, "
          f"{counts['FAIL']} failed")
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
