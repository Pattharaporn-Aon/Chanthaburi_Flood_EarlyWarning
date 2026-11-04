"""Hourly ERA5-Land and ERA5 download from the Copernicus Climate Data Store (run in Google Colab).

Reads the CDS API token from Colab Secrets (name CDS_KEY), downloads month by month
with six requests queued at once, skips months already on Drive, then de-accumulates
ERA5-Land precipitation and runoff and writes one hourly grid per dataset.
"""
# ERA5-Land and ERA5 hourly download and processing for the Tha Chalaep flood-warning study
# 2. Settings
import os
from google.colab import userdata
CDS_KEY = userdata.get("CDS_KEY")   # stored in Colab Secrets

OUT = "/content/drive/MyDrive/ThaChalaep_FloodWarning/era5_raw"
os.makedirs(f"{OUT}/era5land", exist_ok=True)
os.makedirs(f"{OUT}/era5", exist_ok=True)

START = (2019, 1)
END   = (2026, 10)          # change to the latest month needed

AREA_LAND = [13.3, 101.7, 12.3, 102.7]   # N, W, S, E  (Chanthaburi basin with margin)
AREA_SEA  = [13.3, 101.7, 12.0, 102.7]   # extended south to include sea cells off the river mouth

VARS_LAND = ["total_precipitation", "surface_runoff", "sub_surface_runoff",
             "volumetric_soil_water_layer_1", "volumetric_soil_water_layer_2"]
VARS_ERA5 = ["10m_u_component_of_wind", "10m_v_component_of_wind",
             "mean_sea_level_pressure", "total_precipitation"]

with open(os.path.expanduser("~/.cdsapirc"), "w") as f:
    f.write(f"url: https://cds.climate.copernicus.eu/api\nkey: {CDS_KEY}\n")

# 3. Download month by month (resumable)
import cdsapi, calendar, zipfile, shutil, time

HOURS = [f"{h:02d}:00" for h in range(24)]

def months(start, end):
    y, m = start
    while (y, m) <= end:
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1

def fetch(dataset, variables, area, y, m, folder):
    target = f"{folder}/{y}{m:02d}.nc"
    if os.path.exists(target) or os.path.isdir(target.replace('.nc', '')):
        return "skip"
    ndays = calendar.monthrange(y, m)[1]
    req = {
        "variable": variables,
        "year": str(y), "month": f"{m:02d}",
        "day": [f"{d:02d}" for d in range(1, ndays + 1)],
        "time": HOURS,
        "area": area,
        "data_format": "netcdf",
        "download_format": "unarchived",
    }
    if dataset == "reanalysis-era5-single-levels":
        req["product_type"] = ["reanalysis"]
    tmp = target + ".part"
    client().retrieve(dataset, req, tmp)
    # ERA5 may return a zip holding separate files for instantaneous and accumulated variables
    if zipfile.is_zipfile(tmp):
        d = target.replace('.nc', '')
        os.makedirs(d, exist_ok=True)
        with zipfile.ZipFile(tmp) as z:
            z.extractall(d)
        os.remove(tmp)
    else:
        shutil.move(tmp, target)
    return "ok"

# Parallel download: several requests wait in the CDS queue at the same time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
_local = threading.local()
def client():
    if not hasattr(_local, "c"):
        _local.c = cdsapi.Client(quiet=True, progress=False)
    return _local.c

def fetch_safe(job):
    ds, vs, ar, sub, y, m = job
    msg = ""
    for attempt in range(3):
        try:
            return job, fetch(ds, vs, ar, y, m, f"{OUT}/{sub}")
        except Exception as e:
            msg = str(e)
            if "not available" in msg.lower() or "no data" in msg.lower():
                return job, "not released"
            time.sleep(30)
    return job, "error: " + msg[:150]

jobs = [(ds, vs, ar, sub, y, m) for y, m in months(START, END)
        for ds, vs, ar, sub in [("reanalysis-era5-land", VARS_LAND, AREA_LAND, "era5land"),
                                ("reanalysis-era5-single-levels", VARS_ERA5, AREA_SEA, "era5")]]
log = []
done = 0
with ThreadPoolExecutor(max_workers=6) as ex:
    futs = [ex.submit(fetch_safe, j) for j in jobs]
    for f in as_completed(futs):
        (ds, vs, ar, sub, y, m), status = f.result()
        done += 1
        print(f"[{done}/{len(jobs)}] {sub} {y}-{m:02d} {status}", flush=True)
        if status.startswith("error"):
            log.append((sub, y, m))
