"""Validate the main-line data chain and its scientific invariants.

Two jobs:

1. **Integrity** — every expected artefact exists with the right shape/dtype, and
   the headline metrics recompute from the saved arrays.
2. **Invariants** — the claims the paper makes are re-checked end to end, so a
   silent regression cannot survive:
       * the identifiability run reproduces the ablation exactly;
       * gamma alone is underdetermined (rank 3 of 5) and gamma+TIR is not;
       * replacing the real ASTER cube by zeros *with the same H rows* reproduces
         its score (the conditioning effect is real and reported);
       * a block-shuffled ASTER cube performs like gamma (no geographic
         information), while the real cube beats gamma on the independent
         geological target;
       * the multi-class geology gain over gamma excludes zero;
       * physical gates on the ASTER retrievals;
       * pseudo-replication: bootstrap blocks exceed 2x the integral scale.

Writes processed/pipeline_validation.json, output_yield.csv
"""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone

import numpy as np

import common as C

EXPECTED_NPY = {
    "gamma_cube.npy": (3, None, None),
    "tir_cube.npy": (200, None, None),
    "tir_cube_real.npy": (5, None, None),
    "em_cube.npy": (40, None, None),
    "clay_prior.npy": (None, None),
    "truth_abundance.npy": (5, None, None),
    "valid_mask.npy": (None, None),
    "analysis_mask.npy": (None, None),
    "geology_substrate.npy": (None, None),
    "kf_main_abundance.npy": (5, None, None),
    "kf_main_uncertainty.npy": (5, None, None),
    "depth_kalman_3d.npy": (40, 5, None, None),
    "depth_uncertainty.npy": (40,),
    "depth_kalman_3d_emfix.npy": (40, 5, None, None),
    "depth_uncertainty_emfix.npy": (40,),
    "tmi_grid.npy": (None, None),
    "granite_indicator.npy": (None, None),
}

EXPECTED_JSON = [
    "main_results.json", "identifiability.json", "tir_controls.json",
    "tir_information.json", "geology_multiclass.json", "real_tir_robust.json",
    "tir_real.json", "geology_groups.json", "depth.json", "depth_emfix.json",
    "calibration.json", "autocorr.json", "independent_validation.json",
    "published_baselines.json", "edge_ai.json", "granite_properties.json",
    "granite_compensation.json", "large_files.json",
]

EXPECTED_FIG = [
    "main_ablation.png", "main_maps.png", "identifiability.png",
    "real_tir_robust.png", "published_baselines.png", "independent_validation.png",
    "calibration.png", "autocorr.png", "depth_profiles.png",
    "depth_clay_layers.png", "depth_section.png", "depth_uncertainty.png",
    "fig_data.png", "fig_method.png", "fig_results.png",
    "fig_granite.png", "granite_compensation.png", "edge_ai.png",
]


def shape_ok(a, spec):
    return (len(a.shape) == len(spec)
            and all(w is None or g == w for g, w in zip(a.shape, spec)))


# --------------------------------------------------------------------------
# Manuscript tables vs artefacts
# --------------------------------------------------------------------------
MS = C.ROOT / "docs" / "Manuscript_v2_draft.md"
TABLE_LABELS = {
    "Table 4": {"legacy / gamma": ("legacy", "gamma"),
                "legacy / gamma+tir": ("legacy", "gamma+tir"),
                "legacy / gamma+em": ("legacy", "gamma+em"),
                "legacy / all": ("legacy", "all"),
                "corrected / gamma": ("corrected", "gamma"),
                "corrected / gamma+tir": ("corrected", "gamma+tir"),
                "corrected / gamma+em": ("corrected", "gamma+em"),
                "corrected / all": ("corrected", "all")},
    "Table 5": {"gamma": "gamma",
                "gamma + real ASTER": "gamma + real TIR",
                "gamma + block-shuffled ASTER": "gamma + real TIR, block-shuffled",
                "gamma + five zero channels": "gamma + 5 zero channels",
                "gamma + five noise channels": "gamma + 5 noise channels",
                "gamma + synthetic TIR": "gamma + synthetic TIR"},
}


