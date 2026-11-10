from docx import Document

d = Document(r"D:\A_MineralProspecting\docs\Manuscript_v2_draft.docx")
for p in d.paragraphs[:6]:
    if p.text.strip():
        print(repr(p.text))
hits = [p.text for p in d.paragraphs if "0009-0002-3231-0444" in p.text]
print("paragraphs containing the ORCID:", len(hits))
for h in hits:
    print("  ", h[:110])
