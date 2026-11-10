"""Rewrite the headline docs for the real-ASTER main line."""
import json
from pathlib import Path

ROOT = Path(r"D:\A_MineralProspecting")
J = lambda f: json.load(open(ROOT / "processed" / f, encoding="utf-8"))  # noqa: E731

main = J("main_results.json")
ctl = {r["config"]: r for r in J("tir_controls.json")["rows"]}
mc = J("geology_multiclass.json")["summary"]
idf = J("identifiability.json")

# --------------------------------------------------------------- RESULTS.md
A = {r["config"]: r for r in main["ablation"]
     if r["branch"] == "real-aster" and r["em_model"] == "corrected"}
B = {r["config"]: r for r in main["ablation"]
     if r["branch"] == "real-aster" and r["em_model"] == "legacy"}
rows = []
for m, tag in ((A, "corrected"), (B, "legacy")):
    for c in ("gamma", "gamma+tir", "gamma+em", "all"):
        r = m[c]
        rows.append(f"| {tag} | {c} | {r['f1']:.3f} | {r['ap']:.3f} | "
                    f"{r['recall']:.3f} | {r['precision']:.3f} | {r['geo_auc']:.3f} |")

RESULTS = f"""# Results — real ASTER main line

Every number comes from `processed/main_results.json` and the artefacts listed
below. Mask: radiometric survey ∩ full ASTER coverage, **{main['mask_pixels']:,}
pixels** ({main['mask_pixels']/1904900:.1%} of the grid).

## 1. Ablation

| EM model | configuration | F1 | AP | recall | precision | geology AUC |
|---|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

## 2. The central result: conditioning versus information

| configuration | F1 | geology AUC | 4-class balanced accuracy |
|---|---:|---:|---:|
| gamma | {ctl['gamma']['f1']:.3f} | {ctl['gamma']['geo_auc']:.3f} | {mc['gamma']['balanced_accuracy_mean']:.3f} |
| gamma + real ASTER | {ctl['gamma + real TIR']['f1']:.3f} | {ctl['gamma + real TIR']['geo_auc']:.3f} | {mc['gamma + real ASTER']['balanced_accuracy_mean']:.3f} |
| gamma + block-shuffled ASTER | {ctl['gamma + real TIR, block-shuffled']['f1']:.3f} | {ctl['gamma + real TIR, block-shuffled']['geo_auc']:.3f} | {mc['gamma + block-shuffled ASTER']['balanced_accuracy_mean']:.3f} |
| gamma + five noise channels | {ctl['gamma + 5 noise channels']['f1']:.3f} | {ctl['gamma + 5 noise channels']['geo_auc']:.3f} | — |
| gamma + synthetic TIR | {ctl['gamma + synthetic TIR']['f1']:.3f} | {ctl['gamma + synthetic TIR']['geo_auc']:.3f} | {mc['gamma + synthetic TIR']['balanced_accuracy_mean']:.3f} |

Inside the estimator, noise-filled and shuffled copies score like the real cube:
the gain is conditioning. Without a response matrix the information gain is
{mc['gamma + real ASTER']['gain_vs_gamma_mean']:+.3f} balanced accuracy
(95 % CI {mc['gamma + real ASTER']['gain_vs_gamma_ci95'][0]:+.3f} to
{mc['gamma + real ASTER']['gain_vs_gamma_ci95'][1]:+.3f}, improving in
{mc['gamma + real ASTER']['repeats_improved']}/20 repeats), and it disappears for
a shuffled cube ({mc['gamma + block-shuffled ASTER']['gain_vs_gamma_mean']:+.3f}).

## 3. Identifiability

| model | subset | equations | rank | κ | clay variance |
|---|---|---:|---:|---:|---:|
| legacy | gamma | 3 | 3 | {idf['models']['legacy']['sets']['gamma']['kappa']:.1f} | {idf['models']['legacy']['sets']['gamma']['var_clay_pred']:.2e} |
| legacy | gamma+TIR | 8 | 5 | {idf['models']['legacy']['sets']['gamma+tir']['kappa']:.1f} | {idf['models']['legacy']['sets']['gamma+tir']['var_clay_pred']:.2e} |
| corrected | all | 11 | 5 | {idf['models']['corrected']['sets']['all']['kappa']:.1f} | {idf['models']['corrected']['sets']['all']['var_clay_pred']:.2e} |

The variance gain index is positive for every addition and agrees with the F1 sign
in {sum(idf['sign_agreement_f1'].values())}/{len(idf['sign_agreement_f1'])} cases:
it cannot be used as evidence that fusion helps.

## 4. Estimator comparison (real ASTER, corrected EM)

| method | F1 | AP | geology AUC | components |
|---|---:|---:|---:|---:|
""" + "\n".join(
    f"| {r['method']} | {r['f1']:.3f} | {r['ap']:.3f} | {r['geo_auc']:.3f} | {r['components']:,} |"
    for r in sorted(main["baselines"], key=lambda r: -r["f1"])) + f"""

## 5. Bootstrap contrasts

| contrast | Δ | 95 % CI | P(better) |
|---|---:|---|---:|
""" + "\n".join(
    f"| F1 {k} | {v['delta_mean']:+.3f} | [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}] | {v['p_better']:.2f} |"
    for k, v in main["bootstrap_f1"].items()) + "\n" + "\n".join(
    f"| AUC {k} | {v['delta_mean']:+.3f} | [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}] | — |"
    for k, v in main["bootstrap_geo_auc"].items()) + f"""

## 6. Stability and uncertainty

Ten repeats with 1 % channel noise: F1 {main['repeats']['summary']['f1']['mean']:.5f} ±
{main['repeats']['summary']['f1']['std']:.5f}; geology AUC
{main['repeats']['summary']['geo_auc']['mean']:.4f} ±
{main['repeats']['summary']['geo_auc']['std']:.4f}.

Calibration: 68 %/95 % coverage {main['calibration']['coverage_68']:.3f}/
{main['calibration']['coverage_95']:.3f}, variance scale
{main['calibration']['variance_scale']:.1f}. The filter variance is **not** a
confidence interval.

Pseudo-replication: integral scale {main['autocorr']['integral_scale_px'][0]:.0f} px
({main['autocorr']['integral_scale_m'][0]:.0f} m), design effect
{main['autocorr']['design_effect']:.0f}, **N_eff {main['autocorr']['n_eff']:.0f}**
from {main['autocorr']['n_valid']:,} pixels.

## Files

`main_results.json`, `main_ablation.csv`, `main_baselines.csv`,
`tir_controls.json`, `tir_information.json`, `geology_multiclass.json`,
`identifiability.json`, `real_tir_robust.json`, `independent_validation.json`,
`published_baselines.json`, `depth.json`, `calibration.json`, `autocorr.json`.
"""
(ROOT / "docs" / "RESULTS.md").write_text(RESULTS, encoding="utf-8")

