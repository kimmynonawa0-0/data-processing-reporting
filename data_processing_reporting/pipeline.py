"""Run the shared sales validation, analysis, and reporting workflow."""

from pathlib import Path

from .analysis import calculate_sales_metrics, prepare_sales_data
from .excel_report import export_excel_report
from .pdf_report import export_pdf_report
from .validation import find_data_issues


def process_sales_data(columns, rows, source_name, output_directory: Path):
    """Process validated rows and return data, metrics, and report paths."""
    issues = find_data_issues(columns, rows)

    if issues:
        return {
            "status": "validation_failed",
            "issues": issues,
            "sales": None,
            "metrics": None,
            "excel_report": "",
            "pdf_report": "",
        }

    sales = prepare_sales_data(rows)
    metrics = calculate_sales_metrics(sales)
    source_stem = Path(source_name).stem

    excel_output = output_directory / f"{source_stem}_report.xlsx"
    export_excel_report(sales, metrics, excel_output)

    pdf_output = output_directory / f"{source_stem}_report.pdf"
    export_pdf_report(metrics, source_name, pdf_output)

    return {
        "status": "success",
        "issues": [],
        "sales": sales,
        "metrics": metrics,
        "excel_report": excel_output,
        "pdf_report": pdf_output,
    }
