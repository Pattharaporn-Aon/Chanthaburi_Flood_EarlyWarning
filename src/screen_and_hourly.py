"""Screen the ten-minute record and build an hourly series.

Screening rules
1. Exact zeros are removed (sensor fault or data-logger placeholder).
2. Spikes are removed where a reading departs by more than 0.40 m from the
   centred two-hour rolling median.

Hourly values are the mean of the screened readings in each clock hour,
kept only where at least three readings are present.

Usage
-----
python src/screen_and_hourly.py data/processed/tachalaep_raw.csv data/processed
"""
import sys

import pandas as pd

SPIKE_M = 0.40
MIN_PER_HOUR = 3


def main(raw_csv, out_dir):
    v = pd.read_csv(raw_csv, parse_dates=["t"]).set_index("t").level_m
    n0 = len(v)
    v = v[v > 0]
    med = v.rolling("2h", center=True).median()
    spikes = (v - med).abs() > SPIKE_M
    v = v[~spikes]
    print(f"readings {n0}, zeros removed {n0 - len(v) - spikes.sum()}, spikes removed {spikes.sum()}")
    v.to_csv(f"{out_dir}/tachalaep_screened.csv")

    h = v.resample("1h").mean().where(v.resample("1h").count() >= MIN_PER_HOUR)
    h.rename("obs").to_frame().to_csv(f"{out_dir}/tachalaep_hourly_obs.csv")

    cov = v.resample("MS").count().to_frame("readings")
    cov["coverage_pct"] = (cov.readings / (cov.index.days_in_month * 144) * 100).round(1)
    cov.to_csv("results/monthly_coverage.csv")
    print(f"hourly values {h.notna().sum()} of {len(h)} ({h.isna().mean() * 100:.1f} % missing)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
