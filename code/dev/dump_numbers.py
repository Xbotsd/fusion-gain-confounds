"""Dump every number the manuscript cites, from the authoritative JSON."""
import json
from pathlib import Path

P = Path(r"D:\A_MineralProspecting\processed")


def j(n):
    return json.load(open(P / n, encoding="utf-8"))


print("=== fusion.json (legacy main) ===")
f = j("fusion.json")
print(" runtime", round(f["runtime_s"], 2), "proxy", {k: round(v, 4) for k, v in f["proxy"].items()})
print(" clay mean", round(f["clay_mean"], 4) if "clay_mean" in f else "?")

print("\n=== em_fix.json (corrected) ===")
e = j("em_fix.json")
for r in e["rows"]:
    print(f"  {r['method']:16s} F1={r['f1']:.4f} AP={r['ap']:.4f} R={r['recall']:.4f} "
          f"P={r['precision']:.4f} comp={r['components']} grad={r['gradient']:.5f}")
b = e["bootstrap"]
print("  bootstrap: indep", [round(x, 3) for x in b["independent"]["ci95"]],
      "emfix", [round(x, 3) for x in b["em_fix"]["ci95"]])
print("  delta", round(b["delta"]["mean"], 4), [round(x, 3) for x in b["delta"]["ci95"]],
      "p_better", b["delta"]["p_better"])

print("\n=== em_fix_repeats (10 runs) ===")
r10 = j("em_fix_repeats.json")["summary"]
for k, v in r10.items():
    print(f"  {k}: {v['mean']:.6f} +/- {v['std']:.6f}")

print("\n=== ablation legacy vs emfix ===")
for name in ("ablation.json", "ablation_emfix.json"):
    print(" ", name)
    for r in j(name):
        print(f"    {r['config']:10s} clay={r['clay_mean']:.4f} F1={r['f1']:.4f} "
              f"R={r['recall']:.4f} P={r['precision']:.4f} RMSE_truth={r['rmse_truth']:.4f} "
              f"r={r['r_truth']:.3f}")

print("\n=== validation legacy vs emfix ===")
for name in ("validation.json", "validation_emfix.json"):
    v = j(name)
    print(f"  {name}: overall R={v['overall_recall']:.4f} F1={v['overall_f1']:.4f}")
    print("   family:", {k: round(x, 4) for k, x in v["family_recall"].items()})
    print("   degradation:", {k: round(x["recall"], 4) for k, x in v["degradation"].items()})
    print("   temp:", [(t["temperature"], round(t["recall"], 3), round(t["f1"], 3))
                       for t in v["temperature"]])

print("\n=== depth legacy vs emfix ===")
for name in ("depth.json", "depth_emfix.json"):
    d = j(name)
    lm = d["layer_mean"]
    print(f"  {name}: clay layer0={lm[0][2]:.4f} layer39={lm[-1][2]:.4f} "
          f"depths {d['depth_m'][0]:.1f}..{d['depth_m'][-1]:.1f} runtime {d['runtime_s']:.1f}")
    if name == "depth.json":
        for k in (0, 5, 10, 20, 30, 39):
            print(f"    L{k} depth {d['depth_m'][k]:6.1f}: " +
                  " ".join(f"{x:.3f}" for x in lm[k]))

print("\n=== calibration legacy vs emfix ===")
for name in ("calibration.json", "calibration_emfix.json"):
    c = j(name)
    print(f"  {name}: cov68={c['coverage_68']:.4f} cov95={c['coverage_95']:.4f} "
          f"scale={c['variance_scale']:.2f} bias={c['bias']:.4f} rmse={c['rmse']:.4f} "
          f"mean_sigma={c['mean_sigma']:.4f} "
          f"scaled68={c['coverage_68_scaled']:.4f} scaled95={c['coverage_95_scaled']:.4f}")

print("\n=== baselines / advantage ===")
for r in j("baselines.json"):
    print(f"  {r['method']:22s} clay={r['clay_mean']:.3f} grad={r['gradient']:.5f} "
          f"R={r['recall']:.3f} F1={r['f1']:.3f}")

print("\n=== published baselines ===")
for r in j("published_baselines.json"):
    print(f"  {r['method']:42s} AP={r['ap']:.4f} F1m={r['f1_matched']:.4f}")

