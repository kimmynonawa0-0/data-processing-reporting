"""Tests for the generic clean-and-report pipeline."""

import matplotlib.pyplot as plt
import pandas as pd

from data_processing_reporting.generic_pipeline import process_generic_data


MESSY_DATA = pd.DataFrame(
    {
        "order_date": ["2026-01-05", "2026-01-05", "2026-01-08", None],
        "price": ["4.50", "4.50", None, "24.99"],
        "quantity": [3, 3, 2, 1],
        "product": ["Pen ", "Pen", "Paper", "Ink"],
    }
)


def test_process_generic_data_cleans_and_charts(tmp_path):
    result = process_generic_data(MESSY_DATA, "messy.csv", tmp_path)

    assert result["status"] == "success"
    assert result["profile"]["row_count"] == 4
    assert result["audit"]["rows_before"] == 4
    assert result["audit"]["rows_after"] == 3
    assert result["audit"]["duplicates_dropped"] == 1
    assert result["audit"]["columns_trimmed"] == ["product"]
    assert result["cleaned"]["price"].notna().all()

    for _, chart in result["charts"]:
        plt.close(chart)


def test_process_generic_data_exports_files(tmp_path):
    result = process_generic_data(MESSY_DATA, "messy.csv", tmp_path)

    assert result["cleaned_csv"].exists()
    assert result["cleaned_excel"].exists()
    assert result["pdf_report"].exists()
    assert result["pdf_report"].stat().st_size > 0

    for _, chart in result["charts"]:
        plt.close(chart)


def test_cleaned_csv_matches_the_cleaned_data(tmp_path):
    result = process_generic_data(MESSY_DATA, "messy.csv", tmp_path)

    exported = pd.read_csv(result["cleaned_csv"])

    assert len(exported) == result["audit"]["rows_after"]
    assert exported["product"].tolist() == ["Pen", "Paper", "Ink"]

    for _, chart in result["charts"]:
        plt.close(chart)


def test_cleaned_excel_has_audit_sheet(tmp_path):
    result = process_generic_data(MESSY_DATA, "messy.csv", tmp_path)

    sheets = pd.ExcelFile(result["cleaned_excel"]).sheet_names

    assert sheets == ["Cleaned Data", "Cleaning Audit"]

    for _, chart in result["charts"]:
        plt.close(chart)


def test_process_generic_data_reports_empty_files(tmp_path):
    result = process_generic_data(pd.DataFrame(), "empty.csv", tmp_path)

    assert result["status"] == "failed"
    assert result["issues"] == ["The file contains no data rows."]
    assert result["cleaned_csv"] == ""
    assert result["cleaned_excel"] == ""
    assert result["pdf_report"] == ""
