"""Tests for the PDF report summaries."""

from data_processing_reporting.pdf_report import build_cleaning_kpis


def test_cleaning_kpis_summarize_the_audit():
    profile = {
        "row_count": 4,
        "columns": ["name", "amount"],
        "null_counts": {"name": 1, "amount": 1},
    }
    audit = {
        "rows_before": 6,
        "rows_after": 4,
        "duplicates_dropped": 2,
        "nulls_filled": [
            {
                "column": "amount",
                "count": 2,
                "method": "median",
                "value": 10.0,
            }
        ],
    }

    kpis = build_cleaning_kpis(profile, audit)

    assert kpis == [
        ("Rows before", 6),
        ("Rows after", 4),
        ("Duplicates dropped", 2),
        ("Nulls filled", 2),
        ("Missing cells", "25.0%"),
    ]


def test_cleaning_kpis_handle_an_empty_profile():
    profile = {
        "row_count": 0,
        "columns": [],
        "null_counts": {},
    }
    audit = {
        "rows_before": 0,
        "rows_after": 0,
        "duplicates_dropped": 0,
        "nulls_filled": [],
    }

    kpis = build_cleaning_kpis(profile, audit)

    assert kpis[-1] == ("Missing cells", "0%")
