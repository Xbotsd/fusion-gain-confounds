"""Step 1 - real gamma cube, alteration proxy and the TIR-generation truth.

Real input : raw/K.gxf, raw/eU.gxf, raw/eTh.gxf  (USGS Ivanpah survey, 50 m)
Outputs    : gamma_cube.npy, clay_prior.npy, truth_abundance.npy,
             valid_mask.npy, ratio_*.npy

`truth_abundance` is the abundance field used to synthesise TIR in
prepare_tir.py (the draft's "0.4K+0.2U" recipe).  It is *not* an independent
geological truth; docs/DATA_PROVENANCE.md spells this out.
"""
import numpy as np

import common as C


def main():
    C.OUT.mkdir(parents=True, exist_ok=True)
    gamma = C.load_gamma_planes()
    if np.isnan(gamma).all():
        raise RuntimeError("gamma grids are empty")
    np.save(C.OUT / "gamma_cube.npy", gamma.astype(np.float32))

    prior = C.clay_prior_from_gamma(gamma)
    np.save(C.OUT / "clay_prior.npy", prior)

    valid = np.isfinite(gamma).all(axis=0)
    np.save(C.OUT / "valid_mask.npy", valid)

    k, u, th = (C.normalize_p2p98(gamma[i]) for i in range(3))
    raw = {
        "Quartz": 0.4 * k + 0.2 * u,
        "Feldspar": 0.3 * k + 0.3 * (1.0 - u),
        "Clay": 0.3 * k + 0.3 * th,
        "Calcite": 0.2 * u * (1.0 - k),
        "Dolomite": 0.2 * th * (1.0 - k),
    }
    total = sum(raw.values()) + 1e-6
    truth = np.stack([raw[m] / total for m in C.MINERALS]).astype(np.float32)
    truth[:, ~valid] = np.nan
    np.save(C.OUT / "truth_abundance.npy", truth)

    eps = 1e-6
    for name, arr in {
        "ratio_K_eU": gamma[0] / (gamma[1] + eps),
        "ratio_K_eTh": gamma[0] / (gamma[2] + eps),
        "ratio_eU_eTh": gamma[1] / (gamma[2] + eps),
    }.items():
        np.save(C.OUT / f"{name}.npy", arr.astype(np.float32))

    print(f"grid            : {gamma.shape[1]} x {gamma.shape[2]} @ 50 m")
    print(f"valid pixels    : {valid.mean():.3f}")
    for i, name in enumerate(("K [%]", "eU [ppm]", "eTh [ppm]")):
        v = gamma[i][valid]
        print(f"{name:12s}   : median {np.nanmedian(v):8.3f}  p2-p98 "
              f"{np.nanpercentile(v, 2):8.3f} - {np.nanpercentile(v, 98):8.3f}")
    print(f"clay_prior      : mean {prior.mean():.4f}  >0.55 {(prior > 0.55).mean():.4f}")
    print(f"truth clay      : mean {np.nanmean(truth[C.TARGET]):.4f}")
    print(f"saved           : {C.OUT}")


if __name__ == "__main__":
    main()
