"""Export sales metrics and generic cleaning results as PDF reports."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def export_pdf_report(metrics, source_name, output_file: Path):
    """Create a PDF with the headline KPIs and grouped revenue charts."""
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
        0.90,
        f"Total revenue: {metrics['total_revenue']:.2f}",
        ha="center",
        fontsize=14,
        fontweight="bold",
    )
    figure.text(
        0.5,
        0.87,
        (
            f"Units: {metrics['total_units']} | Rows: {metrics['row_count']} | "
            f"Average order value: {metrics['average_order_value']:.2f} | "
            f"Products: {metrics['unique_products']}"
        ),
        ha="center",
        fontsize=11,
    )
    figure.text(
        0.5,
        0.845,
        f"Order dates: {metrics['date_range'][0]} to {metrics['date_range'][1]}",
        ha="center",
        fontsize=11,
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

    top_products = list(metrics["revenue_by_product"].items())[:5]
    top_products_line = "Top products: " + ", ".join(
        f"{product} ({revenue:.2f})" for product, revenue in top_products
    )
    figure.text(0.5, 0.055, top_products_line, ha="center", fontsize=9)

    figure.text(
        0.5,
        0.03,
        "Amounts are assumed to use one currency because the source has no currency column.",
        ha="center",
        fontsize=9,
    )
    figure.tight_layout(rect=(0.06, 0.10, 0.96, 0.85))
    figure.savefig(output_file, format="pdf")
    plt.close(figure)

    return output_file


def export_generic_pdf_report(profile, audit, charts, source_name, output_file):
    """Create a PDF with the cleaning summary and auto-generated charts."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    column_lines = [
        f"- {column} ({column_type})"
        for column, column_type in profile["column_types"].items()
    ]

    fill_lines = [
        f"- {fill['column']}: {fill['count']} filled using "
        f"{fill['method']} ({fill['value']})"
        for fill in audit["nulls_filled"]
    ]
    if not fill_lines:
        fill_lines = ["- None"]

    remaining_lines = [
        f"- {column}: {count}"
        for column, count in audit["nulls_remaining"].items()
    ]
    if not remaining_lines:
        remaining_lines = ["- None"]

    trimmed = ", ".join(audit["columns_trimmed"]) or "None"

    cell_count = profile["row_count"] * len(profile["columns"])
    null_count = sum(profile["null_counts"].values())
    null_share = f"{null_count / cell_count * 100:.1f}%" if cell_count else "0%"

    summary_lines = [
        f"Rows before cleaning: {audit['rows_before']}",
        f"Rows after cleaning: {audit['rows_after']}",
        f"Duplicate rows dropped: {audit['duplicates_dropped']}",
        f"Text columns trimmed: {trimmed}",
        f"Missing cells before cleaning: {null_share}",
        "",
        "Columns:",
        *column_lines,
        "",
        "Nulls filled:",
        *fill_lines,
        "",
        "Nulls remaining:",
        *remaining_lines,
    ]

    with PdfPages(output_file) as pdf:
        figure = plt.figure(figsize=(8.27, 11.69))
        figure.text(
            0.5,
            0.95,
            "Data Cleaning Report",
            ha="center",
            fontsize=18,
            fontweight="bold",
        )
        figure.text(
            0.5,
            0.91,
            f"Source: {source_name}",
            ha="center",
            fontsize=11,
        )
        figure.text(
            0.08,
            0.85,
            "\n".join(summary_lines),
            va="top",
            fontsize=11,
        )
        pdf.savefig(figure)
        plt.close(figure)

        for chart, _ in charts:
            pdf.savefig(chart)
            plt.close(chart)

    return output_file
