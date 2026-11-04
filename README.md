# Flood early warning for Chanthaburi from the Tha Chalaep tide gauge

Code and processed data for a flood early-warning study of Chanthaburi, Eastern Thailand. The study combines the Marine Department water-level record at Tha Chalaep with ERA5-Land and ERA5 reanalysis data. Floods in Chanthaburi city are most severe when river runoff arrives during a high tide and the river cannot drain to the sea. The study separates the predictable tide from the non-tidal signal and estimates the probability that the water level exceeds warning thresholds.



## Status

| Stage | Status |
|---|---|
| Tha Chalaep record: parsing, screening, hourly series | done |
| Harmonic analysis, non-tidal residual and anomaly | done |
| Flood-event table and spring-tide scenario | done (event dates to be checked against DDPM records) |
| ERA5-Land and ERA5 hourly download | running |
| Basin averages and combined hourly table | next |
| Probabilistic warning model and hindcast evaluation | planned |

## Main results so far

* 373,349 readings at about ten-minute intervals from 9 May 2019 to 8 October 2026. The hourly series has 4.9 % missing hours.
* The tide is strongly diurnal (form factor 4.54, K1 0.46 m, O1 0.31 m, M2 0.12 m). The harmonic model explains 94.4 % of the hourly variance.
* During the September 2026 flood the non-tidal anomaly rose by about 0.3 m within 24 hours from the evening of 24 September and stayed near +0.15 m until 28 September. Low waters remained 0.13 to 0.23 m above the predicted tide.
* The September 2026 flood coincided with neap tides. The same non-tidal signal on spring tides gives about 3.90 m at the gauge against the observed 3.23 m and close to the hourly record of 4.05 m (7 December 2025).
* The largest non-tidal anomalies occur from December to February during the northeast monsoon. A warning rule based on the gauge level alone would therefore raise false alarms, which motivates the use of rainfall, runoff and wind.

## Repository layout

```
data/
  raw/          Marine Department exports (not included, see data/README.md)
  processed/    tachalaep_hourly.csv and tachalaep_hourly_obs.csv
  events/       flood_events.csv
  era5/         ERA5-Land and ERA5 hourly grids (not included, created by src/era5_download.py)
src/            analysis scripts, run in the order listed below
notebooks/      Colab notebook for the ERA5 download
results/        tables produced by the scripts
figures/        figures produced by the scripts
```

## How to reproduce

```bash
pip install -r requirements.txt
python src/parse_marine_dept.py <folder with .xls files> data/processed/tachalaep_raw.csv
python src/screen_and_hourly.py data/processed/tachalaep_raw.csv data/processed
python src/harmonic_analysis.py data/processed/tachalaep_hourly_obs.csv data/processed/tachalaep_hourly.csv
python src/event_analysis.py
python src/fig_sep2026_event.py
```

`run_all.sh` runs the same steps. The ERA5 download needs a Copernicus Climate Data Store account, an API token and acceptance of the *Licence to use Copernicus Products*. `src/era5_download.py` is written for Google Colab and reads the token from Colab Secrets under the name `CDS_KEY`.

## Files

| File | Content |
|---|---|
| `src/parse_marine_dept.py` | Converts the Marine Department .xls exports (HTML tables, Buddhist-era dates) to one CSV |
| `src/screen_and_hourly.py` | Removes exact zeros and spikes, builds the hourly series and the monthly coverage table |
| `src/harmonic_analysis.py` | UTide harmonic fit, non-tidal residual, de-seasoned anomaly and summary statistics |
| `src/event_analysis.py` | Water level, tidal phase and spring-tide scenario for each flood event |
| `src/fig_sep2026_event.py` | Figure of the September 2026 flood |
| `src/era5_download.py` | Hourly ERA5-Land and ERA5 download from CDS, de-accumulation and conversion to Thai time |
| `data/processed/tachalaep_hourly.csv` | Hourly observed level, predicted tide, residual and anomaly (m) |
| `data/events/flood_events.csv` | Flood events with dates, area and source |
| `results/harmonic_summary.csv` | Variance explained, form factor and principal amplitudes |
| `results/constituents.csv` | Amplitudes and Greenwich phases of all fitted constituents |
| `results/monthly_coverage.csv` | Number of readings and coverage per month |
| `results/event_summary.csv` | Event table with the spring-tide scenario |
| `figures/tachalaep_sep2026.png` | September 2026 flood figure |

## Data sources

* Water level: Marine Department of Thailand, Tha Chalaep station, Chanthaburi. Levels are relative to the gauge datum.
* ERA5-Land and ERA5: Copernicus Climate Change Service (C3S) Climate Data Store. Contains modified Copernicus Climate Change Service information 2026.

## Author

Pattharaporn Thongnim, Department of Mathematics, Faculty of Science, Burapha University. ORCID 0000-0001-8904-3979.

## Licence

Code: MIT licence. Data remain under the terms of their providers.
