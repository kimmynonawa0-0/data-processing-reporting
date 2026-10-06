"""Tests for sales data preparation and metrics."""

import pytest

from data_processing_reporting.analysis import (
    calculate_sales_metrics,
    prepare_sales_data,
)


SAMPLE_ROWS = [
    {
        "order_date": "2026-01-05",
        "product": "Notebook",
        "category": "Stationery",
        "quantity": "3",
        "unit_price": "4.50",
    },
    {
        "order_date": "2026-01-08",
        "product": "Pen Set",
        "category": "Stationery",
        "quantity": "2",
        "unit_price": "6.00",
    },
    {
        "order_date": "2026-01-12",
        "product": "Desk Lamp",
        "category": "Electronics",
        "quantity": "1",
        "unit_price": "24.99",
    },
    {
        "order_date": "2026-02-02",
        "product": "Notebook",
        "category": "Stationery",
        "quantity": "5",
        "unit_price": "4.50",
    },
    {
        "order_date": "2026-02-15",
        "product": "USB Hub",
        "category": "Electronics",
        "quantity": "2",
        "unit_price": "18.75",
    },
]


def test_prepare_sales_data_adds_revenue_and_month():
    sales = prepare_sales_data(SAMPLE_ROWS)

    assert sales["revenue"].tolist() == pytest.approx(
        [13.50, 12.00, 24.99, 22.50, 37.50]
    )
    assert sales["month"].tolist() == [
        "2026-01",
        "2026-01",
        "2026-01",
        "2026-02",
        "2026-02",
    ]


def test_prepare_sales_data_removes_outer_text_spaces():
    row = SAMPLE_ROWS[0].copy()
    row["product"] = "  Notebook "
    row["category"] = " Stationery  "

    sales = prepare_sales_data([row])

    assert sales.loc[0, "product"] == "Notebook"
    assert sales.loc[0, "category"] == "Stationery"


def test_calculate_sales_metrics_returns_expected_totals():
    sales = prepare_sales_data(SAMPLE_ROWS)
    metrics = calculate_sales_metrics(sales)

    assert metrics["total_revenue"] == pytest.approx(110.49)
    assert metrics["revenue_by_category"] == pytest.approx(
        {"Electronics": 62.49, "Stationery": 48.00}
    )
    assert metrics["revenue_by_month"] == pytest.approx(
        {"2026-01": 50.49, "2026-02": 60.00}
    )
