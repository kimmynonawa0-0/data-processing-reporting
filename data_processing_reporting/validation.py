"""Check CSV data for basic quality issues."""

from datetime import date
from decimal import Decimal, InvalidOperation


REQUIRED_COLUMNS = [
    "order_date",
    "product",
    "category",
    "quantity",
    "unit_price",
]


def check_order_date(value, row_number):
    """Return an issue when a date is not in YYYY-MM-DD format."""
    try:
        parsed_date = date.fromisoformat(value)
    except ValueError:
        return f"Row {row_number}: invalid order_date '{value}'"

    if parsed_date.isoformat() != value:
        return f"Row {row_number}: invalid order_date '{value}'"

    return None


def check_quantity(value, row_number):
    """Return an issue when quantity is not a positive whole number."""
    try:
        quantity = int(value)
    except ValueError:
        return f"Row {row_number}: quantity must be a positive whole number"

    if quantity <= 0:
        return f"Row {row_number}: quantity must be a positive whole number"

    return None


def check_unit_price(value, row_number):
    """Return an issue when unit price is not a nonnegative number."""
    try:
        unit_price = Decimal(value)
    except InvalidOperation:
        return f"Row {row_number}: unit_price must be a nonnegative number"

    if not unit_price.is_finite() or unit_price < 0:
        return f"Row {row_number}: unit_price must be a nonnegative number"

    return None


def find_data_issues(columns, rows):
    """Return missing fields, blank values, and invalid value formats."""
    issues = []

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in columns
    ]

    if missing_columns:
        issues.append(f"Missing required columns: {', '.join(missing_columns)}")

    if not rows:
        issues.append("CSV contains no data rows")

    for row_number, row in enumerate(rows, start=2):
        for column in REQUIRED_COLUMNS:
            if column not in columns:
                continue

            value = row.get(column)
            if value is None or not value.strip():
                issues.append(f"Row {row_number}: blank value in '{column}'")
                continue

            value = value.strip()
            issue = None

            if column == "order_date":
                issue = check_order_date(value, row_number)
            elif column == "quantity":
                issue = check_quantity(value, row_number)
            elif column == "unit_price":
                issue = check_unit_price(value, row_number)

            if issue:
                issues.append(issue)

    return issues
