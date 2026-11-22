"""Tests for cleaning actions and the cleaning audit."""

import json

import pandas as pd

from data_processing_reporting.cleaner import (
    clean_data,
    deduplicate_rows,
    fill_null_values,
    text_columns,
    trim_text_columns,
)


def test_trim_removes_outer_spaces_from_text_columns():
    data = pd.DataFrame(
        {
            "product": [" Pen ", " Paper"],
            "quantity": [3, 2],
        }
    )

    clean, trimmed_columns = trim_text_columns(data)

    assert clean["product"].tolist() == ["Pen", "Paper"]
    assert trimmed_columns == ["product"]


def test_trim_skips_mixed_type_columns():
    data = pd.DataFrame({"values": ["Pen", 3, None]})

    clean, trimmed_columns = trim_text_columns(data)

    assert clean["values"].tolist() == ["Pen", 3, None]
    assert trimmed_columns == []


def test_text_columns_ignores_null_values():
    data = pd.DataFrame({"product": ["Pen", None]})

    assert text_columns(data, {"product": "categorical"}) == ["product"]


def test_deduplicate_rows_counts_dropped_rows():
    data = pd.DataFrame(
        {
            "product": ["Pen", "Pen", "Paper"],
            "quantity": [3, 3, 2],
        }
    )

    clean, dropped = deduplicate_rows(data)

    assert dropped == 1
    assert clean["product"].tolist() == ["Pen", "Paper"]


def test_deduplicate_rows_resets_the_index():
    data = pd.DataFrame({"product": ["Pen", "Pen"]})

    clean, _ = deduplicate_rows(data)

    assert clean.index.tolist() == [0]


def test_fill_numeric_column_uses_median():
    data = pd.DataFrame({"price": [4.0, 8.0, None, None]})

    filled, fills = fill_null_values(data, {"price": "numeric"})

    assert filled["price"].tolist() == [4.0, 8.0, 6.0, 6.0]
    assert fills == [
        {"column": "price", "method": "median", "value": 6.0, "count": 2}
    ]


def test_fill_numeric_column_without_values_uses_zero():
    data = pd.DataFrame({"price": [None, None]})

    filled, fills = fill_null_values(data, {"price": "numeric"})

    assert filled["price"].tolist() == [0, 0]
    assert fills == [
        {"column": "price", "method": "zero", "value": 0, "count": 2}
    ]


def test_fill_categorical_column_uses_mode():
    data = pd.DataFrame({"category": ["Pen", "Pen", "Paper", None]})

    filled, fills = fill_null_values(data, {"category": "categorical"})

    assert filled["category"].tolist() == ["Pen", "Pen", "Paper", "Pen"]
    assert fills == [
        {"column": "category", "method": "mode", "value": "Pen", "count": 1}
    ]


def test_fill_categorical_column_without_values_uses_placeholder():
    data = pd.DataFrame({"category": [None, None]})

    filled, fills = fill_null_values(data, {"category": "categorical"})

    assert filled["category"].tolist() == ["Unknown", "Unknown"]
    assert fills == [
        {
            "column": "category",
            "method": "placeholder",
            "value": "Unknown",
            "count": 2,
        }
    ]


def test_fill_datetime_column_uses_nearest_date():
    data = pd.DataFrame(
        {"order_date": [None, "2026-01-05", "2026-01-08", None]}
    )

    filled, fills = fill_null_values(data, {"order_date": "datetime"})

    assert filled["order_date"].tolist() == [
        "2026-01-05",
        "2026-01-05",
        "2026-01-08",
        "2026-01-08",
    ]
    assert fills == [
        {
            "column": "order_date",
            "method": "nearest date",
            "value": None,
            "count": 2,
        }
    ]


def test_fill_leaves_a_column_without_nulls_untouched():
    data = pd.DataFrame({"price": [4.0, 8.0]})

    filled, fills = fill_null_values(data, {"price": "numeric"})

    assert fills == []
    assert filled["price"].tolist() == [4.0, 8.0]


def test_clean_data_reports_every_change():
    data = pd.DataFrame(
        {
            "order_date": ["2026-01-05", "2026-01-05", "2026-01-08"],
            "price": ["4.50", "4.50", None],
            "product": ["Pen ", "Pen", "Paper"],
        }
    )

    cleaned, audit = clean_data(data)

    assert audit["rows_before"] == 3
    assert audit["rows_after"] == 2
    assert audit["duplicates_dropped"] == 1
    assert audit["columns_trimmed"] == ["product"]
    assert audit["nulls_filled"] == [
        {"column": "price", "method": "median", "value": 4.5, "count": 1}
    ]
    assert audit["nulls_remaining"] == {}


def test_clean_data_reports_nulls_it_could_not_fill():
    data = pd.DataFrame(
        {
            "order_date": pd.to_datetime([None, None]),
            "price": [4.50, 6.00],
        }
    )

    cleaned, audit = clean_data(data)

    assert audit["nulls_remaining"] == {"order_date": 2}
    assert cleaned["order_date"].isna().all()


def test_cleaning_audit_is_json_serializable():
    data = pd.DataFrame(
        {
            "order_date": [None, "2026-01-05", "2026-01-05"],
            "price": ["4.50", None, "6.00"],
            "product": ["Pen ", "Pen", "Paper"],
        }
    )

    _, audit = clean_data(data)

    json.dumps(audit)
