# Real TIR / EM data search

The user asked for real TIR/EM data downloaded and used in the experiment. This
note records what was found and why no matching real image was used.

## Found and used

| source | what it is | use |
|---|---|---|
| ASU Thermal Emission Spectral Library | measured lab emissivity for quartz, feldspar, clay, calcite, dolomite | ASU endmember variant (`docs/ASU_VARIANT.md`) |
| USGS SIM 3206 | surficial geologic map and GIS database, Ivanpah 30' × 60' | independent substrate check (`docs/INDEPENDENT_VALIDATION.md`) |
| USGS AEM Basin and Range 2022–2023 | real helicopter AEM resistivity models, DOI 10.5066/P1UKDJSM | metadata reviewed; not used (see below) |

## Found but not usable

1. **USGS AEM 2022–2023** — covers western Nevada/eastern California, but the
   southern bound is about 36.97°N; Ivanpah is about 35.4°N. It does not overlap
   the survey. The netCDF collection is also ~17.5 GB. Using it would be a
   cross-site transfer experiment, not a same-area validation.
2. **ASTER L1T / ECOSTRESS / Landsat TIRS** — real thermal infrared, but access
   requires NASA Earthdata Login and the native resolution is 70–100 m (ASTER
   90 m, Landsat 100 m), not the 50 m survey grid. No credentials were available
   in this environment. The unfinished `code/extract_tir_from_ecostress.py`
   expects a local `raw/ecostress` folder that does not exist.
3. **Airborne EM over Ivanpah** — no public same-area AEM survey was found. The
   USGS AEM coverage above is the nearest regional dataset.

## Consequence

The main experiment still uses **synthetic TIR and EM** generated from real
endmembers/AEM statistics. The real-data checks are:

- real ASU endmembers (negative control, F1 0.132);
- real USGS geology (qualitative substrate consistency, p<0.001);
- real gamma survey (the primary modality).

This is a limitation, not a hidden assumption. A true real-TIR/EM test needs
either an Earthdata account plus ASTER/ECOSTRESS acquisition, or a field
spectrometer/AEM survey over the Ivanpah grid.

## What would be needed

- NASA Earthdata account and ASTER/ECOSTRESS granules for the Ivanpah footprint;
- or a USGS/industry AEM survey covering 35.3–35.6°N, 115.6–115.1°W;
- ground spectra or alteration maps for independent validation.

## Files

`raw/ASU_spectra/`, `raw/sim3206_database/`,
`processed/asu_endmembers.npy`, `processed/geology_substrate.npy`.