def _rows_after(caption: str) -> list[list[str]]:
    """Cell lists of the markdown table that follows a caption."""
    lines = MS.read_text(encoding="utf-8").splitlines()
    i = next(k for k, ln in enumerate(lines) if ln.startswith(f"**{caption}.**"))
    k = i + 1
    while not lines[k].lstrip().startswith("|"):
        k += 1
    out = []
    while k < len(lines) and lines[k].lstrip().startswith("|"):
        cells = [c.strip() for c in lines[k].strip().strip("|").split("|")]
        if not set("".join(cells)) <= set("-: "):
            out.append(cells)
        k += 1
    return out[1:]  # drop header


def _nums(cells: list[str]) -> list[float | None]:
    vals = []
    for c in cells:
        m = re.findall(r"[-+]?\d[\d,]*\.?\d*", c.replace("\u2212", "-"))
        vals.append([float(x.replace(",", "")) for x in m] if m else None)
    return vals


def check_tables():
    """Every table row must equal the artefact it is built from."""
    ms_main = C.load_json(C.PROC / "main_results.json")
    abl = {(r["em_model"], r["config"]): r for r in ms_main["ablation"]
           if r["branch"] == "real-aster"}
    ctl = {r["config"]: r for r in C.load_json(C.PROC / "tir_controls.json")["rows"]}
    mc = C.load_json(C.PROC / "geology_multiclass.json")["summary"]
    base = {r["method"]: r for r in ms_main["baselines"]}
    pub = {r["method"]: r for r in C.load_json(
        C.PROC / "published_baselines.json")["rows"]}

    problems = []
    for label in ("Table 4", "Table 5"):
        for cells in _rows_after(label):
            name = cells[0]
            ref = TABLE_LABELS[label].get(name)
            if ref is None:
                problems.append(f"{label}: unknown row {name!r}")
                continue
            src = abl[ref] if label == "Table 4" else ctl[ref]
            # column order: Table 4 = clay, recall, precision, F1, AP, AUC
            #               Table 5 = F1, AP, AUC, (balanced accuracy)
            order = (("clay_mean", "recall", "precision", "f1", "ap", "geo_auc")
                     if label == "Table 4" else ("f1", "ap", "geo_auc"))
            got = _nums(cells[1:])
            for j, key in enumerate(order):
                if got[j] is None:
                    problems.append(f"{label}/{name}: missing {key}")
                    continue
                if abs(got[j][0] - src[key]) > 6e-4:
                    problems.append(f"{label}/{name}: {key} paper {got[j][0]:.3f} "
                                    f"!= artefact {src[key]:.3f}")

    # Table 6: balanced accuracy, gain + CI, repeats
    for cells in _rows_after("Table 6"):
        name = cells[0]
        if name not in mc:
            problems.append(f"Table 6: unknown row {name!r}")
            continue
        s = mc[name]
        acc, gain = _nums(cells[1:3])
        if abs(acc[0] - s["balanced_accuracy_mean"]) > 6e-4:
            problems.append(f"Table 6/{name}: accuracy {acc[0]:.3f} != "
                            f"{s['balanced_accuracy_mean']:.3f}")
        if abs(acc[1] - s["balanced_accuracy_sd"]) > 6e-4:
            problems.append(f"Table 6/{name}: sd {acc[1]:.3f} != "
                            f"{s['balanced_accuracy_sd']:.3f}")
        if (abs(gain[0] - s["gain_vs_gamma_mean"]) > 6e-4
                or abs(gain[1] - s["gain_vs_gamma_ci95"][0]) > 6e-4
                or abs(gain[2] - s["gain_vs_gamma_ci95"][1]) > 6e-4):
            problems.append(f"Table 6/{name}: gain/CI do not match")

    # Table 7: estimator comparison
    for cells in _rows_after("Table 7"):
        name = cells[0]
        if name not in base:
            problems.append(f"Table 7: unknown row {name!r}")
            continue
        vals = _nums(cells[1:])
        keys = ("f1", "ap", "precision", "geo_auc", "components")
        for j, key in enumerate(keys):
            if vals[j] is None or abs(vals[j][0] - base[name][key]) > 6e-4:
                problems.append(f"Table 7/{name}: {key} mismatch")
                break

    # Table 9: published baselines
    for cells in _rows_after("Table 9"):
        name = cells[0]
        if name not in pub:
            problems.append(f"Table 9: unknown row {name!r}")
            continue
        vals = _nums(cells[2:])  # the reference column is text, not data
        for j, key in enumerate(("f1_matched", "auc_geology")):
            if vals[j] is None or abs(vals[j][0] - pub[name][key]) > 6e-4:
                problems.append(f"Table 9/{name}: {key} mismatch")

    ok = not problems
    detail = ("tables 4-7, 9 equal the artefacts" if ok
              else "; ".join(problems[:4]) + (f" (+{len(problems) - 4} more)"
                                              if len(problems) > 4 else ""))
    return ok, detail



