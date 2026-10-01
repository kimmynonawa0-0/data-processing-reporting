"""Record the result of each processed CSV file."""

import csv
from datetime import datetime, timezone
from pathlib import Path


LOG_COLUMNS = [
    "processed_at_utc",
    "input_file",
    "status",
    "row_count",
    "issues",
    "excel_report",
    "pdf_report",
]


def append_processing_result(log_file: Path, result):
    """Append one processing result to a CSV log."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not log_file.exists() or log_file.stat().st_size == 0

    log_row = {
        "processed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **result,
    }

    with log_file.open("a", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=LOG_COLUMNS)
        if needs_header:
            writer.writeheader()
        writer.writerow(log_row)
