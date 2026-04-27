import pandas as pd

## Define RISK metrics
## In this analysis, I choose these 4 to measure RISK: Maximum Ramp, Tail Probability (95%),
## Conditional Tail Expectation (CVaR-like), 3-hour Ramp Magnitude


def compute_risk_metrics(df, fixed_threshold=None):

    df = df.copy()
    df["ramp_1h"] = df["NET_LOAD"].diff()
    df["ramp_3h"] = df["NET_LOAD"].diff(3)
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
    }
