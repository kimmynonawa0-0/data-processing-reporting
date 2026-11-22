"""Clean generic tabular data: trim text, drop duplicates, fill nulls."""

import pandas as pd

from .profiler import infer_column_types, profile_data


def text_columns(data: pd.DataFrame, column_types):
    """Return categorical columns whose non-null values are all strings."""
    columns = []

    for column, column_type in column_types.items():
        if column_type != "categorical":
            continue

        values = data[column].dropna()
        if not values.empty and values.map(type).eq(str).all():
            columns.append(column)

    return columns


def trim_text_columns(data: pd.DataFrame):
    """Remove outer spaces from categorical text columns."""
    clean = data.copy()
    column_types = infer_column_types(clean)
    trimmed_columns = text_columns(clean, column_types)

    for column in trimmed_columns:
        clean[column] = clean[column].str.strip()

    return clean, trimmed_columns


def deduplicate_rows(data: pd.DataFrame):
    """Remove exact duplicate rows and return the number dropped."""
    clean = data.drop_duplicates().reset_index(drop=True)
    dropped = len(data) - len(clean)

    return clean, dropped


def to_plain_value(value):
    """Convert a pandas scalar into a plain JSON-safe value."""
    if value is None or isinstance(value, (str, bool, int, float)):
        return value

    if hasattr(value, "item"):
        return value.item()

    return str(value)


def fill_numeric_column(data, column, fills):
    """Convert to numbers and fill nulls with the median, or zero if empty."""
    values = pd.to_numeric(data[column], errors="coerce")
    null_count = int(values.isna().sum())

    if null_count == 0:
        data[column] = values
        return

    median = values.median()

    if pd.isna(median):
        data[column] = values.fillna(0)
        fills.append(
            {"column": column, "method": "zero", "value": 0, "count": null_count}
        )
        return

    data[column] = values.fillna(median)
    fills.append(
        {
            "column": column,
            "method": "median",
            "value": to_plain_value(median),
            "count": null_count,
        }
    )


def fill_categorical_column(data, column, fills):
    """Fill nulls with the most common value, or 'Unknown' when empty."""
    values = data[column]
    null_count = int(values.isna().sum())

    if null_count == 0:
        return

    modes = values.mode()

    if modes.empty:
        fill_value = "Unknown"
        method = "placeholder"
    else:
        fill_value = to_plain_value(modes.iloc[0])
        method = "mode"

    data[column] = values.fillna(fill_value)
    fills.append(
        {
            "column": column,
            "method": method,
            "value": fill_value,
            "count": null_count,
        }
    )


def fill_datetime_column(data, column, fills):
    """Fill nulls with the nearest date, when any date exists."""
    values = data[column]
    null_count = int(values.isna().sum())

    if null_count == 0:
        return

    filled = values.ffill().bfill()

    if filled.notna().all():
        data[column] = filled
        fills.append(
            {
                "column": column,
                "method": "nearest date",
                "value": None,
                "count": null_count,
            }
        )


def fill_null_values(data: pd.DataFrame, column_types):
    """Fill nulls with a type-appropriate value and record each action."""
    filled = data.copy()
    fills = []

    for column, column_type in column_types.items():
        if column_type == "numeric":
            fill_numeric_column(filled, column, fills)
        elif column_type == "datetime":
            fill_datetime_column(filled, column, fills)
        elif column_type == "categorical":
            fill_categorical_column(filled, column, fills)

    return filled, fills


def clean_data(data: pd.DataFrame):
    """Run the full cleaning workflow and audit every change."""
    column_types = profile_data(data)["column_types"]
    rows_before = len(data)

    cleaned, trimmed_columns = trim_text_columns(data)
    cleaned, duplicates_dropped = deduplicate_rows(cleaned)
    cleaned, nulls_filled = fill_null_values(cleaned, column_types)

    audit = {
        "rows_before": rows_before,
        "rows_after": len(cleaned),
        "duplicates_dropped": duplicates_dropped,
        "columns_trimmed": trimmed_columns,
        "nulls_filled": nulls_filled,
        "nulls_remaining": {
            column: int(cleaned[column].isna().sum())
            for column in cleaned.columns
            if cleaned[column].isna().any()
        },
    }

    return cleaned, audit
