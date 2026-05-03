import pandas as pd

## Define RISK metrics
## In this analysis, I choose these 4 to measure RISK: Maximum Ramp, Tail Probability (95%),
## Conditional Tail Expectation (CVaR-like), 3-hour Ramp Magnitude


def compute_risk_metrics(df, net_load_col="NET_LOAD", fixed_threshold=None):

    df = df.copy()
    df["ramp_1h"] = df[net_load_col].diff()
    df["ramp_3h"] = df[net_load_col].diff(3)
    abs_ramp_1h = df["ramp_1h"].abs()
    abs_ramp_3h = df["ramp_3h"].abs()

    # Core 1-hour ramp risk metrics
    max_ramp_up = df[df["ramp_1h"] > 0]["ramp_1h"].max()
    max_ramp_down = df[df["ramp_1h"] < 0]["ramp_1h"].min()
    if fixed_threshold is None:
        threshold = abs_ramp_1h.quantile(0.95)
    else:
        threshold = fixed_threshold

    tail_prob = (abs_ramp_1h > threshold).mean()
    conditional_tail = df.loc[abs_ramp_1h > threshold, "ramp_1h"].abs().mean()

    # Additional risk metrics
    p99_ramp_1h = abs_ramp_1h.quantile(0.99)
    mean_abs_ramp_1h = abs_ramp_1h.mean()
    std_abs_ramp_1h = abs_ramp_1h.std()

    # 3-hour ramp metrics
    max_ramp_3h = abs_ramp_3h.max()
    p95_ramp_3h = abs_ramp_3h.quantile(0.95)

    # Ramp Variance
    ramp_variance_1h = df["ramp_1h"].var(ddof=0)
    ramp_variance_3h = df["ramp_3h"].var(ddof=0)
    return {
        "max_ramp_up": max_ramp_up,
        "max_ramp_down": max_ramp_down,
        "threshold_P95": threshold,
        "tail_probability": tail_prob,
        "conditional_tail": conditional_tail,
        "p99_ramp_1h": p99_ramp_1h,
        "mean_abs_ramp_1h": mean_abs_ramp_1h,
        "std_abs_ramp_1h": std_abs_ramp_1h,
        "max_ramp_3h": max_ramp_3h,
        "p95_ramp_3h": p95_ramp_3h,
        "ramp_variance_1h": ramp_variance_1h,
        "ramp_variance_3h": ramp_variance_3h,
    }


# Category 1: Magnitude Metrics (max_ramp_up, max_ramp_down, max_ramp_3h)
# What they tell us: The absolute physical limits of the system.
# Category 2: Distribution Metrics (mean_abs_ramp_1h, std_abs_ramp_1h, p95_ramp_3h)
# What they tell us: The "day-to-day" volatility. If these rise, the grid becomes more expensive to operate even if it doesn't fail.
# Category 3: Tail Risk Metrics (threshold_P95, tail_probability, conditional_tail, p99_ramp_1h)
# What they tell us: The "Black Swan" events. These are the metrics that lead to blackouts
