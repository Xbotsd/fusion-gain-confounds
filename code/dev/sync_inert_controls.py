"""Sync the zeros/noise conditioning numbers across the docs (idempotent)."""
import json
import pathlib
import textwrap

root = pathlib.Path(__file__).resolve().parents[2]
ctl = {r["config"]: r for r in json.loads(
    (root / "processed" / "tir_controls.json").read_text(encoding="utf-8"))["rows"]}
real, zero, noise = (ctl["gamma + real TIR"], ctl["gamma + 5 zero channels"],
                     ctl["gamma + 5 noise channels"])
gam = ctl["gamma"]
gain = real["f1"] - gam["f1"]
sh_lo = round((zero["f1"] - gam["f1"]) / gain * 100)
sh_hi = round((noise["f1"] - gam["f1"]) / gain * 100)
print(f"F1 real {real['f1']:.3f} zeros {zero['f1']:.3f} noise {noise['f1']:.3f}; "
      f"AUC {real['geo_auc']:.3f}/{zero['geo_auc']:.3f}/{noise['geo_auc']:.3f}; "
      f"shares {sh_lo}-{sh_hi}%")


def sub(path, pairs):
    p = root / path
    t = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if old in t:
            t = t.replace(old, new)
            print(f"{path}: {old[:42]!r} -> ok")
        else:
            print(f"{path}: !! missing {old[:42]!r}")
    p.write_text(t, encoding="utf-8")


w = 78

sub("README.md", [
    ("channels of **zeros** with the same response rows reproduce F1 0.649 and AUC\n"
     "0.922, so most of that gain is **conditioning**.",
     f"channels that carry no information - all zeros, Gaussian noise, or the\n"
     f"block-shuffled cube - recover {sh_lo}-{sh_hi} % of that F1 gain and all of\n"
     f"the AUC gain, so most of it is **conditioning**."),
])

sub("docs/RESULTS.md", [
    ("| gamma + five noise channels | 0.649 | 0.922 | — |",
     f"| gamma + five zero channels | {zero['f1']:.3f} | {zero['geo_auc']:.3f} | — |\n"
     f"| gamma + five noise channels | {noise['f1']:.3f} | {noise['geo_auc']:.3f} | — |"),
])

sub("docs/GAP_AUDIT.md", [
    ("| Identifiability | 9/10 | rank, κ, variance-gain index and a zero-filled control |",
     "| Identifiability | 9/10 | rank, κ, variance-gain index, zero/noise/shuffle controls |"),
    ("* **The conditioning confound measured**: five channels of zeros with the ASTER H\n"
     "rows reproduce F1 0.649 vs 0.652 and AUC 0.922 vs 0.913.",
     f"* **The conditioning confound measured**: five inert channels with the ASTER H\n"
     f"rows recover {sh_lo}-{sh_hi} % of the F1 gain (F1 {zero['f1']:.3f} for zeros,\n"
     f"{noise['f1']:.3f} for noise, {real['f1']:.3f} for the real cube) and an AUC at\n"
     f"least as high ({zero['geo_auc']:.3f}, {noise['geo_auc']:.3f} vs "
     f"{real['geo_auc']:.3f})."),
])

sub("docs/READINESS_AUDIT.md", [
    ("1. **Conditioning control.** Appending five channels of *zeros* with the ASTER\n"
     "rows of `H` reproduces almost the whole fused gain (F1 0.649 vs 0.652;\n"
     "geological AUC 0.922 vs 0.913).",
     f"1. **Conditioning control.** Appending five inert channels with the ASTER rows\n"
     f"of `H` recovers {sh_lo}-{sh_hi} % of the fused F1 gain (0.614 for zeros,\n"
     f"0.649 for noise, against 0.652) and a geological AUC at least as high\n"
     f"(0.919 and 0.922 against 0.913)."),
])

sub("docs/COVER_LETTER.md", [
    ("geology from 0.387 to 0.913. Five channels of *zeros* with the same response rows\n"
     "reproduce 0.649 and 0.922, and a block-shuffled cube reproduces them too: most of\n"
     "the gain is conditioning of a rank-3 inverse problem, not mineralogical\n"
     "information.",
     f"geology from 0.387 to 0.913. Five inert channels with the same response rows\n"
     f"recover {sh_lo}-{sh_hi} % of that F1 gain and an AUC at least as high (0.919\n"
     f"with all-zero channels, 0.922 with Gaussian noise), and a block-shuffled cube\n"
     f"does the same: most of the gain is conditioning of a rank-3 inverse problem,\n"
     f"not mineralogical information."),
])

sub("docs/SUPPLEMENTARY.md", [
    ("conditioning (zeros reproduce it); the model-free information gain is +0.179",
     f"conditioning ({sh_lo}-{sh_hi} % of the F1 gain is reproduced by inert channels);"
     " the model-free information gain is +0.179"),
])

sub("docs/JOURNAL_SHORTLIST.md", [
    ("但同形零通道得到 0.922——说明大部分增益是条件改善而非信息。",
     f"但同形惰性通道（全零、高斯噪声、块置换）即可复现 F1 增益的 {sh_lo}–{sh_hi}%、"
     f"AUC 增益的全部——说明大部分增益是条件改善而非信息。"),
])

sub("docs/Manuscript_v2_draft.md", [
    ("20 invariants (including the zero-filled and shuffled controls)",
     "22 invariants (including the zero, noise and shuffled controls)"),
])

# counters: 20 -> 22 everywhere they are quoted
for rel in ("docs/GAP_AUDIT.md", "docs/READINESS_AUDIT.md", "README.md",
            "docs/README.md", "docs/SUPPLEMENTARY.md"):
    p = root / rel
    t = p.read_text(encoding="utf-8")
    t2 = (t.replace("20/20 invariants", "22/22 invariants")
            .replace("53 artefacts, 20 invariants", "53 artefacts, 22 invariants")
            .replace("**20/20**", "**22/22**")
            .replace("checks 53 artefacts and 20 invariants",
                     "checks 53 artefacts and 22 invariants"))
    if t2 != t:
        p.write_text(t2, encoding="utf-8")
        print(f"{rel}: invariant counter bumped")
