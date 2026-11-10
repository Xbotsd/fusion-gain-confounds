"""Replace the abstract with a <=250-word version and assert the limit."""
import re
from pathlib import Path

P = Path(r"D:\A_MineralProspecting\docs\Manuscript_v2_draft.md")
TOK = re.compile(r"[A-Za-z0-9\u00c0-\u024f'\-]+")

NEW = (
    "Multi-modal fusion is widely proposed for airborne mineral exploration, yet "
    "reported gains are rarely comparable because studies use different response "
    "matrices, synthetic recipes and metrics. We present a reproducible benchmark "
    "on the real USGS airborne radiometric survey of Ivanpah-Clark Mountain "
    "(Nevada-California, 2019-2020) with documented synthetic thermal-infrared "
    "(TIR) and electromagnetic (EM) modalities, one response matrix, one "
    "valid-pixel mask and one contingency-table metric. The legacy fusion model "
    "shows no gain, and we diagnose why: its EM row is linear in raw resistivity, "
    "gives all five minerals a response and assigns clay the lowest resistivity, "
    "so it is mis-signed, ill-conditioned (kappa 1156 versus 48.5) and suppresses "
    "the TIR contrast. Expressing EM as log10 resistivity with a clay-only "
    "response raises proxy F1 from 0.267 to 0.498 and average precision from "
    "0.126 to 0.513, above every generic baseline, with a 128-px block-bootstrap "
    "gain of +0.167 [0.118, 0.216]. We then bound the claim. Because the target "
    "is gamma-derived, two published gamma ratios beat the fusion "
    "(F-parameter average precision 0.650), gamma alone wins the ablation "
    "(F1 0.519 versus 0.498) and losing both auxiliary modalities is "
    "indistinguishable from normal (BH p = 0.91); on an independent TIR truth the "
    "ordering reverses. A variance-based gain index does not predict this, "
    "agreeing with the F1 change in only one of six cases. A fusion gain must "
    "therefore be reported against a stated target, a metric and a "
    "response-matrix consistency check; a gamma-derived target cannot demonstrate "
    "multimodal superiority."
)

t = P.read_text(encoding="utf-8")
start = t.index("## Abstract")
end = t.index("**Keywords:**")
old = t[start:end]
n_new = len(TOK.findall(NEW))
print("old words:", len(TOK.findall(old)))
print("new words:", n_new)
assert n_new <= 250, n_new
t = t[:start] + "## Abstract\n\n" + NEW + "\n\n" + t[end:]
P.write_text(t, encoding="utf-8")
print("abstract replaced")
