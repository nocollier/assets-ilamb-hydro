import re

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from shapely.geometry import Point
from tqdm import tqdm

RES = 0.25

df = gpd.read_file("Shapefile/WBD_HUC02_9505V3/WBD_HUC02_9505V3.shp")

# Logically add in the watersheds that are connected but not in the CONUS
for r, row in df[df["Name"].str.startswith("Upstream")].iterrows():

    # To which US HUC does this belong?
    match = re.search("Upstream of (.*) in (.*)", row["Name"])
    if not match:
        raise ValueError("Failed to find a match")
    parent = match.group(1)

    # Find the US HUC index and take the union of geometries
    ind = df["Name"] == parent
    ind = ind[ind].index
    df.loc[ind, "geometry"] = df.loc[ind, "geometry"].union(row["geometry"])

    # Now we don't need this row anymore
    df = df.drop(r)

# Interpolate to a fixed grid (this takes a while :/)
lat1d = np.arange(
    df.bounds.min()["miny"] - 0.6 * RES, df.bounds.max()["maxy"] + 0.6 * RES, RES
)
lon1d = np.arange(
    df.bounds.min()["minx"] - 0.6 * RES, df.bounds.max()["maxx"] + 0.6 * RES, RES
)
lon, lat = np.meshgrid(lon1d, lat1d)
ids = np.empty(lat.shape, dtype=int)
for i, j in tqdm(np.ndindex(ids.shape), total=ids.size):
    ind = df.contains(Point(lon[i, j], lat[i, j]))
    ind = ind[ind].index
    assert len(ind) <= 1
    ids[i, j] = -1 if len(ind) == 0 else ind[0]

# Create the dataset
ds = xr.DataArray(
    data=ids, dims=["lat", "lon"], coords=dict(lat=lat1d, lon=lon1d)
).to_dataset(name="ids")
ds["labels"] = df["R02"].to_list()
ds["names"] = df["Name"].str.replace(" Region", "").to_list()
ds["ids"].attrs.update(_FillValue=-1, labels="labels", names="names")
ds.to_netcdf("CONUS_HUC2.nc")

# Now create a 'global' CONUS.
ds = xr.DataArray(
    data=ids.clip(-1, 0), dims=["lat", "lon"], coords=dict(lat=lat1d, lon=lon1d)
).to_dataset(name="ids")
ds["labels"] = ["global"]
ds["names"] = ["CONUS"]
ds["ids"].attrs.update(_FillValue=-1, labels="labels", names="names")
ds.to_netcdf("CONUS.nc")
