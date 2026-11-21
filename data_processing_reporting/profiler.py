"""Infer the type of each column in a tabular dataset."""

import pandas as pd


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
