import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from dashboard_forecast.train import train_final_prophet_model


def run(
    daily_views_path: Path,
    model_output_path: Path,
    validation_predictions_path: Path,
    metrics_output_path: Path,
    model_summary_path: Path,
    validation_days: int = 14,
) -> None:
    train_final_prophet_model(
        daily_views_path=daily_views_path,
        model_output_path=model_output_path,
        validation_predictions_path=validation_predictions_path,
        metrics_output_path=metrics_output_path,
        model_summary_path=model_summary_path,
        validation_days=validation_days,
    )

    print(f"Saved model to: {model_output_path}")
    print(f"Saved validation predictions to: {validation_predictions_path}")
    print(f"Saved metrics to: {metrics_output_path}")
    print(f"Saved model summary to: {model_summary_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train final Prophet model.")

    parser.add_argument("--daily-views", type=Path, required=True)
    parser.add_argument("--model-output", type=Path, required=True)
    parser.add_argument("--validation-predictions", type=Path, required=True)
    parser.add_argument("--metrics-output", type=Path, required=True)
    parser.add_argument("--model-summary", type=Path, required=True)
    parser.add_argument("--validation-days", type=int, default=14)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    run(
        daily_views_path=args.daily_views,
        model_output_path=args.model_output,
        validation_predictions_path=args.validation_predictions,
        metrics_output_path=args.metrics_output,
        model_summary_path=args.model_summary,
        validation_days=args.validation_days,
    )


if __name__ == "__main__":
    main()