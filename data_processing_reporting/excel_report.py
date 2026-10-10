"""Export analyzed sales data to an Excel workbook."""

from pathlib import Path

import pandas as pd


def format_number_column(worksheet, header_name, number_format):
    """Apply an Excel number format to a column selected by its header."""
    header_cell = next(
        cell for cell in worksheet[1] if cell.value == header_name
    )

    for row in worksheet.iter_rows(
        min_row=2,
        min_col=header_cell.column,
        max_col=header_cell.column,
    ):
        row[0].number_format = number_format


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

        for worksheet in writer.sheets.values():
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions

        cleaned_data = writer.sheets["Cleaned Data"]
        summary_sheet = writer.sheets["Summary"]
        format_number_column(cleaned_data, "unit_price", "0.00")
        format_number_column(cleaned_data, "revenue", "0.00")
        format_number_column(summary_sheet, "revenue", "0.00")

    return output_file
