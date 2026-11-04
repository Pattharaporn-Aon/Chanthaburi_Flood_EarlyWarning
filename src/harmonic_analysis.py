"""Harmonic analysis, non-tidal residual and de-seasoned anomaly.

* UTide ordinary least squares fit with nodal corrections to the hourly series.
* resid = observed - predicted tide.
* anom  = resid minus its 30-day centred running median, smoothed with a
  25-hour centred mean. This removes the seasonal mean-level cycle and the
  remaining tidal energy, leaving events of one to several days such as
  river floods and wind set-up.

Usage
-----
python src/harmonic_analysis.py data/processed/tachalaep_hourly_obs.csv data/processed/tachalaep_hourly.csv
"""
import sys
import warnings

import numpy as np
import pandas as pd
import utide

warnings.filterwarnings("ignore")
LAT = 12.5  # approximate latitude used for nodal corrections


def main(hourly_csv, out_csv):
    h = pd.read_csv(hourly_csv, parse_dates=["t"]).set_index("t").obs
    ok = h.notna().values
    coef = utide.solve(h.index[ok], h.values[ok], lat=LAT, method="ols",
                       conf_int="none", trend=False, nodal=True, verbose=False)
    tide = utide.reconstruct(h.index, coef, verbose=False).h
    out = pd.DataFrame({"obs": h, "tide": tide})
    out["resid"] = out.obs - out.tide
    base = out.resid.rolling("30D", center=True, min_periods=24 * 10).median()
    out["anom"] = (out.resid - base).rolling("25h", center=True, min_periods=18).mean()
    out.to_csv(out_csv)

    const = pd.DataFrame({"name": coef.name, "amplitude_m": coef.A, "phase_deg": coef.g})
    const.sort_values("amplitude_m", ascending=False).to_csv("results/constituents.csv", index=False)
    a = dict(zip(coef.name, coef.A))
    form = (a["K1"] + a["O1"]) / (a["M2"] + a["S2"])
    explained = 1 - np.nanvar(out.resid) / np.nanvar(out.obs)
    summary = pd.Series({"variance_explained": round(explained, 4), "form_factor": round(form, 2),
                         "K1_m": round(a["K1"], 3), "O1_m": round(a["O1"], 3),
                         "M2_m": round(a["M2"], 3), "S2_m": round(a["S2"], 3),
                         "resid_sd_m": round(np.nanstd(out.resid), 3),
                         "anom_p99_m": round(out.anom.quantile(.99), 3)})
    summary.to_csv("results/harmonic_summary.csv", header=["value"])
    print(summary.to_string())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
