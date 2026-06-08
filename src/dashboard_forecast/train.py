import json
from pathlib import Path

import numpy as np
import pandas as pd
from prophet import Prophet
from prophet.serialize import model_to_json
from sklearn.metrics import mean_absolute_error, mean_squared_error


def calculate_metrics(actual, predicted) -> dict:
    actual = np.array(actual)
    predicted = np.array(predicted)

    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))

    return {
        "mae": float(mae),
        "rmse": float(rmse),
    }


def train_final_prophet_model(
    daily_views_path: Path,
    model_output_path: Path,
    validation_predictions_path: Path,
    metrics_output_path: Path,
    model_summary_path: Path,
    validation_days: int = 14,
) -> None:
    df = pd.read_parquet(daily_views_path)

    df["ds"] = pd.to_datetime(
        df["ds"],
        errors="coerce",
        format="mixed",
    )

    df = df.dropna(subset=["ds"])
    df = df[["ds", "y"]].sort_values("ds")

    if len(df) <= validation_days:
        raise ValueError(
            f"Not enough rows for validation. "
            f"Rows available: {len(df)}, validation_days={validation_days}"
        )

    train_df = df.iloc[:-validation_days].copy()
    valid_df = df.iloc[-validation_days:].copy()

    validation_model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode="multiplicative",
        changepoint_prior_scale=0.05,
        interval_width=0.90,
    )

    validation_model.fit(train_df)

    future = validation_model.make_future_dataframe(
        periods=validation_days,
        freq="D",
    )

    forecast = validation_model.predict(future)

    valid_forecast = forecast[forecast["ds"].isin(valid_df["ds"])][
        ["ds", "yhat", "yhat_lower", "yhat_upper"]
    ]

    validation_predictions = valid_df.merge(
        valid_forecast,
        on="ds",
        how="left",
    )

    metrics = calculate_metrics(
        validation_predictions["y"],
        validation_predictions["yhat"],
    )

    coverage = (
        (validation_predictions["y"] >= validation_predictions["yhat_lower"])
        & (validation_predictions["y"] <= validation_predictions["yhat_upper"])
    ).mean()

    metrics["coverage"] = float(coverage)

    model_summary = {
        "best_model": "prophet_multiplicative",
        "selection_metric": "mae",
        "validation_days": validation_days,
        "train_start": str(train_df["ds"].min().date()),
        "train_end": str(train_df["ds"].max().date()),
        "validation_start": str(valid_df["ds"].min().date()),
        "validation_end": str(valid_df["ds"].max().date()),
        "model_params": {
            "yearly_seasonality": True,
            "weekly_seasonality": True,
            "daily_seasonality": False,
            "seasonality_mode": "multiplicative",
            "changepoint_prior_scale": 0.05,
            "interval_width": 0.90,
        },
        "metrics": {
            "mae": metrics["mae"],
            "rmse": metrics["rmse"],
            "coverage": metrics["coverage"],
        },
    }

    validation_predictions_path.parent.mkdir(parents=True, exist_ok=True)
    validation_predictions.to_parquet(validation_predictions_path, index=False)

    metrics_output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(metrics_output_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)

    model_summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(model_summary_path, "w", encoding="utf-8") as f:
        json.dump(model_summary, f, indent=4)

    final_model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode="multiplicative",
        changepoint_prior_scale=0.05,
        interval_width=0.90,
    )

    final_model.fit(df)

    model_output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(model_output_path, "w", encoding="utf-8") as f:
        f.write(model_to_json(final_model))