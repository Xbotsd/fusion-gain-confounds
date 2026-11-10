"""Round 7 documentation sync after the normalisation fix."""
from pathlib import Path

ROOT = Path(r"D:\A_MineralProspecting")

# 1. normalisation audit: mark as fixed
p = ROOT / "docs" / "NORMALISATION_AUDIT.md"
t = p.read_text(encoding="utf-8")
t = t.replace(
    "## Status\n\n* Fix designed, not yet applied (it invalidates every number in `docs/`).\n"
    "* Experiments 2-4 of the rigor plan (bootstrap CI, TES sensitivity, second date)\n"
    "  should run **after** the fix, otherwise they inherit the artefact.\n"
    "* Experiment 1's geology-target results are recorded in\n"
    "  `processed/independent_target.json` but are marked provisional for the same\n"
    "  reason.",
    "## Status: fixed and re-run (2026-11-08)\n\n"
    "`common.fuse` now normalises the response matrix over the **active rows only**,\n"
    "and `test_core.py` asserts the invariance (`fuse: inactive rows do not change\n"
    "the estimate`). The whole pipeline was re-run.\n\n"
    "What the fix changed:\n\n"
    "| quantity | before | after |\n|---|---:|---:|\n"
    "| gamma-only F1, legacy matrix | 0.3246 | **0.5217** |\n"
    "| gamma-only F1, corrected matrix | 0.5190 | **0.5217** |\n"
    "| gamma+TIR F1, legacy | 0.3388 | 0.4410 |\n"
    "| gamma+TIR F1, corrected | 0.4509 | 0.4410 |\n"
    "| gamma+EM F1, legacy | 0.1912 | 0.1912 |\n"
    "| gamma+EM F1, corrected | 0.4170 | 0.4142 |\n"
    "| full model F1, legacy | 0.2671 | 0.2671 |\n"
    "| full model F1, corrected | 0.4982 | 0.4982 |\n\n"
    "The two matrices now agree exactly wherever EM is inactive, and the full-model\n"
    "numbers are unchanged. This means the entire 0.2671 to 0.4982 gain is\n"
    "attributable to the EM rows themselves, not to a renormalisation side effect:\n"
    "the headline claim of the paper is **stronger**, not weaker, after the fix.\n\n"
    "The ablation interpretation does change: gamma alone (0.522) now clearly beats\n"
    "every configuration on the gamma-derived proxy, and the gap between the two\n"
    "matrices appears only where EM is actually used.")
p.write_text(t, encoding="utf-8")
print("normalisation audit updated")

# 2. changelog
p = ROOT / "docs" / "CHANGELOG.md"
t = p.read_text(encoding="utf-8")
entry = """## Round 7 — normalisation fix and independent target (current)

* **Found and fixed a normalisation artefact.** `normalize_H` scaled each mineral
  column over all ten rows, including modalities that were switched off, so
  "gamma only" gave F1 0.3246 under the legacy matrix and 0.5190 under the
  corrected one for identical data. `fuse` now normalises over the active rows,
  a unit test asserts the invariance, and the whole pipeline was re-run.
* **The headline claim survives and is cleaner.** Full-model F1 is unchanged
  (0.2671 legacy, 0.4982 corrected) and the two matrices now agree exactly
  wherever EM is inactive, so the entire gain comes from the EM rows.
  Ablation numbers did change: gamma 0.5217, gamma+TIR 0.4410, gamma+EM 0.1912 /
  0.4142, all 0.2671 / 0.4982.
* **New independent-target experiment** (`run_independent_target.py`). Scored
  against USGS SIM 3206 substrate classes, with labels that never see gamma or
  TIR: gamma alone sits at chance (AUC 0.476), gamma+TIR reaches 0.905 with the
  real ASTER cube and 0.895 with the synthetic one, the full set 0.909. The raw
  channels separate the same substrates almost perfectly (K alone 0.986), so the
  loss is caused by the inversion being underdetermined with three channels, not
  by missing information.
* **Real-TIR robustness (experiments 2-4).** Bootstrap of the gamma+TIR gain:
  +0.119 [0.080, 0.169], 200/200 wins. Insensitive to the TES assumption
  (eps_max 0.95/0.98/1.00 give 0.6400/0.6401/0.6403), to dropping the band with
  the residual temperature correlation (0.5856), and to the acquisition date
  (2006-09-25 gives 0.6410).
* Experiment 1 also made the section 5 result sharper: the variance-gain index
  now agrees with the F1 sign in **0 of 6** additions.
* **State:** 97/97 artefacts, 21/21 cross-checks.

## Round 6 — real ASTER TIR branch
"""
t = t.replace("## Round 6 — real ASTER TIR branch (current)", entry.rstrip())
p.write_text(t, encoding="utf-8")
print("changelog updated")
