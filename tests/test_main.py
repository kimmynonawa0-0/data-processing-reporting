"""Tests for the command-line entry point."""

import csv

import data_processing_reporting.__main__ as cli


VALID_ROWS = (
    "order_date,product,category,quantity,unit_price\n"
    "2026-01-05,Notebook,Stationery,3,4.50\n"
)


def write_csv(folder, name, text):
    """Write a CSV file into a folder and return its path."""
    csv_file = folder / name
    csv_file.write_text(text, encoding="utf-8")
    return csv_file


def test_process_csv_reports_success(tmp_path, capsys, monkeypatch):
    outputs = tmp_path / "outputs"
    monkeypatch.setattr(cli, "OUTPUT_DIRECTORY", outputs)
    input_file = write_csv(tmp_path, "orders.csv", VALID_ROWS)

    result = cli.process_csv(input_file)
    output = capsys.readouterr().out

    assert result["status"] == "success"
    assert "Total revenue: 13.50" in output
    assert (outputs / "orders_report.xlsx").exists()
    assert (outputs / "orders_report.pdf").exists()


def test_process_csv_reports_validation_failure(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    monkeypatch.setattr(cli, "OUTPUT_DIRECTORY", outputs)
    input_file = write_csv(
        tmp_path,
        "bad.csv",
        "order_date,product\n2026-01-05,Notebook\n",
    )

    result = cli.process_csv(input_file)

    assert result["status"] == "validation_failed"
    assert not (outputs / "bad_report.xlsx").exists()
    assert not (outputs / "bad_report.pdf").exists()


def test_main_processes_folder_and_writes_log(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    log_file = outputs / "processing_log.csv"
    monkeypatch.setattr(cli, "OUTPUT_DIRECTORY", outputs)
    monkeypatch.setattr(cli, "PROCESSING_LOG", log_file)
    data_folder = tmp_path / "data"
    data_folder.mkdir()
    write_csv(data_folder, "sample.csv", VALID_ROWS)
    monkeypatch.setattr(
        "sys.argv", ["data_processing_reporting", str(data_folder)]
    )

    exit_code = cli.main()

    assert exit_code == 0
    with log_file.open(encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))
    assert len(rows) == 1
    assert rows[0]["status"] == "success"


def test_main_returns_one_when_a_file_fails(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    log_file = outputs / "processing_log.csv"
    monkeypatch.setattr(cli, "OUTPUT_DIRECTORY", outputs)
    monkeypatch.setattr(cli, "PROCESSING_LOG", log_file)
    data_folder = tmp_path / "data"
    data_folder.mkdir()
    write_csv(
        data_folder,
        "bad.csv",
        "order_date,product\n2026-01-05,Notebook\n",
    )
    monkeypatch.setattr(
        "sys.argv", ["data_processing_reporting", str(data_folder)]
    )

    exit_code = cli.main()

    assert exit_code == 1
    with log_file.open(encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))
    assert rows[0]["status"] == "validation_failed"


def test_main_reports_missing_input(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["data_processing_reporting", str(tmp_path / "missing")],
    )

    exit_code = cli.main()

    assert exit_code == 1
    assert "No CSV files found" in capsys.readouterr().out
