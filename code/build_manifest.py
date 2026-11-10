"""Build a machine-readable manifest of the whole project.

For every file under raw/, processed/, docs/ and code/ it records:
  * relative path, size, SHA-256;
  * schema for .npy (shape, dtype), .csv (rows, header), .json (top-level keys);
  * pipeline stage inferred from the filename;
  * a summary of counts and bytes per stage.

Writes processed/data_manifest.json.
"""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "processed" / "data_manifest.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stage_of(rel: str) -> str:
    p = rel.replace("\\", "/")
    name = Path(p).name
    if "/" not in p:
        suffix = Path(p).suffix.lower()
        if suffix in {".shp", ".shx", ".dbf", ".prj", ".sbn", ".sbx", ".cpg", ".xml"}:
            return "survey_vector"
        if suffix == ".pdf":
            return "report"
        if suffix == ".csv":
            return "survey_data"
        if suffix == ".docx":
            return "manuscript"
        return "root"
    if p.startswith("raw/"):
        return "raw"
    if p.startswith("code/"):
        return "code"
    if p.startswith("docs/"):
        return "docs"
    if p.startswith("processed/em/"):
        return "assets_em"
    if p.startswith("processed/spectra/"):
        return "assets_spectra"
    if name.endswith(".log"):
        return "logs"
    if name.startswith(("repeat", "repeats")):
        return "repeats"
    if name.startswith(("pipeline_validation", "data_manifest", "output_yield")):
        return "audit"
    if name.startswith(("gamma_cube", "tir_cube", "em_cube", "clay_prior",
                        "truth_abundance", "valid_mask", "ratio_",
                        "em_dep_", "em_layer_")):
        return "prepared"
    if name.startswith(("kf_", "wls_", "fusion")):
        return "fusion"
    if name.startswith("depth"):
        return "depth"
    if name.startswith(("ablation", "validation", "baselines", "sensitivity",
                        "environment", "resolution")):
        return "evaluation"
    if name.startswith("env_"):
        return "environment"
    if name.startswith(("fig_", "kf_fusion_final", "kf_uncertainty_map")):
        return "figures"
    return "other"


def schema(path: Path):
    suffix = path.suffix.lower()
    try:
        if suffix == ".npy":
            a = np.load(path, mmap_mode="r")
            return {"shape": list(a.shape), "dtype": str(a.dtype)}
        if suffix == ".csv":
            with open(path, "r", encoding="utf-8", errors="ignore", newline="") as f:
                reader = csv.reader(f)
                header = next(reader, [])
                rows = sum(1 for _ in reader)
            return {"rows": rows, "columns": len(header), "header": header[:20]}
        if suffix == ".json":
            d = json.loads(path.read_text(encoding="utf-8"))
            return {"keys": sorted(d)[:20] if isinstance(d, dict) else None}
    except Exception as exc:  # noqa: BLE001
        return {"schema_error": str(exc)}
    return {}


def main():
    files = []
    summary = {}
    root_suffixes = {".shp", ".shx", ".dbf", ".prj", ".sbn", ".sbx",
                     ".cpg", ".xml", ".pdf", ".csv", ".docx", ".bat"}
    candidates = [p for p in ROOT.glob("*")
                  if p.is_file() and (p.suffix.lower() in root_suffixes
                                      or p.name in {"LICENSE", "run.bat"})]
    for folder in ("raw", "processed", "docs", "code"):
        candidates.extend(sorted((ROOT / folder).rglob("*")))
    for path in candidates:
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix in {".pyc"}:
            continue
        if path == OUT:
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        item = {
            "path": rel,
            "stage": stage_of(rel),
            "size": path.stat().st_size,
            "sha256": sha256(path),
            "schema": schema(path),
        }
        files.append(item)
        s = summary.setdefault(item["stage"], {"files": 0, "bytes": 0})
        s["files"] += 1
        s["bytes"] += item["size"]

    report = {
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "root": str(ROOT),
        "n_files": len(files),
        "total_bytes": sum(f["size"] for f in files),
        "summary": summary,
        "files": files,
    }
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"saved {OUT}")
    print(f"files {len(files)}  size {report['total_bytes']/1e9:.2f} GB")
    for k, v in summary.items():
        print(f"  {k:12s} {v['files']:4d} files  {v['bytes']/1e6:9.2f} MB")


if __name__ == "__main__":
    main()
