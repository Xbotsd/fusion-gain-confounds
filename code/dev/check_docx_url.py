from docx import Document

d = Document(r"D:\A_MineralProspecting\docs\Manuscript_v2_draft.docx")
hits = [p.text for p in d.paragraphs if "github.com" in p.text]
print("docx paragraphs with the URL:", len(hits))
for h in hits:
    print("...", h[-110:])
