from pathlib import Path

import pandas as pd

from dashboard_forecast.data_loader import iter_json_records


def extract_dashboard_id(record: dict) -> str | None:
    view_args = record.get("view-args") or {}

    dashboard_id = view_args.get("id")

    if dashboard_id is not None:
        return dashboard_id

    path = record.get("path")

    if path and path.startswith("/dashboards/"):
        return path.replace("/dashboards/", "")

    return None


def prepare_dashboard_events(
    raw_folder: Path,
    output_events_path: Path,
    method: str = "GET",
    endpoint: str = "dashboards.view_dashboard",
) -> pd.DataFrame:
    rows = []

    total_records = 0
    matching_records = 0
    missing_dashboard_id = 0
    missing_timestamp_or_user = 0

    for record in iter_json_records(raw_folder):
        total_records += 1

        if record.get("method") != method:
            continue

        if record.get("endpoint") != endpoint:
            continue

        matching_records += 1

        dashboard_id = extract_dashboard_id(record)

        if dashboard_id is None:
            missing_dashboard_id += 1
            continue

        timestamp = record.get("timestamp")
        user = record.get("user")

        if timestamp is None or user is None:
            missing_timestamp_or_user += 1
            continue

        rows.append(
            {
                "timestamp": timestamp,
                "user": user,
                "method": record.get("method"),
                "endpoint": record.get("endpoint"),
                "status": record.get("status"),
                "dashboard_id": dashboard_id,
                "path": record.get("path"),
                "browser": record.get("browser"),
                "browser_platform": record.get("browser-platform"),
                "browser_version": record.get("browser-version"),
            }
        )

    print(f"Total raw records read: {total_records:,}")
    print(f"Matching GET dashboard views: {matching_records:,}")
    print(f"Rows collected before datetime parsing: {len(rows):,}")
    print(f"Missing dashboard_id: {missing_dashboard_id:,}")
    print(f"Missing timestamp or user: {missing_timestamp_or_user:,}")

    events = pd.DataFrame(rows)

    if events.empty:
        raise ValueError("No valid dashboard view events found.")

    events["timestamp"] = pd.to_datetime(
        events["timestamp"],
        errors="coerce",
        format="mixed",
    )

    bad_timestamps = events["timestamp"].isna().sum()
    print(f"Bad timestamps after parsing: {bad_timestamps:,}")

    events = events.dropna(subset=["timestamp"])

    events["date"] = events["timestamp"].dt.date

    output_events_path.parent.mkdir(parents=True, exist_ok=True)
    events.to_parquet(output_events_path, index=False)

    return events