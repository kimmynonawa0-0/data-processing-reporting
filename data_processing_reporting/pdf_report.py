"""Export sales metrics as a one-page PDF report."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


def export_pdf_report(metrics, source_name, output_file: Path):
    """Create a PDF with the total and grouped revenue charts."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    categories = list(metrics["revenue_by_category"].keys())
    category_revenue = list(metrics["revenue_by_category"].values())
    months = list(metrics["revenue_by_month"].keys())
    monthly_revenue = list(metrics["revenue_by_month"].values())

    figure, charts = plt.subplots(2, 1, figsize=(8.27, 11.69))
    figure.suptitle("Sales Analysis Report", fontsize=18, fontweight="bold")
    figure.text(0.5, 0.93, f"Source: {source_name}", ha="center")
    figure.text(
        0.5,
        0.89,
        f"Total revenue: {metrics['total_revenue']:.2f}",
        ha="center",
        fontsize=14,
        fontweight="bold",
    )

    category_bars = charts[0].bar(categories, category_revenue, color="#4C78A8")
    charts[0].set_title("Revenue by Category")
    charts[0].set_ylabel("Revenue")
    charts[0].bar_label(category_bars, fmt="%.2f", padding=3)

    month_bars = charts[1].bar(months, monthly_revenue, color="#F58518")
    charts[1].set_title("Revenue by Month")
    charts[1].set_ylabel("Revenue")
    charts[1].bar_label(month_bars, fmt="%.2f", padding=3)

    for chart in charts:
        chart.grid(axis="y", linestyle="--", alpha=0.4)

    figure.text(
        0.5,
        0.03,
        "Amounts are assumed to use one currency because the source has no currency column.",
        ha="center",
        fontsize=9,
    )
    figure.tight_layout(rect=(0.06, 0.06, 0.96, 0.85))
    figure.savefig(output_file, format="pdf")
    plt.close(figure)

    return output_file
