"""Run the whole pipeline in order.

Architecture
------------
prepare   real cubes (gamma, ASTER TIR, EM, geology) + analysis mask
main      the paper: ablation, baselines, bootstrap, repeats, calibration
controls  information-vs-conditioning tests and the independent geology target
aux       depth, published baselines, threshold, H perturbation, scenarios, edge
legacy    the synthetic-TIR reference experiments (kept for the comparison)

Usage (any Python >= 3.9 works as the launcher; the pipeline itself is run
with an interpreter that has numpy/scipy/GDAL — usually the `geo` conda env):

  python run_all.py            # prepare, main, controls, aux, figures, audit
  python run_all.py prepare    # data preparation only
  python run_all.py main       # the paper's experiments
  python run_all.py legacy     # synthetic-TIR reference branch
  python run_all.py asu        # network: ASU endmembers + variant
  python run_all.py refs       # network: Crossref suggestions
"""
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

STAGES = {
    "prepare": ["prepare_gamma.py", "prepare_tir.py", "prepare_em.py",
                "prepare_tir_real.py", "prepare_geology.py"],
    "main": ["run_main.py"],
    "controls": ["run_tir_controls.py", "run_tir_information.py",
                 "run_geology_multiclass.py", "run_identifiability.py",
                 "run_real_tir_robust.py"],
    "aux": ["run_depth.py", "run_depth_emfix.py",
            "run_published_baselines.py", "independent_validation.py",
            "uncertainty_calibration.py", "autocorr_sample_size.py",
            "run_edge_ai.py", "prepare_granite.py",
            "run_granite_compensation.py", "prepare_tmi.py"],
    "legacy": ["run_ablation.py", "run_validation.py", "run_baselines.py",
               "run_advantage.py", "run_em_fix.py", "run_repeats.py",
               "run_sensitivity.py", "run_environment.py",
               "threshold_sensitivity.py", "structured_perturbation.py",
               "scenario_bootstrap.py",
               "run_em_beta_sensitivity.py", "run_generation_sensitivity.py",
               "run_v2.py"],
    "asu": ["fetch_asu_spectra.py", "run_asu_variant.py"],
    "refs": ["verify_references.py"],
    "figures": ["make_figures.py"],
    "audit": ["test_core.py", "check_coverage.py", "audit_data.py",
              "validate_pipeline.py", "report_large_files.py",
              "build_manifest.py"],
}

# "all" excludes the network-dependent ASU/Crossref stages and the optional
# synthetic-TIR legacy branch; run them explicitly.
ALL_STAGES = ("prepare", "main", "controls", "aux", "figures", "audit")

DEPS = "import numpy, scipy, matplotlib, osgeo"  # required by the pipeline


def deps_ok(exe: str) -> bool:
    r = subprocess.run([exe, "-c", DEPS], capture_output=True)
    return r.returncode == 0


def resolve_python() -> str:
    """Return an interpreter with the pipeline dependencies.

    Tries the current interpreter first; if it lacks the dependencies (e.g. a
    base Python without GDAL), falls back to known conda-env locations and to
    `conda run`.
    """
    if deps_ok(sys.executable):
        return sys.executable

    candidates = []
    env = os.environ.get("AMPYTHON")
    if env:
        candidates.append(Path(env))
    for root in (Path(r"D:\miniconda3\envs"), Path(r"D:\anaconda3\envs"),
                 Path.home() / "miniconda3" / "envs",
                 Path.home() / "anaconda3" / "envs"):
        if root.is_dir():
            for e in sorted(root.iterdir()):
                candidates.append(e / "python.exe")
    for cand in candidates:
        if cand.is_file() and deps_ok(str(cand)):
            print(f"[env] {sys.executable} lacks numpy/scipy/GDAL; "
                  f"using {cand}", flush=True)
            return str(cand)

    raise SystemExit(
        f"\n[env] No interpreter with numpy/scipy/matplotlib/GDAL was found.\n"
        f"  tried : {sys.executable}\n"
        f"  fix   : conda activate geo   (or set AMPYTHON=<python.exe>)\n"
        f"          then rerun this command"
    )


def run(script, python_exe):
    print(f"\n{'='*70}\n>>> {script}\n{'='*70}", flush=True)
    t0 = time.time()
    subprocess.run([python_exe, str(HERE / script)], check=True)
    print(f"<<< {script}  {time.time()-t0:.1f} s", flush=True)


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg == "all":
        keys = ALL_STAGES
    elif arg in STAGES:
        keys = (arg,)
    else:
        raise SystemExit(f"unknown stage {arg!r}; choose from {list(STAGES)} or all")
    python_exe = resolve_python()
    scripts = [s for k in keys for s in STAGES[k]]
    for s in scripts:
        run(s, python_exe)


if __name__ == "__main__":
    main()
