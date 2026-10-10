"""Tests for Excel report usability settings."""

from pathlib import Path

from openpyxl import load_workbook

from data_processing_reporting.analysis import (
    calculate_sales_metrics,
    prepare_sales_data,
)
from data_processing_reporting.excel_report import export_excel_report


REPORT_FILE = Path("outputs") / "test_reports" / "excel_navigation_test.xlsx"


def test_excel_report_usability_settings():
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

        cleaned_data = workbook["Cleaned Data"]
        summary = workbook["Summary"]
        assert cleaned_data["E2"].number_format == "0.00"
        assert cleaned_data["F2"].number_format == "0.00"
        assert summary["C2"].number_format == "0.00"
    finally:
        if workbook:
            workbook.close()
        REPORT_FILE.unlink(missing_ok=True)
