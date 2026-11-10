"""Insert the numbered tables into the rewritten manuscript, from artefacts."""
import json
from pathlib import Path

ROOT = Path(r"D:\A_MineralProspecting")
P = ROOT / "docs" / "Manuscript_v2_draft.md"
J = lambda f: json.load(open(ROOT / "processed" / f, encoding="utf-8"))  # noqa: E731

main = J("main_results.json")
ctl = {r["config"]: r for r in J("tir_controls.json")["rows"]}
mc = J("geology_multiclass.json")["summary"]
rob = J("real_tir_robust.json")
pb = J("published_baselines.json")["rows"]
depth = J("depth.json")
depth_fix = J("depth_emfix.json")

T1 = """**Table 1.** Data layers, provenance, native resolution and role.

| layer | source | resolution | role |
|---|---|---|---|
| K, eU, eTh | USGS airborne radiometrics, Ivanpah–Clark Mtn, 2019–2020 | 50 m | real observation |
| ASTER TIR ×5 | ASTER L1T v003, 2006-10-18, emissivity normalisation | 90 m → 50 m | real observation |
| EM ×3 layers | synthetic (Wisconsin AEM statistics, seed 12345) | 50 m | documented augmentation |
| TMI | USGS aeromagnetics | 50 m | edge experiment only |
| substrate | USGS SIM 3206 geologic map (DOI 10.3133/sim3206) | 50 m | independent target |
| clay_prior | derived from K and eTh | 50 m | circular proxy target |
"""

T2 = """**Table 2.** The three targets used in this paper and why each is needed.

| target | definition | what it can show |
|---|---|---|
| Gamma proxy | `clay_prior > 0.55`, computed from K and eTh | comparability with the literature; circular for gamma |
| Geology, inversion | AUC, clay-bearing vs clay-poor substrates, estimated clay | end-to-end behaviour of the model |
| Geology, model-free | balanced accuracy, 4 substrate classes, raw channels, block CV | information that conditioning cannot fake |
"""

rows = []
for r in main["ablation"]:
    if r["branch"] == "real-aster":
        rows.append(f"| {r['em_model']} / {r['config']} | {r['clay_mean']:.3f} | "
                    f"{r['recall']:.3f} | {r['precision']:.3f} | {r['f1']:.3f} | "
                    f"{r['ap']:.3f} | {r['geo_auc']:.3f} |")
T3 = ("**Table 3.** Modality ablation on the real-ASTER layout, both EM models "
      "(1,237,644 analysis pixels).\n\n"
      "| EM model / configuration | clay mean | recall | precision | F1 | AP | geology AUC |\n"
      "|---|---:|---:|---:|---:|---:|---:|\n" + "\n".join(rows) + "\n")

rows = []
for r in sorted(main["baselines"], key=lambda r: -r["f1"]):
    rows.append(f"| {r['method']} | {r['f1']:.3f} | {r['ap']:.3f} | "
                f"{r['precision']:.3f} | {r['geo_auc']:.3f} | {r['components']:,} |")
T4 = ("**Table 4.** Estimator comparison on the same mask and metric "
      "(real ASTER, corrected EM).\n\n"
      "| method | F1 | AP | precision | geology AUC | components |\n"
      "|---|---:|---:|---:|---:|---:|\n" + "\n".join(rows) + "\n")

T5 = f"""**Table 5.** Conditioning controls. "Five noise channels" and "zeros" use
the real ASTER rows of `H` with data that carry no information; the block-shuffled
cube keeps the ASTER marginals and destroys geographic registration.

| configuration | F1 | AP | geology AUC | 4-class balanced accuracy |
|---|---:|---:|---:|---:|
| gamma | {ctl['gamma']['f1']:.3f} | {ctl['gamma']['ap']:.3f} | {ctl['gamma']['geo_auc']:.3f} | {mc['gamma']['balanced_accuracy_mean']:.3f} |
| gamma + real ASTER | {ctl['gamma + real TIR']['f1']:.3f} | {ctl['gamma + real TIR']['ap']:.3f} | {ctl['gamma + real TIR']['geo_auc']:.3f} | {mc['gamma + real ASTER']['balanced_accuracy_mean']:.3f} |
| gamma + block-shuffled ASTER | {ctl['gamma + real TIR, block-shuffled']['f1']:.3f} | {ctl['gamma + real TIR, block-shuffled']['ap']:.3f} | {ctl['gamma + real TIR, block-shuffled']['geo_auc']:.3f} | {mc['gamma + block-shuffled ASTER']['balanced_accuracy_mean']:.3f} |
| gamma + five noise channels | {ctl['gamma + 5 noise channels']['f1']:.3f} | {ctl['gamma + 5 noise channels']['ap']:.3f} | {ctl['gamma + 5 noise channels']['geo_auc']:.3f} | — |
| gamma + synthetic TIR | {ctl['gamma + synthetic TIR']['f1']:.3f} | {ctl['gamma + synthetic TIR']['ap']:.3f} | {ctl['gamma + synthetic TIR']['geo_auc']:.3f} | {mc['gamma + synthetic TIR']['balanced_accuracy_mean']:.3f} |
"""

