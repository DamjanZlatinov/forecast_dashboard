import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from dashboard_forecast.monitoring import create_monitoring_report


def run(
    events_path: Path,
    daily_views_path: Path,
    validation_predictions_path: Path,
    metrics_path: Path,
    output_report_path: Path,
) -> None:
    report = create_monitoring_report(
        events_path=events_path,
        daily_views_path=daily_views_path,
        validation_predictions_path=validation_predictions_path,
        metrics_path=metrics_path,
        output_report_path=output_report_path,
    )

    print(f"Saved monitoring report to: {output_report_path}")
    print(json.dumps(report, indent=4))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create monitoring report.")

    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--daily-views", type=Path, required=True)
    parser.add_argument("--validation-predictions", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--output-report", type=Path, required=True)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    run(
        events_path=args.events,
        daily_views_path=args.daily_views,
        validation_predictions_path=args.validation_predictions,
        metrics_path=args.metrics,
        output_report_path=args.output_report,
    )


if __name__ == "__main__":
    main()