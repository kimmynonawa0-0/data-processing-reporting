"""Tests for the shared sales processing pipeline."""

from pathlib import Path

from data_processing_reporting.csv_reader import read_csv_bytes
from data_processing_reporting.pipeline import process_sales_data


VALID_CSV = b"""order_date,product,category,quantity,unit_price
2026-01-05,Notebook,Stationery,3,4.50
2026-02-15,USB Hub,Electronics,2,18.75
"""
REPORT_DIRECTORY = Path("outputs") / "test_reports"


def test_valid_uploaded_data_generates_reports():
    columns, rows = read_csv_bytes(VALID_CSV)

    result = process_sales_data(
        columns,
        rows,
        "pipeline_test.csv",
        REPORT_DIRECTORY,
    )

    try:
        assert result["status"] == "success"
        assert result["metrics"]["total_revenue"] == 51.00
        assert result["excel_report"].exists()
        assert result["pdf_report"].exists()
    finally:
        result["excel_report"].unlink(missing_ok=True)
        result["pdf_report"].unlink(missing_ok=True)


def test_invalid_uploaded_data_does_not_generate_reports():
    invalid_csv = b"order_date,product\n2026-01-05,Notebook\n"
    columns, rows = read_csv_bytes(invalid_csv)

    result = process_sales_data(
        columns,
        rows,
        "invalid.csv",
        REPORT_DIRECTORY,
    )

    assert result["status"] == "validation_failed"
    assert result["metrics"] is None
    assert not (REPORT_DIRECTORY / "invalid_report.xlsx").exists()
    assert not (REPORT_DIRECTORY / "invalid_report.pdf").exists()
