import json, pathlib, re
root = pathlib.Path(__file__).resolve().parents[2]
d = json.loads((root / 'processed' / 'autocorr.json').read_text())
for k, v in d['fields'].items():
    print('%-24s n_eff %8.1f  deff %9.0f  tau %5.1f px' % (
        k, v['n_eff'], v['design_effect'], v['integral_scale_x_px']))
print('---')
src = (root / 'code' / 'validate_pipeline.py').read_text(encoding='utf-8').splitlines()
for i, line in enumerate(src):
    if 'n_eff' in line:
        print(i + 1, line.strip())
