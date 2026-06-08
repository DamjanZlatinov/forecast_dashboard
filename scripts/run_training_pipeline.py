from pathlib import Path

from step_01_prepare_data import run as prepare_data
from step_02_build_features import run as build_features
from step_03_train_model import run as train_model


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    raw_folder = PROJECT_ROOT / "data/raw/requests"

    events_path = PROJECT_ROOT / "data/interim/dashboard_events.parquet"
    daily_views_path = PROJECT_ROOT / "data/processed/daily_dashboard_views.parquet"

    model_path = PROJECT_ROOT / "models/prophet_dashboard_views.json"
    validation_predictions_path = (
        PROJECT_ROOT / "data/processed/validation_predictions.parquet"
    )

    metrics_output_path = PROJECT_ROOT / "reports/metrics/evaluation_metrics.json"
    model_summary_path = PROJECT_ROOT / "reports/metrics/model_summary.json"

    print("Training pipeline started.")

    print("\nStep 1: Prepare data")
    prepare_data(
        raw_folder=raw_folder,
        output_events_path=events_path,
    )

    print("\nStep 2: Build features")
    build_features(
        events_path=events_path,
        output_daily_views_path=daily_views_path,
    )

    print("\nStep 3: Train model")
    train_model(
        daily_views_path=daily_views_path,
        model_output_path=model_path,
        validation_predictions_path=validation_predictions_path,
        metrics_output_path=metrics_output_path,
        model_summary_path=model_summary_path,
        validation_days=14,
    )

    print("\nTraining pipeline finished successfully.")
    print(f"Model: {model_path}")
    print(f"Metrics: {metrics_output_path}")
    print(f"Model summary: {model_summary_path}")


if __name__ == "__main__":
    main()