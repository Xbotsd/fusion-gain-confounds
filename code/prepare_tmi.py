"""Resample the real Ivanpah TMI grid onto the gamma analysis grid.

TMI.gxf is (1777, 1078); the gamma cubes are (1772, 1075). Both are 50 m grids
of the same survey; this module reads both geotransforms and warps TMI onto the
gamma grid with GDAL (ReadRaster to avoid gdal_array).
"""
from __future__ import annotations

import numpy as np
from osgeo import gdal

import common as C

gdal.UseExceptions()


def geotransform(path):
    ds = gdal.Open(str(path))
    return ds.GetGeoTransform(), ds.RasterXSize, ds.RasterYSize


def resample_tmi() -> np.ndarray:
    src = gdal.Open(str(C.RAW / "TMI.gxf"))
    ref = gdal.Open(str(C.RAW / "K.gxf"))
    gt = ref.GetGeoTransform()
    w, h = ref.RasterXSize, ref.RasterYSize
    dst = gdal.GetDriverByName("MEM").Create("", w, h, 1, gdal.GDT_Float32)
    dst.SetGeoTransform(gt)
    dst.SetProjection(ref.GetProjection())
    gdal.ReprojectImage(src, dst, src.GetProjection(), ref.GetProjection(),
                        gdal.GRA_Bilinear)
    buf = dst.GetRasterBand(1).ReadRaster(0, 0, w, h, buf_type=gdal.GDT_Float32)
    return np.frombuffer(buf, dtype=np.float32).reshape(h, w).copy()


def main():
    tmi = resample_tmi()
    mask = C.load_valid_mask()
    print("resampled TMI", tmi.shape,
          "range %.1f..%.1f nT" % (tmi.min(), tmi.max()))
    print("on valid: mean %.1f std %.1f nT" % (tmi[mask].mean(), tmi[mask].std()))
    np.save(C.PROC / "tmi_grid.npy", tmi)
    print("saved processed/tmi_grid.npy")


if __name__ == "__main__":
    main()
