"""Command-line entry point for Data Analytics Automation."""

import argparse
from csv import Error as CsvError
from pathlib import Path

from .csv_reader import read_csv
from .generic_pipeline import process_generic_data
from .pipeline import process_sales_data
from .processing_log import append_processing_result
from .tabular_reader import SUPPORTED_SUFFIXES, read_tabular


DEFAULT_INPUT = Path(__file__).resolve().parent.parent / "data" / "sample_sales.csv"
DEFAULT_GENERIC_INPUT = (
    Path(__file__).resolve().parent.parent / "data" / "sample_messy.csv"
)
OUTPUT_DIRECTORY = Path(__file__).resolve().parent.parent / "outputs"
PROCESSING_LOG_NAME = "processing_log.csv"


def get_arguments():
    """Parse the input path, output directory, and workflow options."""
    parser = argparse.ArgumentParser(
        description="Validate and analyze CSV files, or clean any CSV or "
        "Excel file."
    )
    parser.add_argument(
        "input_path",
        nargs="?",
        type=Path,
        default=None,
        help="File or folder to process (default: data/sample_sales.csv, "
        "or data/sample_messy.csv with --generic)",
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=OUTPUT_DIRECTORY,
        help="Folder for the generated reports and processing log "
        "(default: outputs)",
    )
    parser.add_argument(
        "--generic",
        action="store_true",
        help="Run the generic clean-and-report workflow instead of the "
        "sales workflow",
    )
    return parser.parse_args()


def find_csv_files(input_path):
    """Return one CSV file or the CSV files inside a folder tree."""
    if input_path.is_file() and input_path.suffix.lower() == ".csv":
        return [input_path]

    if input_path.is_dir():
        return sorted(
            file
            for file in input_path.rglob("*")
            if file.is_file() and file.suffix.lower() == ".csv"
        )

    return []


def find_generic_files(input_path):
    """Return one CSV or Excel file or the supported files in a folder tree."""
    if input_path.is_file() and input_path.suffix.lower() in SUPPORTED_SUFFIXES:
        return [input_path]

    if input_path.is_dir():
        return sorted(
            file
            for file in input_path.rglob("*")
            if file.is_file() and file.suffix.lower() in SUPPORTED_SUFFIXES
        )

    return []


def process_csv(input_file, output_directory):
    """Validate, analyze, and export reports for one CSV file."""
    columns, rows = read_csv(input_file)
    result = process_sales_data(
        columns, rows, input_file.name, output_directory
    )
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
        print(f"Total units: {metrics['total_units']}")

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


def process_generic_file(input_file, output_directory):
    """Profile, clean, chart, and export reports for one data file."""
    data = read_tabular(input_file)
    result = process_generic_data(data, input_file.name, output_directory)

    print(f"File: {input_file}")

    if result["status"] == "failed":
        print("Processing failed.")
        for issue in result["issues"]:
            print(f"- {issue}")
    else:
        profile = result["profile"]
        audit = result["audit"]
        print(f"Columns: {', '.join(profile['column_types'])}")
        print(f"Rows before cleaning: {audit['rows_before']}")
        print(f"Rows after cleaning: {audit['rows_after']}")
        print(f"Duplicate rows dropped: {audit['duplicates_dropped']}")

        print("Nulls filled:")
        if audit["nulls_filled"]:
            for fill in audit["nulls_filled"]:
                print(
                    f"- {fill['column']}: {fill['count']} filled using "
                    f"{fill['method']} ({fill['value']})"
                )
        else:
            print("- None")

        if audit["nulls_remaining"]:
            print("Nulls remaining:")
            for column, count in audit["nulls_remaining"].items():
                print(f"- {column}: {count}")

        print(f"Charts generated: {len(result['charts'])}")
        print(f"Cleaned CSV: {result['cleaned_csv']}")
        print(f"Cleaned Excel: {result['cleaned_excel']}")
        print(f"PDF report: {result['pdf_report']}")

    return {
        "input_file": str(input_file.resolve()),
        "status": result["status"],
        "row_count": (
            result["profile"]["row_count"] if result["profile"] else ""
        ),
        "issues": "; ".join(result["issues"]),
        "excel_report": str(result["cleaned_excel"]),
        "pdf_report": str(result["pdf_report"]),
    }


def run_generic(input_path, output_directory):
    """Process every CSV or Excel file through the generic workflow."""
    processing_log = output_directory / PROCESSING_LOG_NAME
    input_files = find_generic_files(input_path)

    if not input_files:
        print(f"No CSV or Excel files found: {input_path}")
        return 1

    print(f"Files found: {len(input_files)}")
    has_failures = False
    successful_files = 0

    for input_file in input_files:
        print(f"\nProcessing: {input_file}")

        try:
            result = process_generic_file(input_file, output_directory)
        except (OSError, ValueError) as error:
            print(f"Processing failed: {error}")
            result = {
                "input_file": str(input_file.resolve()),
                "status": "processing_failed",
                "row_count": "",
                "issues": str(error),
                "excel_report": "",
                "pdf_report": "",
            }

        append_processing_result(processing_log, result)

        if result["status"] == "success":
            successful_files += 1
        else:
            has_failures = True

    failed_files = len(input_files) - successful_files
    print(f"\nDone: {successful_files} succeeded, {failed_files} failed.")
    print(f"Processing log: {processing_log}")
    return 1 if has_failures else 0


def main():
    arguments = get_arguments()

    if arguments.input_path is None:
        input_path = (
            DEFAULT_GENERIC_INPUT if arguments.generic else DEFAULT_INPUT
        )
    else:
        input_path = arguments.input_path

    output_directory = arguments.output_directory

    if arguments.generic:
        return run_generic(input_path, output_directory)

    processing_log = output_directory / PROCESSING_LOG_NAME
    input_files = find_csv_files(input_path)

    if not input_files:
        print(f"No CSV files found: {input_path}")
        return 1

    print(f"CSV files found: {len(input_files)}")
    has_failures = False
    successful_files = 0

    for input_file in input_files:
        print(f"\nProcessing: {input_file}")

        try:
            result = process_csv(input_file, output_directory)
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

        append_processing_result(processing_log, result)

        if result["status"] != "success":
            has_failures = True
        else:
            successful_files += 1

    failed_files = len(input_files) - successful_files
    print(f"\nDone: {successful_files} succeeded, {failed_files} failed.")
    print(f"Processing log: {processing_log}")
    return 1 if has_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
