import json
import pathlib

root = pathlib.Path(__file__).resolve().parents[2]
d = json.loads((root / "processed" / "main_results.json").read_text(encoding="utf-8"))
print(json.dumps(d["autocorr"], indent=1))
