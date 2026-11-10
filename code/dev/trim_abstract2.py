"""Trim the abstract to <= 250 words, keeping the load-bearing numbers."""
import re
from pathlib import Path

P = Path(r"D:\A_MineralProspecting\docs\Manuscript_v2_draft.md")
TOK = re.compile(r"[A-Za-z0-9\u00c0-\u024f'\u2019-]+")

NEW = (
    "Reported fusion gains in airborne mineral exploration are rarely reproducible "
    "because of two confounds: the target is derived from "
    "the channels being inverted, and the inversion is underdetermined, so adding "
    "any channel changes conditioning rather than information. We separate both on "
    "a real-data benchmark over the Ivanpah-Clark Mountain area: USGS radiometrics "
    "(295,943 samples), real ASTER L1T thermal infrared (five emissivity bands), "
    "real aeromagnetics and the USGS SIM 3206 geologic map, with one "
    "synthetic electromagnetic augmentation since no measured airborne EM exists. Three gamma channels for five minerals give rank 3, and gamma "
    "alone scores at chance against independent geology (AUC 0.387). Five ASTER "
    "bands raise proxy F1 from 0.531 to 0.652 and geological AUC to 0.913 - but "
    "five channels of zeros with the same response rows reproduce F1 0.649 and AUC "
    "0.922, so most of that gain is conditioning. A model-free test isolates the "
    "information: gamma plus ASTER classifies four similar substrates at balanced "
    "accuracy 0.529 versus 0.350 for gamma (+0.179, CI [0.120, 0.241], 20/20 repeats), while a shuffled cube gives 0.354. Correcting a "
    "mis-specified electromagnetic row raises F1 from 0.168 to 0.497 but still "
    "loses to gamma plus thermal. Effective sample size is 122, not 1.2 million "
    "pixels, and the filter variance is not a confidence interval (coverage "
    "0.13). Fusion studies should report the rank of the inverse problem and an "
    "information test that does not use the response matrix."
)

t = P.read_text(encoding="utf-8")
start, end = t.index("## Abstract"), t.index("**Keywords:**")
print("old words:", len(TOK.findall(t[start:end])))
print("new words:", len(TOK.findall(NEW)))
assert len(TOK.findall(NEW)) <= 250
t = t[:start] + "## Abstract\n\n" + NEW + "\n\n" + t[end:]
P.write_text(t, encoding="utf-8")
print("abstract replaced")
