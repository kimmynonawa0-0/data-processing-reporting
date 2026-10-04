"""Local Streamlit interface for the sales reporting pipeline."""

from csv import Error as CsvError
from pathlib import Path

import pandas as pd
import streamlit as st

from data_processing_reporting.csv_reader import read_csv_bytes
from data_processing_reporting.pipeline import process_sales_data


OUTPUT_DIRECTORY = Path(__file__).resolve().parent / "outputs"


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


def show_analysis(result):
    """Display the cleaned data and calculated revenue metrics."""
    metrics = result["metrics"]
    st.success("Validation passed.")
    st.metric("Total revenue", f"{metrics['total_revenue']:.2f}")

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


def main():
    st.set_page_config(page_title="Sales Data Processing", layout="wide")
    st.title("Sales Data Processing and Reporting")
    st.write(
        "Upload one sales CSV to validate its data, calculate revenue, "
        "and download Excel and PDF reports."
    )

    uploaded_file = st.file_uploader("Upload a sales CSV", type="csv")
    if uploaded_file is None:
        st.info("The CSV must include order_date, product, category, quantity, and unit_price.")
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
        return

    show_analysis(result)


if __name__ == "__main__":
    main()
