"""Tests for the automatic chart builders."""

import matplotlib.pyplot as plt
import pandas as pd

from data_processing_reporting.chart_builder import (
    MAX_CATEGORY_BARS,
    MAX_CHARTS,
    build_category_bars,
    build_charts,
    build_correlation_heatmap,
    build_monthly_line,
    build_numeric_histogram,
)


def close(chart):
    if chart:
        plt.close(chart[0])


def test_histogram_has_a_title_with_the_column_name():
    data = pd.DataFrame({"price": [1, 2, 3, 4, 5]})

    chart = build_numeric_histogram(data, "price")

    assert chart[1] == "Distribution of price"
    assert len(chart[0].axes) == 1
    close(chart)


def test_histogram_skips_an_empty_column():
    data = pd.DataFrame({"price": [None, None]})

    assert build_numeric_histogram(data, "price") is None


def test_monthly_line_counts_rows_per_month():
    data = pd.DataFrame(
        {"order_date": ["2026-01-05", "2026-01-08", "2026-02-15"]}
    )

    chart = build_monthly_line(data, "order_date")

    assert chart[1] == "Activity by month: order_date"
    line = chart[0].axes[0].lines[0]
    assert list(line.get_xdata()) == ["2026-01", "2026-02"]
    assert list(line.get_ydata()) == [2, 1]
    close(chart)


def test_monthly_line_skips_an_empty_column():
    data = pd.DataFrame({"order_date": [None, None]})

    assert build_monthly_line(data, "order_date") is None


def test_category_bars_show_the_most_common_categories():
    data = pd.DataFrame(
        {"category": ["Pen"] * 4 + ["Paper"] * 2 + ["Ink"] * 1}
    )

    chart = build_category_bars(data, "category")

    assert chart[1] == "Top categories: category"
    bars = chart[0].axes[0].patches
    assert [bar.get_height() for bar in bars] == [4, 2, 1]
    close(chart)


def test_category_bars_are_limited_to_the_top_categories():
    data = pd.DataFrame(
        {
            "category": [
                f"Category {number}" for number in range(MAX_CATEGORY_BARS + 5)
            ]
        }
    )

    chart = build_category_bars(data, "category")

    assert len(chart[0].axes[0].patches) == MAX_CATEGORY_BARS
    close(chart)


def test_correlation_heatmap_labels_each_pair():
    data = pd.DataFrame({"price": [1, 2, 3], "quantity": [3, 2, 1]})

    chart = build_correlation_heatmap(data, ["price", "quantity"])

    assert chart[1] == "Correlation of numeric columns"
    axis = chart[0].axes[0]
    labels = [text.get_text() for text in axis.texts]
    assert "1.00" in labels
    assert "-1.00" in labels
    close(chart)


def test_build_charts_uses_each_column_type():
    data = pd.DataFrame(
        {
            "order_date": ["2026-01-05", "2026-01-08", "2026-02-15"],
            "price": [4.5, 6.0, 24.99],
            "quantity": [3, 2, 1],
            "product": ["Pen", "Paper", "Ink"],
        }
    )

    charts = build_charts(
        data,
        {
            "order_date": "datetime",
            "price": "numeric",
            "quantity": "numeric",
            "product": "categorical",
        },
    )
    titles = [title for _, title in charts]

    assert titles == [
        "Activity by month: order_date",
        "Distribution of price",
        "Distribution of quantity",
        "Top categories: product",
        "Correlation of numeric columns",
    ]
    for _, chart in charts:
        plt.close(chart)


def test_build_charts_skips_high_cardinality_categories():
    data = pd.DataFrame({"product": [f"Item {number}" for number in range(30)]})

    charts = build_charts(data, {"product": "categorical"}, ["product"])

    assert charts == []


def test_build_charts_skips_columns_without_values():
    data = pd.DataFrame(
        {
            "order_date": [None, None],
            "price": [4.5, 6.0],
        }
    )

    charts = build_charts(data, {"order_date": "datetime", "price": "numeric"})

    assert len(charts) == 1
    for _, chart in charts:
        plt.close(chart)


def test_build_charts_stops_at_the_chart_limit():
    data = pd.DataFrame(
        {f"number_{index}": range(10) for index in range(MAX_CHARTS + 2)}
    )

    charts = build_charts(
        data, {column: "numeric" for column in data.columns}
    )

    assert len(charts) == MAX_CHARTS
    for _, chart in charts:
        plt.close(chart)
