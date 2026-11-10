"""Reverse-engineer Geosoft GRD v2: hex dump header area + try int16/float32 views."""
import pathlib
import struct
import tempfile
import zipfile

import numpy as np

z = zipfile.ZipFile(r"D:\A_MineralProspecting\raw\Sulitjelma_2025_EM_Database_AIQ_Res.zip")
d = pathlib.Path(tempfile.mkdtemp())
for n in z.namelist():
    if n.endswith(".GRD"):
        z.extract(n, d)
g = d / "Sulitjelma_2025_EM_Database_AIQ_Res.GRD"
raw = g.read_bytes()

out = []
out.append(f"file size {len(raw)}")
ny, nx = 938, 512
out.append(f"cells {ny*nx} -> {ny*nx*2} (int16) {ny*nx*4} (f32)")

for start in range(0x40, 0x140, 16):
    chunk = raw[start:start + 16]
    out.append(f"{start:#04x}: {chunk.hex(' ')}")

# candidate data start offsets
for off in (0x54, 0x5C, 0x60, 0x64, 0x80):
    i16 = np.frombuffer(raw, dtype="<i2", offset=off, count=24)
    f32 = np.frombuffer(raw, dtype="<f4", offset=off, count=12)
    out.append(f"off {off:#04x} i16: {i16.tolist()}")
    out.append(f"off {off:#04x} f32: {np.round(f32, 3).tolist()}")

# scan for first plausible large float (resistivity range 1..1e6)
n = (len(raw) - 0x40) // 4
f32all = np.frombuffer(raw, dtype="<f4", offset=0x40, count=n)
ok = np.where((np.abs(f32all) > 1) & (np.abs(f32all) < 1e7) & np.isfinite(f32all))[0]
out.append(f"first plausible floats at word idx (from 0x40): {ok[:10].tolist()}")
for i in ok[:10]:
    out.append(f"  byte {0x40 + 4 * i:#06x}: {f32all[i]:.4g}")

pathlib.Path(r"D:\A_MineralProspecting\raw\grd_hex.txt").write_text(
    "\n".join(out), encoding="utf-8")
print("saved raw/grd_hex.txt")