rows = []
for n, s in mc.items():
    lo, hi = s["gain_vs_gamma_ci95"]
    rows.append(f"| {n} | {s['balanced_accuracy_mean']:.3f} ± "
                f"{s['balanced_accuracy_sd']:.3f} | {s['gain_vs_gamma_mean']:+.3f} "
                f"[{lo:+.3f}, {hi:+.3f}] | {s['repeats_improved']}/20 |")
T6 = (f"**Table 6.** Model-free information test: balanced accuracy for four "
      f"geologically similar substrates, 128-px block cross-validation, "
      f"{mc['gamma']['repeats_improved'] and 20} repeats, chance 0.25.\n\n"
      "| features | balanced accuracy | gain vs gamma [95 % CI] | repeats improved |\n"
      "|---|---:|---|---:|\n" + "\n".join(rows) + "\n")

rows = []
for name, meta in rob["variants"].items():
    sub = [r for r in rob["rows"] if r["variant"] == name]
    g = next(r for r in sub if r["config"] == "gamma")["f1"]
    gt = next(r for r in sub if r["config"] == "gamma+tir")["f1"]
    rows.append(f"| {name} | {g:.3f} | {gt:.3f} |")
b = rob["bootstrap"]
T7 = (f"**Table 7.** Sensitivity of the thermal result to the retrieval and the "
      f"acquisition. Bootstrap of the gamma+TIR gain: "
      f"{b['delta_mean']:+.3f} [{b['ci95'][0]:+.3f}, {b['ci95'][1]:+.3f}].\n\n"
      "| variant | gamma F1 | gamma+TIR F1 |\n|---|---:|---:|\n" + "\n".join(rows) + "\n")

rows = []
for r in pb:
    rows.append(f"| {r['method']} | {r['reference']} | {r['f1_matched']:.3f} | "
                f"{r['auc_geology']:.3f} |")
T8 = ("**Table 8.** Published single-modality practice versus the fusion, on the "
      "same mask and with the matched-prevalence rule.\n\n"
      "| method | reference | matched F1 | geology AUC |\n"
      "|---|---|---:|---:|\n" + "\n".join(rows) + "\n")

t = P.read_text(encoding="utf-8")

# T1/T2 before section 3
anchor = "## 3. Data\n"
t = t.replace(anchor, "## 3. Data\n\n" + T1 + "\n" + T2 + "\n", 1)
t = t.replace("The observation vector has eleven channels: three gamma, five ASTER\nemissivity and three synthetic EM.",
              "The observation vector has eleven channels: three gamma, five ASTER\nemissivity and three synthetic EM (Table 1). Every metric is defined in Table 2.")

# T3 replaces the ablation table
old_t3 = t[t.index("| configuration | clay mean | recall | precision | F1 | AP | geology AUC |"):]
old_t3 = old_t3[:old_t3.index("\n\n")].rstrip() + "\n"
t = t.replace(old_t3, T3, 1)

# T5 replaces the controls table
old_t5 = t[t.index("| configuration | F1 | AP | geology AUC | balanced accuracy (4-class) |"):]
old_t5 = old_t5[:old_t5.index("\n\n")].rstrip() + "\n"
t = t.replace(old_t5, T5 + "\n" + T6, 1)

# T4 after the estimator paragraph
anchor4 = "### 7.5 The EM correction is real but does not win"
t = t.replace(anchor4, T4 + "\n" + anchor4, 1)

# T7 after the robustness paragraph, T8 after the published paragraph
anchor7 = "### 7.7 Depth"
t = t.replace(anchor7, T7 + "\n" + anchor7, 1)
anchor8 = "### 7.9 Uncertainty and pseudo-replication"
t = t.replace(anchor8, T8 + "\n" + anchor8, 1)

# reference fixes
t = t.replace("Table 3. With the corrected EM model", "Table 3. With the corrected EM model")
t = t.replace("Table 4. On the proxy", "Table 4. On the proxy")
t = t.replace("Table 8. On the matched-prevalence rule", "Table 8. On the matched-prevalence rule")
t = t.replace("The 40-layer Kalman recursion", "The 40-layer Kalman recursion")
P.write_text(t, encoding="utf-8")
print("tables inserted; depth rows:", len(depth["layer_mean"]), len(depth_fix["layer_mean"]))
