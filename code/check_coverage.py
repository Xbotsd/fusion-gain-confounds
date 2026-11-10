"""Coverage check: every validated artefact must have a producer in run_all.py.

This guards the failure mode where a new artefact is added to
validate_pipeline.EXPECTED_* but its script is forgotten in run_all.STAGES,
so a fresh `run_all.py all` would fail validation.

Exit code 0 when covered, 1 otherwise. Listed in the `audit` stage.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE))

import validate_pipeline as V  # noqa: E402

# artefacts built by appending a suffix at run time (--emfix wrappers)
SUFFIXED = re.compile(r"_emfix\.(json|csv|md|png|npy)$")


def main():
    run_all_src = (CODE / "run_all.py").read_text(encoding="utf-8")
    listed = set(re.findall(r'"([a-z0-9_]+\.py)"', run_all_src))

    expected = (list(V.EXPECTED_NPY) + list(V.EXPECTED_JSON)
                + list(V.EXPECTED_FIG))

    producers = {}
    for py in sorted(CODE.glob("*.py")):
        if py.name in {"run_all.py", "validate_pipeline.py", "test_core.py",
                       "check_coverage.py"}:
            continue
        src = py.read_text(encoding="utf-8", errors="ignore")
        for name in expected:
            stem = name.split("/")[-1]
            base = stem.rsplit(".", 1)[0]
            if (f'"{stem}"' in src or f"'{stem}'" in src
                    or f'"{base}"' in src or f"'{base}'" in src):
                producers.setdefault(name, set()).add(py.name)

    problems = []
    for name in expected:
        prod = producers.get(name, set())
        if not prod:
            if SUFFIXED.search(name):
                continue  # produced by a suffix-building script
            problems.append((name, "no producer script found"))
            continue
        covered = [p for p in prod if p in listed]
        if not covered:
            problems.append((name, f"producer(s) {sorted(prod)} not in run_all"))

    print(f"expected artefacts : {len(expected)}")
    print(f"uncovered          : {len(problems)}")
    for name, why in problems:
        print(f"  [!] {name}: {why}")

    if problems:
        print("FAIL: add the producer scripts to run_all.STAGES")
        sys.exit(1)
    print("PASS: every artefact has a producer in run_all.py")


if __name__ == "__main__":
    main()