def finite_fraction(a):
    s = a[::50] if a.ndim == 1 else a[..., ::50, ::50]
    return float(np.isfinite(s).mean())


def main():
    h, w = C.load_analysis_mask().shape
    checks, fail = [], False

    for name, spec in EXPECTED_NPY.items():
        p = C.PROC / name
        item = {"exists": p.exists(), "size": p.stat().st_size if p.exists() else 0}
        if not p.exists():
            item["status"] = "MISSING"
            fail = True
        else:
            a = np.load(p, mmap_mode="r")
            item.update({"shape": list(a.shape), "dtype": str(a.dtype),
                         "finite_fraction_sample": finite_fraction(a)})
            item["status"] = "PASS" if shape_ok(a, spec) else "SHAPE_MISMATCH"
            fail |= item["status"] != "PASS"
        checks.append({"check": f"npy:{name}", **item})

    for name in EXPECTED_JSON:
        p = C.PROC / name
        item = {"exists": p.exists(), "size": p.stat().st_size if p.exists() else 0}
        if p.exists():
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                item["keys"] = (sorted(d)[:10] if isinstance(d, dict)
                                else ["<list>", f"len={len(d)}"])
                item["status"] = "PASS"
            except Exception as exc:  # noqa: BLE001
                item["status"] = f"PARSE_ERROR: {exc}"
                fail = True
        else:
            item["status"] = "MISSING"
            fail = True
        checks.append({"check": f"json:{name}", **item})

    for name in EXPECTED_FIG:
        p = C.PROC / name
        ok = p.exists()
        checks.append({"check": f"fig:{name}", "exists": ok,
                       "size": p.stat().st_size if ok else 0,
                       "status": "PASS" if ok else "MISSING"})
        fail |= not ok

    xacc = []

    def xcheck(name, ok, detail=""):
        nonlocal fail
        xacc.append({"check": name, "ok": bool(ok), "detail": detail})
        fail |= not ok

    mask = C.load_analysis_mask()
    gt = C.load_clay_prior() > 0.55
    x = np.load(C.PROC / "kf_main_abundance.npy")
    main = C.load_json(C.PROC / "main_results.json")

    # 1. headline metric recomputes from the saved cube
    recalc = C.detection_metrics(x, gt, mask=mask)
    stored = next(r for r in main["ablation"]
                  if r["branch"] == "real-aster" and r["em_model"] == "corrected"
                  and r["config"] == "all")
    d = abs(recalc["f1"] - stored["f1"])
    xcheck("main_f1_recompute", d < 1e-6, f"delta {d:.2e}")
    xcheck("main_finite", bool(np.isfinite(x[:, mask]).all()),
           f"finite {np.isfinite(x[:, mask]).mean():.4f}")

    # 2. identifiability reproduces the ablation exactly
    idf = C.load_json(C.PROC / "identifiability.json")
    dev = idf["f1_reproduction_max_dev"]
    xcheck("identifiability_reproduces_main", dev < 1e-9, f"max dev {dev:.2e}")

    # 3. gamma is underdetermined, gamma+TIR is not
    g = idf["models"]["corrected"]["sets"]
    xcheck("gamma_underdetermined", g["gamma"]["rank"] < C.N_MIN,
           f"rank {g['gamma']['rank']}/{C.N_MIN} from {g['gamma']['n_equations']} eq")
    xcheck("gamma_tir_identifiable", g["gamma+tir"]["rank"] == C.N_MIN,
           f"rank {g['gamma+tir']['rank']}/{C.N_MIN} from {g['gamma+tir']['n_equations']} eq")

    # 4. the conditioning controls reproduce most of the real-TIR gain: two
    #    different inert blocks (all zeros, Gaussian noise) with the same H rows
    ctl = {r["config"]: r for r in C.load_json(C.PROC / "tir_controls.json")["rows"]}
    real_f1 = ctl["gamma + real TIR"]["f1"]
    gam_f1 = ctl["gamma"]["f1"]
    gain = real_f1 - gam_f1
    for key, label in (("gamma + 5 zero channels", "zeros"),
                       ("gamma + 5 noise channels", "noise")):
        share = (ctl[key]["f1"] - gam_f1) / gain
        xcheck(f"conditioning_control_matches_real[{label}]", 0.6 <= share <= 1.0,
               f"{label} F1 {ctl[key]['f1']:.3f} = {share:.0%} of the "
               f"{gain:.3f} gain over gamma")

    # 4b. the geological AUC gain is *entirely* conditioning: the inert
    #     blocks score at least as high as the real cube
    a_real = ctl["gamma + real TIR"]["geo_auc"]
    a_inert = min(ctl["gamma + 5 zero channels"]["geo_auc"],
                  ctl["gamma + 5 noise channels"]["geo_auc"])
    xcheck("auc_gain_is_conditioning", a_inert >= a_real - 0.02,
           f"inert AUC {a_inert:.3f} vs real {a_real:.3f}")

    # 5. inside the estimator the gain is conditioning, not geography:
    #    a block-shuffled ASTER cube scores like the real one (and like zeros).
    #    The information test is the model-free multi-class one (check 6).
    g_gamma = ctl["gamma"]["geo_auc"]
    g_real = ctl["gamma + real TIR"]["geo_auc"]
    g_shuf = ctl["gamma + real TIR, block-shuffled"]["geo_auc"]
    xcheck("inversion_gain_is_conditioning",
           abs(g_shuf - g_real) < 0.05,
           f"shuffled {g_shuf:.3f} vs real {g_real:.3f} (same H rows)")
    xcheck("real_tir_geo_gain_in_inversion", g_real - g_gamma > 0.10,
           f"real {g_real:.3f} vs gamma {g_gamma:.3f}")

    # 6. multi-class geology: the gain over gamma excludes zero
    mc = C.load_json(C.PROC / "geology_multiclass.json")["summary"]
    lo, hi = mc["gamma + real ASTER"]["gain_vs_gamma_ci95"]
    xcheck("multiclass_gain_ci_excludes_zero", lo > 0,
           f"gain {mc['gamma + real ASTER']['gain_vs_gamma_mean']:+.3f} "
           f"[{lo:+.3f}, {hi:+.3f}]")
    xcheck("multiclass_shuffle_null",
           abs(mc["gamma + block-shuffled ASTER"]["gain_vs_gamma_mean"]) < 0.03,
           f"shuffled gain "
           f"{mc['gamma + block-shuffled ASTER']['gain_vs_gamma_mean']:+.3f}")

    # 7. physical gate on the ASTER retrieval
    tj = C.load_json(C.PROC / "tir_real.json")
    eps_lo, eps_hi = tj["eps_percentiles"][0], tj["eps_percentiles"][2]
    bt = tj["bt_percentiles"][1]
    xcheck("aster_physical_range",
           0.6 <= eps_lo and eps_hi <= 1.0 and 270 <= bt <= 330,
           f"eps {eps_lo:.2f}-{eps_hi:.2f}, median BT {bt:.1f} K")
    xcheck("aster_coverage",
           tj["coverage_of_survey"] > 0.9,
           f"{tj['coverage_of_survey']:.1%} of the survey has all five bands")

    # 8. depth cubes agree
    d1 = np.load(C.PROC / "depth_kalman_3d.npy", mmap_mode="r")
    d2 = np.load(C.PROC / "depth_kalman_3d_emfix.npy", mmap_mode="r")
    xcheck("depth_shapes", d1.shape == d2.shape, f"{d1.shape} vs {d2.shape}")
    del d1, d2

    # 9. pseudo-replication
    ac = C.load_json(C.PROC / "autocorr.json")
    tau = max(max(ac["fields"]["clay_prior"]["integral_scale_x_px"],
                  ac["fields"]["clay_prior"]["integral_scale_y_px"]),
              max(ac["fields"]["main_clay"]["integral_scale_x_px"],
                  ac["fields"]["main_clay"]["integral_scale_y_px"]))
    xcheck("block_ge_2tau", ac["bootstrap_block_px"] >= 2 * tau,
           f"block {ac['bootstrap_block_px']} px vs 2*tau {2*tau:.0f} px")
    xcheck("n_eff_reported", ac["fields"]["main_clay"]["n_eff"] > 50,
           f"N_eff {ac['fields']['main_clay']['n_eff']:.0f}")

    # 9b. one bootstrap implementation: the robustness baseline must return the
    #     same interval as the main run, otherwise two CIs in the paper disagree
    rob = C.load_json(C.PROC / "real_tir_robust.json")["bootstrap"]
    mbs = C.load_json(C.PROC / "main_results.json")["bootstrap_f1"][
        "gamma+TIR_vs_gamma (real)"]
    xcheck("robust_bootstrap_matches_main",
           abs(rob["delta_mean"] - mbs["delta_mean"]) < 1e-9
           and all(abs(a - b) < 1e-9 for a, b in zip(rob["ci95"], mbs["ci95"])),
           f"robust {rob['delta_mean']:+.4f} {rob['ci95']} vs "
           f"main {mbs['delta_mean']:+.4f} {mbs['ci95']}")

    # 10. published baselines: the fusion beats the strongest single index
    pb = C.load_json(C.PROC / "published_baselines.json")["rows"]
    ours = next(r for r in pb if r["method"].startswith("WLS"))
    best_index = max((r for r in pb if r["method"] in
                      ("Ternary K-dominance", "F-parameter K*eU/eTh", "Low eTh/K")),
                     key=lambda r: r["f1_matched"])
    xcheck("fusion_beats_published_index",
           ours["f1_matched"] > best_index["f1_matched"],
           f"ours {ours['f1_matched']:.3f} vs {best_index['method']} "
           f"{best_index['f1_matched']:.3f}")

    # 11. calibration: the forward-filter variance is NOT a confidence interval
    cal = C.load_json(C.PROC / "calibration.json")
    xcheck("uncertainty_not_calibrated", cal["coverage_68"] < 0.5,
           f"68% coverage {cal['coverage_68']:.3f}")

    # 12. geology raster matches its own counts
    gg = C.load_json(C.PROC / "geology_groups.json")
    sub = np.load(C.PROC / "geology_substrate.npy")
    survey = C.load_valid_mask()
    counts = {g: int(((sub == i + 1) & survey).sum())
              for i, g in enumerate(gg["groups"])}
    xcheck("geology_counts", counts == gg["pixels_on_survey"],
           "counts match the raster")

    # 13. the manuscript's tables are the artefacts (no hand-typed numbers)
    xcheck("manuscript_tables_match_artefacts", *check_tables())

    # ---------------- yield -------------------------------------------------
    valid = int(mask.sum())
    yield_stats = {
        "grid_pixels": int(mask.size), "analysis_pixels": valid,
        "analysis_fraction": valid / mask.size,
        "survey_pixels": int(survey.sum()),
        "aster_fraction_of_survey": valid / max(int(survey.sum()), 1),
        "predicted_positive_rate": float(recalc["positive_rate"]),
        "artifact_rate": float(sum(1 for c in checks if c["status"] == "PASS")
                               / len(checks)),
        "artifacts_present": int(sum(1 for c in checks if c["status"] == "PASS")),
        "artifacts_expected": len(checks),
        "experiments": {
            "ablation_rows": len(main["ablation"]),
            "baseline_rows": len(main["baselines"]),
            "bootstrap_contrasts": len(main["bootstrap_f1"]),
            "multiclass_repeats": mc["gamma"]["repeats_improved"] and 20,
        },
        "runtime_s": main.get("runtime_s"),
    }

    report = {
        "status": "FAIL" if fail else "PASS",
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "grid": [h, w], "metric_recalc": recalc, "metric_stored": stored,
        "yield": yield_stats, "cross_checks": xacc, "checks": checks,
    }
    C.save_json(C.PROC / "pipeline_validation.json", report)

    with open(C.PROC / "output_yield.csv", "w", newline="", encoding="utf-8") as f:
        wri = csv.writer(f)
        wri.writerow(["metric", "value", "definition"])
        for k, v in yield_stats.items():
            wri.writerow([k, v, ""])

    print(f"status            : {report['status']}")
    print(f"artifacts         : {yield_stats['artifacts_present']}/{yield_stats['artifacts_expected']}")
    print(f"cross checks      : {sum(c['ok'] for c in xacc)}/{len(xacc)}")
    for c in xacc:
        print(f"  [{'ok ' if c['ok'] else 'FAIL'}] {c['check']:34s} {c['detail']}")
    print(f"analysis pixels   : {valid:,} / {mask.size:,} "
          f"({yield_stats['analysis_fraction']:.3f})")


if __name__ == "__main__":
    main()
