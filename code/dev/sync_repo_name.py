"""Point every reference at the renamed repository."""
import pathlib

root = pathlib.Path(__file__).resolve().parents[2]
OLD = "https://github.com/Xbotsd/ivanpah-fusion-benchmark"
NEW = "https://github.com/Xbotsd/fusion-gain-confounds"

changed = []
for p in list(root.glob("*.md")) + list((root / "docs").rglob("*.md")) + [
        root / "CITATION.cff", root / ".zenodo.json"]:
    if not p.exists():
        continue
    t = p.read_text(encoding="utf-8")
    if OLD in t:
        p.write_text(t.replace(OLD, NEW), encoding="utf-8")
        changed.append(str(p.relative_to(root)))

print("updated:", changed)

# any stragglers anywhere in tracked text?
import subprocess
out = subprocess.run(["git", "grep", "-l", "ivanpah-fusion-benchmark"],
                     cwd=root, capture_output=True, text=True)
print("stragglers:", out.stdout.strip() or "none")
