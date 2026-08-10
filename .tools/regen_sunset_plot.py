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

sunset_hours = [17, 18, 19, 20]
summer_months = [5, 6, 7, 8, 9]

df_sunset = df[
    df['hour'].isin(sunset_hours) &
    df['month'].isin(summer_months)
].copy()

daily_sunset = []
for date, day_df in df_sunset.groupby(df_sunset['datetime'].dt.date):
    day_df = day_df.sort_values('hour')
    if len(day_df) != 4 or not all(h in day_df['hour'].values for h in sunset_hours):
        continue
    nl_17 = day_df[day_df['hour']==17]['NET_LOAD'].values[0]
    nl_20 = day_df[day_df['hour']==20]['NET_LOAD'].values[0]
    wind_avg = day_df['ERCOT.WIND.GEN'].mean()
    load_avg = day_df['ERCOT.LOAD'].mean()
    daily_sunset.append({
        'date': date,
        'sunset_ramp_3h': nl_20 - nl_17,
        'wind_avg_MW': wind_avg,
        'peak_solar_penetration': day_df['ERCOT.PVGR.GEN'].max() / load_avg,
    })
daily_sunset = pd.DataFrame(daily_sunset)

z = np.polyfit(daily_sunset['peak_solar_penetration'], daily_sunset['sunset_ramp_3h'], 2)
p = np.poly1d(z)

fig, ax = plt.subplots(figsize=(10, 8))

scatter = ax.scatter(
    daily_sunset['peak_solar_penetration'] * 100,
    daily_sunset['sunset_ramp_3h'],
    c=daily_sunset['wind_avg_MW'],
    cmap='RdYlGn',
    s=55,
    alpha=0.6,
    edgecolors='black',
    linewidths=0.5
)

x_trend = np.linspace(0, 0.55, 200)
ax.plot(x_trend * 100, p(x_trend), 'r--', linewidth=2.5, label='2nd-order polynomial fit')

ax.set_xlim(0, 55)
ax.set_xlabel('Peak Solar Penetration (% of Load)', fontsize=13, fontweight='bold')
ax.set_ylabel('Sunset Ramp 17h to 20h (MW)', fontsize=13, fontweight='bold')
ax.set_title('Nonlinear Relationship: Solar Penetration vs Sunset Ramping Requirement',
             fontsize=14, fontweight='bold')
ax.grid(alpha=0.3)
ax.legend(fontsize=11)

cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Average Wind Output (MW)', fontsize=11)

plt.tight_layout()
plt.savefig(FIGURES_DIR / 'sunset_ramp_vs_solar_penetration.png', dpi=300, bbox_inches='tight')
print('Saved updated figure.')
print(f'Coefficients: a={z[0]:.2f}, b={z[1]:.2f}, c={z[2]:.2f}')
