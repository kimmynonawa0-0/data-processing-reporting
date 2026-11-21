"""Tests for reading CSV and Excel files through one interface."""

from io import BytesIO

import pandas as pd
import pytest

from data_processing_reporting.tabular_reader import (
    read_tabular,
    read_tabular_bytes,
)


def write_sample_csv(directory):
    csv_file = directory / "sample.csv"
    csv_file.write_text(
        "order_date,product,quantity\n"
        "2026-01-05,Notebook,3\n"
        "2026-01-08,Pen Set,2\n",
        encoding="utf-8",
    )
    return csv_file


def write_sample_excel(directory):
    excel_file = directory / "sample.xlsx"
    pd.DataFrame(
        {
            "order_date": ["2026-01-05", "2026-01-08"],
            "product": ["Notebook", "Pen Set"],
            "quantity": [3, 2],
        }
    ).to_excel(excel_file, index=False)
    return excel_file


def sample_excel_bytes():
    buffer = BytesIO()
    pd.DataFrame(
        {
            "order_date": ["2026-01-05", "2026-01-08"],
            "product": ["Notebook", "Pen Set"],
            "quantity": [3, 2],
        }
    ).to_excel(buffer, index=False)
    return buffer.getvalue()


def test_read_tabular_reads_csv_file(tmp_path):
    data = read_tabular(write_sample_csv(tmp_path))

    assert data["product"].tolist() == ["Notebook", "Pen Set"]
    assert data["quantity"].tolist() == [3, 2]


def test_read_tabular_reads_excel_file(tmp_path):
    data = read_tabular(write_sample_excel(tmp_path))

    assert data["product"].tolist() == ["Notebook", "Pen Set"]
    assert data["quantity"].tolist() == [3, 2]


def test_read_tabular_rejects_unsupported_file_type(tmp_path):
    text_file = tmp_path / "notes.txt"
    text_file.write_text("not a table", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported file type"):
        read_tabular(text_file)


def test_read_tabular_bytes_reads_csv():
    data = read_tabular_bytes(
        b"order_date,product\n2026-01-05,Notebook\n",
        "sample.csv",
    )

    assert data["product"].tolist() == ["Notebook"]


def test_read_tabular_bytes_reads_excel():
    data = read_tabular_bytes(sample_excel_bytes(), "sample.xlsx")

    assert data["product"].tolist() == ["Notebook", "Pen Set"]


def test_read_tabular_bytes_rejects_unsupported_file_type():
    with pytest.raises(ValueError, match="Unsupported file type"):
        read_tabular_bytes(b"not a table", "notes.txt")


def test_empty_csv_raises_a_clear_error():
    with pytest.raises(ValueError, match="contains no data"):
        read_tabular_bytes(b"", "empty.csv")
