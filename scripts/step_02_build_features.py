import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from dashboard_forecast.features import build_daily_dashboard_views


def run(
    events_path: Path,
    output_daily_views_path: Path,
) -> None:
    daily_views = build_daily_dashboard_views(
        events_path=events_path,
        output_daily_views_path=output_daily_views_path,
    )

    print(f"Saved daily views to: {output_daily_views_path}")
    print(f"Rows: {len(daily_views):,}")
    print(f"Date range: {daily_views['ds'].min()} to {daily_views['ds'].max()}")
    print(f"Total views: {daily_views['y'].sum():,}")
    print(f"Average daily views: {daily_views['y'].mean():.2f}")
    print(f"Median daily views: {daily_views['y'].median():.2f}")
    print(f"Max daily views: {daily_views['y'].max():,}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build daily dashboard views dataset."
    )

    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--output-daily", type=Path, required=True)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    run(
        events_path=args.events,
        output_daily_views_path=args.output_daily,
    )


if __name__ == "__main__":
    main()