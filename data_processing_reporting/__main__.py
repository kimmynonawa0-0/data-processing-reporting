"""Command-line entry point for Data-Processing-Reporting."""

import argparse
from csv import Error as CsvError
from pathlib import Path

from .csv_reader import read_csv
from .pipeline import process_sales_data
from .processing_log import append_processing_result


DEFAULT_INPUT = Path(__file__).resolve().parent.parent / "data" / "sample_sales.csv"
OUTPUT_DIRECTORY = Path(__file__).resolve().parent.parent / "outputs"
PROCESSING_LOG = OUTPUT_DIRECTORY / "processing_log.csv"


def get_input_path():
    """Get the CSV file or folder path provided by the user."""
    parser = argparse.ArgumentParser(
        description="Validate and analyze one CSV file or a folder of CSV files."
    )
    parser.add_argument(
        "input_path",
        nargs="?",
        type=Path,
        default=DEFAULT_INPUT,
        help="CSV file or folder to process (default: data/sample_sales.csv)",
    )
    return parser.parse_args().input_path


def find_csv_files(input_path):
    """Return one CSV file or the CSV files directly inside a folder."""
    if input_path.is_file() and input_path.suffix.lower() == ".csv":
        return [input_path]

    if input_path.is_dir():
        return sorted(
            file
            for file in input_path.iterdir()
            if file.is_file() and file.suffix.lower() == ".csv"
        )

    return []


def process_csv(input_file):
    """Validate, analyze, and export reports for one CSV file."""
    columns, rows = read_csv(input_file)
    result = process_sales_data(columns, rows, input_file.name, OUTPUT_DIRECTORY)
    issues = result["issues"]

    print(f"File: {input_file}")
    print(f"Columns: {', '.join(columns)}")
    print(f"Number of rows: {len(rows)}")

    print("\nValidation:")
    if issues:
        for issue in issues:
            print(f"- {issue}")
    else:
        print("Passed: all required fields contain valid values.")

    print("\nSales analysis:")
    if issues:
        print("Skipped because the CSV has validation issues.")
    else:
        metrics = result["metrics"]
        print(f"Total revenue: {metrics['total_revenue']:.2f}")

        print("Revenue by category:")
        for category, revenue in metrics["revenue_by_category"].items():
            print(f"- {category}: {revenue:.2f}")

        print("Revenue by month:")
        for month, revenue in metrics["revenue_by_month"].items():
            print(f"- {month}: {revenue:.2f}")

        print(f"Excel report: {result['excel_report']}")
        print(f"PDF report: {result['pdf_report']}")

    print("\nPreview:")

    for row in rows[:5]:
        values = [row[column] for column in columns]
        print(" | ".join(values))

    return {
        "input_file": str(input_file.resolve()),
        "status": result["status"],
        "row_count": len(rows),
        "issues": "; ".join(issues),
        "excel_report": str(result["excel_report"]),
        "pdf_report": str(result["pdf_report"]),
    }


def main():
    input_path = get_input_path()
    input_files = find_csv_files(input_path)

    if not input_files:
        print(f"No CSV files found: {input_path}")
        return 1

    print(f"CSV files found: {len(input_files)}")
    has_failures = False

    for input_file in input_files:
        print(f"\nProcessing: {input_file}")

        try:
            result = process_csv(input_file)
        except (OSError, UnicodeError, CsvError) as error:
            print(f"Processing failed: {error}")
            result = {
                "input_file": str(input_file.resolve()),
                "status": "processing_failed",
                "row_count": "",
                "issues": str(error),
                "excel_report": "",
                "pdf_report": "",
            }

        append_processing_result(PROCESSING_LOG, result)

        if result["status"] != "success":
            has_failures = True

    print(f"\nProcessing log: {PROCESSING_LOG}")
    return 1 if has_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
