"""Journal-format fixes: six keywords, double-spaced review copy."""
import pathlib

root = pathlib.Path(__file__).resolve().parents[2]

ms = root / "docs" / "Manuscript_v2_draft.md"
t = ms.read_text(encoding="utf-8")
old = ("**Keywords:** airborne mineral exploration; gamma-ray spectrometry; "
       "thermal infrared; ASTER; multi-modal fusion; identifiability; "
       "reproducibility; benchmark")
new = ("**Keywords:** airborne mineral exploration; gamma-ray spectrometry; "
       "thermal infrared; ASTER; multi-modal fusion; identifiability")
assert t.count(old) == 1, "keyword line not found"
ms.write_text(t.replace(old, new), encoding="utf-8")
print("keywords: 8 -> 6")

b = root / "docs" / "build_draft_docx.py"
s = b.read_text(encoding="utf-8")
old2 = '    st.paragraph_format.line_spacing = 1.4'
new2 = ('    st.paragraph_format.line_spacing = 2.0  # double-spaced review copy '
        '(Elsevier)')
assert s.count(old2) == 1
b.write_text(s.replace(old2, new2), encoding="utf-8")
print("line spacing: 1.4 -> 2.0")