print("failed:", log)

# 4. Combine monthly files into one hourly grid per dataset
import glob, numpy as np, pandas as pd, xarray as xr

def open_month(path):
    files = [path] if path.endswith('.nc') else sorted(glob.glob(f"{path}/*.nc"))
    ds = xr.merge([xr.open_dataset(f) for f in files], compat="override")
    if "valid_time" in ds.dims:
        ds = ds.rename({"valid_time": "time"})
    drop = [v for v in ["number", "expver"] if v in ds.coords or v in ds.data_vars]
    return ds.drop_vars(drop, errors="ignore")

def open_all(folder):
    items = sorted([p for p in glob.glob(f"{folder}/*") if not p.endswith(".part")])
    ds = xr.concat([open_month(p) for p in items], dim="time")
    ds = ds.sortby("time")
    _, idx = np.unique(ds["time"].values, return_index=True)
    return ds.isel(time=idx)

def deaccumulate(da):
    # Convert ERA5-Land daily-accumulated values to hourly amounts
    hourly = da.diff("time")
    hourly = xr.concat([da.isel(time=[0]) * np.nan, hourly], dim="time")
    first_hour = da["time"].dt.hour == 1
    hourly = xr.where(first_hour, da, hourly)
    # a gap in time makes the difference invalid
    step = da["time"].diff("time") / np.timedelta64(1, "h")
    step = xr.concat([xr.DataArray([1.0], dims="time", coords={"time": da["time"][:1]}), step], dim="time")
    hourly = hourly.where((step == 1) | first_hour)
    return hourly.clip(min=0)

land = open_all(f"{OUT}/era5land")
for v in ["tp", "sro", "ssro"]:
    land[v] = deaccumulate(land[v]) * 1000.0
    land[v].attrs["units"] = "mm per hour"
era5 = open_all(f"{OUT}/era5")
era5["tp"] = era5["tp"] * 1000.0
era5["tp"].attrs["units"] = "mm per hour"
era5["msl"] = era5["msl"] / 100.0
era5["msl"].attrs["units"] = "hPa"

for ds in (land, era5):
    ds.coords["time_ict"] = ("time", (pd.to_datetime(ds["time"].values) + pd.Timedelta(hours=7)).values)

FINAL = "/content/drive/MyDrive/ThaChalaep_FloodWarning/era5_processed"
os.makedirs(FINAL, exist_ok=True)
land.to_netcdf(f"{FINAL}/era5land_hourly_grid.nc")
era5.to_netcdf(f"{FINAL}/era5_hourly_grid.nc")
print(land)
print(era5)

# 5. Quick checks
t0, t1 = str(land.time.values[0])[:16], str(land.time.values[-1])[:16]
print("ERA5-Land", t0, "to", t1, "| grid", land.sizes["latitude"], "x", land.sizes["longitude"])
print("ERA5     ", str(era5.time.values[0])[:16], "to", str(era5.time.values[-1])[:16],
      "| grid", era5.sizes["latitude"], "x", era5.sizes["longitude"])

# missing hours
full = pd.date_range(land.time.values[0], land.time.values[-1], freq="h")
print("missing ERA5-Land hours:", len(full) - land.sizes["time"])

# box-mean rainfall and runoff around the September 2026 flood (Thai time)
box = land[["tp", "sro", "ssro"]].mean(["latitude", "longitude"]).to_dataframe()
box.index = pd.to_datetime(box.index) + pd.Timedelta(hours=7)
print(box.loc["2026-09-20":"2026-09-30"].resample("D").sum().round(1))

# ERA5-Land and ERA5 rainfall should be close, because ERA5-Land is driven by ERA5
e = era5["tp"].sel(latitude=slice(13.3, 12.3)).mean(["latitude", "longitude"]).to_series()
e.index = pd.to_datetime(e.index) + pd.Timedelta(hours=7)
cmp = pd.DataFrame({"era5land": box["tp"].resample("D").sum(), "era5": e.resample("D").sum()}).dropna()
print("daily correlation ERA5-Land vs ERA5:", round(cmp.corr().iloc[0, 1], 3))
