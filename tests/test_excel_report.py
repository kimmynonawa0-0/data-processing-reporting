"""Tests for Excel report usability settings."""

from pathlib import Path

from openpyxl import load_workbook

from data_processing_reporting.analysis import (
    calculate_sales_metrics,
    prepare_sales_data,
)
from data_processing_reporting.excel_report import export_excel_report


REPORT_FILE = Path("outputs") / "test_reports" / "excel_navigation_test.xlsx"


def test_excel_sheets_freeze_headers_and_enable_filters():
    rows = [
        {
            "order_date": "2026-01-05",
            "product": "Notebook",
            "category": "Stationery",
            "quantity": "3",
            "unit_price": "4.50",
        }
    ]
    sales = prepare_sales_data(rows)
    metrics = calculate_sales_metrics(sales)
    workbook = None

    try:
        export_excel_report(sales, metrics, REPORT_FILE)
        workbook = load_workbook(REPORT_FILE)

        for sheet_name in ["Cleaned Data", "Summary"]:
            worksheet = workbook[sheet_name]
            assert worksheet.freeze_panes == "A2"
            assert worksheet.auto_filter.ref == worksheet.dimensions
    finally:
        if workbook:
            workbook.close()
        REPORT_FILE.unlink(missing_ok=True)
