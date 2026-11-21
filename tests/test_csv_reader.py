"""Tests for CSV reading helpers."""

from data_processing_reporting.csv_reader import read_csv, read_csv_bytes


def test_read_csv_returns_columns_and_rows(tmp_path):
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        "order_date,product\n2026-01-05,Notebook\n",
        encoding="utf-8",
    )

    columns, rows = read_csv(csv_file)

    assert columns == ["order_date", "product"]
    assert rows == [{"order_date": "2026-01-05", "product": "Notebook"}]


def test_read_csv_bytes_returns_columns_and_rows():
    columns, rows = read_csv_bytes(
        b"order_date,product\n2026-01-05,Notebook\n"
    )

    assert columns == ["order_date", "product"]
    assert rows == [{"order_date": "2026-01-05", "product": "Notebook"}]


def test_read_csv_bytes_ignores_utf8_bom():
    columns, rows = read_csv_bytes(
        b"\xef\xbb\xbforder_date,product\n2026-01-05,Notebook\n"
    )

    assert columns == ["order_date", "product"]


def test_empty_csv_has_no_columns_or_rows():
    columns, rows = read_csv_bytes(b"")

    assert columns == []
    assert rows == []
