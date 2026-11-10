"""Report pixel size and embedded dpi of every figure, for the submission check."""
import glob
import os

from PIL import Image

root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
for f in sorted(glob.glob(os.path.join(root, "processed", "*.png"))):
    with Image.open(f) as im:
        w, h = im.size
        dpi = im.info.get("dpi", ("?", "?"))
        ok = "OK " if (dpi[0] != "?" and float(dpi[0]) >= 300) else "LOW"
        print(f"{ok} {os.path.basename(f):30s} {w:5d}x{h:5d}  dpi={dpi}  "
              f"{os.path.getsize(f) // 1024:5d} KB")
