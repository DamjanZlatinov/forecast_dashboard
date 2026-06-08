from pathlib import Path

import pandas as pd


def build_daily_dashboard_views(
    events_path: Path,
    output_daily_views_path: Path,
) -> pd.DataFrame:
    events = pd.read_parquet(events_path)

    if events.empty:
        raise ValueError("Input events dataframe is empty.")

    events["timestamp"] = pd.to_datetime(
        events["timestamp"],
        errors="coerce",
        format="mixed",
    )

    events = events.dropna(subset=["timestamp"])

    events["ds"] = events["timestamp"].dt.floor("D")

    daily_views = (
        events
        .groupby("ds")
        .size()
        .reset_index(name="y")
        .sort_values("ds")
    )

    full_dates = pd.DataFrame({
        "ds": pd.date_range(
            start=daily_views["ds"].min(),
            end=daily_views["ds"].max(),
            freq="D",
        )
    })

    daily_views = (
        full_dates
        .merge(daily_views, on="ds", how="left")
        .fillna({"y": 0})
    )

    daily_views["y"] = daily_views["y"].astype(int)

    output_daily_views_path.parent.mkdir(parents=True, exist_ok=True)
    daily_views.to_parquet(output_daily_views_path, index=False)

    return daily_views