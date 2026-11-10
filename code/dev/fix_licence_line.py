import pathlib

root = pathlib.Path(__file__).resolve().parents[2]
r = root / "README.md"
t = r.read_text(encoding="utf-8")
old = "Licence: MIT, with USGS / NASA-METI data notices."
new = "Licence: MIT (Yudong Xu), with third-party data notices in `NOTICE.md`."
assert t.count(old) == 1, "readme licence line not found"
r.write_text(t.replace(old, new), encoding="utf-8")
print("README licence line updated")
