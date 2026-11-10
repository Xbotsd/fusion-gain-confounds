# ASU endmember sensitivity

## Why this exists

The main TIR cube is generated from USGS splib07 reflectance spectra converted to
emissivity. A reviewer may ask whether the conclusions depend on that endmember
library. This note documents a second TIR variant built from measured ASU
thermal-emission spectra, and reports the difference. It is a sensitivity
analysis; the main results still use the USGS library.

## Source data

Downloaded from the ASU Thermal Emission Spectral Library
(<https://speclib.asu.edu/>) with guest access. The export flow used by the web
UI is reproduced in `code/fetch_asu_spectra.py`:

```
login.php?login=1&username=guest&password=guest
ajax/generate_export.php?spectra=<id>&type=lab1&format=ascii
inc/get_exported.php?spectra=<id>&type=lab1&format=ascii&f=<name>
```

Each export is a ZIP with `guest_lab1.txt` (wavenumber, emissivity) and
`guest_meta.txt`. The saved spectra are in `raw/ASU_spectra/`.

| mineral | ASU id | sample | particle size |
|---|---:|---|---|
| Quartz | 479 | BUR-4120 | coarse particulate |
| Feldspar | 468 | Microcline BUR-3460 | coarse particulate |
| Clay | 571 | Kaolinite KGa-1b | coarse particulate |
| Calcite | 604 | C2, 710–1000 µm | calcite library |
| Dolomite | 515 | C20 | hand sample |

The spectra are converted from wavenumber to wavelength (`λ = 10000/ν`),
interpolated to 200 points between 8 and 14 µm, and clipped to [0.5, 1.0].

## TIR variant

`code/run_asu_variant.py`:

1. loads the five ASU spectra;
2. rebuilds the 200-band TIR cube from the same `truth_abundance` field;
3. builds `H_asu` with ASU emissivity at the four inversion bands;
4. runs fusion and ablation with the same mask and metric.

Outputs:

* `processed/asu_endmembers.npy` (200 × 5)
* `processed/tir_cube_asu.npy` (200 × 1772 × 1075)
* `processed/H_asu.npy` (10 × 5)
* `processed/fusion_asu.json`
* `processed/ablation_asu.csv` / `.json`
* `processed/fig_asu_endmembers.png`

## Results

| configuration | clay | recall | precision | F1 |
|---|---:|---:|---:|---:|
| USGS main, all | 0.458 | 0.693 | 0.165 | 0.267 |
| ASU, all | 0.334 | 0.264 | 0.088 | 0.132 |
| ASU, gamma only | 0.342 | 0.773 | 0.205 | 0.325 |
| ASU, gamma + TIR | 0.290 | 0.553 | 0.136 | 0.244 |
| ASU, gamma + EM | 0.351 | 0.392 | 0.127 | 0.191 |

The ASU endmembers have much stronger reststrahlen contrast (quartz 0.626 at
8.6 µm vs 0.92 in the legacy matrix; clay 0.982 vs 0.88). The stronger TIR
modality therefore dominates the fusion and amplifies the mismatch between the
TIR-generation truth (`0.3K + 0.3eTh`) and the evaluation proxy (`clay_prior`).
The lower proxy F1 is not evidence that ASU spectra are worse; it is evidence
that the synthetic TIR field and the evaluation target are different fields.

## Recommendation

The main results should keep the USGS library, with this ASU variant reported as
a sensitivity analysis. A fully consistent next version should (i) generate TIR
and EM from a single truth field, (ii) use log10 resistivity with a clay-only EM
row, and (iii) then repeat the ASU-vs-USGS comparison. Until then, the ASU result
is a useful negative control: it shows that endmember choice can change the
fusion ranking, which is exactly the kind of dependence the benchmark is meant
to expose.
