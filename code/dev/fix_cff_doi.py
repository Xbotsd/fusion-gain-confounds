"""Insert the DOI block into CITATION.cff at top level (after repository-code)."""
import pathlib

root = pathlib.Path(__file__).resolve().parents[2]
cff = root / "CITATION.cff"
lines = cff.read_text(encoding="utf-8").splitlines()

if any(ln.startswith("doi:") and "10.5281" in ln for ln in lines):
    print("CITATION.cff already carries the DOI")
else:
    idx = next(i for i, ln in enumerate(lines) if ln.startswith("repository-code:"))
    block = [
        'version: "1.0.0"',
        'date-released: "2026-11-11"',
        'doi: "10.5281/zenodo.24130421"',
        "identifiers:",
        "  - type: doi",
        "    value: 10.5281/zenodo.24130421",
    ]
    lines[idx + 1:idx + 1] = block
    cff.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("CITATION.cff: doi/version/identifiers inserted")

try:
    import yaml  # type: ignore

    data = yaml.safe_load(cff.read_text(encoding="utf-8"))
    print("YAML ok:", data["doi"], "|", data["version"], "|", data["identifiers"])
except ImportError:
    print("PyYAML not installed; skipped the parse check")
except Exception as exc:  # noqa: BLE001
    print("YAML PARSE ERROR:", exc)