print("\n=== scenario bootstrap (select) ===")
sb = j("scenario_bootstrap.json")
print("  block", sb["block"], "reps", sb["n_rep"])
for r in sb["rows"]:
    print(f"  {r['case']:24s} R={r['recall']:.3f} [{r['recall_ci95'][0]:.3f},{r['recall_ci95'][1]:.3f}]")
print("  significant deltas:")
for d in sb["deltas"]:
    if d["significant_05"]:
        print(f"    {d['case']:24s} d={d['delta_recall']:+.4f} "
              f"[{d['ci95'][0]:+.3f},{d['ci95'][1]:+.3f}] p_bh={d['p_bh']:.2e}")

print("\n=== autocorr ===")
a = j("autocorr.json")
for k, v in a["fields"].items():
    print(f"  {k}: tau_x={v['integral_scale_x_px']:.1f}px ({v['integral_scale_x_m']:.0f}m) "
          f"DE={v['design_effect']:.0f} N_eff={v['n_eff']:.0f} of {v['n_valid']}")
print("  block ok:", a["checks"]["block_ge_2tau"])

print("\n=== granite ===")
g = j("granite_properties.json")
print("  felsic pixels", g["felsic_pixels"])
print("  K felsic/other", round(g["signature"]["K"]["felsic_mean"], 3), round(g["signature"]["K"]["other_mean"], 3))
print("  eTh", round(g["signature"]["eTh"]["felsic_mean"], 3), round(g["signature"]["eTh"]["other_mean"], 3))
print("  indicator", round(g["indicator_mean_on_felsic"], 3), round(g["indicator_mean_on_other"], 3))
print("  conductivity n", g["conductivity"]["n_values"], "p50", round(g["conductivity"]["p50_ohm_m"]))
gc = j("granite_compensation.json")
for k, v in gc["results"].items():
    print(f"  {k:22s} F1={v['f1']:.4f} felsic={v['clay_on_felsic']:.4f} "
          f"other={v['clay_on_other']:.4f} excess={v['felsic_excess']:+.4f}")

print("\n=== edge ai ===")
ea = j("edge_ai.json")
print("  params", ea["params"], "int8 KB", round(ea["int8_size_kb"], 2),
      "latency ms", round(ea["latency_ms_10k"]["int8_sim"], 1),
      "us/sample", round(ea["latency_us_per_sample"], 2))
for k in ("physics", "cnn_float", "cnn_int8"):
    print(f"  {k}: AP={ea[k]['ap']:.4f} F1m={ea[k]['f1_matched']:.4f} RMSE={ea[k]['rmse']:.4f}")

print("\n=== independent validation ===")
iv = j("independent_validation.json")
for r in iv["rows"]:
    print(f"  {r['substrate']:22s} n={r['pixels']:7d} clay={r['clay_mean']:.4f}")
print("  kruskal", iv["kruskal"], "felsic_vs_carbonate", iv["felsic_vs_carbonate"])

print("\n=== v2 ===")
for r in j("v2/ablation_v2.json"):
    print(f"  {r['config']:10s} clay={r['clay_mean']:.4f} R={r['recall']:.4f} F1={r['f1']:.4f}")

print("\n=== structured perturbation ===")
for r in j("structured_perturbation.json"):
    print(f"  {r['variant']:22s} clay={r['clay']:.4f} F1={r['f1']:.4f}")

print("\n=== threshold ===")
th = j("threshold_summary.json")
for k, v in th.items():
    bst = v["best"]
    print(f"  {k:18s} default={v['default']:.4f} best={bst['f1']:.4f} "
          f"(thr={bst['thr']}, k={bst['top_k']}, gt={bst['gt_thr']})")

print("\n=== sensitivity / environment / repeats ===")
s = j("sensitivity.json")
print("  multi_seed stats:", {k: round(v, 5) for k, v in s["multi_seed_stats"].items()}
      if isinstance(s.get("multi_seed_stats"), dict) else "?")
print("  resolution:", [(r.get("scale", r.get("stride")), round(r["recall"], 3))
                         for r in s["resolution"]])
env = j("environment.json")
print("  env scenarios:", [(e["case"] if "case" in e else "", round(e.get("recall", 0), 4))
                            for e in env.get("scenarios", [])][:6])
rep = j("repeats.json")
print("  repeats:", {k: round(v, 6) for k, v in rep["stats"].items()} if isinstance(rep.get("stats"), dict) else "?")
