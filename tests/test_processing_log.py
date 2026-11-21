"""Tests for the processing log."""

import csv

from data_processing_reporting.processing_log import (
    LOG_COLUMNS,
    append_processing_result,
    append_upload_result,
)


RESULT = {
    "input_file": "data/sample_sales.csv",
    "status": "success",
    "row_count": 5,
    "issues": "",
    "excel_report": "outputs/sample_sales_report.xlsx",
    "pdf_report": "outputs/sample_sales_report.pdf",
}


def test_log_writes_header_and_result_row(tmp_path):
    log_file = tmp_path / "nested" / "processing_log.csv"

    append_processing_result(log_file, RESULT)

    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert lines[0] == ",".join(LOG_COLUMNS)
    assert len(lines) == 2
    assert "sample_sales.csv" in lines[1]
    assert "success" in lines[1]


def test_log_appends_rows_without_repeating_header(tmp_path):
    log_file = tmp_path / "processing_log.csv"

    append_processing_result(log_file, RESULT)
    append_processing_result(log_file, RESULT)

    with log_file.open(encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert len(rows) == 2
    assert rows[0]["input_file"] == RESULT["input_file"]
    assert rows[1]["status"] == RESULT["status"]


def test_log_rows_carry_utc_timestamps(tmp_path):
    log_file = tmp_path / "processing_log.csv"

    append_processing_result(log_file, RESULT)

    with log_file.open(encoding="utf-8", newline="") as csv_file:
        row = next(csv.DictReader(csv_file))

    assert "T" in row["processed_at_utc"]
    assert row["processed_at_utc"].endswith("+00:00")


def test_upload_result_rows_match_the_cli_log_shape(tmp_path):
    log_file = tmp_path / "processing_log.csv"
    result = {
        "status": "validation_failed",
        "issues": ["Row 2: blank value in 'product'"],
        "sales": None,
        "excel_report": "",
        "pdf_report": "",
    }

    append_upload_result(log_file, "upload.csv", 3, result)

    with log_file.open(encoding="utf-8", newline="") as csv_file:
        row = next(csv.DictReader(csv_file))

    assert row["input_file"] == "upload.csv"
    assert row["status"] == "validation_failed"
    assert row["row_count"] == "3"
    assert row["issues"] == "Row 2: blank value in 'product'"
    assert row["excel_report"] == ""
    assert row["pdf_report"] == ""
