# Independent geological check (USGS SIM 3206)

## Source

USGS Scientific Investigations Map 3206, *Surficial geologic map of the Ivanpah
30' × 60' quadrangle* (Miller, 2012, DOI 10.3133/sim3206). The GIS database
contains `ivanpah_polygon` with a `PTYPE` field; the substrate material follows
`/` or `-` in the unit code (e.g. `Qha/fpg` = hillslope over felsic plutonic
rock). This is an independent geological layer, not an alteration map.

Downloaded from <https://pubs.usgs.gov/sim/3206/sim3206_database.zip> and
rasterised to the 50 m survey grid (`processed/geology_substrate.npy`).

## Result

| substrate | pixels | mean clay | mean quartz | mean calcite |
|---|---:|---:|---:|---:|
| surficial/alluvium | 504,723 | 0.487 | 0.103 | 0.105 |
| felsic plutonic | 105,249 | 0.426 | 0.126 | 0.124 |
| volcanic | 92,213 | 0.417 | 0.129 | 0.138 |
| partly consolidated | 13,542 | 0.362 | 0.130 | 0.162 |
| metasedimentary | 31,659 | 0.277 | 0.217 | 0.150 |
| mafic plutonic | 9,771 | 0.180 | 0.177 | 0.187 |
| sedimentary | 1,126 | 0.020 | 0.301 | 0.179 |
| carbonate | 6,900 | 0.011 | 0.276 | 0.226 |

Kruskal–Wallis across groups: H = 41,037, p < 0.001. Felsic plutonic vs
carbonate (one-sided Mann–Whitney): p < 0.001.

## Interpretation

The ranking is directionally plausible: clay is highest in alluvium/felsic
plutonic terrain and lowest in carbonate/sedimentary terrain; quartz is higher in
carbonate/sedimentary and lower in alluvium; calcite is highest in carbonate.
This is a **qualitative external consistency check**, not an alteration or
deposit validation. Alluvium can be clay-rich for sedimentary reasons, so the
high alluvium value does not prove hydrothermal alteration.

## Caveats

- The map is surficial geology at 1:100,000; substrate codes are not alteration
  assemblages.
- The survey footprint only partly overlaps the map quadrangle.
- Large n makes the p-values tiny; the effect size/ranking is more informative.
- No known-deposit or alteration-zone label is available in this dataset.

## Files

`processed/independent_validation.json`, `.csv`, `.png`,
`processed/geology_substrate.npy`; script `code/independent_validation.py`.
