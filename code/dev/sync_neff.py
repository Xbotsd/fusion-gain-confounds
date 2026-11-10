"""Sync N_eff / design-effect numbers in the docs with autocorr.json (idempotent)."""
import json
import pathlib
import textwrap

root = pathlib.Path(__file__).resolve().parents[2]
ac = json.loads((root / "processed" / "autocorr.json").read_text())
prior, main = ac["fields"]["clay_prior"], ac["fields"]["main_clay"]
n1, d1 = round(prior["n_eff"]), round(prior["design_effect"])
n2, d2 = round(main["n_eff"]), round(main["design_effect"])
print(f"proxy target N_eff {n1} deff {d1}; inverted map N_eff {n2} deff {d2}")

para = textwrap.fill(
    "The clay field has an integral scale of about 50 px (2.5 km), a design "
    f"effect of {d1:,} and an effective sample size of {n1} from 1,237,644 "
    f"pixels; the inverted clay map, being smoother, gives {n2}. Every "
    "contrast in this paper is therefore reported with a 128-px block "
    "bootstrap.", width=80)

def sub(t, old, new, rel):
    if old in t:
        print(f"{rel}: {old[:40]!r} -> replaced")
        return t.replace(old, new)
    if new in t:
        print(f"{rel}: already current")
        return t
    print(f"!! {rel}: neither old nor new found: {old[:50]!r}")
    return t

# manuscript abstract
p = root / "docs/Manuscript_v2_draft.md"
t = p.read_text(encoding="utf-8")
t = sub(t, "Effective sample size is 122, not 1.2 million pixels",
        f"Effective sample size is {n1}, not 1.2 million pixels", "manuscript/abstract")
start = t.index("The clay field has an integral scale")
end = t.index("128-px block bootstrap.", start) + len("128-px block bootstrap.")
t = t[:start] + para + t[end:]
p.write_text(t, encoding="utf-8")
print("manuscript/7.9 paragraph regenerated")

# results
p = root / "docs/RESULTS.md"
t = p.read_text(encoding="utf-8")
t = sub(t, "design effect\n10168, **N_eff 122**",
        f"design effect\n{d1:,}, **N_eff {n1}** (inverted map {n2})", "RESULTS")
p.write_text(t, encoding="utf-8")

# gap audit
p = root / "docs/GAP_AUDIT.md"
t = p.read_text(encoding="utf-8")
t = sub(t, "N_eff 122", f"N_eff {n1}", "GAP_AUDIT")
p.write_text(t, encoding="utf-8")

# supplementary
p = root / "docs/SUPPLEMENTARY.md"
t = p.read_text(encoding="utf-8")
t = sub(t, "**How many independent samples?** 122 effective samples from 1.24 M pixels;",
        f"**How many independent samples?** {n1} effective samples from 1.24 M pixels "
        f"({n2} for the inverted clay map);", "SUPPLEMENTARY")
p.write_text(t, encoding="utf-8")

# final consistency sweep
import re
bad = []
for f in (root / "docs").glob("*.md"):
    txt = f.read_text(encoding="utf-8")
    for m in re.finditer(r"\b122\b|\b10,168\b|\b10168\b", txt):
        line = txt[:m.start()].count("\n") + 1
        bad.append(f"{f.name}:{line}: {txt.splitlines()[line-1].strip()[:90]}")
print("stale N_eff mentions:", bad if bad else "none")
