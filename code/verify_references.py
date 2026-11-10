"""Verify candidate references against Crossref.

Reads the candidate titles used in docs/Manuscript_v2_draft.md, queries
Crossref, and writes docs/references_verified.md + .json with the best match.
A match is only a suggestion: the authors must check the final citation.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / "docs" / "references_verified.md"
OUT_JSON = ROOT / "docs" / "references_verified.json"

REFS = [
    ("IAEA 2003", "Guidelines for radioelement mapping using gamma ray spectrometry data"),
    ("Minty 1997", "Fundamentals of airborne gamma-ray spectrometry"),
    ("Wilford 1997", "Application of airborne gamma-ray spectrometry in soil regolith mapping and applied geomorphology"),
    ("Dickson 1997", "Interpretation of aerial gamma-ray surveys adding the geochemical factors"),
    ("Fountain 1998", "Airborne electromagnetic systems 50 years of development"),
    ("Siemon 2009", "Laterally constrained inversion of helicopter-borne frequency-domain electromagnetic data"),
    ("Dentith 2014", "Geophysics for the mineral exploration geoscientist"),
    ("Christensen 2000", "A thermal emission spectral library of rock-forming minerals"),
    ("Salisbury 1991", "Infrared spectra of minerals"),
    ("Ramsey 1998", "Mineral abundance determination quantitative deconvolution of thermal emission spectra"),
    ("Kalman 1960", "A new approach to linear filtering and prediction problems"),
    ("Maybeck 1979", "Stochastic models estimation and control"),
    ("Bar-Shalom 2001", "Estimation with applications to tracking and navigation"),
    ("Julier 1997", "A non-divergent estimation algorithm in the presence of correlations"),
    ("Sun 2016", "Return of frustratingly easy domain adaptation"),
    ("Wilkinson 2016", "The FAIR Guiding Principles for scientific data management and stewardship"),
    ("Peng 2011", "Reproducible research in computational science"),
    ("Powers 2011", "Evaluation from precision recall and F-measure to ROC informedness markedness and correlation"),
    ("Reeves 2005", "Aeromagnetic surveys principles practice and interpretation"),
    ("Nabighian 1988", "Electromagnetic methods in applied geophysics"),
    ("Telford 1990", "Applied geophysics"),
    ("Hook 1999", "Use of multispectral thermal infrared data in geological studies"),
    ("Gnojek 1985", "A new zinc mineralization detected by airborne gamma-ray spectrometry in northern Moravia"),
    ("Kruse 1993", "The spectral image processing system SIPS interactive visualization and analysis of imaging spectrometer data"),
]


def query(title: str):
    q = urllib.parse.urlencode({"query.bibliographic": title, "rows": 1,
                                "select": "DOI,title,author,container-title,issued"})
    req = urllib.request.Request(
        f"https://api.crossref.org/works?{q}",
        headers={"User-Agent": "A_MineralProspecting/1.0 (mailto:3468858545@qq.com)"},
    )
    with urllib.request.urlopen(req, timeout=40) as r:
        data = json.load(r)
    items = data["message"]["items"]
    if not items:
        return None
    it = items[0]
    year = None
    if it.get("issued", {}).get("date-parts"):
        year = it["issued"]["date-parts"][0][0]
    authors = it.get("author", [])
    first = authors[0].get("family", "") if authors else ""
    return {
        "doi": it.get("DOI"),
        "title": (it.get("title") or [""])[0],
        "year": year,
        "first_author": first,
        "journal": (it.get("container-title") or [""])[0],
    }


def main():
    rows = []
    for key, title in REFS:
        try:
            hit = query(title)
        except Exception as exc:  # noqa: BLE001
            hit = {"error": str(exc)}
        rows.append({"key": key, "query": title, "match": hit})
        print(f"{key:20s} -> {hit.get('doi') if hit else None}")
        time.sleep(0.3)

    OUT_JSON.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["# Reference verification (Crossref suggestions)", "",
             "A match is a suggestion, not a guarantee; check volume/pages before submission.",
             "", "| key | DOI | year | first author | journal | matched title |",
             "|---|---|---:|---|---|---|"]
    for r in rows:
        m = r["match"] or {}
        if m.get("error"):
            lines.append(f"| {r['key']} | ERROR | | | | {m['error']} |")
            continue
        lines.append(
            f"| {r['key']} | {m.get('doi','')} | {m.get('year','')} | "
            f"{m.get('first_author','')} | {m.get('journal','')} | {m.get('title','')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved {OUT_MD} and {OUT_JSON}")


if __name__ == "__main__":
    main()

