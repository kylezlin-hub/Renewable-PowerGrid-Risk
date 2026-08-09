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

THRESHOLD = 23250  # estimated fleet flexibility benchmark (MW/hr)

# Build solar x wind grid (1.0 to 2.0 in 0.1 steps for both)
solar_range = np.arange(1.0, 2.55, 0.1)
wind_range = np.arange(1.0, 2.05, 0.1)

results = []

for s_mult in solar_range:
    for w_mult in wind_range:
        net_load = df['ERCOT.LOAD'] - w_mult * df['ERCOT.WIND.GEN'] - s_mult * df['ERCOT.PVGR.GEN']
        ramp_1h = net_load.diff().dropna()
        upward_ramps = ramp_1h[ramp_1h > 0]

        hours_exceeding = (upward_ramps > THRESHOLD).sum()
        max_ramp = upward_ramps.max()
        max_shortfall = max(0, max_ramp - THRESHOLD)

        results.append({
            'solar_mult': round(s_mult, 2),
            'wind_mult': round(w_mult, 2),
            'hours_exceeding': hours_exceeding,
            'max_ramp': max_ramp,
            'max_shortfall': max_shortfall,
        })

results_df = pd.DataFrame(results)

# Pivot for heatmap
pivot_hours = results_df.pivot(index='wind_mult', columns='solar_mult', values='hours_exceeding')

# Create heatmap
fig, ax = plt.subplots(figsize=(11, 7))

# Plot with imshow for smooth appearance
solar_vals = sorted(results_df['solar_mult'].unique())
wind_vals = sorted(results_df['wind_mult'].unique())
data = pivot_hours.values

im = ax.imshow(data, origin='lower', aspect='auto',
               extent=[solar_vals[0]-0.05, solar_vals[-1]+0.05,
                       wind_vals[0]-0.05, wind_vals[-1]+0.05],
               cmap='YlOrRd', interpolation='bilinear')

# Add contour lines
X, Y = np.meshgrid(solar_vals, wind_vals)
contours = ax.contour(X, Y, data, levels=[1, 10, 50, 100, 200],
                       colors='black', linewidths=1.2, alpha=0.7)
ax.clabel(contours, inline=True, fontsize=9, fmt='%d hrs')

# Mark the "first exceedance" frontier (where hours > 0 first appears)
frontier = ax.contour(X, Y, data, levels=[0.5], colors='white',
                       linewidths=2.5, linestyles='--')
ax.clabel(frontier, inline=True, fontsize=10, fmt='First exceedance')

cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Hours per Year Exceeding 23,250 MW/hr', fontsize=11)

ax.set_xlabel('Solar Multiplier', fontsize=12, fontweight='bold')
ax.set_ylabel('Wind Multiplier', fontsize=12, fontweight='bold')
ax.set_title('Flexibility-Threshold Exceedance Across Solar × Wind Space\n'
             '(Upward 1-h ramps > 23,250 MW/hr, 2025 ERCOT)',
             fontsize=13, fontweight='bold')
ax.grid(alpha=0.2, color='white')

plt.tight_layout()
plt.savefig(FIGURES_DIR / 'flexibility_exceedance_heatmap.png', dpi=300, bbox_inches='tight')
print('Saved: figures/flexibility_exceedance_heatmap.png')

# Print key stats
print(f'\nExceedance hours at key points:')
for s in [1.0, 1.5, 2.0, 2.5]:
    for w in [1.0, 1.5, 2.0]:
        row = results_df[(results_df['solar_mult'] == s) & (results_df['wind_mult'] == w)]
        if not row.empty:
            print(f'  Solar {s}x, Wind {w}x: {row.iloc[0]["hours_exceeding"]} hrs, '
                  f'max shortfall {row.iloc[0]["max_shortfall"]:.0f} MW')

# Find the frontier: minimum solar multiplier where exceedance first appears at each wind level
print(f'\nFirst-exceedance frontier (solar mult where hours > 0):')
for w in wind_vals:
    subset = results_df[results_df['wind_mult'] == w]
    first_exceed = subset[subset['hours_exceeding'] > 0]['solar_mult'].min()
    print(f'  Wind {w:.1f}x: solar threshold = {first_exceed:.2f}x')
