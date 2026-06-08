import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from dashboard_forecast.forecast import forecast_next_days


def run(
    daily_views_path: Path,
    model_path: Path,
    forecast_output_path: Path,
    forecast_plot_path: Path,
    start_date: str | None = None,
    horizon_days: int = 7,
) -> None:
    forecast = forecast_next_days(
        daily_views_path=daily_views_path,
        model_path=model_path,
        forecast_output_path=forecast_output_path,
        forecast_plot_path=forecast_plot_path,
        start_date=start_date,
        horizon_days=horizon_days,
    )

    print(f"Saved forecast to: {forecast_output_path}")
    print(f"Saved forecast plot to: {forecast_plot_path}")
    print("\nForecast:")
    print(forecast)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Forecast dashboard views.")

    parser.add_argument("--daily-views", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--forecast-output", type=Path, required=True)
    parser.add_argument("--forecast-plot", type=Path, required=True)
    parser.add_argument("--start-date", type=str, default=None)
    parser.add_argument("--horizon-days", type=int, default=7)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    run(
        daily_views_path=args.daily_views,
        model_path=args.model_path,
        forecast_output_path=args.forecast_output,
        forecast_plot_path=args.forecast_plot,
        start_date=args.start_date,
        horizon_days=args.horizon_days,
    )


if __name__ == "__main__":
    main()