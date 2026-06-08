from pathlib import Path

from monitor_01_create_report import run as create_monitoring_report


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    events_path = PROJECT_ROOT / "data/interim/dashboard_events.parquet"
    daily_views_path = PROJECT_ROOT / "data/processed/daily_dashboard_views.parquet"
    validation_predictions_path = (
        PROJECT_ROOT / "data/processed/validation_predictions.parquet"
    )
    metrics_path = PROJECT_ROOT / "reports/metrics/evaluation_metrics.json"

    output_report_path = PROJECT_ROOT / "reports/metrics/monitoring_report.json"

    print("Monitoring pipeline started.")

    print("\nStep 1: Create monitoring report")
    create_monitoring_report(
        events_path=events_path,
        daily_views_path=daily_views_path,
        validation_predictions_path=validation_predictions_path,
        metrics_path=metrics_path,
        output_report_path=output_report_path,
    )

    print("\nMonitoring pipeline finished successfully.")
    print(f"Monitoring report: {output_report_path}")


if __name__ == "__main__":
    main()