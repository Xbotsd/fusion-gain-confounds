"""Round-5 final sync: add the new figure to the validator, refresh counts."""
from pathlib import Path

ROOT = Path(r"D:\A_MineralProspecting")

# 1. register the new figure
v = ROOT / "code" / "validate_pipeline.py"
t = v.read_text(encoding="utf-8")
if "generation_sensitivity.png" not in t:
    t = t.replace('    "identifiability.png",',
                  '    "identifiability.png", "generation_sensitivity.png",')
    v.write_text(t, encoding="utf-8")
    print("validator: figure registered")

# 2. refresh manifest size/count in the docs
SUBS = {
    "docs/GAP_AUDIT.md": [("6,688 files / 12.77 GB", "6,700 files / 11.24 GB")],
    "docs/PIPELINE_AUDIT.md": [
        ("(6,688 files)", "(6,700 files)"),
        ("| **6,688** |", "| **6,700** |"),
        ("6,688 files, 12.77 GB", "6,700 files, 11.24 GB"),
    ],
    "docs/CONTINUITY_CHECK.md": [("6,688 文件 / 12.77 GB", "6,700 文件 / 11.24 GB")],
    "docs/READINESS_AUDIT.md": [
        ("6,688 files / 12.77 GB", "6,700 files / 11.24 GB"),
        ("90 validated artefacts, 15 cross-checks", "94 validated artefacts, 19 cross-checks"),
    ],
}
for f, pairs in SUBS.items():
    p = ROOT / f
    s = p.read_text(encoding="utf-8")
    for a, b in pairs:
        if s.count(a) == 0:
            print("MISS", f, a[:40])
        s = s.replace(a, b)
    p.write_text(s, encoding="utf-8")
    print("updated", f)
