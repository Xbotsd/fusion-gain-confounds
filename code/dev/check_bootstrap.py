"""Check that the two block-bootstrap implementations agree on the same inputs."""
import importlib.util
import pathlib
import sys

import numpy as np

root = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "code"))
import common as C  # noqa: E402


def load(name):
    spec = importlib.util.spec_from_file_location(name, root / "code" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


import json
x = np.load(root / "processed" / "kf_main_abundance.npy")
print("kf_main_abundance shape", x.shape)
