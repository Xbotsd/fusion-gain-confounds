import json
from collections import Counter

v = json.load(open(r"D:\A_MineralProspecting\processed\validation_emfix.json",
                   encoding="utf-8"))
print("validation_emfix scenarios:", len(v["scenarios"]))
for r in v["scenarios"]:
    if "leave" in r["case"] or r["case"] == "normal":
        print(f"  {r['case']:22s} R={r['recall']:.4f} F1={r['f1']:.4f}")

sb = json.load(open(r"D:\A_MineralProspecting\processed\scenario_bootstrap.json",
                    encoding="utf-8"))
print("\nscenario_bootstrap rows:", len(sb["rows"]))
names = [r["case"] for r in sb["rows"]]
dups = {k: c for k, c in Counter(names).items() if c > 1}
print("duplicates:", dups)
