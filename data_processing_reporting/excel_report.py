"""Export analyzed sales data to an Excel workbook."""

from pathlib import Path

import pandas as pd


def create_summary_table(metrics):
    """Arrange the calculated metrics as rows for an Excel sheet."""
    summary_rows = [
        {
            "section": "Overall",
            "label": "Total revenue",
            "revenue": metrics["total_revenue"],
        }
    ]

    for category, revenue in metrics["revenue_by_category"].items():
        summary_rows.append(
            {"section": "Category", "label": category, "revenue": revenue}
        )

    for month, revenue in metrics["revenue_by_month"].items():
        summary_rows.append(
            {"section": "Month", "label": month, "revenue": revenue}
        )

    return pd.DataFrame(summary_rows)


def export_excel_report(sales, metrics, output_file: Path):
    """Write cleaned sales data and summary metrics to an Excel workbook."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    summary = create_summary_table(metrics)

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        sales.to_excel(writer, sheet_name="Cleaned Data", index=False)
        summary.to_excel(writer, sheet_name="Summary", index=False)

    return output_file
