"""Download five ASU thermal-emission endmembers (guest access, no API key).

The ASU Spectral Library exposes a small export flow used by its web UI:
  login.php?login=1&username=guest&password=guest
  ajax/generate_export.php?spectra=<id>&type=lab1&format=ascii
  inc/get_exported.php?spectra=<id>&type=lab1&format=ascii&f=<name>

Each export is a ZIP with `guest_lab1.txt` (wavenumber, emissivity) and
`guest_meta.txt`.  This script saves the two-column spectra under
raw/ASU_spectra/ and writes a small metadata JSON.

Requires only the Python standard library.  Network access to
speclib.asu.edu is needed; retries handle the occasional TLS timeout.
"""
from __future__ import annotations

import io
import json
import re
import time
import urllib.parse
import urllib.request
import zipfile
from http.cookiejar import CookieJar
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "raw" / "ASU_spectra"
BASE = "https://speclib.asu.edu"

# mineral name -> ASU spectrum id (public library unless noted)
TARGETS = {
    "Quartz": 479,       # BUR-4120, coarse particulate
    "Feldspar": 468,     # Microcline BUR-3460, coarse particulate
    "Clay": 571,         # Kaolinite KGa-1b, coarse particulate
    "Calcite": 604,      # C2, 710-1000 um (ASU Calcite library 1734)
    "Dolomite": 515,     # C20, hand sample
}


def opener():
    jar = CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def get(op, url, timeout=60, retries=3):
    last = None
    for k in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with op.open(req, timeout=timeout) as r:
                return r.read()
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(2 + k)
    raise RuntimeError(f"failed {url}: {last}")


def fetch_one(op, mineral: str, spec_id: int):
    q = urllib.parse.urlencode({"spectra": spec_id, "type": "lab1", "format": "ascii"})
    gen = get(op, f"{BASE}/ajax/generate_export.php?{q}")
    if gen.strip() != b"1":
        raise RuntimeError(f"generate_export returned {gen[:80]!r}")
    q2 = urllib.parse.urlencode({"spectra": spec_id, "type": "lab1",
                                 "format": "ascii", "f": f"{mineral}_{spec_id}"})
    blob = get(op, f"{BASE}/inc/get_exported.php?{q2}")
    z = zipfile.ZipFile(io.BytesIO(blob))
    names = z.namelist()
    data_name = next(n for n in names if n.endswith("lab1.txt"))
    meta_name = next(n for n in names if n.endswith("meta.txt"))
    text = z.read(data_name).decode("utf-8", "ignore")
    meta = z.read(meta_name).decode("utf-8", "ignore")
    rows = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            try:
                rows.append((float(parts[0]), float(parts[1])))
            except ValueError:
                continue
    if len(rows) < 20:
        raise RuntimeError(f"only {len(rows)} numeric rows for {mineral}")
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{mineral}_{spec_id}.txt"
    path.write_text("\n".join(f"{wn:.6f}\t{em:.8f}" for wn, em in rows),
                    encoding="utf-8")
    return {
        "mineral": mineral,
        "spec_id": spec_id,
        "rows": len(rows),
        "wavenumber_range": [min(r[0] for r in rows), max(r[0] for r in rows)],
        "emissivity_range": [min(r[1] for r in rows), max(r[1] for r in rows)],
        "meta_head": meta.splitlines()[:2],
        "file": str(path.relative_to(ROOT)).replace("\\", "/"),
    }


def main():
    op = opener()
    get(op, f"{BASE}/login.php?login=1&username=guest&password=guest")
    records = []
    for mineral, spec_id in TARGETS.items():
        rec = fetch_one(op, mineral, spec_id)
        records.append(rec)
        print(f"{mineral:10s} id={spec_id:4d} rows={rec['rows']:4d} "
              f"wn={rec['wavenumber_range']} em={rec['emissivity_range']}")
    (OUT / "meta.json").write_text(
        json.dumps({"source": "ASU Thermal Emission Spectral Library",
                    "url": BASE, "records": records}, indent=2),
        encoding="utf-8")
    print(f"saved {len(records)} spectra to {OUT}")


if __name__ == "__main__":
    main()
