#!/usr/bin/env bash
# Usage: bash run_all.sh <folder with Marine Department .xls files>
set -e
python src/parse_marine_dept.py "$1" data/processed/tachalaep_raw.csv
python src/screen_and_hourly.py data/processed/tachalaep_raw.csv data/processed
python src/harmonic_analysis.py data/processed/tachalaep_hourly_obs.csv data/processed/tachalaep_hourly.csv
python src/event_analysis.py
python src/fig_sep2026_event.py
