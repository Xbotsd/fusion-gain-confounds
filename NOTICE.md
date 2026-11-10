# Data notices

The MIT licence in `LICENSE` covers the code and the derived products of this
repository. The third-party data listed below remain under their own terms and
must be cited from their original sources.

| data | source | terms |
|---|---|---|
| raw gamma grids (K, eU, eTh, TMI, GXF) and the radiometric CSV | USGS airborne survey, Ivanpah–Clark Mountain, NV–CA (2019–2020) | U.S. Government work, public domain |
| surficial geology | USGS SIM 3206, DOI 10.3133/sim3206 | U.S. Government work, public domain |
| ASTER L1T v003 thermal infrared | NASA / JAXA / METI, via the Microsoft Planetary Computer STAC API | free and open, cite the mission |
| ASU endmember spectra | ASU Thermal Emission Spectral Library | free for research use, cite the library |
| NGU FDEM apparent-resistivity statistics | NGU surveys (Sulitjelma 2025, Rørås 2020) | open data, cite NGU |
| synthetic TIR and EM cubes, all derived products | this repository | MIT, same as the code |

`processed/data_manifest.json` carries a SHA-256 for every file that was present
when the manifest was built; `raw/aster/*/manifest.json` carries the STAC
identifiers and hashes of the seven archived ASTER scenes.
