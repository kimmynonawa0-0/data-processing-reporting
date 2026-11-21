"""Tests for column type inference and the data quality card."""

import json

import pandas as pd

from data_processing_reporting.profiler import (
    HIGH_CARDINALITY_LIMIT,
    column_type_hint,
    infer_column_type,
    infer_column_types,
    profile_data,
)


def make_series(values):
    return pd.Series(values, dtype="object")


def test_infers_numeric_column_from_numbers():
    assert infer_column_type(make_series([1, 2.5, 3])) == "numeric"


def test_infers_numeric_column_from_number_strings():
    assert infer_column_type(make_series(["1", "2.5", "3"])) == "numeric"


def test_infers_datetime_column_from_date_strings():
    assert (
        infer_column_type(make_series(["2026-01-05", "2026-01-08"]))
        == "datetime"
    )


def test_infers_datetime_column_from_datetime_dtype():
    assert (
        infer_column_type(pd.to_datetime(["2026-01-05", "2026-01-08"]))
        == "datetime"
    )


def test_infers_categorical_column_from_text():
    assert infer_column_type(make_series(["Pen", "Paper", "Ink"])) == "categorical"


def test_infers_categorical_column_when_values_are_mixed():
    assert infer_column_type(make_series([1, "Pen"])) == "categorical"


def test_infers_categorical_column_when_all_values_are_null():
    assert infer_column_type(make_series([None, None])) == "categorical"


def test_infer_column_types_covers_every_column():
    data = pd.DataFrame(
        {
            "order_date": ["2026-01-05"],
            "price": ["4.50"],
            "product": ["Pen"],
        }
    )

    assert infer_column_types(data) == {
        "order_date": "datetime",
        "price": "numeric",
        "product": "categorical",
    }


def test_column_name_hints_a_type():
    assert column_type_hint("unit_price") == "numeric"
    assert column_type_hint("order_date") == "datetime"
    assert column_type_hint("Total Revenue") == "numeric"


def test_column_name_without_hint_returns_none():
    assert column_type_hint("product") is None
    assert column_type_hint("customer_name") is None


def test_profile_data_counts_quality_issues():
    data = pd.DataFrame(
        {
            "order_date": ["2026-01-05", "2026-01-05", None],
            "price": ["4.50", "4.50", "6.00"],
            "product": ["Pen", "Pen", "Paper"],
        }
    )

    card = profile_data(data)

    assert card["row_count"] == 3
    assert card["duplicate_rows"] == 1
    assert card["null_counts"] == {"order_date": 1, "price": 0, "product": 0}
    assert card["column_types"] == {
        "order_date": "datetime",
        "price": "numeric",
        "product": "categorical",
    }
    assert card["type_hints"] == {"order_date": "datetime", "price": "numeric"}
    assert card["cardinality"] == {"order_date": 1, "price": 2, "product": 2}


def test_profile_data_flags_high_cardinality_categories():
    data = pd.DataFrame(
        {
            "category": [
                f"Category {number}"
                for number in range(HIGH_CARDINALITY_LIMIT + 1)
            ]
        }
    )

    card = profile_data(data)

    assert card["high_cardinality_columns"] == ["category"]


def test_data_card_is_json_serializable():
    data = pd.DataFrame(
        {
            "order_date": ["2026-01-05", None],
            "price": [4.5, 6.0],
            "product": ["Pen", "Paper"],
        }
    )

    json.dumps(profile_data(data))
