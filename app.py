"""Local Streamlit interface for the sales and generic cleaning workflows."""

import hashlib
from csv import Error as CsvError
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from data_processing_reporting.chart_builder import build_charts
from data_processing_reporting.csv_reader import read_csv_bytes
from data_processing_reporting.generic_pipeline import process_generic_data
from data_processing_reporting.pipeline import process_sales_data
from data_processing_reporting.processing_log import append_upload_result
from data_processing_reporting.tabular_reader import read_tabular_bytes


OUTPUT_DIRECTORY = Path(__file__).resolve().parent / "outputs"
PROCESSING_LOG = OUTPUT_DIRECTORY / "processing_log.csv"


@st.cache_data(show_spinner=False)
def run_sales_pipeline(columns, rows, source_name):
    """Process one sales upload once and reuse the result on reruns."""
    return process_sales_data(columns, rows, source_name, OUTPUT_DIRECTORY)


@st.cache_data(show_spinner=False)
def run_generic_pipeline(data, source_name):
    """Clean one generic upload once and reuse the result on reruns."""
    result = process_generic_data(data, source_name, OUTPUT_DIRECTORY)
    result["charts"] = []
    return result


def log_upload_once(uploaded_file, row_count, log_values):
    """Record an upload in the processing log only once per file."""
    file_key = hashlib.sha1(uploaded_file.getvalue()).hexdigest()
    logged_uploads = st.session_state.setdefault("logged_uploads", set())

    if file_key in logged_uploads:
        return

    append_upload_result(
        PROCESSING_LOG, uploaded_file.name, row_count, log_values
    )
    logged_uploads.add(file_key)


def show_download_button(column, label, report_path, mime):
    """Show one download button for a generated report."""
    with column:
        st.download_button(
            label,
            data=report_path.read_bytes(),
            file_name=report_path.name,
            mime=mime,
        )


