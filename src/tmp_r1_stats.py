import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path('C:/Renewable-PowerGrid-Risk')
df = pd.read_csv(ROOT / 'data/processed/hourly_load_renewable_merged.csv', parse_dates=['datetime'])
df = df[df['datetime'].dt.year == 2025].copy()
df['hour'] = df['datetime'].dt.hour
df['month'] = df['datetime'].dt.month

# Net load ramp
df['ramp_1h'] = df['NET_LOAD'].diff()

# Seasons
def get_season(m):
    if m in [12, 1, 2]: return 'Winter'
    elif m in [3, 4, 5]: return 'Spring'
    elif m in [6, 7, 8]: return 'Summer'
    else: return 'Fall'

df['season'] = df['month'].apply(get_season)

# Upward ramps only
up = df[df['ramp_1h'] > 0].copy()

# Mean upward ramp by hour
hourly_mean = up.groupby('hour')['ramp_1h'].mean()
print('=== Mean upward 1h ramp by hour (top 6) ===')
print(hourly_mean.nlargest(6).round(0))

# Peak sunset hours
sunset_mean = up[up['hour'].isin([17,18,19,20])]['ramp_1h'].mean()
non_sunset_mean = up[~up['hour'].isin([17,18,19,20])]['ramp_1h'].mean()
print(f'\nMean upward ramp, sunset (17-20): {sunset_mean:.0f} MW')
print(f'Mean upward ramp, non-sunset: {non_sunset_mean:.0f} MW')
print(f'Ratio: {sunset_mean/non_sunset_mean:.1f}x')

# By season
season_mean = up.groupby('season')['ramp_1h'].mean()
print('\n=== Mean upward ramp by season ===')
print(season_mean.round(0))

# Sunset-hour mean by season
sunset_season = up[up['hour'].isin([17,18,19,20])].groupby('season')['ramp_1h'].mean()
print('\n=== Mean upward ramp in sunset window by season ===')
print(sunset_season.round(0))

# What fraction of extreme ramps (>P95) occur in sunset window?
threshold = up['ramp_1h'].quantile(0.95)
extreme = up[up['ramp_1h'] > threshold]
frac_sunset = extreme['hour'].isin([17,18,19,20]).mean()
print(f'\nAll-hours upward P95 threshold: {threshold:.0f} MW')
print(f'Fraction of P95 exceedances in sunset window (17-20): {frac_sunset*100:.1f}%')

# Winter vs other seasons for sunset ramps
winter_sunset = up[(up['hour'].isin([17,18,19,20])) & (up['season']=='Winter')]['ramp_1h']
summer_sunset = up[(up['hour'].isin([17,18,19,20])) & (up['season']=='Summer')]['ramp_1h']
fall_sunset = up[(up['hour'].isin([17,18,19,20])) & (up['season']=='Fall')]['ramp_1h']
spring_sunset = up[(up['hour'].isin([17,18,19,20])) & (up['season']=='Spring')]['ramp_1h']
print(f'\nMean sunset upward ramp by season:')
print(f'  Winter: {winter_sunset.mean():.0f} MW (max: {winter_sunset.max():.0f} MW)')
print(f'  Spring: {spring_sunset.mean():.0f} MW (max: {spring_sunset.max():.0f} MW)')
print(f'  Summer: {summer_sunset.mean():.0f} MW (max: {summer_sunset.max():.0f} MW)')
print(f'  Fall:   {fall_sunset.mean():.0f} MW (max: {fall_sunset.max():.0f} MW)')

# Peak hour
peak_hour = hourly_mean.idxmax()
peak_val = hourly_mean.max()
print(f'\nPeak hour: {peak_hour}:00, mean upward ramp = {peak_val:.0f} MW')
