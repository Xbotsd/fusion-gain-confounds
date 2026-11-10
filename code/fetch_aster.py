"""Archive the raw ASTER L1T TIR scenes used by the pipeline (network, run once).

Downloads, for each acquisition date, every ASTER L1T scene that intersects the
survey footprint: the TIR GeoTIFF (5 bands, 90 m, uint16 DN) and its granule
XML.  Files go to raw/aster/<date>/ together with a manifest recording the STAC
item ids, source URLs (without the SAS token), sizes and SHA-256.

After this has run once, `prepare_tir_real.py` works offline from raw/aster/.
"""
from __future__ import annotations

import hashlib
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import common as C

STAC = "https://planetarycomputer.microsoft.com/api/stac/v1"
SAS = "https://planetarycomputer.microsoft.com/api/sas/v1/token/aster-l1t"
BBOX = "-116.6,34.7,-114.9,35.9"
DATES = ("2006-10-18", "2006-09-25")
DEST = C.RAW / "aster"


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "amp/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def fetch(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "amp/1.0"})
    with urllib.request.urlopen(req, timeout=600) as r, open(path, "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(dates=DATES):
    token = get_json(SAS)["token"]
    for date in dates:
        q = urllib.parse.urlencode({
            "collections": "aster-l1t", "bbox": BBOX,
            "datetime": f"{date}T00:00:00Z/{date}T23:59:59Z", "limit": 50})
        items = get_json(f"{STAC}/search?{q}")["features"]
        out = DEST / date
        out.mkdir(parents=True, exist_ok=True)
        rows = []
        for it in items:
            for key in ("TIR", "xml"):
                href = it["assets"][key]["href"]
                name = Path(urllib.parse.urlparse(href).path).name
                path = out / name
                if not path.exists():
                    print(f"  downloading {name}")
                    fetch(href + "?" + token, path)
                rows.append({"item": it["id"], "asset": key, "file": name,
                             "url": href, "bytes": path.stat().st_size,
                             "sha256": sha256(path),
                             "datetime": it["properties"]["datetime"],
                             "bbox": it.get("bbox")})
        C.save_json(out / "manifest.json", {
            "source": "Microsoft Planetary Computer, collection aster-l1t "
                      "(ASTER L1T v003, NASA/METI)",
            "stac_api": STAC, "date": date, "bbox_query": BBOX,
            "n_scenes": len(items), "files": rows})
        print(f"{date}: {len(items)} scenes, {len(rows)} files -> {out}")


if __name__ == "__main__":
    main(tuple(sys.argv[1:]) or DATES)