def show_downloads(result):
    """Show buttons for the generated Excel and PDF reports."""
    excel_column, pdf_column = st.columns(2)

    show_download_button(
        excel_column,
        "Download Excel report",
        result["excel_report"],
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    show_download_button(
        pdf_column,
        "Download PDF report",
        result["pdf_report"],
        "application/pdf",
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


def build_sales_charts(metrics):
    """Build styled bar and trend charts for the sales metrics."""
    categories = list(metrics["revenue_by_category"].keys())
    category_revenue = list(metrics["revenue_by_category"].values())
    months = list(metrics["revenue_by_month"].keys())
    monthly_revenue = list(metrics["revenue_by_month"].values())

    category_figure, category_axis = plt.subplots(figsize=(8, 4))
    category_bars = category_axis.bar(
        categories, category_revenue, color="#4C78A8"
    )
    category_axis.set_title("Revenue by category")
    category_axis.set_ylabel("Revenue")
    category_axis.bar_label(category_bars, fmt="%.2f", padding=3)
    category_axis.grid(axis="y", linestyle="--", alpha=0.4)
    category_figure.tight_layout()

    month_figure, month_axis = plt.subplots(figsize=(8, 4))
    month_axis.plot(
        months, monthly_revenue, marker="o", color="#F58518"
    )
    month_axis.set_title("Revenue by month")
    month_axis.set_ylabel("Revenue")
    month_axis.grid(linestyle="--", alpha=0.4)
    month_figure.tight_layout()

    return category_figure, month_figure


def build_top_products_table(metrics):
    """Return the products ranked by revenue as a display table."""
    rows = [
        {"Product": product, "Revenue": revenue}
        for product, revenue in metrics["revenue_by_product"].items()
    ]
    return pd.DataFrame(rows)


def build_category_share_table(metrics):
    """Return each category's revenue and its share of the total."""
    total_revenue = metrics["total_revenue"]
    rows = [
        {
            "Category": category,
            "Revenue": revenue,
            "Share": f"{revenue / total_revenue * 100:.1f}%",
        }
        for category, revenue in metrics["revenue_by_category"].items()
    ]
    return pd.DataFrame(rows)


def show_analysis(result):
    """Display the cleaned data and calculated revenue metrics."""
    metrics = result["metrics"]
    st.success("Validation passed.")
    show_kpi_row(metrics)
    st.caption(
        f"Orders from {metrics['date_range'][0]} to {metrics['date_range'][1]}"
    )

    chart_column, detail_column = st.columns([3, 2])

    with chart_column:
        st.subheader("Revenue by category and month")
        category_figure, month_figure = build_sales_charts(metrics)
        category_plot, month_plot = st.columns(2)
        category_plot.pyplot(category_figure)
        month_plot.pyplot(month_figure)
        plt.close(category_figure)
        plt.close(month_figure)

    with detail_column:
        st.subheader("Top products")
        top_products = build_top_products_table(metrics)
        st.dataframe(top_products, width="stretch", hide_index=True)

        st.subheader("Category share")
        category_share = build_category_share_table(metrics)
        st.dataframe(category_share, width="stretch", hide_index=True)

    st.subheader("Cleaned data")
    st.dataframe(result["sales"], width="stretch")
    show_downloads(result)


def show_generic_downloads(result):
    """Show buttons for the cleaned CSV, Excel, and PDF report."""
    csv_column, excel_column, pdf_column = st.columns(3)

    show_download_button(
        csv_column,
        "Download cleaned CSV",
        result["cleaned_csv"],
        "text/csv",
    )
    show_download_button(
        excel_column,
        "Download cleaned Excel",
        result["cleaned_excel"],
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    show_download_button(
        pdf_column,
        "Download PDF report",
        result["pdf_report"],
        "application/pdf",
    )


def show_quality_card(profile):
    """Show a data quality overview card for the uploaded file."""
    null_count = sum(profile["null_counts"].values())
    cell_count = profile["row_count"] * len(profile["columns"])
    null_share = f"{null_count / cell_count * 100:.1f}%" if cell_count else "0%"

    type_mix = ", ".join(
        f"{name} ({count})"
        for name, count in pd.Series(profile["column_types"].values())
        .value_counts()
        .items()
    )

    st.subheader("Data quality")
    row_column, column_column, null_column, duplicate_column = st.columns(4)
    row_column.metric("Rows", profile["row_count"])
    column_column.metric("Columns", f"{len(profile['columns'])}")
    null_column.metric("Missing cells", null_share)
    duplicate_column.metric("Duplicate rows", profile["duplicate_rows"])
    st.caption(f"Column types: {type_mix}")


def show_chart_grid(charts):
    """Show the generated charts in a two-column responsive grid."""
    st.subheader("Charts")
    if not charts:
        st.info("No charts could be generated for this file.")
        return

    for index in range(0, len(charts), 2):
        left_column, right_column = st.columns(2)
        left_column.pyplot(charts[index][0])
        plt.close(charts[index][0])
        if index + 1 < len(charts):
            right_column.pyplot(charts[index + 1][0])
            plt.close(charts[index + 1][0])


def show_cleaning_summary(result):
    """Display the quality card, cleaning audit, charts, and cleaned data."""
    profile = result["profile"]
    audit = result["audit"]

    st.success("Cleaning complete.")
    before_column, dropped_column, after_column = st.columns(3)
    before_column.metric("Rows before", audit["rows_before"])
    dropped_column.metric("Duplicates dropped", audit["duplicates_dropped"])
    after_column.metric("Rows after", audit["rows_after"])

    show_quality_card(profile)

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

    with st.expander("Cleaning audit", expanded=True):
        if audit["columns_trimmed"]:
            st.write(
                f"Text trimmed in: {', '.join(audit['columns_trimmed'])}"
            )

        if audit["nulls_filled"]:
            st.write("Nulls filled")
            fill_rows = [
                {
                    "Column": fill["column"],
                    "Method": fill["method"],
                    "Value": fill["value"],
                    "Filled": fill["count"],
                }
                for fill in audit["nulls_filled"]
            ]
            st.dataframe(pd.DataFrame(fill_rows), width="stretch")

        if not audit["columns_trimmed"] and not audit["nulls_filled"]:
            st.info("No text trimming or null fills were needed.")

    show_chart_grid(result["charts"])

    with st.expander("Cleaned data"):
        st.dataframe(result["cleaned"], width="stretch")

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
    result = run_sales_pipeline(columns, rows, uploaded_file.name)

    if result["issues"]:
        st.error("The file has validation issues. Reports were not generated.")
        for issue in result["issues"]:
            st.write(f"- {issue}")
        log_upload_once(uploaded_file, len(rows), result)
        return

    show_analysis(result)
    log_upload_once(uploaded_file, len(rows), result)


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
    result = run_generic_pipeline(data, uploaded_file.name)

    if result["status"] == "failed":
        st.error("The file could not be processed.")
        for issue in result["issues"]:
            st.write(f"- {issue}")
        log_upload_once(
            uploaded_file,
            len(data),
            {
                "status": "failed",
                "issues": result["issues"],
                "excel_report": "",
                "pdf_report": "",
            },
        )
        return

    result["charts"] = build_charts(
        result["cleaned"],
        result["profile"]["column_types"],
        result["profile"]["high_cardinality_columns"],
    )
    show_cleaning_summary(result)
    log_upload_once(
        uploaded_file,
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
