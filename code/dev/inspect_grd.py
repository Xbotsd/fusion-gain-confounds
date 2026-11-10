"""Inspect a Geosoft GRD grid (header + .gi info) without console encoding issues."""
import pathlib
import struct
import sys
import tempfile
import zipfile

z = zipfile.ZipFile(r"D:\A_MineralProspecting\raw\Sulitjelma_2025_EM_Database_AIQ_Res.zip")
d = pathlib.Path(tempfile.mkdtemp())
for n in z.namelist():
    if n.endswith((".GRD", ".gi")):
        z.extract(n, d)
g = d / "Sulitjelma_2025_EM_Database_AIQ_Res.GRD"
raw = g.read_bytes()

out = []
out.append("GRD head hex: " + raw[:80].hex())
# Geosoft header: int32 magic, int32 version, int32 ny, int32 nx ...
magic, ver, ny, nx, celltype = struct.unpack("<5i", raw[:20])
out.append(f"magic={magic} ver={ver} ny={ny} nx={nx} celltype={celltype}")
out.append(f"floats at 20..44: {struct.unpack('<4f', raw[20:36])}")

gi = (d / "Sulitjelma_2025_EM_Database_AIQ_Res.GRD.gi").read_bytes()
out.append("GI first 400 bytes repr:")
out.append(repr(gi[:400]))
pathlib.Path(r"D:\A_MineralProspecting\raw\grd_inspect.txt").write_text(
    "\n".join(out), encoding="utf-8")
print("saved raw/grd_inspect.txt")
