import json

d = json.load(open(r"D:\A_MineralProspecting\processed\depth_emfix.json",
                   encoding="utf-8"))
lm = d["layer_mean"]
dep = d["depth_m"]
print("depth_emfix selected layers (Qz Fsp Clay Cal Dol):")
for k in (0, 5, 10, 20, 30, 39):
    print(f"  L{k:2d} {dep[k]:7.1f} m  " + "  ".join(f"{x:.3f}" for x in lm[k]))
print("min/max clay:", round(min(r[2] for r in lm), 4),
      round(max(r[2] for r in lm), 4))

dl = json.load(open(r"D:\A_MineralProspecting\processed\depth.json",
                    encoding="utf-8"))
print("\ndepth legacy selected:")
for k in (0, 5, 10, 20, 30, 39):
    print(f"  L{k:2d} {dl['depth_m'][k]:7.1f} m  " + "  ".join(f"{x:.3f}" for x in dl["layer_mean"][k]))
