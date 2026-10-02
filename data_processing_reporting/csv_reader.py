"""Read data from a CSV file."""

import csv
from io import StringIO
from pathlib import Path


def read_rows(csv_file):
    """Return the column names and rows from an open text CSV file."""
    reader = csv.DictReader(csv_file)
    columns = reader.fieldnames or []
    rows = list(reader)

    return columns, rows


def read_csv(file_path: Path):
    """Return the column names and rows from a CSV file."""
    with file_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        return read_rows(csv_file)


def read_csv_bytes(file_bytes):
    """Return the column names and rows from uploaded CSV bytes."""
    csv_text = file_bytes.decode("utf-8-sig")
    return read_rows(StringIO(csv_text, newline=""))
