"""Add the independent-target finding (experiment 1) to the manuscript."""
import json
from pathlib import Path

P = Path(r"D:\A_MineralProspecting\docs\Manuscript_v2_draft.md")
t = P.read_text(encoding="utf-8")
res = json.load(open(r"D:\A_MineralProspecting\processed\independent_target.json",
                    encoding="utf-8"))


def get(branch, model, cfg, key="auc"):
    return next(r[key] for r in res["rows"]
                if r["branch"] == branch and r["em_model"] == model
                and r["config"] == cfg)


g = get("real-aster", "corrected", "gamma")
gt = get("real-aster", "corrected", "gamma+tir")
ga = get("real-aster", "corrected", "all")
sg = get("synthetic-handset", "corrected", "gamma+tir")

NEW = (
    "### 7.9 Independent geological check\n\n"
    "Two checks use data that the inversion never sees: the USGS SIM 3206\n"
    "surficial map (substrate classes) and, as an independent continuous target,\n"
    "the same map's lithological groups. The map is rasterised to the 50 m grid and\n"
    "the clay estimate is scored against it.\n\n"
    "Clay is highest in alluvium (0.487), felsic plutonic (0.426) and volcanic\n"
    "(0.417) substrates and lowest in sedimentary (0.020) and carbonate (0.011)\n"
    "substrates; Kruskal-Wallis p < 0.001 and felsic > carbonate p < 0.001. The\n"
    "ranking is directionally consistent with the geology.\n\n"
    "The stronger test pools the substrates that should carry clay (alluvium,\n"
    "felsic plutonic) against those that should not (carbonate, sedimentary) and\n"
    "asks how well each configuration separates them by AUC. The labels contain no\n"
    "gamma or TIR information. Gamma alone sits at chance (**AUC "
    f"{g:.3f}**), gamma+TIR reaches **{gt:.3f}** with the real ASTER cube, and the\n"
    f"full set {ga:.3f}. The synthetic TIR cube reaches {sg:.3f}.\n\n"
    "The gamma-only result needs an explanation, because the raw channels separate\n"
    "the same substrates almost perfectly (K alone gives AUC 0.986, the clay proxy\n"
    "0.953). The inversion, not the data, destroys the signal: with three channels\n"
    "and five abundances the system is underdetermined, so the ridge solution is a\n"
    "minimum-norm compromise rather than a clay map. Adding TIR makes the system\n"
    "overdetermined and the geological contrast reappears. This is the empirical\n"
    "counterpart of the identifiability analysis of Section 5: a channel that\n"
    "carries information only helps if the inverse problem can use it.\n\n"
    "The map describes surficial substrate, not alteration assemblages, so this\n"
    "remains a consistency check rather than an accuracy validation."
)

start = t.index("### 7.9 Independent geological check")
end = t.index("### 7.10")
t = t[:start] + NEW + "\n\n" + t[end:]
P.write_text(t, encoding="utf-8")
print("section 7.9 replaced; AUC gamma %.3f real+TIR %.3f all %.3f synthetic+TIR %.3f"
      % (g, gt, ga, sg))
