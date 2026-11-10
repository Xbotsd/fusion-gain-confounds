"""Print the scenario bootstrap summary."""
import json

d = json.load(open(r"D:\A_MineralProspecting\processed\scenario_bootstrap.json",
                   encoding="utf-8"))
print("scenarios:", len(d["rows"]), "block", d["block"], "reps", d["n_rep"])
print()
print("=== significant vs normal (BH < 0.05) ===")
for x in d["deltas"]:
    if x["significant_05"]:
        print(f"{x['case']:22s} d={x['delta_recall']:+.4f} "
              f"CI[{x['ci95'][0]:+.3f},{x['ci95'][1]:+.3f}] "
              f"p_bh={x['p_bh']:.4f}")
print()
print("=== NOT significant ===")
for x in d["deltas"]:
    if not x["significant_05"]:
        print(f"{x['case']:22s} d={x['delta_recall']:+.4f} "
              f"CI[{x['ci95'][0]:+.3f},{x['ci95'][1]:+.3f}] "
              f"p_bh={x['p_bh']:.3f}")
