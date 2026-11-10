"""Step 2 - synthesise the TIR emissivity cube.

TIR(lambda) = sum_m abundance_m * (1 - reflectance_m(lambda))
with endmembers from the USGS splib07 library (processed/spectra/*.npy).
This is the documented, reproducible recipe of the draft; it is synthetic,
not a measured TIR image.
"""
import numpy as np

import common as C


def main():
    truth = np.load(C.OUT / "truth_abundance.npy")
    n_bands = 200
    tir = np.zeros((n_bands,) + truth.shape[1:], dtype=np.float32)

    endmembers = {}
    for m in C.MINERALS:
        path = C.SPEC / f"{m}_TIR.npy"
        if not path.exists():
            raise FileNotFoundError(path)
        spec = np.load(path)
        mean_spec = spec if spec.ndim == 1 else np.nanmean(spec, axis=0)
        endmembers[m] = np.clip(1.0 - mean_spec, 0.5, 1.0).astype(np.float32)

    for i in range(n_bands):
        band = np.zeros(truth.shape[1:], dtype=np.float32)
        for j, m in enumerate(C.MINERALS):
            band += truth[j] * endmembers[m][i]
        tir[i] = band

    # Outside the real survey footprint the TIR cube is undefined; the loader
    # fills it with 0.5 and metrics exclude it via valid_mask.
    valid = np.isfinite(np.load(C.OUT / "gamma_cube.npy")).all(axis=0)
    tir[:, ~valid] = np.nan

    np.save(C.OUT / "tir_cube.npy", tir)
    print(f"TIR cube       : {tir.shape}  range {np.nanmin(tir):.3f}-{np.nanmax(tir):.3f}")
    print(f"invalid pixels : {(~valid).mean():.3f}")
    print("bands used     :", C.TIR_WAVELENGTHS, "um")
    print(f"saved           : {C.OUT / 'tir_cube.npy'}")


if __name__ == "__main__":
    main()
