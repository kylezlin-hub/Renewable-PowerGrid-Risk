"""
Figure generator for Paper 1, result R6 — "Renewable-driven risk patterns
persisted across three historical weather years and under amplified load stress."

Two-panel figure:
  (a) Tail probability vs solar scaling (1.0×–2.5×) with one line per
      normalized year (2023, 2024, 2025). Shows tight tracking = consistent
      solar-driven response; small interannual spread.
  (b) Tail probability vs weather-strength multiplier (0×–3×) for baseline
      and 2.5× solar. Shows nearly flat lines = weather is secondary.

Data sources:
  - data/processed/multi_year_solar_scaling_sweep.csv
  - data/processed/weather_strength_sweep_dominance.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path('C:/Renewable-PowerGrid-Risk')
PROCESSED_DIR = ROOT / 'data' / 'processed'
FIGURES_DIR = ROOT / 'figures'

# --- Palette (consistent with other paper figures) ---
SURFACE   = '#fcfcfb'
INK       = '#0b0b0b'
INK_2     = '#52514e'
MUTED     = '#898781'
GRID      = '#e1e0d9'
AXIS      = '#c3c2b7'

YEAR_COLORS = {2023: '#1f77b4', 2024: '#2ca02c', 2025: '#d62728'}
YEAR_LABELS = {2023: '2023 (P98 heat summer)', 2024: '2024', 2025: '2025'}
SCENARIO_COLORS = {'baseline': '#2a78d6', '2.5x_solar': '#d62728'}
SCENARIO_LABELS = {'baseline': 'Baseline (1.0× solar)', '2.5x_solar': '2.5× solar'}

# --- Load data ---
sweep_df = pd.read_csv(PROCESSED_DIR / 'multi_year_solar_scaling_sweep.csv')
weather_df = pd.read_csv(PROCESSED_DIR / 'weather_strength_sweep_dominance.csv')

# --- Figure setup ---
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

fig, (axA, axB) = plt.subplots(1, 2, figsize=(13, 5.5))
fig.patch.set_facecolor(SURFACE)

# ---- Panel (a): Tail probability vs solar scaling, by year ----
solar_scalings = sorted(sweep_df['Solar Scaling'].unique())

for year in [2023, 2024, 2025]:
    sub = sweep_df[sweep_df['Year'] == year].sort_values('Solar Scaling')
    axA.plot(sub['Solar Scaling'], sub['Tail Probability (%)'],
             marker='o', markersize=8, linewidth=2.4,
             color=YEAR_COLORS[year], label=YEAR_LABELS[year],
             markeredgecolor=SURFACE, markeredgewidth=1.2, zorder=3)

# Shade the interannual spread
for s in solar_scalings:
    vals = sweep_df[sweep_df['Solar Scaling'] == s]['Tail Probability (%)']
    axA.fill_between([s - 0.05, s + 0.05], vals.min(), vals.max(),
                     alpha=0.08, color='gray', zorder=1)

# Annotate the spread vs signal
axA.annotate('',
             xy=(2.5, sweep_df[sweep_df['Solar Scaling'] == 2.5]['Tail Probability (%)'].min()),
             xytext=(2.5, sweep_df[sweep_df['Solar Scaling'] == 1.0]['Tail Probability (%)'].max()),
             arrowprops=dict(arrowstyle='<->', color=INK_2, lw=1.5))
mid_y = (sweep_df[sweep_df['Solar Scaling'] == 2.5]['Tail Probability (%)'].min() +
          sweep_df[sweep_df['Solar Scaling'] == 1.0]['Tail Probability (%)'].max()) / 2
axA.text(2.58, mid_y, '15–17 pp\nsolar signal', fontsize=9, color=INK_2, va='center')

# Annotate interannual spread at 2.5×
spread_at_25 = sweep_df[sweep_df['Solar Scaling'] == 2.5]['Tail Probability (%)']
axA.annotate(f'~{spread_at_25.max() - spread_at_25.min():.0f} pp\nspread',
             xy=(2.35, spread_at_25.mean()), fontsize=8.5, color=MUTED,
             ha='center', va='center',
             bbox=dict(boxstyle='round,pad=0.3', facecolor=SURFACE, edgecolor=AXIS, alpha=0.9))

axA.set_xlabel('Solar Scaling Factor', fontsize=11)
axA.set_ylabel('Tail Probability (%)', fontsize=11)
axA.set_title('(a)  Solar-scaling response across normalized years',
              fontsize=11.5, fontweight='bold', loc='left', color=INK)
axA.set_xticks(solar_scalings)
axA.set_xticklabels([f'{x:.1f}×' for x in solar_scalings], fontsize=10)
axA.set_ylim(0, 28)
axA.grid(axis='y', color=GRID, linewidth=0.8, alpha=0.7)
axA.set_axisbelow(True)
for s in ('top', 'right'):
    axA.spines[s].set_visible(False)
axA.legend(loc='upper left', frameon=False, fontsize=9.5)

# ---- Panel (b): Tail probability vs weather strength ----
for scenario in ['baseline', '2.5x_solar']:
    sub = weather_df[weather_df['Scenario'] == scenario].sort_values('Weather Strength')
    axB.plot(sub['Weather Strength'], sub['Tail Probability (%)'],
             marker='o', markersize=8, linewidth=2.4,
             color=SCENARIO_COLORS[scenario], label=SCENARIO_LABELS[scenario],
             markeredgecolor=SURFACE, markeredgewidth=1.2, zorder=3)

# Annotate the tiny weather effect at 2.5× solar
w_base = weather_df[(weather_df['Scenario'] == '2.5x_solar') & (weather_df['Weather Strength'] == 0.0)]['Tail Probability (%)'].iloc[0]
w_max = weather_df[(weather_df['Scenario'] == '2.5x_solar') & (weather_df['Weather Strength'] == 3.0)]['Tail Probability (%)'].iloc[0]
axB.annotate(f'+{w_max - w_base:.2f} pp\n(4.3% of solar effect)',
             xy=(3.0, w_max), xytext=(2.2, w_max + 2.5),
             fontsize=9, color=SCENARIO_COLORS['2.5x_solar'], fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=SCENARIO_COLORS['2.5x_solar'], lw=1.2),
             ha='center')

# Baseline annotation
b_base = weather_df[(weather_df['Scenario'] == 'baseline') & (weather_df['Weather Strength'] == 0.0)]['Tail Probability (%)'].iloc[0]
b_max = weather_df[(weather_df['Scenario'] == 'baseline') & (weather_df['Weather Strength'] == 3.0)]['Tail Probability (%)'].iloc[0]
axB.annotate(f'+{b_max - b_base:.2f} pp',
             xy=(3.0, b_max), xytext=(2.2, b_max + 2.0),
             fontsize=9, color=SCENARIO_COLORS['baseline'], fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=SCENARIO_COLORS['baseline'], lw=1.2),
             ha='center')

axB.set_xlabel('Weather-Effect Strength Multiplier', fontsize=11)
axB.set_ylabel('Tail Probability (%)', fontsize=11)
axB.set_title('(b)  Weather perturbation effect',
              fontsize=11.5, fontweight='bold', loc='left', color=INK)
axB.set_xticks([0, 0.5, 1.0, 2.0, 3.0])
axB.set_xticklabels(['0×', '0.5×', '1×', '2×', '3×'], fontsize=10)
axB.set_ylim(0, 28)
axB.grid(axis='y', color=GRID, linewidth=0.8, alpha=0.7)
axB.set_axisbelow(True)
for s in ('top', 'right'):
    axB.spines[s].set_visible(False)
axB.legend(loc='upper left', frameon=False, fontsize=9.5)

# --- Caption and suptitle ---
fig.text(0.5, -0.03,
         'Panel (a): 2023/2024 normalized to 2025 system level (solar peak-ratio, wind peak-ratio, mean-load ratio).  '
         'Panel (b): 2023 heat-year temperature anomaly applied to 2025 load at varying strengths.',
         ha='center', fontsize=8.5, color=MUTED, wrap=True)

fig.suptitle('Solar scaling had a larger effect on ramping risk than interannual weather variability',
             fontsize=13, fontweight='bold', color=INK, y=1.03)

plt.tight_layout(w_pad=3.5)
out = FIGURES_DIR / 'r6_robustness_combined.png'
plt.savefig(out, dpi=300, bbox_inches='tight', facecolor=SURFACE)
print(f'Saved: {out}')

# Print key stats for verification
print('\n--- Panel (a) key stats ---')
for year in [2023, 2024, 2025]:
    sub = sweep_df[sweep_df['Year'] == year]
    base = sub[sub['Solar Scaling'] == 1.0]['Tail Probability (%)'].iloc[0]
    high = sub[sub['Solar Scaling'] == 2.5]['Tail Probability (%)'].iloc[0]
    print(f'  {year}: {base:.1f}% -> {high:.1f}% (Δ = {high-base:.1f} pp)')

print(f'\n--- Panel (b) key stats ---')
print(f'  2.5x solar, weather 0->3: {w_base:.2f}% -> {w_max:.2f}% (Δ = {w_max-w_base:.2f} pp)')
print(f'  Baseline, weather 0->3: {b_base:.2f}% -> {b_max:.2f}% (Δ = {b_max-b_base:.2f} pp)')
