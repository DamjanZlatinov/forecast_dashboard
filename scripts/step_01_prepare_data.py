import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from dashboard_forecast.preprocessing import prepare_dashboard_events


def run(
    raw_folder: Path,
    output_events_path: Path,
    method: str = "GET",
    endpoint: str = "dashboards.view_dashboard",
) -> None:
    events = prepare_dashboard_events(
        raw_folder=raw_folder,
        output_events_path=output_events_path,
        method=method,
        endpoint=endpoint,
    )

    print(f"Saved events to: {output_events_path}")
    print(f"Rows: {len(events):,}")
    print(f"Date range: {events['date'].min()} to {events['date'].max()}")
    print(f"Unique users: {events['user'].nunique():,}")
    print(f"Unique dashboards: {events['dashboard_id'].nunique():,}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare dashboard view events.")

    parser.add_argument("--raw-folder", type=Path, required=True)
    parser.add_argument("--output-events", type=Path, required=True)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    run(
        raw_folder=args.raw_folder,
        output_events_path=args.output_events,
    )


if __name__ == "__main__":
    main()