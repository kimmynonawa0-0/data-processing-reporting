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


def test_process_csv_reports_success(tmp_path, capsys):
    outputs = tmp_path / "outputs"
    input_file = write_csv(tmp_path, "orders.csv", VALID_ROWS)

    result = cli.process_csv(input_file, outputs)
    output = capsys.readouterr().out

    assert result["status"] == "success"
    assert "Total revenue: 13.50" in output
    assert "Total units: 3" in output
    assert (outputs / "orders_report.xlsx").exists()
    assert (outputs / "orders_report.pdf").exists()


def test_process_csv_reports_validation_failure(tmp_path):
    outputs = tmp_path / "outputs"
    input_file = write_csv(
        tmp_path,
        "bad.csv",
        "order_date,product\n2026-01-05,Notebook\n",
    )

    result = cli.process_csv(input_file, outputs)

    assert result["status"] == "validation_failed"
    assert not (outputs / "bad_report.xlsx").exists()
    assert not (outputs / "bad_report.pdf").exists()


def test_main_processes_folder_and_writes_log(tmp_path, capsys, monkeypatch):
    outputs = tmp_path / "outputs"
    log_file = outputs / "processing_log.csv"
    data_folder = tmp_path / "data"
    data_folder.mkdir()
    write_csv(data_folder, "sample.csv", VALID_ROWS)
    monkeypatch.setattr(
        "sys.argv",
        [
            "data_processing_reporting",
            str(data_folder),
            "--output-directory",
            str(outputs),
        ],
    )

    exit_code = cli.main()

    assert exit_code == 0
    assert "Done: 1 succeeded, 0 failed." in capsys.readouterr().out
    with log_file.open(encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))
    assert len(rows) == 1
    assert rows[0]["status"] == "success"


def test_main_returns_one_when_a_file_fails(tmp_path, capsys, monkeypatch):
    outputs = tmp_path / "outputs"
    log_file = outputs / "processing_log.csv"
    data_folder = tmp_path / "data"
    data_folder.mkdir()
    write_csv(
        data_folder,
        "bad.csv",
        "order_date,product\n2026-01-05,Notebook\n",
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "data_processing_reporting",
            str(data_folder),
            "--output-directory",
            str(outputs),
        ],
    )

    exit_code = cli.main()

    assert exit_code == 1
    assert "Done: 0 succeeded, 1 failed." in capsys.readouterr().out
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


def test_get_arguments_reads_output_directory(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "data_processing_reporting",
            str(tmp_path / "data.csv"),
            "--output-directory",
            str(tmp_path / "reports"),
        ],
    )

    arguments = cli.get_arguments()

    assert arguments.input_path == tmp_path / "data.csv"
    assert arguments.output_directory == tmp_path / "reports"


def test_find_csv_files_accepts_one_csv_file(tmp_path):
    csv_file = write_csv(tmp_path, "one.csv", VALID_ROWS)

    assert cli.find_csv_files(csv_file) == [csv_file]


def test_find_csv_files_scans_nested_folders(tmp_path):
    outer = tmp_path / "data"
    inner = outer / "2026"
    inner.mkdir(parents=True)
    first = write_csv(outer, "a.csv", VALID_ROWS)
    second = write_csv(inner, "b.csv", VALID_ROWS)
    (inner / "notes.txt").write_text("not a CSV", encoding="utf-8")

    files = cli.find_csv_files(outer)

    assert files == sorted([first, second])


def test_find_csv_files_returns_nothing_for_unknown_path(tmp_path):
    assert cli.find_csv_files(tmp_path / "missing") == []


def test_process_generic_file_cleans_and_charts(tmp_path, capsys):
    outputs = tmp_path / "outputs"
    input_file = write_csv(
        tmp_path,
        "messy.csv",
        "order_date,price,product\n"
        "2026-01-05,4.50,Pen\n"
        "2026-01-05,4.50,Pen\n"
        "2026-01-08,,Paper\n",
    )

    result = cli.process_generic_file(input_file, outputs)
    output = capsys.readouterr().out

    assert result["status"] == "success"
    assert "Rows before cleaning: 3" in output
    assert "Rows after cleaning: 2" in output
    assert "- price: 1 filled using median (4.5)" in output
    assert (outputs / "messy_cleaned.csv").exists()
    assert (outputs / "messy_cleaned.xlsx").exists()
    assert (outputs / "messy_report.pdf").exists()


def test_process_generic_file_reports_empty_files(tmp_path):
    outputs = tmp_path / "outputs"
    input_file = write_csv(tmp_path, "empty.csv", "price\n")

    result = cli.process_generic_file(input_file, outputs)

    assert result["status"] == "failed"


def test_main_generic_processes_folder_and_writes_log(
    tmp_path, capsys, monkeypatch
):
    outputs = tmp_path / "outputs"
    log_file = outputs / "processing_log.csv"
    data_folder = tmp_path / "data"
    data_folder.mkdir()
    write_csv(
        data_folder,
        "messy.csv",
        "price,product\n4.50,Pen\n4.50,Pen\n6.00,Paper\n",
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "data_processing_reporting",
            str(data_folder),
            "--generic",
            "--output-directory",
            str(outputs),
        ],
    )

    exit_code = cli.main()

    assert exit_code == 0
    assert "Done: 1 succeeded, 0 failed." in capsys.readouterr().out
    with log_file.open(encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))
    assert len(rows) == 1
    assert rows[0]["status"] == "success"
