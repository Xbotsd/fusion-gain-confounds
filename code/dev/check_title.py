import pathlib

root = pathlib.Path(__file__).resolve().parents[2]
lines = (root / "docs" / "Manuscript_v2_draft.md").read_text(encoding="utf-8").splitlines()[:6]
for i, ln in enumerate(lines, 1):
    print(i, repr(ln))
print("superscript one U+00B9 present:", "\u00b9" in "\n".join(lines))
