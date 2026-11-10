"""Scan the Geosoft .gi (OLE compound) for readable metadata/statistics."""
import pathlib
import re
import tempfile
import zipfile

z = zipfile.ZipFile(r"D:\A_MineralProspecting\raw\Sulitjelma_2025_EM_Database_AIQ_Res.zip")
d = pathlib.Path(tempfile.mkdtemp())
for n in z.namelist():
    if n.endswith(".gi"):
        z.extract(n, d)
gi = (d / "Sulitjelma_2025_EM_Database_AIQ_Res.GRD.gi").read_bytes()

out = [f"gi size {len(gi)}"]
# ASCII strings of length >= 4
strs = re.findall(rb"[\x20-\x7e]{4,}", gi)
for s in strs:
    t = s.decode("ascii")
    out.append(t)

# UTF-16LE strings
u = re.findall(rb"(?:[\x20-\x7e]\x00){4,}", gi)
for s in u[:40]:
    out.append("U16: " + s.decode("utf-16-le"))

pathlib.Path(r"D:\A_MineralProspecting\raw\gi_strings.txt").write_text(
    "\n".join(out), encoding="utf-8")
print(f"saved raw/gi_strings.txt ({len(strs)} ascii, {len(u)} utf16)")
