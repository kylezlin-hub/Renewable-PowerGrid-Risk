from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path('C:/Renewable-PowerGrid-Risk')
PROCESSED_DIR = ROOT / 'data' / 'processed'
FIGURES_DIR = ROOT / 'figures'

df = pd.read_csv(PROCESSED_DIR / 'hourly_load_renewable_merged.csv', parse_dates=['datetime'])
df = df[df['datetime'].dt.year == 2025].copy()

THRESHOLD = 7159  # baseline P95 upward ramp

mults = [1.0, 1.5, 2.0, 2.5]
labels = ['Baseline\n(1.0×)', '1.5×\nSolar', '2.0×\nSolar', '2.5×\nSolar']

# Compute run-length distributions
all_runs = {}
for m in mults:
    nl = df['ERCOT.LOAD'] - df['ERCOT.WIND.GEN'] - m * df['ERCOT.PVGR.GEN']
    ramp = nl.diff()
    exceed = (ramp > THRESHOLD).astype(int).values
    runs = []
    count = 0
    for v in exceed:
        if v == 1:
            count += 1
        elif count > 0:
            runs.append(count)
            count = 0
    if count > 0:
        runs.append(count)
    all_runs[m] = runs

# Build duration distribution data
max_dur = 4
duration_counts = {}
for m in mults:
    runs = all_runs[m]
    counts = {}
    for d in range(1, max_dur + 1):
        if d < max_dur:
            counts[d] = len([r for r in runs if r == d])
        else:
            counts[d] = len([r for r in runs if r >= d])
    duration_counts[m] = counts

# Create figure with two panels
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))

# Panel 1: Stacked bar chart of event duration distribution (% of events)
colors_dur = ['#93c5fd', '#3b82f6', '#1d4ed8', '#1e3a5f']
dur_labels = ['1 hour', '2 hours', '3 hours', '4+ hours']

x = np.arange(len(mults))
width = 0.55

bottoms = np.zeros(len(mults))
for d_idx, d in enumerate(range(1, max_dur + 1)):
    fractions = []
    for m in mults:
        total = sum(duration_counts[m].values())
        fractions.append(duration_counts[m][d] / total * 100)
    bars = ax1.bar(x, fractions, width, bottom=bottoms,
                   color=colors_dur[d_idx], label=dur_labels[d_idx],
                   edgecolor='white', linewidth=0.5)
    # Add percentage labels for significant segments
    for i, (frac, bot) in enumerate(zip(fractions, bottoms)):
        if frac > 8:
            ax1.text(x[i], bot + frac/2, f'{frac:.0f}%',
                    ha='center', va='center', fontsize=9, fontweight='bold',
                    color='white' if d_idx >= 1 else 'black')
    bottoms += fractions

ax1.set_xlabel('Scenario', fontsize=11, fontweight='bold')
ax1.set_ylabel('Share of Extreme-Ramp Events (%)', fontsize=11, fontweight='bold')
ax1.set_title('Event Duration Distribution', fontsize=12, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(labels, fontsize=10)
ax1.legend(loc='upper left', fontsize=9.5)
ax1.set_ylim(0, 105)
ax1.grid(axis='y', alpha=0.3)

# Panel 2: Fraction of extreme hours occurring in multi-hour episodes
multi_hr_frac = []
total_events_list = []
for m in mults:
    runs = all_runs[m]
    total_hrs = sum(runs)
    multi_hrs = sum(r for r in runs if r >= 2)
    multi_hr_frac.append(multi_hrs / total_hrs * 100)
    total_events_list.append(len(runs))

bars2 = ax2.bar(x, multi_hr_frac, width, color=['#2563eb', '#f59e0b', '#dc2626', '#7c2d12'],
                edgecolor='black', linewidth=0.5)

for i, (frac, n) in enumerate(zip(multi_hr_frac, total_events_list)):
    ax2.text(x[i], frac + 2, f'{frac:.0f}%', ha='center', va='bottom',
             fontsize=11, fontweight='bold')
    ax2.text(x[i], frac/2, f'n={n}', ha='center', va='center',
             fontsize=9, color='white', fontweight='bold')

ax2.set_xlabel('Scenario', fontsize=11, fontweight='bold')
ax2.set_ylabel('Extreme Hours in Multi-Hour Episodes (%)', fontsize=11, fontweight='bold')
ax2.set_title('Fraction of Extreme Hours in\nSustained Episodes (≥2 consecutive)', fontsize=12, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(labels, fontsize=10)
ax2.set_ylim(0, 110)
ax2.axhline(y=50, color='gray', linestyle='--', alpha=0.5, linewidth=1)
ax2.grid(axis='y', alpha=0.3)

plt.suptitle('Temporal Clustering of Extreme Upward Ramp Events\n(Threshold: baseline P95 = 7,159 MW)',
             fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(FIGURES_DIR / 'extreme_ramp_clustering.png', dpi=300, bbox_inches='tight')
print('Saved: figures/extreme_ramp_clustering.png')
