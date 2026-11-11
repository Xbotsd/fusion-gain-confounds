import json
import pathlib

variants = {
    "comm_a.json": {"communities": [{"id": "59c3920b-f09b-4dd3-914e-d81ade60b3ae"}]},
    "comm_b.json": {"communities": ["59c3920b-f09b-4dd3-914e-d81ade60b3ae"]},
    "comm_c.json": {"communities": [{"slug": "remote-sensing"}]},
}
tmp = pathlib.Path.home() / "AppData" / "Local" / "Temp"
for name, body in variants.items():
    (tmp / name).write_text(json.dumps(body), encoding="utf-8")
    print("wrote", name, json.dumps(body))
