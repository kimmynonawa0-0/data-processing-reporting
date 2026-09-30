"""Command-line entry point for Data-Processing-Reporting."""

import argparse
from pathlib import Path

from .csv_reader import read_csv
from .validation import find_data_issues


DEFAULT_INPUT = Path(__file__).resolve().parent.parent / "data" / "sample_sales.csv"


def get_input_file():
    """Get the CSV file path provided by the user."""
    parser = argparse.ArgumentParser(
        description="Read a CSV file and check its basic data quality."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        type=Path,
        default=DEFAULT_INPUT,
        help="CSV file to read (default: data/sample_sales.csv)",
    )
    return parser.parse_args().input_file


def main():
    input_file = get_input_file()
    columns, rows = read_csv(input_file)
    issues = find_data_issues(columns, rows)

    print(f"File: {input_file}")
    print(f"Columns: {', '.join(columns)}")
    print(f"Number of rows: {len(rows)}")

    print("\nValidation:")
    if issues:
        for issue in issues:
            print(f"- {issue}")
    else:
        print("Passed: all required columns and values are present.")

    print("\nPreview:")

    for row in rows[:5]:
        values = [row[column] for column in columns]
        print(" | ".join(values))


if __name__ == "__main__":
    main()
