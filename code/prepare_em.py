"""Step 3 - synthesise the EM apparent-resistivity cube.

Recipe (the draft's final generator, seed 12345):
  log10(rho_k) = log10(layer median_k)
                 + 0.50 * (0.55 * clay_z * exp(-depth/250)
                           + 0.55 * independent_field
                           + 0.35 * layer_noise)
40 layers, 0-600 m; layer statistics from the Wisconsin AEM survey 2022.
The result is a controlled correlated field, not a measured EM section.
"""
import numpy as np
from scipy.ndimage import gaussian_filter

import common as C

A_CLAY, A_INDEP, A_NOISE = 0.55, 0.55, 0.35
SCALE = 0.50
SEED = 12345


def standardize(x):
    return (x - x.mean()) / (x.std() + 1e-6)


def main():
    clay = np.load(C.OUT / "clay_prior.npy").astype(np.float32)
    clay_z = standardize(clay)

    med = np.load(C.ASSETS / "em_layer_medians.npy")
    top = np.load(C.ASSETS / "em_dep_top.npy")
    bot = np.load(C.ASSETS / "em_dep_bot.npy")
    valid_m = np.isfinite(med)
    med = np.interp(np.arange(len(med)), np.arange(len(med))[valid_m], med[valid_m])

    rng = np.random.default_rng(SEED)
    h, w = clay.shape
    indep_z = standardize(gaussian_filter(rng.normal(0, 1, (h, w)), sigma=25))

    cube = np.zeros((len(med), h, w), dtype=np.float32)
    for k in range(len(med)):
        depth = (top[k] + bot[k]) / 2.0
        base = np.log10(med[k])
        depth_factor = np.exp(-depth / 250.0)
        noise_z = standardize(gaussian_filter(rng.normal(0, 1, (h, w)), sigma=15))
        log_rho_z = (
            A_CLAY * clay_z * depth_factor
            + A_INDEP * indep_z
            + A_NOISE * noise_z
        )
        cube[k] = np.clip(10 ** (base + SCALE * log_rho_z), 1.0, 10000.0)

    np.save(C.OUT / "em_cube.npy", cube)
    print(f"EM cube        : {cube.shape}  {cube.min():.1f}-{cube.max():.1f} ohm.m")
    print(f"layers         : {top[0]:.2f}-{bot[-1]:.2f} m, median {np.median(med):.1f} ohm.m")
    for k in (0, 10, 20, 30, 39):
        corr = np.corrcoef(clay.ravel(), -cube[k].ravel())[0, 1]
        print(f"  layer {k:2d} ({0.5*(top[k]+bot[k]):6.1f} m): corr(clay, -rho) = {corr:.3f}")
    print(f"saved           : {C.OUT / 'em_cube.npy'}")


if __name__ == "__main__":
    main()
