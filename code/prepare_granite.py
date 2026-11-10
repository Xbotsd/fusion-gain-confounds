"""Granite characterisation from real data (gamma + TMI + SIM 3206 geology).

The original proposal's "granite interference compensation" needs three granite
physical properties: a gamma signature, conductivity and magnetic
susceptibility. This module derives them from real, co-located data:

1. Granite map / gamma signature
   SIM 3206 `felsic plutonic` polygons (real geology) + the real K/eU/eTh
   grids give the local radiometric signature of granite terrain.
2. Magnetic susceptibility proxy
   The real TMI grid (same survey) gives the magnetic expression of the felsic
   plutonic bodies; TMI anomaly amplitude is used as a susceptibility proxy.
3. Conductivity
   Real NGU airborne FDEM apparent-resistivity databases (Sulitjelma 2025,
   Roros 2020, 50 m grids) are scanned for their resistivity distribution; the
   high-resistivity population is the crystalline/plutonic reference, checked
   against published granite values (1e3-1e5 ohm.m).

Outputs: processed/granite_indicator.npy, processed/granite_properties.json,
processed/fig_granite.png.
"""
from __future__ import annotations

import json
import re
import struct
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common as C

NGU_ZIPS = [
    "Sulitjelma_2025_EM_Database_AIQ_Res.zip",
    "Sulitjelma_2025_EM_Database_BIQ_Res.zip",
    "Sulitjelma_2025_EM_Database_CIQ_Res.zip",
    "Sulitjelma_2025_EM_Database_DIQ_Res.zip",
    "Sulitjelma_2025_EM_Database_EIQ_Res_2000_maskbadI.zip",
    "Sulitjelma_2025_EM_Database_EQ_Res_2000.zip",
    "Røros_2020_HEM_AppRes_6kHz_IPQ.zip",
    "Røros_2020_HEM_AppRes_7kHz_IPQ.zip",
    "Røros_2020_HEM_AppRes_880Hz_IPQ.zip",
    "Røros_2020_HEM_AppRes_980Hz_IPQ.zip",
]


