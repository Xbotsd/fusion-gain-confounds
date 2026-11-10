"""Rasterise the USGS SIM 3206 surficial geologic map onto the analysis grid.

This is the independent target of the paper: it is never derived from gamma,
TIR or EM.  The map's polygon attribute PTYPE encodes the substrate after
'/' or '-'; substrates are grouped into eight classes.

Input  : raw/sim3206_database/.../SIM3206_gdb.mdb (downloaded on first run from
         https://pubs.usgs.gov/sim/3206/sim3206_database.zip)
Output : processed/geology_substrate.npy  int16, value = group index + 1, 0 = unmapped
         processed/geology_groups.json    group names, counts, source, DOI
"""
from __future__ import annotations

import urllib.request
import warnings
import zipfile

import numpy as np
from osgeo import gdal, ogr

import common as C

warnings.filterwarnings("ignore", category=FutureWarning)
ogr.DontUseExceptions()

MDB = C.RAW / "sim3206_database" / "sim3206_database" / "SIM3206_gdb.mdb"
URL = "https://pubs.usgs.gov/sim/3206/sim3206_database.zip"


def ensure_db():
    if MDB.exists():
        return
    zpath = C.RAW / "sim3206_database.zip"
    C.RAW.mkdir(parents=True, exist_ok=True)
    print(f"downloading {URL}")
    urllib.request.urlretrieve(URL, zpath)
    with zipfile.ZipFile(zpath) as z:
        z.extractall(C.RAW / "sim3206_database")


def substrate_group(ptype: str) -> str:
    s = ptype.split("/")[-1]
    s = s.split("-")[-1]
    s = s.split("+")[0].strip().lower()
    if s in {"fpg", "fp"}:
        return "felsic plutonic"
    if s in {"mv", "fv"}:
        return "volcanic"
    if s == "ca":
        return "carbonate"
    if s == "pc":
        return "partly consolidated"
    if s == "mr":
        return "metasedimentary"
    if s == "mp":
        return "mafic plutonic"
    if s in {"sl", "ss"}:
        return "sedimentary"
    return "surficial/alluvium"


def main():
    ensure_db()
    ds = ogr.Open(str(MDB))
    src = ds.GetLayerByName("ivanpah_polygon")
    srs = src.GetSpatialRef()
    mem = ogr.GetDriverByName("Memory").CreateDataSource("geo")
    lyr = mem.CreateLayer("poly", srs, ogr.wkbUnknown)
    lyr.CreateField(ogr.FieldDefn("GID", ogr.OFTInteger))
    groups = sorted({substrate_group(f.GetField("PTYPE")) for f in src})
    gid = {g: i + 1 for i, g in enumerate(groups)}
    src.ResetReading()
    for f in src:
        feat = ogr.Feature(lyr.GetLayerDefn())
        feat.SetField("GID", gid[substrate_group(f.GetField("PTYPE"))])
        feat.SetGeometry(f.GetGeometryRef().Clone())
        lyr.CreateFeature(feat)
        feat = None

    kds = gdal.Open(str(C.RAW / "K.gxf"))
    gt = kds.GetGeoTransform()
    w, h = kds.RasterXSize, kds.RasterYSize
    rst = gdal.GetDriverByName("MEM").Create("", w, h, 1, gdal.GDT_Int16)
    rst.SetGeoTransform(gt)
    rst.SetProjection(srs.ExportToWkt())
    gdal.RasterizeLayer(rst, [1], lyr, options=["ATTRIBUTE=GID"])
    buf = rst.ReadRaster(0, 0, w, h, buf_type=gdal.GDT_Int16)
    arr = np.frombuffer(buf, dtype=np.int16).reshape(h, w).copy()
    np.save(C.OUT / "geology_substrate.npy", arr)

    survey = C.load_valid_mask()
    counts = {g: int(((arr == gid[g]) & survey).sum()) for g in groups}
    C.save_json(C.OUT / "geology_groups.json", {
        "source": "USGS SIM 3206 surficial geologic map, Ivanpah 30x60' quadrangle",
        "doi": "10.3133/sim3206", "url": URL,
        "groups": groups, "pixels_on_survey": counts,
        "unmapped_on_survey": int(((arr == 0) & survey).sum()),
        "grid_geotransform": list(gt),
    })
    for g in groups:
        print(f"{g:22s} {counts[g]:8d} px on survey")
    print("saved geology_substrate.npy / geology_groups.json")


if __name__ == "__main__":
    main()
