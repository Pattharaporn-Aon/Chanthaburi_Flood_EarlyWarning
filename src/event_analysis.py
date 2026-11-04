"""Water level at Tha Chalaep during recorded flood events and a spring-tide scenario.

For each event in data/events/flood_events.csv the script reports the observed
maximum, the predicted daily tidal maximum (spring or neap phase) and the peak
non-tidal anomaly. The scenario adds the observed non-tidal residual of the
event to the predicted tide shifted by up to +/-10 days, and reports the
largest total level. The superposition ignores tide-river interaction and is
therefore an upper estimate.

Usage
-----
python src/event_analysis.py
"""
import pandas as pd

o = pd.read_csv("data/processed/tachalaep_hourly.csv", parse_dates=["t"]).set_index("t")
ev = pd.read_csv("data/events/flood_events.csv", parse_dates=["start", "end"])
tide_daily_max = o.tide.resample("D").max()

rows = []
for _, e in ev.iterrows():
    w = o[e.start:e.end + pd.Timedelta("23h")]
    if w.obs.notna().sum() == 0:
        continue
    best_lag, best = 0, -9.0
    for lag in range(-10, 11):
        total = (o.tide.shift(-lag * 24)[e.start:e.end + pd.Timedelta("23h")] + w.resid).max()
        if total > best:
            best_lag, best = lag, total
    fortnight = tide_daily_max[e.start - pd.Timedelta("7D"):e.end + pd.Timedelta("7D")]
    rows.append({
        "event": e.event,
        "obs_max_m": round(w.obs.max(), 2),
        "pred_tide_daily_max_m": round(tide_daily_max[e.start:e.end].mean(), 2),
        "fortnight_tide_max_range_m": f"{fortnight.min():.2f}-{fortnight.max():.2f}",
        "anom_peak_m": round(w.anom.max(), 3),
        "spring_tide_scenario_max_m": round(best, 2),
        "scenario_shift_days": best_lag,
    })
res = pd.DataFrame(rows)
res.to_csv("results/event_summary.csv", index=False)
print(res.to_string(index=False))
print("record hourly maximum:", round(o.obs.max(), 2), "m at", o.obs.idxmax())
