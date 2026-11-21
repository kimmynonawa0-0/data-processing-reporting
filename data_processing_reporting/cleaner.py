"""Clean generic tabular data: trim text, drop duplicates, fill nulls."""

import pandas as pd

from .profiler import infer_column_types


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
