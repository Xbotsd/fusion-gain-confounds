# code/dev — parked utilities

These scripts are NOT part of the pipeline (not in run_all.py, not validated).
They are kept because they document how numbers and documents were produced.

## Data / format archaeology

- `extract_tir_from_ecostress.py` — expects `raw/ecostress/` with ECOSTRESS
  spectral text files, which do not exist locally. Run it manually after
  downloading ECOSTRESS data; it writes `processed/spectra/*_TIR.npy`.
- `inspect_grd.py`, `grd_hex.py`, `gi_strings.py` — one-off reverse-engineering
  of the NGU Geosoft GRD format (used to derive the resistivity statistics in
  `prepare_granite.py`).
- `ocr_request.py` — OCR of a request screenshot (Windows.Media.Ocr).

## Numbers

- `dump_numbers.py` — prints every number the manuscript cites, straight from
  `processed/*.json`.
- `dump_doc_numbers.py` — dumps the scenario tables used by the docs.
- `dump_depth.py` — depth-profile dumps.
- `print_scenario_ci.py` — quick per-scenario CI print (superseded by
  `build_scenario_ci.py`).
- `em_section_numbers.py` — condition numbers, EM contrast, legacy clay weights
  used in manuscript §4.8/§5.2.
- `em_only_diagnostic.py` — EM-only fit under the legacy rows (r = −0.469).
- `em_beta_sensitivity.py` — prototype of `code/run_em_beta_sensitivity.py`.

## Documents

- `rewrite_results.py` — one-off rewrite of manuscript Section 7 into the
  corrected-EM narrative with strict table order.
- `align_framing.py` — rewrites abstract / highlights / contributions /
  conclusion so they match Section 7.
- `build_scenario_ci.py` — regenerates `docs/SCENARIO_CI.md` from
  `processed/scenario_bootstrap.json` (keeps the document in sync by
  construction).

## Housekeeping

- `check_dup.py` — duplicate-scenario check.
- `count_stages.py` — counts stages/scripts in `run_all.STAGES`.
