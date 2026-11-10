"""Count pipeline stages and scripts from run_all.py."""
import re
import pathlib

src = pathlib.Path(r"D:\A_MineralProspecting\code\run_all.py").read_text(
    encoding="utf-8")
blocks = re.findall(r'^    "(\w+)": \[(.*?)\],', src, re.M | re.S)
total = 0
for name, body in blocks:
    n = len(re.findall(r'"[a-z0-9_]+\.py"', body))
    total += n
    print(f"  {name}: {n}")
print("all-stage scripts:", total)
m = re.search(r"ALL_STAGES = \((.*?)\)", src, re.S)
full = re.findall(r'"(\w+)"', m.group(1))
print("ALL_STAGES:", full)
print("script count in ALL_STAGES:",
      sum(len(re.findall(r'"[a-z0-9_]+\.py"',
                         dict((k, b) for k, b in blocks)[s]))
          for s in full))
