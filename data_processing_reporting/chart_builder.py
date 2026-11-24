"""Build charts automatically from the inferred type of each column."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

MAX_CATEGORY_BARS = 10
MAX_CHARTS = 6


def build_numeric_histogram(data, column):
    """Return a figure and title with a histogram of one numeric column."""
    values = pd.to_numeric(data[column], errors="coerce").dropna()

    if values.empty:
        return None

    figure, axis = plt.subplots(figsize=(8, 4))
    axis.hist(values, bins=20, color="#4C78A8", edgecolor="white")
    axis.set_title(f"Distribution of {column}")
    axis.set_xlabel(column)
    axis.set_ylabel("Frequency")
    axis.grid(axis="y", linestyle="--", alpha=0.4)
    figure.tight_layout()

    return figure, f"Distribution of {column}"


def build_monthly_line(data, column):
    """Return a figure and title with a monthly series for a date column."""
    dates = pd.to_datetime(data[column], errors="coerce").dropna()
    counts = dates.dt.to_period("M").value_counts().sort_index()

    if counts.empty:
        return None

    figure, axis = plt.subplots(figsize=(8, 4))
    months = counts.index.astype(str)
    axis.plot(months, counts.values, marker="o", color="#F58518")
    axis.set_title(f"Activity by month: {column}")
    axis.set_xlabel("Month")
    axis.set_ylabel("Rows")
    axis.grid(linestyle="--", alpha=0.4)
    plt.setp(axis.get_xticklabels(), rotation=45, ha="right")
    figure.tight_layout()

    return figure, f"Activity by month: {column}"


def build_category_bars(data, column, limit=MAX_CATEGORY_BARS):
    """Return a figure and title with the most common categories as bars."""
    counts = data[column].value_counts(dropna=True).head(limit)

    if counts.empty:
        return None

    figure, axis = plt.subplots(figsize=(8, 4))
    bars = axis.bar(counts.index.astype(str), counts.values, color="#54A24B")
    axis.set_title(f"Top categories: {column}")
    axis.set_ylabel("Count")
    axis.bar_label(bars, padding=3)
    axis.grid(axis="y", linestyle="--", alpha=0.4)
    plt.setp(axis.get_xticklabels(), rotation=45, ha="right")
    figure.tight_layout()

    return figure, f"Top categories: {column}"


def build_numeric_boxplot(data, column):
    """Return a figure and title with a box plot of one numeric column."""
    values = pd.to_numeric(data[column], errors="coerce").dropna()

    if values.empty:
        return None

    figure, axis = plt.subplots(figsize=(8, 4))
    axis.boxplot(
        values,
        orientation="horizontal",
        patch_artist=True,
        boxprops=dict(facecolor="#B6992D"),
    )
    axis.set_title(f"Spread of {column}")
    axis.set_xlabel(column)
    axis.set_yticks([])
    axis.grid(axis="x", linestyle="--", alpha=0.4)
    figure.tight_layout()

    return figure, f"Spread of {column}"


def build_numeric_scatter(data, first_column, second_column):
    """Return a figure and title with a scatter of two numeric columns."""
    pair = data[[first_column, second_column]].apply(
        pd.to_numeric, errors="coerce"
    ).dropna()

    if pair.empty:
        return None

    figure, axis = plt.subplots(figsize=(8, 4))
    axis.scatter(
        pair[first_column], pair[second_column], color="#54A24B", alpha=0.7
    )
    axis.set_title(f"{second_column} vs {first_column}")
    axis.set_xlabel(first_column)
    axis.set_ylabel(second_column)
    axis.grid(linestyle="--", alpha=0.4)
    figure.tight_layout()

    return figure, f"{second_column} vs {first_column}"


def build_correlation_heatmap(data, numeric_columns):
    """Return a figure and title with a correlation heatmap."""
    numeric = data[numeric_columns].apply(pd.to_numeric, errors="coerce")
    correlation = numeric.corr()

    figure, axis = plt.subplots(figsize=(6, 5))
    heatmap = axis.imshow(correlation, cmap="coolwarm", vmin=-1, vmax=1)
    figure.colorbar(heatmap, ax=axis)
    axis.set_xticks(
        range(len(numeric_columns)), numeric_columns, rotation=45, ha="right"
    )
    axis.set_yticks(range(len(numeric_columns)), numeric_columns)
    axis.set_title("Correlation of numeric columns")

    for row in range(len(numeric_columns)):
        for column in range(len(numeric_columns)):
            value = correlation.iloc[row, column]
            label = "–" if pd.isna(value) else f"{value:.2f}"
            axis.text(
                column, row, label, ha="center", va="center", fontsize=9
            )

    figure.tight_layout()

    return figure, "Correlation of numeric columns"


def build_charts(data, column_types, high_cardinality_columns=(), limit=MAX_CHARTS):
    """Return (title, figure) pairs for every chartable column."""
    charts = []
    numeric_columns = [
        column
        for column, column_type in column_types.items()
        if column_type == "numeric"
    ]

    for column, column_type in column_types.items():
        if len(charts) >= limit:
            break

        if column_type == "numeric":
            chart = build_numeric_histogram(data, column)
        elif column_type == "datetime":
            chart = build_monthly_line(data, column)
        elif (
            column_type == "categorical"
            and column not in high_cardinality_columns
        ):
            chart = build_category_bars(data, column)
        else:
            continue

        if chart:
            charts.append(chart)

    for column in numeric_columns:
        if len(charts) >= limit:
            break
        chart = build_numeric_boxplot(data, column)
        if chart:
            charts.append(chart)

    if len(numeric_columns) >= 2 and len(charts) < limit:
        chart = build_numeric_scatter(data, numeric_columns[0], numeric_columns[1])
        if chart:
            charts.append(chart)

    if len(numeric_columns) >= 2 and len(charts) < limit:
        chart = build_correlation_heatmap(data, numeric_columns)
        if chart:
            charts.append(chart)

    return charts
