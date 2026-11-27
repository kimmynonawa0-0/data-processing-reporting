"""Tests for sales CSV validation."""

import pytest

from data_processing_reporting.validation import REQUIRED_COLUMNS, find_data_issues


VALID_ROW = {
    "order_date": "2026-01-05",
    "product": "Notebook",
    "category": "Stationery",
    "quantity": "3",
    "unit_price": "4.50",
}


def test_valid_data_has_no_issues():
    issues = find_data_issues(REQUIRED_COLUMNS, [VALID_ROW])

    assert issues == []


def test_missing_column_and_blank_value_are_reported():
    columns = ["order_date", "product", "quantity", "unit_price"]
    row = VALID_ROW.copy()
    row["product"] = ""

    issues = find_data_issues(columns, [row])

    assert "Missing required columns: category" in issues
    assert "Row 2: blank value in 'product'" in issues


@pytest.mark.parametrize(
    ("field", "value", "expected_issue"),
    [
        ("order_date", "01/05/2026", "Row 2: invalid order_date '01/05/2026'"),
        ("order_date", "2026-13-01", "Row 2: invalid order_date '2026-13-01'"),
        ("quantity", "1.5", "Row 2: quantity must be a positive whole number"),
        ("quantity", "0", "Row 2: quantity must be a positive whole number"),
        ("unit_price", "-4.50", "Row 2: unit_price must be a nonnegative number"),
        ("unit_price", "abc", "Row 2: unit_price must be a nonnegative number"),
    ],
)
def test_invalid_values_are_reported(field, value, expected_issue):
    row = VALID_ROW.copy()
    row[field] = value

    issues = find_data_issues(REQUIRED_COLUMNS, [row])

    assert expected_issue in issues


def test_empty_data_is_reported():
    issues = find_data_issues(REQUIRED_COLUMNS, [])

    assert issues == ["CSV contains no data rows"]


def test_csv_without_header_row_is_reported():
    issues = find_data_issues([], [])

    assert issues == ["CSV has no header row"]


def test_duplicate_row_is_reported():
    first_row = VALID_ROW.copy()
    duplicate_row = VALID_ROW.copy()

    issues = find_data_issues(REQUIRED_COLUMNS, [first_row, duplicate_row])

    assert issues == ["Row 3: duplicate of row 2"]
