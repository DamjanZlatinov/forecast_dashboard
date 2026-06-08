from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from prophet.serialize import model_from_json


def forecast_next_days(
    daily_views_path: Path,
    model_path: Path,
    forecast_output_path: Path,
    forecast_plot_path: Path,
    start_date: str | None = None,
    horizon_days: int = 7,
) -> pd.DataFrame:
    daily_views = pd.read_parquet(daily_views_path)

    daily_views["ds"] = pd.to_datetime(
        daily_views["ds"],
        errors="coerce",
        format="mixed",
    )

    daily_views = daily_views.dropna(subset=["ds"])
    daily_views = daily_views[["ds", "y"]].sort_values("ds")

    last_history_date = daily_views["ds"].max()

    if start_date is None:
        forecast_start_date = last_history_date + pd.Timedelta(days=1)
    else:
        forecast_start_date = pd.to_datetime(start_date)

    if forecast_start_date <= last_history_date:
        raise ValueError(
            f"start_date must be after the last historical date. "
            f"Last historical date: {last_history_date.date()}, "
            f"provided start_date: {forecast_start_date.date()}"
        )

    forecast_end_date = forecast_start_date + pd.Timedelta(days=horizon_days - 1)

    periods_needed = (forecast_end_date - last_history_date).days

    with open(model_path, "r", encoding="utf-8") as f:
        model = model_from_json(f.read())

    future = model.make_future_dataframe(
        periods=periods_needed,
        freq="D",
    )

    forecast = model.predict(future)

    forecast_output = forecast[
        (forecast["ds"] >= forecast_start_date)
        & (forecast["ds"] <= forecast_end_date)
    ][["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()

    forecast_output_path.parent.mkdir(parents=True, exist_ok=True)
    forecast_output.to_csv(forecast_output_path, index=False)

    history = daily_views.tail(90)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=history["ds"],
            y=history["y"],
            mode="lines",
            name="Historical actuals",
            line=dict(color="#999999", width=2),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=forecast_output["ds"],
            y=forecast_output["yhat"],
            mode="lines+markers",
            name=f"{horizon_days}-day forecast",
            line=dict(color="#EB140A", width=3),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=pd.concat([forecast_output["ds"], forecast_output["ds"][::-1]]),
            y=pd.concat([
                forecast_output["yhat_upper"],
                forecast_output["yhat_lower"][::-1],
            ]),
            fill="toself",
            line=dict(width=0),
            name="90% prediction interval",
            opacity=0.25,
        )
    )

    fig.update_layout(
        title=f"Dashboard Views Forecast from {forecast_start_date.date()}",
        template="plotly_white",
        height=550,
        xaxis_title="Date",
        yaxis_title="Daily dashboard views",
        hovermode="x unified",
        font=dict(size=13, color="#333333"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    fig.update_xaxes(showgrid=True, gridcolor="#F2F2F2")
    fig.update_yaxes(showgrid=True, gridcolor="#F2F2F2")

    forecast_plot_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(forecast_plot_path)

    return forecast_output