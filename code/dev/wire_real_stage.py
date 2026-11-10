"""Round 6: wire the real-ASTER-TIR branch into the pipeline and validate it."""
from pathlib import Path

ROOT = Path(r"D:\A_MineralProspecting")

# 1. new network stage
p = ROOT / "code" / "run_all.py"
t = p.read_text(encoding="utf-8")
if '"real"' not in t:
    t = t.replace('    "refs": ["verify_references.py"],',
                  '    "real": ["prepare_tir_real.py", "run_real_tir.py"],\n'
                  '    "refs": ["verify_references.py"],')
    t = t.replace('ALL_STAGES = ("prepare", "core", "eval", "eval_emfix", "variants", "edge",\n'
                  '              "figures", "audit")',
                  'ALL_STAGES = ("prepare", "core", "eval", "eval_emfix", "variants", "edge",\n'
                  '              "figures", "audit")\n'
                  '# "real" needs network access to the ASTER archive; run it explicitly.')
    p.write_text(t, encoding="utf-8")
    print("run_all: real stage added")

# 2. expected artefacts
p = ROOT / "code" / "validate_pipeline.py"
t = p.read_text(encoding="utf-8")
if "tir_real.json" not in t:
    t = t.replace('    "identifiability.json", "generation_sensitivity.json",',
                  '    "identifiability.json", "generation_sensitivity.json",\n'
                  '    "tir_real.json", "real_tir.json",')
    t = t.replace('    "generation_sensitivity.png",',
                  '    "generation_sensitivity.png", "real_tir.png",')
    t = t.replace('    "truth_abundance.npy": (5, None, None),',
                  '    "truth_abundance.npy": (5, None, None),\n'
                  '    "tir_cube_real.npy": (5, None, None),')
    p.write_text(t, encoding="utf-8")
    print("validate_pipeline: artefacts registered")

# 3. cross-check: the reference branch must reproduce em_fix.json
t = (ROOT / "code" / "validate_pipeline.py").read_text(encoding="utf-8")
anchor = "    # 2. validation_emfix overall vs its own normal scenario"
add = '''    # 1h. the real-TIR comparison must reproduce the published reference row
    try:
        rt = C.load_json(C.PROC / "real_tir.json")
        row = next(r for r in rt["rows"]
                   if r["branch"] == "synthetic-handset"
                   and r["em_model"] == "corrected" and r["config"] == "all")
        emf = C.load_json(C.PROC / "em_fix.json")
        ref = next(r for r in emf["rows"] if r["method"] == "EM-fix Kalman")
        d = abs(row["f1"] - ref["f1"])
        xcheck("real_tir_reference_row", d < 1e-6, f"delta {d:.2e}")
    except Exception as exc:  # noqa: BLE001
        xcheck("real_tir_reference_row", False, str(exc))

    # 1i. the real ASTER cube must be physically plausible
    try:
        tj = C.load_json(C.PROC / "tir_real.json")
        eps_lo, eps_hi = tj["eps_percentiles"][0], tj["eps_percentiles"][2]
        bt = tj["bt_percentiles"][1]
        ok = 0.6 <= eps_lo and eps_hi <= 1.0 and 270 <= bt <= 330
        xcheck("real_tir_physical_range", ok,
               f"eps {eps_lo:.2f}-{eps_hi:.2f}, median BT {bt:.1f} K")
    except Exception as exc:  # noqa: BLE001
        xcheck("real_tir_physical_range", False, str(exc))

'''
if "real_tir_reference_row" not in t:
    t = t.replace(anchor, add + anchor)
    (ROOT / "code" / "validate_pipeline.py").write_text(t, encoding="utf-8")
    print("validate_pipeline: two cross-checks added")
