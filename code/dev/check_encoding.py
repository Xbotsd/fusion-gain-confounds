import pathlib

root = pathlib.Path(__file__).resolve().parents[2]

readme = (root / "README.md").read_text(encoding="utf-8").splitlines()[:5]
for i, ln in enumerate(readme, 1):
    print(i, repr(ln))

cff = (root / "CITATION.cff").read_text(encoding="utf-8")
for key in ("doi:", "version:", "date-released:", "repository-code:"):
    print(key, "->", [ln for ln in cff.splitlines() if ln.startswith(key)])

# any replacement characters anywhere?
bad = []
for p in list(root.glob("*.md")) + list((root / "docs").rglob("*.md")):
    t = p.read_text(encoding="utf-8")
    if "\ufffd" in t:
        bad.append((str(p.relative_to(root)), t.count("\ufffd")))
print("files containing U+FFFD:", bad or "none")
