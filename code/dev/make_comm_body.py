import json
import pathlib

body = {"receiver": "59c3920b-f09b-4dd3-914e-d81ade60b3ae",
        "type": "community-inclusion"}
p = pathlib.Path.home() / "AppData" / "Local" / "Temp" / "zenodo_comm.json"
p.write_text(json.dumps(body), encoding="utf-8")
print("wrote", p)
