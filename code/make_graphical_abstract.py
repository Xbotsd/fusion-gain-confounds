"""Graphical abstract: the same data, three ways of reading the gain.

Reads only `processed/*.json`, so the picture cannot drift from the tables.
Output: docs/graphical_abstract.png (2656 x 1062 px, 200 dpi) and a
half-width version for the submission form.
"""
from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common as C

INK = "#1b1b1b"
GREY = "#8a8a8a"
BLUE = "#1f4e79"
RED = "#b03a2e"
GREEN = "#2e7d4f"


def main():
    main_res = json.loads((C.PROC / "main_results.json").read_text(encoding="utf-8"))
    ctl = {r["config"]: r for r in
           json.loads((C.PROC / "tir_controls.json").read_text(encoding="utf-8"))["rows"]}
    mc = json.loads((C.PROC / "geology_multiclass.json").read_text(encoding="utf-8"))
    ranks = json.loads((C.PROC / "identifiability.json").read_text(encoding="utf-8"))

    fig = plt.figure(figsize=(13.28, 5.31), dpi=200)
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.25, 1.1], wspace=0.42)
    fig.patch.set_facecolor("white")

    # ---- (1) what is actually being inverted --------------------------------
    ax0 = fig.add_subplot(gs[0, 0])
    ax0.axis("off")
    ax0.set_title("1. Rank 3 of 5", fontsize=12, loc="left", color=INK,
                  fontweight="bold")
    ax0.text(0.0, 0.78, "3 gamma channels", fontsize=11, color=BLUE)
    ax0.text(0.0, 0.60, "5 mineral unknowns", fontsize=11, color=RED)
    rank = ranks.get("gamma", {}).get("rank", 3)
    ax0.text(0.0, 0.38, f"rank {rank} of 5", fontsize=22, color=RED,
             fontweight="bold")
    ax0.text(0.0, 0.18, "any added channel changes the\nconditioning before it\n"
                        "adds mineralogical information", fontsize=10, color=INK)
    ax0.set_xlim(0, 1)
    ax0.set_ylim(0, 1)

    # ---- (2) inside the estimator: real == zeros == shuffled ---------------
    ax1 = fig.add_subplot(gs[0, 1])
    labels = ["gamma", "gamma\n+ real ASTER", "gamma\n+ zeros", "gamma\n+ shuffled"]
    keys = ["gamma", "gamma + real TIR", "gamma + 5 zero channels",
            "gamma + real TIR, block-shuffled"]
    vals = [ctl[k]["f1"] for k in keys]
    cols = [GREY, BLUE, RED, RED]
    bars = ax1.bar(labels, vals, color=cols, width=0.62)
    for b, v in zip(bars, vals):
        ax1.text(b.get_x() + b.get_width() / 2, v + 0.012, f"{v:.3f}",
                 ha="center", fontsize=10, color=INK)
    ax1.set_ylim(0, 0.78)
    ax1.set_ylabel("proxy F1", fontsize=10)
    ax1.set_title("2. Same H rows, no extra information",
                  fontsize=12, loc="left", color=INK, fontweight="bold")
    ax1.tick_params(labelsize=9)
    for s in ("top", "right"):
        ax1.spines[s].set_visible(False)
    ax1.annotate("same H rows", xy=(2.5, 0.70), fontsize=9, color=RED, ha="center")

    # ---- (3) without the response matrix ----------------------------------
    ax2 = fig.add_subplot(gs[0, 2])
    names = ["gamma", "gamma +\nreal ASTER", "gamma +\nshuffled"]
    mkeys = ["gamma", "gamma + real ASTER", "gamma + block-shuffled ASTER"]
    mv = [mc["summary"][k]["balanced_accuracy_mean"] for k in mkeys]
    err = [mc["summary"][k]["balanced_accuracy_sd"] for k in mkeys]
    bars = ax2.bar(names, mv, yerr=err, color=[GREY, GREEN, RED], width=0.6,
                   capsize=4, error_kw={"lw": 1, "ecolor": INK})
    for b, v, e in zip(bars, mv, err):
        ax2.text(b.get_x() + b.get_width() / 2, v + e + 0.012, f"{v:.3f}",
                 ha="center", fontsize=10, color=INK)
    ax2.axhline(mc["chance"], ls=":", lw=1, color=INK)
    ax2.text(2.42, mc["chance"] + 0.01, "chance", fontsize=8, color=INK, ha="right")
    ax2.set_ylim(0, 0.78)
    ax2.set_ylabel("balanced accuracy (4 substrates)", fontsize=10)
    gain = mc["summary"]["gamma + real ASTER"]["gain_vs_gamma_mean"]
    lo, hi = mc["summary"]["gamma + real ASTER"]["gain_vs_gamma_ci95"]
    ax2.set_title("3. Without H: a real, smaller gain", fontsize=12, loc="left",
                  color=INK, fontweight="bold")
    ax2.text(0.5, 0.90, f"gain +{gain:.3f}  [{lo:.3f}, {hi:.3f}]",
             transform=ax2.transAxes, ha="center", fontsize=9, color=GREEN,
             bbox=dict(fc="white", ec="none", pad=1.5))
    ax2.tick_params(labelsize=9)
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)

    fig.text(0.01, 0.015,
             "Real USGS radiometrics, real ASTER L1T TIR, real aeromagnetics and "
             "USGS SIM 3206 geology over Ivanpah-Clark Mountain, NV-CA; "
             "EM synthetic and labelled as such.",
             fontsize=8, color=GREY)

    out = C.ROOT / "docs" / "graphical_abstract.png"
    fig.savefig(out, dpi=200, facecolor="white", bbox_inches="tight")
    print("saved", out)
    print("gamma", round(vals[0], 3), "real", round(vals[1], 3),
          "zeros", round(vals[2], 3), "shuffled", round(vals[3], 3))
    print("multiclass", [round(v, 3) for v in mv], "gain", round(gain, 3))


if __name__ == "__main__":
    main()
