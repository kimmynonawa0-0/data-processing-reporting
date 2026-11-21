"""Infer column types and build a serializable data quality card."""

import re

import pandas as pd


HIGH_CARDINALITY_LIMIT = 20

TYPE_HINTS = [
    ("date", "datetime"),
    ("time", "datetime"),
    ("price", "numeric"),
    ("amount", "numeric"),
    ("revenue", "numeric"),
    ("sales", "numeric"),
    ("quantity", "numeric"),
    ("qty", "numeric"),
    ("total", "numeric"),
    ("count", "numeric"),
]


def column_type_hint(column_name):
    """Return the type hinted by a column name, or None."""
    lowered_name = column_name.lower()

    for fragment, hinted_type in TYPE_HINTS:
        if re.search(rf"(^|[\s_]){fragment}($|[\s_])", lowered_name):
            return hinted_type

    return None


def infer_column_type(series: pd.Series):
    """Return 'numeric', 'datetime', or 'categorical' for one column."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    non_null_values = series.dropna()
    if non_null_values.empty:
        return "categorical"

    numeric_values = pd.to_numeric(non_null_values, errors="coerce")
    if numeric_values.notna().all():
        return "numeric"

    if non_null_values.map(type).eq(str).all():
        date_values = pd.to_datetime(
            non_null_values, errors="coerce", format="mixed"
        )
        if date_values.notna().all():
            return "datetime"

    return "categorical"


def infer_column_types(data: pd.DataFrame):
    """Return the inferred type of every column."""
    return {
        column: infer_column_type(data[column]) for column in data.columns
    }


def profile_data(data: pd.DataFrame):
    """Return a JSON-serializable data card describing a raw dataset."""
    column_types = infer_column_types(data)

    high_cardinality_columns = [
        column
        for column, column_type in column_types.items()
        if column_type == "categorical"
        and data[column].nunique(dropna=True) > HIGH_CARDINALITY_LIMIT
    ]

    type_hints = {
        column: hinted_type
        for column in data.columns
        if (hinted_type := column_type_hint(column))
    }

    return {
        "columns": list(data.columns),
        "row_count": len(data),
        "column_types": column_types,
        "type_hints": type_hints,
        "null_counts": {
            column: int(data[column].isna().sum()) for column in data.columns
        },
        "duplicate_rows": int(data.duplicated().sum()),
        "cardinality": {
            column: int(data[column].nunique(dropna=True))
            for column in data.columns
        },
        "high_cardinality_columns": high_cardinality_columns,
    }
