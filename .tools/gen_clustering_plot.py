"""
Figure generator for Paper 1, result R6 — "Extreme ramps cluster into
multi-hour events."

Design notes
------------
* Threshold and event definition match notebook 04 exactly: an "extreme" hour
  is |Δ net load (1h)| > 6,033 MW (the 2025 baseline P95 used throughout the
  paper). Events are maximal runs of consecutive extreme hours. This reproduces
  the numbers cited in the Results worksheet (mean event duration 1.37 -> 2.36 h,
  max consecutive extreme hours 3 -> 5) so the figure is consistent with Table 1.
* Two panels, one Figure:
    (a) event-duration COMPOSITION as a 100% stacked bar. Duration bins are an
        ORDINAL magnitude, so they use a single-hue blue sequential ramp
        (light = short, dark = long) rather than categorical colors.
    (b) the two headline scalars, mean event duration and max consecutive
        extreme hours, BOTH in hours -> a single shared y-axis (no dual axis).
* Colors are documented, pre-validated values from the data-viz reference
  palette (sequential blue ramp; categorical slots 1 blue / 2 orange).
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

ROOT = Path('C:/Renewable-PowerGrid-Risk')
PROCESSED_DIR = ROOT / 'data' / 'processed'
FIGURES_DIR = ROOT / 'figures'

# --- Palette (from dataviz reference palette.md; do not eyeball-substitute) ---
SURFACE   = '#fcfcfb'
INK       = '#0b0b0b'
INK_2     = '#52514e'
MUTED     = '#898781'
GRID      = '#e1e0d9'
AXIS      = '#c3c2b7'
SEQ_BLUE  = ['#86b6ef', '#3987e5', '#1c5cab', '#0d366b']  # ordinal ramp, 1h->4+h
CAT_BLUE  = '#2a78d6'   # slot 1  -> mean duration
CAT_ORANGE = '#eb6834'  # slot 2  -> max consecutive

THRESHOLD = 6033  # MW, |1h net-load ramp|; 2025 baseline P95 (matches nb04)
MULTS  = [1.0, 1.5, 2.0, 2.5]
LABELS = ['Baseline\n(1.0×)', '1.5×\nSolar', '2.0×\nSolar', '2.5×\nSolar']
MAX_DUR = 4  # last bin is "4+"

# ----------------------------------------------------------------------------
df = pd.read_csv(PROCESSED_DIR / 'hourly_load_renewable_merged.csv', parse_dates=['datetime'])
df = df[df['datetime'].dt.year == 2025].copy().sort_values('datetime')


def event_runs(net_load):
    """Maximal runs of consecutive hours with |1h ramp| > THRESHOLD."""
    ramp = net_load.diff()
    extreme = (ramp.abs() > THRESHOLD).astype(int).values
    runs, count = [], 0
    for v in extreme:
        if v == 1:
            count += 1
        elif count > 0:
            runs.append(count)
            count = 0
    if count > 0:
        runs.append(count)
    return np.array(runs)


runs_by_mult, mean_dur, max_dur, n_events = {}, [], [], []
for m in MULTS:
    nl = df['ERCOT.LOAD'] - df['ERCOT.WIND.GEN'] - m * df['ERCOT.PVGR.GEN']
    r = event_runs(nl)
    runs_by_mult[m] = r
    mean_dur.append(r.mean())
    max_dur.append(int(r.max()))
    n_events.append(len(r))

# duration-bin shares (%) per scenario, bins 1h / 2h / 3h / 4+h
shares = np.zeros((len(MULTS), MAX_DUR))
for i, m in enumerate(MULTS):
    r = runs_by_mult[m]
    for d in range(1, MAX_DUR + 1):
        mask = (r == d) if d < MAX_DUR else (r >= d)
        shares[i, d - 1] = mask.mean() * 100

# ----------------------------------------------------------------------------
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

fig, (axA, axB) = plt.subplots(1, 2, figsize=(12.5, 5.4), gridspec_kw={'width_ratios': [1.15, 1]})
fig.patch.set_facecolor(SURFACE)
x = np.arange(len(MULTS))

# ---- Panel (a): 100% stacked event-duration composition --------------------
bin_labels = ['1 h (isolated)', '2 h', '3 h', '4+ h']
bottoms = np.zeros(len(MULTS))
for d_idx in range(MAX_DUR):
    vals = shares[:, d_idx]
    axA.bar(x, vals, 0.62, bottom=bottoms, color=SEQ_BLUE[d_idx],
            edgecolor=SURFACE, linewidth=1.6, zorder=3)
    for i, (v, b) in enumerate(zip(vals, bottoms)):
        if v >= 6:
            txt_color = 'white' if d_idx >= 2 else INK
            axA.text(x[i], b + v / 2, f'{v:.0f}', ha='center', va='center',
                     fontsize=10, fontweight='bold', color=txt_color, zorder=4)
        elif v > 0:
            # Keep tiny nonzero shares visible so rare 3h/4+h episodes are not mistaken for zero.
            label_y = min(b + v + 1.0, 99.2)
            axA.text(x[i], label_y, f'{v:.1f}', ha='center', va='bottom',
                     fontsize=8.5, fontweight='bold', color=SEQ_BLUE[d_idx], zorder=5)
    bottoms += vals

axA.set_ylabel('Share of extreme-ramp events (%)', fontsize=11)
axA.set_title('(a)  Event-duration composition', fontsize=12, fontweight='bold',
              loc='left', color=INK)
axA.set_xticks(x)
axA.set_xticklabels(LABELS, fontsize=10)
axA.set_ylim(0, 100)
axA.set_yticks(range(0, 101, 20))
axA.grid(axis='y', color=GRID, linewidth=0.8, zorder=0)
axA.set_axisbelow(True)
for s in ('top', 'right'):
    axA.spines[s].set_visible(False)
axA.spines['left'].set_color(AXIS)
axA.spines['bottom'].set_color(AXIS)

# duration legend ABOVE the panel (single row) so it never overlaps the bars
dur_handles = [Patch(facecolor=SEQ_BLUE[i], edgecolor=SURFACE, label=bin_labels[i])
               for i in range(MAX_DUR)]
axA.legend(handles=dur_handles, loc='lower left', bbox_to_anchor=(0.0, 1.02),
           ncol=4, frameon=False, fontsize=9.5, handlelength=1.1,
           columnspacing=1.2, handletextpad=0.5)

# ---- Panel (b): mean duration (bars) + max consecutive (markers), one axis --
bars = axB.bar(x, mean_dur, 0.52, color=CAT_BLUE, edgecolor=SURFACE,
               linewidth=1.0, zorder=3, label='Mean event duration')
for i, v in enumerate(mean_dur):
    axB.text(x[i], v + 0.08, f'{v:.2f} h', ha='center', va='bottom',
             fontsize=10, fontweight='bold', color=INK, zorder=5)

axB.plot(x, max_dur, color=CAT_ORANGE, linewidth=2.0, marker='o', markersize=9,
         markeredgecolor=SURFACE, markeredgewidth=1.4, zorder=4,
         label='Max consecutive extreme hours')
for i, v in enumerate(max_dur):
    axB.annotate(f'{v} h', (x[i], v), textcoords='offset points', xytext=(0, 10),
                 ha='center', fontsize=10, fontweight='bold', color=CAT_ORANGE, zorder=5)

# annotate event counts at the base so the sample size is visible
# n here means number of extreme-ramp event episodes, not number of extreme hours
for i, n in enumerate(n_events):
    axB.text(x[i], 0.12, f'{n} events', ha='center', va='bottom', fontsize=8.5,
             color='white', fontweight='bold', zorder=6)

axB.set_ylabel('Duration (consecutive hours)', fontsize=11)
axB.set_title('(b)  Event persistence', fontsize=12, fontweight='bold',
              loc='left', color=INK)
axB.set_xticks(x)
axB.set_xticklabels(LABELS, fontsize=10)
axB.set_ylim(0, 6)
axB.set_yticks(range(0, 7))
axB.grid(axis='y', color=GRID, linewidth=0.8, zorder=0)
axB.set_axisbelow(True)
for s in ('top', 'right'):
    axB.spines[s].set_visible(False)
axB.spines['left'].set_color(AXIS)
axB.spines['bottom'].set_color(AXIS)
axB.legend(loc='upper left', frameon=False, fontsize=9.5)

fig.text(0.5, -0.02,
         'Extreme hour: |1-h net-load ramp| > 6,033 MW (2025 baseline P95).  '
         'Panel (a) shows the share of event episodes in each duration bin (1 h, 2 h, 3 h, 4+ h).  '
         'Panel (b) reports mean duration and maximum consecutive duration; labels at the base are event counts.  '
         'Events are maximal runs of consecutive extreme hours; ERCOT 2025, solar-scaled.',
         ha='center', fontsize=8.5, color=MUTED)

fig.suptitle('Extreme net-load ramps cluster into longer episodes as solar penetration rises',
             fontsize=13.5, fontweight='bold', color=INK, y=1.04, x=0.5)

plt.tight_layout(w_pad=3.0)
out = FIGURES_DIR / 'extreme_ramp_clustering.png'
plt.savefig(out, dpi=300, bbox_inches='tight', facecolor=SURFACE)
print(f'Saved: {out}')
print('\nStats used (matches nb04 / R6):')
for m, md, mx, n in zip(MULTS, mean_dur, max_dur, n_events):
    print(f'  {m}x: mean={md:.2f} h  max={mx} h  n_events={n}')
