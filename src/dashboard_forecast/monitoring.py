import json
from pathlib import Path

import pandas as pd


def create_monitoring_report(
    events_path: Path,
    daily_views_path: Path,
    validation_predictions_path: Path,
    metrics_path: Path,
    output_report_path: Path,
) -> dict:
    events = pd.read_parquet(events_path)
    daily_views = pd.read_parquet(daily_views_path)
    validation_predictions = pd.read_parquet(validation_predictions_path)

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    events["timestamp"] = pd.to_datetime(
        events["timestamp"],
        errors="coerce",
        format="mixed",
    )

    daily_views["ds"] = pd.to_datetime(
        daily_views["ds"],
        errors="coerce",
        format="mixed",
    )

    validation_predictions["ds"] = pd.to_datetime(
        validation_predictions["ds"],
        errors="coerce",
        format="mixed",
    )

    latest_7d_avg = daily_views.tail(7)["y"].mean()
    previous_28d_avg = daily_views.iloc[-35:-7]["y"].mean()

    if previous_28d_avg > 0:
        latest_vs_previous_change = (
            latest_7d_avg - previous_28d_avg
        ) / previous_28d_avg
    else:
        latest_vs_previous_change = 0.0

    validation_predictions["absolute_error"] = (
        validation_predictions["y"] - validation_predictions["yhat"]
    ).abs()

    alerts = []

    if metrics.get("mae", 0) > 60:
        alerts.append("MAE is above threshold.")

    if metrics.get("coverage", 1) < 0.50:
        alerts.append("Prediction interval coverage is below threshold.")

    if latest_vs_previous_change < -0.40:
        alerts.append(
            "Latest 7-day average views dropped more than 40% compared to previous 28 days."
        )

    report = {
        "data_monitoring": {
            "event_rows": int(len(events)),
            "daily_rows": int(len(daily_views)),
            "date_min": str(daily_views["ds"].min().date()),
            "date_max": str(daily_views["ds"].max().date()),
            "total_views": int(daily_views["y"].sum()),
            "unique_users": int(events["user"].nunique()),
            "unique_dashboards": int(events["dashboard_id"].nunique()),
            "latest_7d_avg_views": round(float(latest_7d_avg), 4),
            "previous_28d_avg_views": round(float(previous_28d_avg), 4),
            "latest_vs_previous_change": round(float(latest_vs_previous_change), 4),
        },
        "model_monitoring": {
            "validation_rows": int(len(validation_predictions)),
            "mae": round(float(metrics.get("mae")), 4),
            "rmse": round(float(metrics.get("rmse")), 4),
            "coverage": round(float(metrics.get("coverage")), 4),
            "mean_validation_absolute_error": round(
                float(validation_predictions["absolute_error"].mean()), 4
            ),
            "max_validation_absolute_error": round(
                float(validation_predictions["absolute_error"].max()), 4
            ),
        },
        "alerts": alerts,
        "status": "warning" if alerts else "ok",
    }

    output_report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    return report