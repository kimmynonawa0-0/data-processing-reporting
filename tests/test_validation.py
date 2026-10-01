"""Tests for sales CSV validation."""

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


def test_invalid_date_quantity_and_price_are_reported():
    row = VALID_ROW.copy()
    row["order_date"] = "01/05/2026"
    row["quantity"] = "1.5"
    row["unit_price"] = "-4.50"

    issues = find_data_issues(REQUIRED_COLUMNS, [row])

    assert "Row 2: invalid order_date '01/05/2026'" in issues
    assert "Row 2: quantity must be a positive whole number" in issues
    assert "Row 2: unit_price must be a nonnegative number" in issues


def test_empty_data_is_reported():
    issues = find_data_issues(REQUIRED_COLUMNS, [])

    assert issues == ["CSV contains no data rows"]
