"""Point run_main's docstring at the authoritative autocorrelation artefact."""
import pathlib

p = pathlib.Path(__file__).resolve().parents[1] / "run_main.py"
t = p.read_text(encoding="utf-8")
old = "F. autocorr      integral scale, design effect, N_eff for the main clay map"
new = ("F. autocorr      quick integral scale / design effect / N_eff for the fused map\n"
       "                 (the values quoted in the paper come from autocorr.json)")
assert t.count(old) == 1
p.write_text(t.replace(old, new), encoding="utf-8")
print("docstring updated")
