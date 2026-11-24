"""Local Streamlit interface for the sales and generic cleaning workflows."""

from csv import Error as CsvError
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from data_processing_reporting.csv_reader import read_csv_bytes
from data_processing_reporting.generic_pipeline import process_generic_data
from data_processing_reporting.pipeline import process_sales_data
from data_processing_reporting.processing_log import append_upload_result
from data_processing_reporting.tabular_reader import read_tabular_bytes


OUTPUT_DIRECTORY = Path(__file__).resolve().parent / "outputs"
PROCESSING_LOG = OUTPUT_DIRECTORY / "processing_log.csv"


def show_downloads(result):
    """Show buttons for the generated Excel and PDF reports."""
    excel_report = result["excel_report"]
    pdf_report = result["pdf_report"]
    excel_column, pdf_column = st.columns(2)

    with excel_column:
        st.download_button(
            "Download Excel report",
            data=excel_report.read_bytes(),
            file_name=excel_report.name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    with pdf_column:
        st.download_button(
            "Download PDF report",
            data=pdf_report.read_bytes(),
            file_name=pdf_report.name,
            mime="application/pdf",
        )


def show_kpi_row(metrics):
    """Show the headline sales numbers as a row of metrics."""
    revenue_column, units_column, order_column, products_column = st.columns(4)

    revenue_column.metric("Total revenue", f"{metrics['total_revenue']:.2f}")
    units_column.metric("Total units", f"{metrics['total_units']}")
    order_column.metric(
        "Average order value", f"{metrics['average_order_value']:.2f}"
    )
    products_column.metric("Unique products", f"{metrics['unique_products']}")


def show_analysis(result):
    """Display the cleaned data and calculated revenue metrics."""
    metrics = result["metrics"]
    st.success("Validation passed.")
    show_kpi_row(metrics)
    st.caption(
        f"Orders from {metrics['date_range'][0]} to {metrics['date_range'][1]}"
    )

    category_chart = pd.Series(
        metrics["revenue_by_category"], name="Revenue"
    )
    monthly_chart = pd.Series(metrics["revenue_by_month"], name="Revenue")

    st.subheader("Revenue by category")
    st.bar_chart(category_chart)
    st.subheader("Revenue by month")
    st.bar_chart(monthly_chart)

    st.subheader("Cleaned data")
    st.dataframe(result["sales"], use_container_width=True)
    show_downloads(result)


def show_generic_downloads(result):
    """Show buttons for the cleaned CSV, Excel, and PDF report."""
    cleaned_csv = result["cleaned_csv"]
    cleaned_excel = result["cleaned_excel"]
    pdf_report = result["pdf_report"]
    csv_column, excel_column, pdf_column = st.columns(3)

    with csv_column:
        st.download_button(
            "Download cleaned CSV",
            data=cleaned_csv.read_bytes(),
            file_name=cleaned_csv.name,
            mime="text/csv",
        )

    with excel_column:
        st.download_button(
            "Download cleaned Excel",
            data=cleaned_excel.read_bytes(),
            file_name=cleaned_excel.name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    with pdf_column:
        st.download_button(
            "Download PDF report",
            data=pdf_report.read_bytes(),
            file_name=pdf_report.name,
            mime="application/pdf",
        )


def show_cleaning_summary(result):
    """Display the cleaning audit, cleaned data, and charts."""
    profile = result["profile"]
    audit = result["audit"]

    st.success("Cleaning complete.")
    before_column, dropped_column, after_column = st.columns(3)
    before_column.metric("Rows before", audit["rows_before"])
    dropped_column.metric("Duplicates dropped", audit["duplicates_dropped"])
    after_column.metric("Rows after", audit["rows_after"])

    if audit["columns_trimmed"]:
        st.write(f"Text trimmed in: {', '.join(audit['columns_trimmed'])}")

    if audit["nulls_filled"]:
        st.subheader("Nulls filled")
        fill_rows = [
            {
                "Column": fill["column"],
                "Method": fill["method"],
                "Value": fill["value"],
                "Filled": fill["count"],
            }
            for fill in audit["nulls_filled"]
        ]
        st.dataframe(pd.DataFrame(fill_rows), use_container_width=True)

    if audit["nulls_remaining"]:
        st.warning(
            "Some nulls could not be filled: "
            + ", ".join(
                f"{column} ({count})"
                for column, count in audit["nulls_remaining"].items()
            )
        )

    if profile["high_cardinality_columns"]:
        st.caption(
            "Not charted (too many unique values): "
            + ", ".join(profile["high_cardinality_columns"])
        )

    st.subheader("Cleaned data")
    st.dataframe(result["cleaned"], use_container_width=True)

    st.subheader("Charts")
    if result["charts"]:
        for _, chart in result["charts"]:
            st.pyplot(chart)
    else:
        st.info("No charts could be generated for this file.")

    show_generic_downloads(result)


def show_sales_upload():
    """Run the sales CSV upload workflow."""
    uploaded_file = st.file_uploader("Upload a sales CSV", type="csv")
    if uploaded_file is None:
        st.info(
            "The CSV must include order_date, product, category, "
            "quantity, and unit_price."
        )
        return

    try:
        columns, rows = read_csv_bytes(uploaded_file.getvalue())
    except (UnicodeDecodeError, CsvError) as error:
        st.error(f"The CSV could not be read: {error}")
        return

    st.caption(f"{uploaded_file.name}: {len(rows)} data rows")
    result = process_sales_data(
        columns,
        rows,
        uploaded_file.name,
        OUTPUT_DIRECTORY,
    )

    if result["issues"]:
        st.error("The file has validation issues. Reports were not generated.")
        for issue in result["issues"]:
            st.write(f"- {issue}")
        append_upload_result(
            PROCESSING_LOG, uploaded_file.name, len(rows), result
        )
        return

    show_analysis(result)
    append_upload_result(PROCESSING_LOG, uploaded_file.name, len(rows), result)


def show_cleaner_upload():
    """Run the generic clean-and-chart upload workflow."""
    uploaded_file = st.file_uploader(
        "Upload a CSV or Excel file", type=["csv", "xlsx"]
    )
    if uploaded_file is None:
        st.info(
            "The file can have any columns. Cleaning and charts are "
            "chosen automatically by column type."
        )
        return

    try:
        data = read_tabular_bytes(uploaded_file.getvalue(), uploaded_file.name)
    except ValueError as error:
        st.error(f"The file could not be read: {error}")
        return

    st.caption(f"{uploaded_file.name}: {len(data)} data rows")
    result = process_generic_data(data, uploaded_file.name, OUTPUT_DIRECTORY)

    if result["status"] == "failed":
        st.error("The file could not be processed.")
        for issue in result["issues"]:
            st.write(f"- {issue}")
        append_upload_result(
            PROCESSING_LOG,
            uploaded_file.name,
            len(data),
            {
                "status": "failed",
                "issues": result["issues"],
                "excel_report": "",
                "pdf_report": "",
            },
        )
        return

    show_cleaning_summary(result)
    append_upload_result(
        PROCESSING_LOG,
        uploaded_file.name,
        result["profile"]["row_count"],
        {
            "status": "success",
            "issues": [],
            "excel_report": result["cleaned_excel"],
            "pdf_report": result["pdf_report"],
        },
    )


def main():
    st.set_page_config(page_title="Data Analytics Automation", layout="wide")
    st.title("Data Analytics Automation")

    sales_tab, cleaner_tab = st.tabs(["Sales Reports", "Data Cleaner"])

    with sales_tab:
        st.write(
            "Upload one sales CSV to validate its data, calculate revenue, "
            "and download Excel and PDF reports."
        )
        show_sales_upload()

    with cleaner_tab:
        st.write(
            "Upload any CSV or Excel file to profile it, clean it, "
            "and generate charts automatically."
        )
        show_cleaner_upload()


if __name__ == "__main__":
    main()
