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
    """Return total, average, and grouped revenue metrics for the sales."""
    revenue_by_category = (
        sales.groupby("category")["revenue"]
        .sum()
        .round(2)
        .sort_values(ascending=False, kind="stable")
        .to_dict()
    )
    revenue_by_month = (
        sales.groupby("month")["revenue"]
        .sum()
        .round(2)
        .sort_index()
        .to_dict()
    )
    revenue_by_product = (
        sales.groupby("product")["revenue"]
        .sum()
        .round(2)
        .sort_values(ascending=False, kind="stable")
        .to_dict()
    )

    total_revenue = round(float(sales["revenue"].sum()), 2)

    return {
        "total_revenue": total_revenue,
        "total_units": int(sales["quantity"].sum()),
        "row_count": len(sales),
        "unique_products": int(sales["product"].nunique()),
        "average_order_value": round(total_revenue / len(sales), 2),
        "date_range": [
            sales["order_date"].min().date().isoformat(),
            sales["order_date"].max().date().isoformat(),
        ],
        "revenue_by_category": revenue_by_category,
        "revenue_by_month": revenue_by_month,
        "revenue_by_product": revenue_by_product,
    }
