"""Read tabular data from CSV and Excel files through one interface."""

from io import BytesIO
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError

SUPPORTED_SUFFIXES = [".csv", ".xlsx"]


def check_file_type(suffix):
    """Return a supported lower-case suffix or raise a clear error."""
    file_type = suffix.lower()

    if file_type not in SUPPORTED_SUFFIXES:
        raise ValueError(
            f"Unsupported file type '{file_type}'. "
            f"Supported file types: {', '.join(SUPPORTED_SUFFIXES)}"
        )

    return file_type


def read_buffer(buffer, file_type):
    """Return a DataFrame read from one open buffer."""
    if file_type == ".csv":
        return pd.read_csv(buffer, encoding="utf-8-sig")

    return pd.read_excel(buffer, sheet_name=0)


def read_tabular(file_path: Path):
    """Return a DataFrame read from a CSV or Excel file."""
    file_type = check_file_type(file_path.suffix)

    try:
        return read_buffer(file_path, file_type)
    except EmptyDataError as error:
        raise ValueError("The file contains no data.") from error


def read_tabular_bytes(file_bytes, file_name):
    """Return a DataFrame read from uploaded CSV or Excel bytes."""
    file_type = check_file_type(Path(file_name).suffix)

    try:
        return read_buffer(BytesIO(file_bytes), file_type)
    except EmptyDataError as error:
        raise ValueError("The file contains no data.") from error
