"""Dump the numbers used in the documentation tables (docs/*.md)."""
import json
from pathlib import Path

P = Path(r"D:\A_MineralProspecting\processed")


def j(name):
    return json.load(open(P / name, encoding="utf-8"))


for tag, fname in (("legacy", "validation.json"), ("emfix", "validation_emfix.json")):
    d = j(fname)
    print(f"--- {fname} ({tag})")
    print("overall recall %.4f  f1 %.4f" % (d["overall_recall"], d["overall_f1"]))
    print("families", {k: round(v, 4) for k, v in d["family_recall"].items()})
    for r in d["scenarios"]:
        print("  %-34s R=%.4f P=%.4f F1=%.4f rmse=%.3f r=%+.3f" %
              (r["case"], r["recall"], r["precision"], r["f1"],
               r["rmse_truth"], r["r_truth"]))
