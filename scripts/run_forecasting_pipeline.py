from pathlib import Path

from step_04_forecast import run as forecast


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    daily_views_path = PROJECT_ROOT / "data/processed/daily_dashboard_views.parquet"
    model_path = PROJECT_ROOT / "models/prophet_dashboard_views.json"

    forecast_output_path = PROJECT_ROOT / "data/processed/forecast_next_7_days.csv"
    forecast_plot_path = PROJECT_ROOT / "reports/figures/forecast_next_7_days.html"

    start_date = "2021-01-11"
    horizon_days = 7

    print("Forecasting pipeline started.")

    print("\nStep 1: Forecast dashboard views")
    forecast(
        daily_views_path=daily_views_path,
        model_path=model_path,
        forecast_output_path=forecast_output_path,
        forecast_plot_path=forecast_plot_path,
        start_date=start_date,
        horizon_days=horizon_days,
    )

    print("\nForecasting pipeline finished successfully.")
    print(f"Forecast start date: {start_date}")
    print(f"Forecast horizon days: {horizon_days}")
    print(f"Forecast output: {forecast_output_path}")
    print(f"Forecast plot: {forecast_plot_path}")


if __name__ == "__main__":
    main()