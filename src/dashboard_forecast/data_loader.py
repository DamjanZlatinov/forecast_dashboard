import json
from pathlib import Path


def read_json_records(file_path: Path) -> list[dict]:
    content = file_path.read_text(encoding="utf-8").strip()

    if not content:
        return []

    # Case 1: full file is valid JSON object or JSON array
    try:
        parsed = json.loads(content)

        if isinstance(parsed, list):
            return parsed

        if isinstance(parsed, dict):
            return [parsed]

    except json.JSONDecodeError:
        pass

    # Case 2: JSON lines
    records = []

    for line in content.splitlines():
        line = line.strip()

        if not line:
            continue

        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    return records


def iter_json_records(raw_folder: Path):
    json_files = sorted(raw_folder.rglob("*.json"))

    print(f"JSON files found by loader: {len(json_files):,}")

    if not json_files:
        raise FileNotFoundError(f"No JSON files found in: {raw_folder}")

    for file_path in json_files:
        records = read_json_records(file_path)

        for record in records:
            yield record