"""Export sales and generic cleaning results to Excel workbooks."""

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
            "value": metrics["total_revenue"],
        },
        {
            "section": "Overall",
            "label": "Total units",
            "value": metrics["total_units"],
        },
        {
            "section": "Overall",
            "label": "Average order value",
            "value": metrics["average_order_value"],
        },
        {
            "section": "Overall",
            "label": "Unique products",
            "value": metrics["unique_products"],
        },
        {
            "section": "Overall",
            "label": "Date range",
            "value": (
                f"{metrics['date_range'][0]} to {metrics['date_range'][1]}"
            ),
        },
    ]

    for product, revenue in metrics["revenue_by_product"].items():
        summary_rows.append(
            {"section": "Product", "label": product, "value": revenue}
        )

    for category, revenue in metrics["revenue_by_category"].items():
        summary_rows.append(
            {"section": "Category", "label": category, "value": revenue}
        )

    for month, revenue in metrics["revenue_by_month"].items():
        summary_rows.append(
            {"section": "Month", "label": month, "value": revenue}
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
        format_number_column(cleaned_data, "order_date", "yyyy-mm-dd")
        format_number_column(cleaned_data, "unit_price", "0.00")
        format_number_column(cleaned_data, "revenue", "0.00")
        format_number_column(summary_sheet, "value", "0.00")

        integer_labels = {"Total units", "Unique products"}
        for row in summary_sheet.iter_rows(min_row=2):
            if row[1].value in integer_labels:
                row[2].number_format = "0"

    return output_file


def create_audit_table(audit):
    """Arrange the cleaning audit as rows for an Excel sheet."""
    rows = [
        {
            "section": "Rows",
            "label": "Before cleaning",
            "value": audit["rows_before"],
        },
        {
            "section": "Rows",
            "label": "After cleaning",
            "value": audit["rows_after"],
        },
        {
            "section": "Rows",
            "label": "Duplicates dropped",
            "value": audit["duplicates_dropped"],
        },
    ]

    for column in audit["columns_trimmed"]:
        rows.append({"section": "Text", "label": "Trimmed", "value": column})

    for fill in audit["nulls_filled"]:
        rows.append(
            {
                "section": "Nulls",
                "label": fill["column"],
                "value": (
                    f"{fill['count']} filled using {fill['method']}"
                    f" ({fill['value']})"
                ),
            }
        )

    for column, count in audit["nulls_remaining"].items():
        rows.append(
            {
                "section": "Nulls",
                "label": column,
                "value": f"{count} could not be filled",
            }
        )

    return pd.DataFrame(rows)


def export_generic_excel_report(cleaned, audit, output_file: Path):
    """Write cleaned data and the cleaning audit to an Excel workbook."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    audit_table = create_audit_table(audit)

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        cleaned.to_excel(writer, sheet_name="Cleaned Data", index=False)
        audit_table.to_excel(writer, sheet_name="Cleaning Audit", index=False)

        for worksheet in writer.sheets.values():
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions

    return output_file
