"""Add the graphical-abstract script and the new controls to the inventory."""
import pathlib

p = pathlib.Path(__file__).resolve().parents[2] / "docs" / "SUPPLEMENTARY.md"
t = p.read_text(encoding="utf-8")

a = "| `run_tir_controls.py` | zero-filled, block-shuffled, noise and ridge controls |"
b = ("| `run_tir_controls.py` | all-zero, Gaussian-noise, block- and pixel-shuffled, "
     "ridge controls |")
assert t.count(a) == 1, "controls row not found"
t = t.replace(a, b)

a2 = "| `build_manifest.py` | SHA-256 inventory |"
b2 = ("| `make_figures.py`, `make_graphical_abstract.py` | paper figures and the "
      "graphical abstract |\n| `build_manifest.py` | SHA-256 inventory |")
assert t.count(a2) == 1, "manifest row not found"
t = t.replace(a2, b2)

p.write_text(t, encoding="utf-8")
print("supplementary inventory updated")
