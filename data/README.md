# Data

## Tha Chalaep water level (Marine Department of Thailand)

* Station: Tha Chalaep, Chanthaburi. Station code and benchmark (datum) to be confirmed with the Marine Department.
* Period: 9 May 2019 to 8 October 2026, readings at about ten-minute intervals.
* Original format: exports from the Marine Department portal saved as .xls files that contain HTML tables with three columns: date (dd/mm/yyyy, Buddhist era), time (hh:mm:ss) and water level (m).
* Levels are relative to the gauge datum and not to mean sea level.

The original exports and the ten-minute CSV files (`data/raw/`, `data/processed/tachalaep_raw.csv`, `data/processed/tachalaep_screened.csv`) are not included in this repository until permission to redistribute the record has been confirmed. They are listed in `.gitignore`.

### data/processed/tachalaep_hourly_obs.csv

| Column | Unit | Description |
|---|---|---|
| t | local time (UTC+7) | start of the hour |
| obs | m | mean of the screened readings in the hour, missing where fewer than three readings exist |

### data/processed/tachalaep_hourly.csv

| Column | Unit | Description |
|---|---|---|
| t | local time (UTC+7) | start of the hour |
| obs | m | observed hourly level |
| tide | m | predicted tide from the harmonic model, including the mean level |
| resid | m | obs minus tide |
| anom | m | resid minus its 30-day running median, smoothed with a 25-hour running mean |

## Flood events (data/events/flood_events.csv)

Event dates are compiled from news reports and official warnings. Each row lists its source. The dates are to be checked against the records of the Chanthaburi Office of Disaster Prevention and Mitigation (DDPM).

## ERA5-Land and ERA5 (not included)

Created by `src/era5_download.py` in Google Colab.

| Dataset | Variables | Area (N, W, S, E) | Grid |
|---|---|---|---|
| ERA5-Land hourly | total_precipitation, surface_runoff, sub_surface_runoff, volumetric_soil_water_layer_1, volumetric_soil_water_layer_2 | 13.3, 101.7, 12.3, 102.7 | 0.1 degree |
| ERA5 hourly single levels | 10m_u_component_of_wind, 10m_v_component_of_wind, mean_sea_level_pressure, total_precipitation | 13.3, 101.7, 12.0, 102.7 | 0.25 degree |

Period: January 2019 to October 2026. ERA5-Land precipitation and runoff are accumulated from 00 UTC and are converted to hourly amounts. Precipitation and runoff are given in mm per hour, pressure in hPa. Both UTC (`time`) and Thai time (`time_ict`) are stored.

Source: Copernicus Climate Change Service (C3S) Climate Data Store, under the Licence to use Copernicus Products.
