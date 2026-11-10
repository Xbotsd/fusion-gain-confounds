"""Rewrite the conditioning paragraphs so they match the literal zeros control.

The controls now include five all-zero channels (F1 0.614) alongside the Gaussian
noise channels (0.649) and the block-shuffled cube (0.634), against 0.652 for the
real cube and 0.531 for gamma. So the F1 gain decomposes into 69-98 % conditioning
and the geological AUC gain is entirely conditioning.
"""
import json
import pathlib
import re
import textwrap

root = pathlib.Path(__file__).resolve().parents[2]
proc = root / "processed"
ms_path = root / "docs" / "Manuscript_v2_draft.md"

ctl = {r["config"]: r for r in
       json.loads((proc / "tir_controls.json").read_text(encoding="utf-8"))["rows"]}
real, zeros = ctl["gamma + real TIR"], ctl["gamma + 5 zero channels"]
noise = ctl["gamma + 5 noise channels"]
shuf = ctl["gamma + real TIR, block-shuffled"]
gam = ctl["gamma"]
gain = real["f1"] - gam["f1"]
share_zero = (zeros["f1"] - gam["f1"]) / gain
share_noise = (noise["f1"] - gam["f1"]) / gain
share_shuf = (shuf["f1"] - gam["f1"]) / gain
print(f"gain {gain:.4f}; shares zeros {share_zero:.0%}, noise {share_noise:.0%}, "
      f"shuffled {share_shuf:.0%}")
print(f"F1 real {real['f1']:.4f} zeros {zeros['f1']:.4f} "
      f"noise {noise['f1']:.4f} shuffled {shuf['f1']:.4f} gamma {gam['f1']:.4f}")
print(f"AUC real {real['geo_auc']:.4f} zeros {zeros['geo_auc']:.4f} "
      f"noise {noise['geo_auc']:.4f} shuffled {shuf['geo_auc']:.4f} "
      f"gamma {gam['geo_auc']:.4f}")

lo, hi = round(share_zero * 100), round(share_noise * 100)
t = ms_path.read_text(encoding="utf-8")

reps = []

# --- abstract -------------------------------------------------------------
reps.append((
    "Five ASTER bands raise proxy F1 from 0.531 to 0.652 and geological AUC to "
    "0.913 - but five channels of zeros with the same response rows reproduce "
    "F1 0.649 and AUC 0.922, so most of that gain is conditioning.",
    f"Five ASTER bands raise proxy F1 from 0.531 to 0.652 and geological AUC to "
    f"0.913 - but five uninformative channels with the same response rows recover "
    f"{lo}-{hi} % of the F1 gain and all of the AUC gain, so most of it is "
    f"conditioning."))

# --- highlights -----------------------------------------------------------
reps.append((
    "- Real ASTER TIR lifts proxy F1 to 0.652; identical zero channels give 0.649",
    f"- Real ASTER TIR lifts proxy F1 to 0.652; inert channels recover {lo}-{hi} %"))

# --- contribution (i) -----------------------------------------------------
reps.append((
    "channels of *zeros* with the correct response rows reproduces the fused score of\n"
    "the real thermal data (F1 0.649 versus 0.652; geological AUC 0.922 versus 0.913),\n"
    "which measures the conditioning effect directly.",
    "channels that carry no information - all zeros, Gaussian noise, or the real cube\n"
    f"block-shuffled - recover {lo}-{hi} % of its F1 gain ({zeros['f1']:.3f}, "
    f"{noise['f1']:.3f} and {shuf['f1']:.3f} against {real['f1']:.3f}) and all of its\n"
    "geological AUC gain, which measures the conditioning effect directly."))

# --- section 7.3 lead-in --------------------------------------------------
reps.append((
    "Replacing the real ASTER cube with five channels of **zeros**, keeping the same\n"
    "response rows, reproduces almost the entire effect:",
    "Replacing the real ASTER cube with channels that carry no information, while\n"
    "keeping the same response rows, recovers most of the effect. The share depends\n"
    "on which inert control is used, so Table 5 reports three:"))

# --- Table 5 itself -------------------------------------------------------
reps.append((
    "**Table 5.** Conditioning controls. \"Five noise channels\" and \"zeros\" use\n"
    "the real ASTER rows of `H` with data that carry no information; the block-shuffled\n"
    "cube keeps the ASTER marginals and destroys geographic registration.",
    "**Table 5.** Conditioning controls. The zero and noise blocks use the real ASTER\n"
    "rows of `H` with data that carry no information; the block-shuffled cube keeps\n"
    "the ASTER marginals and destroys geographic registration. Columns are proxy F1,\n"
    "average precision, geological AUC and the model-free balanced accuracy."))

reps.append((
    "| gamma + block-shuffled ASTER | 0.634 | 0.635 | 0.913 | 0.354 |\n"
    "| gamma + five noise channels | 0.649 | 0.687 | 0.922 | — |",
    "| gamma + block-shuffled ASTER | 0.634 | 0.635 | 0.913 | 0.354 |\n"
    "| gamma + five zero channels | 0.614 | 0.774 | 0.919 | — |\n"
    "| gamma + five noise channels | 0.649 | 0.687 | 0.922 | — |"))

# --- the paragraph after Table 6 -----------------------------------------
reps.append((
    "Inside the estimator, zeros and shuffled copies score like the real cube, because\n"
    "the extra rows regularise a rank-3 problem.",
    "Inside the estimator, zeros, noise and shuffled copies all score close to the real\n"
    f"cube ({lo}-{hi} % of the F1 gain, and a geological AUC at or above the real\n"
    "cube's), because the extra rows regularise a rank-3 problem."))

reps.append((
    "The honest reading is that real ASTER TIR does carry information about substrate\n"
    "that gamma does not (20 of 20 repeats, CI [0.120, 0.241]), but the +0.12 F1 and\n"
    "+0.46 AUC reported by the inversion overstate it by roughly a factor of four.",
    "The honest reading is that real ASTER TIR does carry information about substrate\n"
    "that gamma does not (20 of 20 repeats, CI [0.120, 0.241]), but the +0.12 F1 and\n"
    "+0.53 AUC reported by the inversion overstate it: for the AUC there is no\n"
    "information left at all once conditioning is controlled, and for F1 the true\n"
    "share is roughly a third."))

# --- conclusion -----------------------------------------------------------
reps.append((
    "infrared to gamma-ray data is mostly an artefact of an underdetermined inversion:\n"
    "five channels of zeros with the same response rows reproduce 0.649 of the 0.652\n"
    "F1 and 0.922 of the 0.913 geological AUC.",
    "infrared to gamma-ray data is mostly an artefact of an underdetermined inversion:\n"
    "five uninformative channels with the same response rows recover "
    f"{lo}-{hi} % of the\n"
    f"F1 gain ({zeros['f1']:.3f} for zeros, {noise['f1']:.3f} for noise, against "
    f"{real['f1']:.3f} for the\n"
    f"real cube) and a geological AUC at least as high "
    f"({zeros['geo_auc']:.3f} and {noise['geo_auc']:.3f}\n"
    f"against {real['geo_auc']:.3f})."))

for old, new in reps:
    if old in t:
        t = t.replace(old, new)
        print("replaced:", old.splitlines()[0][:58])
    else:
        print("!! NOT FOUND:", old.splitlines()[0][:58])

ms_path.write_text(t, encoding="utf-8")
