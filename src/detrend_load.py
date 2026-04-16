"""
detrend_load.py
---------------
Remove long-term load growth from ERCOT hourly load data so the
remaining signal reflects the pure load–weather relationship.

Method
------
Primary  – Rolling-median trend (fast, no extra deps):
    A centred rolling window of 8 760 hours (~1 year) smooths out all
    intra-year seasonality, leaving only the multi-year growth trend.
    detrended_load = observed – rolling_trend + mean(rolling_trend)

Optional – STL decomposition (more rigorous, requires statsmodels):
    Pass  method="stl"  to use STL instead.

Both methods preserve the original mean level so the detrended series
remains interpretable in MW.

Inputs
------
  data/processed/hourly_load_renewable_merged.csv   (written by data_exploration.ipynb)

Outputs
-------
  data/processed/hourly_load_detrended.csv
  figures/load_detrending_diagnostic.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
FIGURES_DIR = ROOT / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

INPUT_CSV = PROCESSED_DIR / "hourly_load_renewable_merged.csv"
OUTPUT_CSV = PROCESSED_DIR / "hourly_load_detrended.csv"
PLOT_OUT = FIGURES_DIR / "load_detrending_diagnostic.png"

LOAD_COL = "ERCOT.LOAD"
DATETIME_COL = "datetime"
ANCHOR_DATE = "2025-12-31"

# Rolling window size: ~1 year of hourly data
ROLLING_WINDOW = 8760


# ---------------------------------------------------------------------------
# Trend estimators
# ---------------------------------------------------------------------------


def _anchor_level(trend: pd.Series, anchor_date: str = ANCHOR_DATE) -> float:
    """Return the mean trend level over the anchor date, with sensible fallbacks."""
    anchor_mask = trend.index.strftime("%Y-%m-%d") == anchor_date
    anchor_values = trend.loc[anchor_mask].dropna()
    if not anchor_values.empty:
        return float(anchor_values.mean())

    fallback_values = trend.loc[trend.index <= pd.Timestamp(anchor_date)].dropna()
    if not fallback_values.empty:
        return float(fallback_values.iloc[-1])

    raise ValueError(f"Could not determine anchor level for {anchor_date}.")


def _rolling_median_detrend(
    series: pd.Series, anchor_level: float
) -> tuple[pd.Series, pd.Series]:
    """
    Estimate trend as a centred rolling median over ~1 year.
    Edges are filled with the nearest valid trend value.
    Returns (trend, detrended_load anchored to anchor_level).
    """
    trend_vals = series.rolling(
        window=ROLLING_WINDOW, center=True, min_periods=ROLLING_WINDOW // 2
    ).median()
    # Forward/backward fill remaining NaNs at series edges
    trend_vals = trend_vals.ffill().bfill()
    trend = pd.Series(trend_vals.values, index=series.index, name="load_trend")
    detrended = series - trend + anchor_level
    return trend, detrended


def _stl_detrend(series: pd.Series, anchor_level: float) -> tuple[pd.Series, pd.Series]:
    """Return (trend, detrended_load) using STL (annual period, robust fit)."""
    from statsmodels.tsa.seasonal import STL

    # STL period must be odd
    stl = STL(series, period=8761, robust=True)
    result = stl.fit()
    trend = pd.Series(result.trend, index=series.index, name="load_trend")
    detrended = series - trend + anchor_level
    return trend, detrended


def _ols_detrend(series: pd.Series, anchor_level: float) -> tuple[pd.Series, pd.Series]:
    """Return (trend, detrended_load) using simple linear OLS trend."""
    t = np.arange(len(series), dtype=float)
    coeffs = np.polyfit(t, series.values, deg=1)
    trend_vals = np.polyval(coeffs, t)
    trend = pd.Series(trend_vals, index=series.index, name="load_trend")
    detrended = series - trend + anchor_level
    return trend, detrended


def detrend(df: pd.DataFrame, method: str = "rolling") -> pd.DataFrame:
    """
    Remove long-term load growth from `LOAD_COL`.

    Parameters
    ----------
    df     : DataFrame containing DATETIME_COL and LOAD_COL.
    method : "rolling" (default) | "stl" | "ols"
    """
    series = df[LOAD_COL].copy()
    series.index = df[DATETIME_COL]

    if method == "rolling":
        preview_trend = (
            series.rolling(
                window=ROLLING_WINDOW, center=True, min_periods=ROLLING_WINDOW // 2
            )
            .median()
            .ffill()
            .bfill()
        )
        anchor_level = _anchor_level(preview_trend)
    elif method == "ols":
        t = np.arange(len(series), dtype=float)
        preview_trend = pd.Series(
            np.polyval(np.polyfit(t, series.values, deg=1), t), index=series.index
        )
        anchor_level = _anchor_level(preview_trend)
    else:
        # Use a fast rolling preview to define the anchor even when final method is STL.
        preview_trend = (
            series.rolling(
                window=ROLLING_WINDOW, center=True, min_periods=ROLLING_WINDOW // 2
            )
            .median()
            .ffill()
            .bfill()
        )
        anchor_level = _anchor_level(preview_trend)

    print(f"  Anchor date      : {ANCHOR_DATE}")
    print(f"  Anchor level     : {anchor_level:,.0f} MW")

    if method == "stl":
        print("  Running STL decomposition (this may take a minute) …")
        try:
            trend, detrended = _stl_detrend(series, anchor_level)
            method_label = "STL"
            print("  STL complete.")
        except (ImportError, ModuleNotFoundError, ValueError) as exc:
            print(f"  STL failed ({exc}). Falling back to rolling-median trend.")
            trend, detrended = _rolling_median_detrend(series, anchor_level)
            method_label = "rolling-median (STL fallback)"
    elif method == "ols":
        print("  Fitting OLS linear trend …")
        trend, detrended = _ols_detrend(series, anchor_level)
        method_label = "OLS linear"
    else:
        print(f"  Computing rolling-median trend (window = {ROLLING_WINDOW} h) …")
        trend, detrended = _rolling_median_detrend(series, anchor_level)
        method_label = "rolling-median"

    out = df.copy()
    out["load_trend"] = trend.values
    out["detrended_load_mw"] = detrended.values
    out["detrend_method"] = method_label
    out["detrend_anchor_date"] = ANCHOR_DATE
    out["detrend_anchor_level_mw"] = anchor_level
    return out


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------


def _load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=[DATETIME_COL])
    df = df.sort_values(DATETIME_COL).reset_index(drop=True)
    missing = df[LOAD_COL].isna().sum()
    if missing:
        print(f"  Filling {missing} NaN load values with linear interpolation.")
        df[LOAD_COL] = df[LOAD_COL].interpolate(method="time")
    return df


# ---------------------------------------------------------------------------
# Diagnostic plot
# ---------------------------------------------------------------------------


def _plot(df: pd.DataFrame, out_path: Path) -> None:
    anchor_level = df["detrend_anchor_level_mw"].iloc[0]
    fig, axes = plt.subplots(3, 1, figsize=(16, 10), sharex=True)

    axes[0].plot(
        df[DATETIME_COL], df[LOAD_COL], lw=0.4, color="steelblue", label="Observed load"
    )
    axes[0].plot(
        df[DATETIME_COL], df["load_trend"], lw=1.5, color="tomato", label="Trend"
    )
    axes[0].set_title("ERCOT Load – Observed vs. Estimated Long-Term Growth Trend")
    axes[0].set_ylabel("MW")
    axes[0].legend(loc="upper left", fontsize=8)

    axes[1].plot(df[DATETIME_COL], df["detrended_load_mw"], lw=0.4, color="darkorange")
    axes[1].axhline(
        anchor_level,
        color="gray",
        lw=1,
        ls="--",
        label=f"12/31/2025 anchor ({anchor_level:,.0f} MW)",
    )
    axes[1].set_title("Detrended Load (growth removed, anchored to 12/31/2025 level)")
    axes[1].set_ylabel("MW")
    axes[1].legend(loc="upper left", fontsize=8)

    # Monthly mean comparison: original vs detrended
    monthly_orig = df.groupby(df[DATETIME_COL].dt.to_period("M"))[LOAD_COL].mean()
    monthly_det = df.groupby(df[DATETIME_COL].dt.to_period("M"))[
        "detrended_load_mw"
    ].mean()
    axes[2].plot(
        monthly_orig.index.to_timestamp(),
        monthly_orig.values,
        lw=1.2,
        color="steelblue",
        label="Monthly mean – original",
    )
    axes[2].plot(
        monthly_det.index.to_timestamp(),
        monthly_det.values,
        lw=1.2,
        color="darkorange",
        label="Monthly mean – detrended",
    )
    axes[2].set_title("Monthly Mean Load: Original vs. Detrended")
    axes[2].set_ylabel("MW")
    axes[2].legend(loc="upper left", fontsize=8)

    plt.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  Diagnostic plot saved → {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print(f"Loading: {INPUT_CSV}")
    df = _load_data(INPUT_CSV)
    print(
        f"  Rows: {len(df):,}  |  Date range: {df[DATETIME_COL].min().date()} – {df[DATETIME_COL].max().date()}"
    )

    print("Detrending load …")
    df = detrend(df, method="stl")  # change to "stl" or "ols" if preferred

    print(f"Saving output → {OUTPUT_CSV}")
    df.to_csv(OUTPUT_CSV, index=False)

    print("Generating diagnostic plot …")
    _plot(df, PLOT_OUT)

    orig_mean = df[LOAD_COL].mean()
    det_mean = df["detrended_load_mw"].mean()
    trend_range = df["load_trend"].max() - df["load_trend"].min()
    anchor_level = df["detrend_anchor_level_mw"].iloc[0]
    print("\nSummary")
    print(f"  Method          : {df['detrend_method'].iloc[0]}")
    print(f"  Original mean   : {orig_mean:,.0f} MW")
    print(f"  Anchor date     : {df['detrend_anchor_date'].iloc[0]}")
    print(f"  Anchor level    : {anchor_level:,.0f} MW")
    print(f"  Detrended mean  : {det_mean:,.0f} MW")
    print(f"  Trend range     : {trend_range:,.0f} MW  (total growth removed)")
    print("Done.")


if __name__ == "__main__":
    main()
