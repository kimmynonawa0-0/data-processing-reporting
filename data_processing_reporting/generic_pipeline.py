"""Run the shared profile, clean, and chart workflow for generic files."""

from pathlib import Path

from .chart_builder import build_charts
from .cleaner import clean_data
from .profiler import profile_data


def process_generic_data(data, source_name, output_directory: Path):
    """Profile, clean, and chart any tabular dataset."""
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

    return {
        "status": "success",
        "issues": [],
        "profile": profile,
        "audit": audit,
        "cleaned": cleaned,
        "charts": charts,
        "cleaned_csv": "",
        "cleaned_excel": "",
        "pdf_report": "",
    }
