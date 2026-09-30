"""Check CSV data for basic quality issues."""


REQUIRED_COLUMNS = [
    "order_date",
    "product",
    "category",
    "quantity",
    "unit_price",
]


def find_data_issues(columns, rows):
    """Return a list of missing columns and blank required values."""
    issues = []

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in columns
    ]

    if missing_columns:
        issues.append(f"Missing required columns: {', '.join(missing_columns)}")

    for row_number, row in enumerate(rows, start=2):
        for column in REQUIRED_COLUMNS:
            if column not in columns:
                continue

            value = row.get(column)
            if value is None or not value.strip():
                issues.append(f"Row {row_number}: blank value in '{column}'")

    return issues
