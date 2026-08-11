"""
Figure 1 for Paper 1 — Representative ERCOT duck-curve day.

Shows load, wind generation, solar generation, and net load over 24 hours on
the summer 2025 day with the largest sunset ramp (NET_LOAD@21h − NET_LOAD@17h).
The 17:00–21:00 sunset window is shaded and annotated.

Output: figures/duck_curve_representative_day.png
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = Path('C:/Renewable-PowerGrid-Risk')
DATA = ROOT / 'data' / 'processed' / 'hourly_load_renewable_merged.csv'
FIGURES = ROOT / 'figures'

SURFACE   = '#fcfcfb'
INK       = '#0b0b0b'
INK_2     = '#52514e'
MUTED     = '#898781'
GRID      = '#e1e0d9'
AXIS      = '#c3c2b7'

CLR_LOAD  = '#2a78d6'
CLR_WIND  = '#1baf7a'
CLR_SOLAR = '#eda100'
CLR_NET   = '#eb6834'
CLR_SHADE = '#e1e0d9'

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Segoe UI', 'DejaVu Sans', 'Arial'],
    'figure.facecolor': SURFACE,
    'axes.facecolor': SURFACE,
    'axes.edgecolor': AXIS,
    'axes.labelcolor': INK_2,
    'text.color': INK,
    'xtick.color': INK_2,
    'ytick.color': INK_2,
})

df = pd.read_csv(DATA, parse_dates=['datetime'])
df['hour'] = df['datetime'].dt.hour
df['date'] = df['datetime'].dt.date

summer25 = df[(df['datetime'].dt.year == 2025) &
              (df['datetime'].dt.month.isin([5, 6, 7, 8, 9]))].copy()

pivot = summer25.pivot_table(index='date', columns='hour', values='NET_LOAD')
pivot['sunset_ramp'] = pivot[21] - pivot[17]
best_date = pivot['sunset_ramp'].idxmax()

day = df[df['date'] == best_date].sort_values('hour').copy()

print(f'Selected day: {best_date}')
print(f'  Sunset ramp (NL@21 − NL@17): {pivot.loc[best_date, "sunset_ramp"]:,.0f} MW')
print(f'  Peak solar: {day["ERCOT.PVGR.GEN"].max():,.0f} MW')
print(f'  Peak wind:  {day["ERCOT.WIND.GEN"].max():,.0f} MW')
print(f'  Peak load:  {day["ERCOT.LOAD"].max():,.0f} MW')

fig, ax = plt.subplots(figsize=(10, 5.5))
fig.patch.set_facecolor(SURFACE)

ax.axvspan(17, 21, color=CLR_SHADE, alpha=0.45, zorder=0,
           label='Sunset window (17:00–21:00)')

ax.plot(day['hour'], day['ERCOT.LOAD'] / 1000, color=CLR_LOAD, linewidth=2.4,
        marker='o', markersize=5, markeredgecolor=SURFACE, markeredgewidth=1,
        label='System load', zorder=3)

ax.fill_between(day['hour'], 0, day['ERCOT.WIND.GEN'] / 1000,
                color=CLR_WIND, alpha=0.18, zorder=1)
ax.plot(day['hour'], day['ERCOT.WIND.GEN'] / 1000, color=CLR_WIND, linewidth=2.0,
        marker='s', markersize=4, markeredgecolor=SURFACE, markeredgewidth=1,
        label='Wind generation', zorder=3)

ax.fill_between(day['hour'], 0, day['ERCOT.PVGR.GEN'] / 1000,
                color=CLR_SOLAR, alpha=0.25, zorder=2)
ax.plot(day['hour'], day['ERCOT.PVGR.GEN'] / 1000, color=CLR_SOLAR, linewidth=2.0,
        marker='D', markersize=4, markeredgecolor=SURFACE, markeredgewidth=1,
        label='Solar generation', zorder=3)

ax.plot(day['hour'], day['NET_LOAD'] / 1000, color=CLR_NET, linewidth=2.8,
        marker='o', markersize=6, markeredgecolor=SURFACE, markeredgewidth=1.2,
        label='Net load', zorder=4)

nl_17 = day.loc[day['hour'] == 17, 'NET_LOAD'].iloc[0] / 1000
nl_21 = day.loc[day['hour'] == 21, 'NET_LOAD'].iloc[0] / 1000
ramp_gw = nl_21 - nl_17

ax.annotate('',
            xy=(21, nl_21), xytext=(21, nl_17),
            arrowprops=dict(arrowstyle='<->', color=INK_2, lw=1.8),
            zorder=5)
ax.text(21.4, (nl_17 + nl_21) / 2,
        f'+{ramp_gw:.1f} GW\nsunset ramp',
        fontsize=10, fontweight='bold', color=INK_2,
        va='center', ha='left')

ax.text(19.5, nl_17 - 3,
        'Rapid net-load ramp\nas solar declines',
        fontsize=9.5, color=MUTED, ha='center', va='top',
        fontstyle='italic')

ax.set_xlabel('Hour of day', fontsize=11)
ax.set_ylabel('Power (GW)', fontsize=11)
ax.set_xticks(range(0, 24))
ax.set_xticklabels([f'{h}:00' if h % 3 == 0 else '' for h in range(24)],
                    fontsize=9)
ax.set_xlim(-0.5, 23.5)
ax.set_ylim(bottom=0)

ax.grid(axis='y', color=GRID, linewidth=0.8, alpha=0.7)
ax.set_axisbelow(True)
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)

ax.legend(loc='upper left', frameon=False, fontsize=9.5)

fig.suptitle(
    f'Load, renewable generation, and net load on a representative ERCOT summer day ({best_date})',
    fontsize=12, fontweight='bold', color=INK, y=0.98)

fig.text(0.5, -0.02,
         'Net load = system load \u2212 wind \u2212 solar. The shaded 17:00\u201321:00 window marks the period '
         'when declining solar output forces a rapid upward transition in net load.',
         ha='center', fontsize=8.5, color=MUTED)

plt.tight_layout(rect=[0, 0.02, 1, 0.95])
out = FIGURES / 'duck_curve_representative_day.png'
plt.savefig(out, dpi=300, bbox_inches='tight', facecolor=SURFACE)
print(f'\nSaved: {out}')
