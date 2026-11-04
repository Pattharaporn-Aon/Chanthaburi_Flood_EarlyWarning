"""Convert Marine Department water-level exports (.xls) into one CSV.

The Marine Department portal exports an HTML table saved with an .xls
extension. Each row holds a date in the Thai Buddhist calendar
(dd/mm/yyyy, B.E.), a clock time and the water level in metres.

Usage
-----
python src/parse_marine_dept.py <folder with .xls files> data/processed/tachalaep_raw.csv
"""
import glob
import re
import sys

import pandas as pd

ROW = re.compile(r"<td[^>]*>([^<]*)</td><td[^>]*>([^<]*)</td><td[^>]*>([^<]*)</td>")


def parse_file(path):
    html = open(path, encoding="utf-8", errors="replace").read()
    return ROW.findall(html)


def main(src_folder, out_csv):
    rows = []
    for f in sorted(glob.glob(f"{src_folder}/**/*.xls", recursive=True)):
        r = parse_file(f)
        print(f"{f}: {len(r)} rows")
        rows += r
    d = pd.DataFrame(rows, columns=["date_be", "time", "level_m"])
    year_ce = d.date_be.str[6:].astype(int) - 543
    d["t"] = pd.to_datetime(d.date_be.str[:6] + year_ce.astype(str) + " " + d.time,
                            format="%d/%m/%Y %H:%M:%S", errors="coerce")
    d["level_m"] = pd.to_numeric(d.level_m, errors="coerce")
    d = d.dropna(subset=["t"]).drop_duplicates("t").sort_values("t")[["t", "level_m"]]
    d.to_csv(out_csv, index=False)
    print(f"{len(d)} readings, {d.t.min()} to {d.t.max()}, exact zeros: {(d.level_m == 0).sum()}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
