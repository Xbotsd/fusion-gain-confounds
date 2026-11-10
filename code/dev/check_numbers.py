"""Print the fresh ablation / control tables next to the numbers the manuscript quotes."""
import json
import pathlib

root = pathlib.Path(__file__).resolve().parents[2]
proc = root / "processed"

main = json.loads((proc / "main_results.json").read_text(encoding="utf-8"))
print("=== ablation (fresh) ===")
print(f"{'branch':12s} {'em':8s} {'config':10s} {'nch':>3s} {'F1':>7s} {'AP':>7s} {'geoAUC':>7s}")
for r in main["ablation"]:
    print(f"{r['branch']:12s} {r['em_model']:8s} {r['config']:10s} {r['n_channels']:3d} "
          f"{r['f1']:7.3f} {r['ap']:7.3f} {r['geo_auc']:7.3f}")

print("\n=== bootstrap F1 (fresh) ===")
for k, v in main["bootstrap_f1"].items():
    print(f"  {k:28s} {v['delta']:+.3f} [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}]")

print("\n=== bootstrap geo AUC (fresh) ===")
for k, v in main["bootstrap_geo_auc"].items():
    print(f"  {k:28s} {v['delta']:+.3f} [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}]")

print("\n=== controls (fresh) ===")
tir = json.loads((proc / "tir_controls.json").read_text(encoding="utf-8"))
for r in tir["rows"]:
    print(f"  {r['config']:26s} F1 {r['f1']:.3f}  AUC {r['geo_auc']:.3f}")
print("  r2_tir_on_gamma", tir["r2_tir_on_gamma"])
