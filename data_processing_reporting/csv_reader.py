"""Read data from a CSV file."""

import csv
from pathlib import Path


def read_csv(file_path: Path):
    """Return the column names and rows from a CSV file."""
    with file_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        columns = reader.fieldnames or []
        rows = list(reader)

    return columns, rows
