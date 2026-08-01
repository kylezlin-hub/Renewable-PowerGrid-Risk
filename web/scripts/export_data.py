"""Export compact 2025 ERCOT data + validation metrics for the web simulator.

Reads the project's merged hourly dataset, keeps only 2025 (the year the
interactive scenario explorer scales), and writes two small JSON files into the
site's public/data folder:

  ercot_2025.json       - column-oriented hourly arrays (load, solar, wind, hour, month)
  baseline_metrics.json - risk metrics for baseline and 2.5x solar, used by the
                          browser math self-test to prove the JS port matches Python

Run from anywhere:
    python web/scripts/export_data.py

The metric definitions here mirror src/metrics.py and notebook 04 exactly so the
exported numbers are an authoritative target for the client-side JavaScript.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
MERGED_CSV = ROOT / "data" / "processed" / "hourly_load_renewable_merged.csv"
OUT_DIR = ROOT / "web" / "public" / "data"

# ---------------------------------------------------------------------------
# Constants (must match notebook 04 / src/metrics.py)
# ---------------------------------------------------------------------------
FIXED_THRESHOLD = 6033          # baseline P95 |ramp_1h|, MW
TOTAL_RAMP_CAPACITY = 23250     # estimated dispatchable ramp capacity, MW/hr
SUNSET_HOURS = [17, 18, 19, 20]
SUMMER_MONTHS = [5, 6, 7, 8, 9]

LOAD = "ERCOT.LOAD"
SOLAR = "ERCOT.PVGR.GEN"
WIND = "ERCOT.WIND.GEN"


# ---------------------------------------------------------------------------
# Metrics (mirror of src/metrics.py, plus sunset + capacity from notebook 04)
# ---------------------------------------------------------------------------
def compute_risk_metrics(df: pd.DataFrame, net_load_col: str = "NET_LOAD",
                         fixed_threshold: float | None = None) -> dict:
    df = df.copy()
    df["ramp_1h"] = df[net_load_col].diff()
    df["ramp_3h"] = df[net_load_col].diff(3)
    abs_1h = df["ramp_1h"].abs()
    abs_3h = df["ramp_3h"].abs()

    threshold = fixed_threshold if fixed_threshold is not None else abs_1h.quantile(0.95)

    return {
        "max_ramp_up": float(df.loc[df["ramp_1h"] > 0, "ramp_1h"].max()),
        "max_ramp_down": float(df.loc[df["ramp_1h"] < 0, "ramp_1h"].min()),
        "threshold_P95": float(threshold),
        "tail_probability": float((abs_1h > threshold).mean()),
        "conditional_tail": float(df.loc[abs_1h > threshold, "ramp_1h"].abs().mean()),
        "p99_ramp_1h": float(abs_1h.quantile(0.99)),
        "mean_abs_ramp_1h": float(abs_1h.mean()),
        "std_abs_ramp_1h": float(abs_1h.std()),
        "max_ramp_3h": float(abs_3h.max()),
        "p95_ramp_3h": float(abs_3h.quantile(0.95)),
        "ramp_variance_1h": float(df["ramp_1h"].var(ddof=0)),
        "ramp_variance_3h": float(df["ramp_3h"].var(ddof=0)),
    }


def sunset_metrics(df: pd.DataFrame) -> dict:
    """Max daily sunset ramp (NET_LOAD@20 - NET_LOAD@17) and days > 20 GW, May-Sep."""
    s = df[df["hour"].isin(SUNSET_HOURS) & df["month"].isin(SUMMER_MONTHS)].copy()
    ramps = []
    for _, day in s.groupby(s["datetime"].dt.date):
        day = day.sort_values("hour")
        if len(day) != 4 or not all(h in day["hour"].values for h in SUNSET_HOURS):
            continue
        nl17 = day.loc[day["hour"] == 17, "NET_LOAD"].values[0]
        nl20 = day.loc[day["hour"] == 20, "NET_LOAD"].values[0]
        ramps.append(nl20 - nl17)
    ramps = np.array(ramps, dtype=float)
    return {
        "max_sunset_ramp": float(ramps.max()) if ramps.size else 0.0,
        "days_over_20GW": int((ramps > 20000).sum()),
    }


def capacity_metrics(df: pd.DataFrame, capacity: float = TOTAL_RAMP_CAPACITY) -> dict:
    ramp = df["NET_LOAD"].diff()
    shortfall = (ramp.abs() - capacity).clip(lower=0)
    return {
        "hours_exceeding_capacity": int((shortfall > 0).sum()),
        "max_shortfall": float(shortfall.max()),
    }


def apply_scenario(df2025: pd.DataFrame, solar_mult: float, wind_mult: float) -> pd.DataFrame:
    d = df2025.copy()
    d[SOLAR] = d[SOLAR] * solar_mult
    d[WIND] = d[WIND] * wind_mult
    d["NET_LOAD"] = d[LOAD] - d[SOLAR] - d[WIND]
    return d


def scenario_summary(df2025: pd.DataFrame, solar_mult: float, wind_mult: float = 1.0) -> dict:
    d = apply_scenario(df2025, solar_mult, wind_mult)
    m = compute_risk_metrics(d, fixed_threshold=FIXED_THRESHOLD)
    m.update(sunset_metrics(d))
    m.update(capacity_metrics(d))
    total_load = d[LOAD].sum()
    m["annual_penetration"] = float((d[WIND].sum() + d[SOLAR].sum()) / total_load)
    m["solar_mult"] = solar_mult
    m["wind_mult"] = wind_mult
    return m


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    if not MERGED_CSV.exists():
        raise SystemExit(
            f"Missing {MERGED_CSV}. Run notebook 01 first to build the merged dataset."
        )

    df = pd.read_csv(MERGED_CSV)
    df["datetime"] = pd.to_datetime(df["datetime"])
    d25 = df[df["datetime"].dt.year == 2025].copy().reset_index(drop=True)
    if d25.empty:
        raise SystemExit("No 2025 rows found in merged dataset.")

    # Derive hour/month if absent (they exist in the merged file, but be safe).
    d25["hour"] = d25["datetime"].dt.hour
    d25["month"] = d25["datetime"].dt.month

    # Round the renewable/load columns to the SAME precision that ships in the
    # JSON, then compute everything from these rounded values. This guarantees the
    # browser (which reads the rounded JSON) reproduces baseline_metrics.json
    # exactly, so the client self-test is a true test of the JS port.
    for col in (LOAD, SOLAR, WIND):
        d25[col] = d25[col].round(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- Compact hourly export (column-oriented, rounded to save bytes) ---
    payload = {
        "meta": {
            "year": 2025,
            "n_hours": int(len(d25)),
            "fixed_threshold": FIXED_THRESHOLD,
            "capacity_mw_per_hr": TOTAL_RAMP_CAPACITY,
            "sunset_hours": SUNSET_HOURS,
            "summer_months": SUMMER_MONTHS,
            "columns": ["timestamp", "hour", "month", "load", "solar", "wind"],
            "source": "data/processed/hourly_load_renewable_merged.csv",
        },
        "timestamp": [t.isoformat() for t in d25["datetime"]],
        "hour": d25["hour"].astype(int).tolist(),
        "month": d25["month"].astype(int).tolist(),
        "load": [round(float(x), 1) for x in d25[LOAD]],
        "solar": [round(float(x), 1) for x in d25[SOLAR]],
        "wind": [round(float(x), 1) for x in d25[WIND]],
    }
    data_path = OUT_DIR / "ercot_2025.json"
    data_path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")

    # --- Validation targets for the browser math self-test ---
    scenarios = {
        "baseline": scenario_summary(d25, 1.0),
        "solar_1_5x": scenario_summary(d25, 1.5),
        "solar_2_0x": scenario_summary(d25, 2.0),
        "solar_2_5x": scenario_summary(d25, 2.5),
    }
    metrics_path = OUT_DIR / "baseline_metrics.json"
    metrics_path.write_text(json.dumps(scenarios, indent=2), encoding="utf-8")

    # --- Console report ---
    size_kb = data_path.stat().st_size / 1024
    print(f"Wrote {data_path}  ({size_kb:,.0f} KB, {len(d25):,} hours)")
    print(f"Wrote {metrics_path}")
    print("\nValidation targets (baseline -> 2.5x solar):")
    b, h = scenarios["baseline"], scenarios["solar_2_5x"]
    print(f"  tail probability:   {b['tail_probability']*100:5.2f}%  -> {h['tail_probability']*100:5.2f}%")
    print(f"  max 1h ramp (MW):   {b['max_ramp_up']:8,.0f}  -> {h['max_ramp_up']:8,.0f}")
    print(f"  max sunset (MW):    {b['max_sunset_ramp']:8,.0f}  -> {h['max_sunset_ramp']:8,.0f}")
    print(f"  P99 1h ramp (MW):   {b['p99_ramp_1h']:8,.0f}  -> {h['p99_ramp_1h']:8,.0f}")
    print(f"  hours > capacity:   {b['hours_exceeding_capacity']:8d}  -> {h['hours_exceeding_capacity']:8d}")
    print(f"  annual penetration: {b['annual_penetration']*100:5.1f}%  -> {h['annual_penetration']*100:5.1f}%")


if __name__ == "__main__":
    main()
