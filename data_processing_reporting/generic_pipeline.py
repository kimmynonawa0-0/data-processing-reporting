"""Run the shared profile, clean, and chart workflow for generic files."""

from pathlib import Path

from .chart_builder import build_charts
from .cleaner import clean_data
from .excel_report import export_generic_excel_report
from .pdf_report import export_generic_pdf_report
from .profiler import profile_data


def export_cleaned_csv(cleaned, output_file: Path):
    """Write the cleaned data to a CSV file."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(output_file, index=False)

    return output_file


def process_generic_data(data, source_name, output_directory: Path):
    """Profile, clean, chart, and export any tabular dataset."""
    if data.empty:
        return {
            "status": "failed",
            "issues": ["The file contains no data rows."],
            "profile": None,
            "audit": None,
            "cleaned": None,
            "charts": [],
            "cleaned_csv": "",
            "cleaned_excel": "",
            "pdf_report": "",
        }

    profile = profile_data(data)
    cleaned, audit = clean_data(data)
    charts = build_charts(
        cleaned,
        profile["column_types"],
        profile["high_cardinality_columns"],
    )

    source_stem = Path(source_name).stem
    cleaned_csv = output_directory / f"{source_stem}_cleaned.csv"
    cleaned_excel = output_directory / f"{source_stem}_cleaned.xlsx"
    pdf_output = output_directory / f"{source_stem}_report.pdf"

    export_cleaned_csv(cleaned, cleaned_csv)
    export_generic_excel_report(cleaned, audit, cleaned_excel)
    export_generic_pdf_report(profile, audit, charts, source_name, pdf_output)

    return {
        "status": "success",
        "issues": [],
        "profile": profile,
        "audit": audit,
        "cleaned": cleaned,
        "charts": charts,
        "cleaned_csv": cleaned_csv,
        "cleaned_excel": cleaned_excel,
        "pdf_report": pdf_output,
    }
