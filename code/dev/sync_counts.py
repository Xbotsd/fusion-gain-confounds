"""Bump the audit counters (invariants 18 -> 19) everywhere they are quoted."""
import pathlib
import re

root = pathlib.Path(__file__).resolve().parents[2]
targets = {
    "docs/GAP_AUDIT.md": [("53/53 artefacts, 18/18 invariants", "53/53 artefacts, 19/19 invariants")],
    "docs/Manuscript_v2_draft.md": [("18 invariants (including the zero-filled and shuffled controls)",
                                     "19 invariants (including the zero-filled and shuffled controls)")],
    "docs/READINESS_AUDIT.md": [("53 artefacts, 18 invariants", "53 artefacts, 19 invariants"),
                                ("| cross-artefact invariants | **18/18** |",
                                 "| cross-artefact invariants | **19/19** |")],
    "README.md": [("checks 53 artefacts and 18 invariants", "checks 53 artefacts and 19 invariants"),
                  ("53 artefacts, 18 invariants", "53 artefacts, 19 invariants")],
    "docs/SUPPLEMENTARY.md": [("53 artefacts, 18 invariants", "53 artefacts, 19 invariants")],
    "docs/COVER_LETTER.md": [],
}
for rel, pairs in targets.items():
    p = root / rel
    t = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if old in t:
            t = t.replace(old, new)
            print(f"{rel}: {old[:45]!r} -> {new[:45]!r}")
        else:
            print(f"!! {rel}: not found {old[:45]!r}")
    p.write_text(t, encoding="utf-8")

# report anything still saying 18 invariants
for f in list((root / "docs").glob("*.md")) + [root / "README.md"]:
    for m in re.finditer(r"18 (?:cross-artefact )?invariants|18/18", f.read_text(encoding="utf-8")):
        print("STALE:", f.name, f.read_text(encoding="utf-8")[:m.start()].count("\n") + 1)