# --------------------------------------------------------- DATA_PROVENANCE
PROV = """# Data provenance

## Real data

| layer | source | identifier | native |
|---|---|---|---|
| K, eU, eTh | USGS airborne radiometric survey, Ivanpah–Clark Mountain NV–CA | delivered `raw/K.gxf`, `eU.gxf`, `eTh.gxf` + line CSV | 50 m, 295,943 samples at 1 Hz, 2019-12-13 → 2020-03-21 |
| ASTER TIR ×5 | ASTER L1T v003 (NASA/METI), via Microsoft Planetary Computer | 4 scenes of 2006-10-18 (+3 of 2006-09-25), archived under `raw/aster/` with STAC ids and SHA-256 | 90 m, 5 bands 8.29–11.29 µm |
| TMI | USGS aeromagnetics, same survey block | `raw/TMI.gxf` | 50 m |
| geology | USGS SIM 3206 surficial geologic map | DOI 10.3133/sim3206, `raw/sim3206_database/` | polygons → 50 m |

The ASTER scenes are downloaded once by `code/fetch_aster.py`, which writes
`raw/aster/<date>/manifest.json` (STAC item id, source URL without the SAS token,
bytes, SHA-256). `code/prepare_tir_real.py` then works **offline** from that
archive, so the thermal cube is reproducible without network access.

## Synthetic data

| layer | recipe | why synthetic |
|---|---|---|
| EM, 40 layers 0–600 m | Wisconsin AEM layer statistics + clay-linked field decaying as exp(−d/250) + independent and noise fields, seed 12345 | no measured airborne EM exists over this footprint; the delivered survey contains only radiometric and magnetic grids |

Every EM result in the manuscript and in `processed/*.json` is labelled
synthetic. No claim is made about field EM behaviour.

## Derived targets

| target | construction | status |
|---|---|---|
| `clay_prior` | 0.5·K + 0.3·(1−eTh) + 0.2·|eU−eTh| on p2–p98 normalised channels, smoothed σ = 15 px | gamma-derived, **circular** for gamma |
| `truth_abundance` | 0.4K+0.2eU etc., renormalised | only used to synthesise the control TIR cube |
| substrate labels | SIM 3206 classes rasterised to the grid | independent of all observed modalities |

## Corrections recorded

* the draft's "Colorado Mineral Belt 2023, 28,472 line-km" description was wrong;
  the grids are Ivanpah 2019–2020;
* ASTER replaces the synthetic splib07 TIR cube as the **main line**; the
  synthetic cube is now an explicit control;
* the analysis mask is the intersection of the radiometric survey and the ASTER
  coverage (97.8 % of the survey), so real and synthetic branches are compared on
  identical pixels.
"""
(ROOT / "docs" / "DATA_PROVENANCE.md").write_text(PROV, encoding="utf-8")
print("RESULTS.md and DATA_PROVENANCE.md rewritten")
