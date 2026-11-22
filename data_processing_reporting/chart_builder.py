"""Build charts automatically from the inferred type of each column."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


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
