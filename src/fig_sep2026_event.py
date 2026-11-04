"""Figure: Tha Chalaep water level during the September 2026 flood.

Upper panel: observed hourly level and predicted tide.
Lower panel: de-seasoned non-tidal anomaly and the daily maximum predicted tide.

Usage
-----
python src/fig_sep2026_event.py
"""
import matplotlib
import matplotlib.dates as md
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")
o = pd.read_csv("data/processed/tachalaep_hourly.csv", parse_dates=["t"]).set_index("t")
w = o["2026-09-15":"2026-10-08"]

fig, ax = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True, dpi=150)
ax[0].plot(w.index, w.obs, color="#1f4e79", lw=1, label="Observed")
ax[0].plot(w.index, w.tide, color="#999999", lw=1, ls="--", label="Predicted tide")
ax[0].axvspan(pd.Timestamp("2026-09-27"), pd.Timestamp("2026-09-28"), color="#d62728", alpha=.12,
              label="Red alert (27 Sep)")
ax[0].set_ylabel("Water level (m, gauge datum)")
ax[0].legend(loc="upper left", fontsize=8, ncol=3)
ax[0].set_title("Tha Chalaep, Chanthaburi: September 2026 flood", fontsize=11)
ax[1].plot(w.index, w.anom, color="#d62728", lw=1.3)
ax[1].axhline(0, color="k", lw=.5)
ax[1].set_ylabel("Non-tidal anomaly (m)", color="#d62728")
ax2 = ax[1].twinx()
dm = o.tide.resample("D").max()["2026-09-15":"2026-10-08"]
ax2.step(dm.index, dm.values, where="post", color="#7f7f7f", lw=1)
ax2.set_ylabel("Daily max predicted tide (m)", color="#7f7f7f")
ax[1].xaxis.set_major_locator(md.DayLocator(interval=3))
ax[1].xaxis.set_major_formatter(md.DateFormatter("%d %b"))
fig.tight_layout()
fig.savefig("figures/tachalaep_sep2026.png")
fig.savefig("figures/tachalaep_sep2026.pdf")
print("saved figures/tachalaep_sep2026.png and .pdf")
