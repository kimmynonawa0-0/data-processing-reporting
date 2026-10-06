"""Prepare sales data and calculate its metrics."""

import pandas as pd


def prepare_sales_data(rows):
    """Convert validated CSV rows into analysis-ready sales data."""
    sales = pd.DataFrame(rows)

    sales["product"] = sales["product"].str.strip()
    sales["category"] = sales["category"].str.strip()
    sales["order_date"] = pd.to_datetime(sales["order_date"])
    sales["quantity"] = pd.to_numeric(sales["quantity"])
    sales["unit_price"] = pd.to_numeric(sales["unit_price"])
    sales["revenue"] = (sales["quantity"] * sales["unit_price"]).round(2)
    sales["month"] = sales["order_date"].dt.strftime("%Y-%m")

    return sales


def calculate_sales_metrics(sales):
    """Return total revenue and revenue grouped by category and month."""
    revenue_by_category = (
        sales.groupby("category")["revenue"].sum().round(2).to_dict()
    )
    revenue_by_month = (
        sales.groupby("month")["revenue"].sum().round(2).to_dict()
    )

    return {
        "total_revenue": round(float(sales["revenue"].sum()), 2),
        "revenue_by_category": revenue_by_category,
        "revenue_by_month": revenue_by_month,
    }