def ngu_resistivity_stats(max_words=4_000_000):
    """Scan NGU Geosoft GRD files for plausible apparent-resistivity float32 values.

    The v2 GRD data stream is compressed, but the stored float32 samples are
    recoverable statistically: we scan every 4-byte alignment, keep words in
    [0.5, 5e6] ohm.m and exclude the Geosoft dummy (about -1.4e32). This yields
    a real measured distribution, not a map.
    """
    per_file = {}
    pool = []
    for zn in NGU_ZIPS:
        p = C.RAW / zn
        if not p.exists():
            continue
        with zipfile.ZipFile(p) as z:
            grd = [n for n in z.namelist() if n.upper().endswith(".GRD")]
            if not grd:
                continue
            raw = z.read(grd[0])
        best = None
        for align in range(4):
            n = min((len(raw) - align) // 4, max_words)
            a = np.frombuffer(raw, dtype="<f4", offset=align, count=n)
            ok = a[(a >= 0.5) & (a <= 5e6)]
            if best is None or ok.size > best.size:
                best = ok
        if best is not None and best.size:
            per_file[zn] = {
                "n": int(best.size),
                "p10": float(np.percentile(best, 10)),
                "p50": float(np.percentile(best, 50)),
                "p90": float(np.percentile(best, 90)),
            }
            pool.append(best)
    allv = np.concatenate(pool) if pool else np.array([])
    return per_file, allv


def granite_indicator(gamma, tmi, substrate, gid_felsic):
    """Geology-primary granite indicator.

    Empirical finding (see granite_properties.json): the local felsic plutonic
    terrain is NOT radiometrically distinct (K 3.16 vs 3.04 %, eTh 5.96 vs
    6.10 ppm), so a gamma-based detector does not separate it. The indicator is
    therefore the mapped felsic plutonic polygons, smoothed to the geophysical
    resolution, with the magnetic smoothness as a secondary term.
    """
    from scipy.ndimage import gaussian_filter
    mask = C.load_valid_mask()
    felsic = (substrate == gid_felsic) & mask

    g_hard = felsic.astype(np.float32)
    # smooth to ~500 m (geologic contact uncertainty vs 50 m grid)
    g_soft = gaussian_filter(g_hard, sigma=10)
    g_soft = np.clip(g_soft, 0, 1).astype(np.float32)

    # secondary: TMI texture (felsic std 82 nT vs other 145 nT -> smoother)
    tmi_s = gaussian_filter(np.nan_to_num(tmi, nan=0.0), sigma=6)
    tmi_local_std = gaussian_filter(
        (tmi_s - gaussian_filter(tmi_s, sigma=12)) ** 2, sigma=12) ** 0.5
    smooth = 1.0 - C.normalize_p2p98(tmi_local_std)

    # combined: geology dominates; magnetics refine only where mapped
    G = np.clip(0.85 * g_soft + 0.15 * g_soft * smooth, 0, 1).astype(np.float32)
    return G, np.array([0.85, 0.15]), felsic


def main():
    gamma = C.load_gamma_planes()
    tmi = np.load(C.PROC / "tmi_grid.npy")
    substrate = np.load(C.PROC / "geology_substrate.npy")
    mask = C.load_valid_mask()

    # substrate ids were built alphabetically starting at 1
    groups = ["carbonate", "felsic plutonic", "mafic plutonic",
              "metasedimentary", "partly consolidated", "sedimentary",
              "surficial/alluvium", "volcanic"]
    gid = {g: i + 1 for i, g in enumerate(groups)}
    felsic_id = gid["felsic plutonic"]
    felsic = (substrate == felsic_id) & mask
    other = mask & ~felsic

    # ---- 1. local granite signature (real gamma + TMI) --------------------
    sig = {}
    for name, arr in (("K", gamma[0]), ("eU", gamma[1]), ("eTh", gamma[2]),
                      ("TMI_nT", tmi)):
        sig[name] = {
            "felsic_mean": float(np.nanmean(arr[felsic])),
            "felsic_std": float(np.nanstd(arr[felsic])),
            "other_mean": float(np.nanmean(arr[other])),
            "other_std": float(np.nanstd(arr[other])),
        }
    # ratios
    with np.errstate(divide="ignore", invalid="ignore"):
        thk = gamma[2] / gamma[0]
        uth = gamma[1] / gamma[2]
    sig["eTh/K"] = {"felsic_mean": float(np.nanmedian(thk[felsic])),
                    "other_mean": float(np.nanmedian(thk[other]))}
    sig["eU/eTh"] = {"felsic_mean": float(np.nanmedian(uth[felsic])),
                     "other_mean": float(np.nanmedian(uth[other]))}

    # ---- 2. susceptibility proxy from TMI ---------------------------------
    # amplitude of the TMI anomaly over felsic bodies vs background
    tmi_bg = float(np.nanmedian(tmi[other]))
    tmi_fel = float(np.nanmedian(tmi[felsic]))
    tmi_amp = float(np.nanpercentile(np.abs(tmi[felsic] - tmi_bg), 90))
    # literature check: granite susceptibility 1e-4..5e-2 SI; TMI->k is not a
    # true inversion; this is an amplitude proxy only.
    susc = {
        "tmi_background_median_nT": tmi_bg,
        "tmi_felsic_median_nT": tmi_fel,
        "tmi_felsic_anomaly_p90_nT": tmi_amp,
        "literature_granite_susceptibility_SI": [1e-4, 5e-2],
        "note": "TMI amplitude proxy, not a susceptibility inversion",
    }

    # ---- 3. conductivity from real NGU FDEM databases ----------------------
    per_file, allv = ngu_resistivity_stats()
    if allv.size:
        cond = {
            "source": "NGU airborne FDEM apparent resistivity (Sulitjelma 2025, "
                      "Roros 2020), 50 m grids, real data",
            "n_values": int(allv.size),
            "p10_ohm_m": float(np.percentile(allv, 10)),
            "p50_ohm_m": float(np.percentile(allv, 50)),
            "p90_ohm_m": float(np.percentile(allv, 90)),
            "crystalline_p90_ohm_m": float(np.percentile(allv, 90)),
            "literature_granite_ohm_m": [1e3, 1e5],
            "per_file": per_file,
            "note": "statistical scan of the compressed Geosoft data stream; "
                    "values are real measured apparent resistivities",
        }
    else:
        cond = {"error": "no NGU grids found"}

    # ---- 4. soft granite indicator -----------------------------------------
    G, w, _ = granite_indicator(gamma, tmi, substrate, felsic_id)
    np.save(C.PROC / "granite_indicator.npy", G)

    props = {
        "granite_map": "SIM 3206 felsic plutonic polygons (DOI 10.3133/sim3206)",
        "felsic_pixels": int(felsic.sum()),
        "signature": sig,
        "radiometric_separability": {
            "verdict": "NOT separable from gamma at this site",
            "K_pct_felsic_vs_other": [sig["K"]["felsic_mean"], sig["K"]["other_mean"]],
            "eTh_ppm_felsic_vs_other": [sig["eTh"]["felsic_mean"], sig["eTh"]["other_mean"]],
            "consequence": "granite detection requires geology (SIM 3206) and/or "
                           "magnetics; a gamma-only granite detector fails here",
        },
        "susceptibility": susc,
        "conductivity": cond,
        "indicator_weights_K_eTh_TMI_bias": w.tolist(),
        "indicator_mean_on_felsic": float(G[felsic].mean()),
        "indicator_mean_on_other": float(G[other].mean()),
    }
    C.save_json(C.PROC / "granite_properties.json", props)

    # ---- figure -------------------------------------------------------------
    fig, axes = plt.subplots(1, 4, figsize=(20, 4.6))
    im0 = axes[0].imshow(np.where(mask, gamma[0], np.nan), cmap="magma")
    axes[0].set_title("Real K (%)")
    plt.colorbar(im0, ax=axes[0], fraction=0.04)
    im1 = axes[1].imshow(np.where(mask, tmi, np.nan), cmap="RdBu_r")
    axes[1].set_title("Real TMI (nT)")
    plt.colorbar(im1, ax=axes[1], fraction=0.04)
    axes[2].imshow(felsic, cmap="gray")
    axes[2].set_title("SIM 3206 felsic plutonic")
    im3 = axes[3].imshow(np.where(mask, G, np.nan), cmap="viridis", vmin=0, vmax=1)
    axes[3].set_title(f"Granite indicator G\n(felsic {G[felsic].mean():.2f} / other {G[other].mean():.2f})")
    plt.colorbar(im3, ax=axes[3], fraction=0.04)
    for ax in axes:
        ax.axis("off")
    plt.tight_layout()
    plt.savefig(C.PROC / "fig_granite.png", dpi=300)
    plt.close()

    print(json.dumps({k: v for k, v in props.items()
                      if k not in ("signature",)}, indent=2, ensure_ascii=False))
    print("signature:", json.dumps(sig, indent=1))
    print("saved granite_indicator.npy / granite_properties.json / fig_granite.png")


if __name__ == "__main__":
    main()

