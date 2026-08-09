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
df['hour'] = df['datetime'].dt.hour

# Restrict to sunset hours (17, 18, 19, 20)
sunset_hours = [17, 18, 19, 20]
df_sunset = df[df['hour'].isin(sunset_hours)].copy()

# Compute baseline P95 from 2025 sunset-hour upward ramps
baseline_net = df_sunset['ERCOT.LOAD'] - df_sunset['ERCOT.WIND.GEN'] - df_sunset['ERCOT.PVGR.GEN']
baseline_ramp = baseline_net.diff().dropna()
baseline_ramp = baseline_ramp[baseline_ramp > 0]
FIXED_THRESHOLD = baseline_ramp.quantile(0.95)
print(f'Computed 2025 baseline P95 (sunset upward ramps): {FIXED_THRESHOLD:.0f} MW')

solar_multipliers = [1.0, 1.5, 2.0, 2.5]
labels = ['Baseline (1.0×)', '1.5× Solar', '2.0× Solar', '2.5× Solar']
colors = ['#2563eb', '#f59e0b', '#dc2626', '#7c2d12']

fig, ax = plt.subplots(figsize=(10, 7))

tail_probs = []

for mult, label, color in zip(solar_multipliers, labels, colors):
    net_load = df_sunset['ERCOT.LOAD'] - df_sunset['ERCOT.WIND.GEN'] - mult * df_sunset['ERCOT.PVGR.GEN']
    ramp_1h = net_load.diff().dropna()
    ramp_1h = ramp_1h[ramp_1h > 0]

    sorted_ramps = np.sort(ramp_1h.values)[::-1]
    exceedance = np.arange(1, len(sorted_ramps) + 1) / len(sorted_ramps)

    ax.plot(sorted_ramps, exceedance, color=color, linewidth=2.2, label=label)

    tail_prob = (ramp_1h > FIXED_THRESHOLD).mean()
    tail_probs.append(tail_prob)

ax.axvline(x=FIXED_THRESHOLD, color='black', linestyle='--', linewidth=1.5, alpha=0.7)
ax.text(FIXED_THRESHOLD + 200, 0.35, f'Fixed threshold\n({FIXED_THRESHOLD:.0f} MW)',
        fontsize=10, ha='left', va='center', style='italic')

for i, (prob, color, label) in enumerate(zip(tail_probs, colors, labels)):
    ax.plot(FIXED_THRESHOLD, prob, 'o', color=color, markersize=9, zorder=5)
    offset_y = 0.008 if i < 2 else -0.008
    ax.annotate(f'{prob*100:.1f}%', xy=(FIXED_THRESHOLD, prob),
                xytext=(FIXED_THRESHOLD - 2500, prob + offset_y),
                fontsize=9.5, fontweight='bold', color=color,
                arrowprops=dict(arrowstyle='->', color=color, lw=1.2))

ax.set_xlabel('Upward Net-Load Ramp (MW)', fontsize=12, fontweight='bold')
ax.set_ylabel('Exceedance Probability', fontsize=12, fontweight='bold')
ax.set_title('Tail-Risk Escalation: Sunset-Hour (17:00–20:00) Ramp Exceedance',
             fontsize=13, fontweight='bold')
ax.set_xlim(0, 40000)
ax.set_ylim(0, 0.50)
ax.legend(fontsize=11, loc='upper right')
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(FIGURES_DIR / 'tail_exceedance_by_scenario.png', dpi=300, bbox_inches='tight')
print('Saved: figures/tail_exceedance_by_scenario.png')
print(f'Tail probabilities at {FIXED_THRESHOLD:.0f} MW: {[f"{p*100:.1f}%" for p in tail_probs]}')
