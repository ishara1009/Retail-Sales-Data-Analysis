"""Create transaction-level and customer-level features."""

import numpy as np
import pandas as pd


def add_transaction_features(data: pd.DataFrame) -> pd.DataFrame:
    """Add value and calendar fields to transaction lines."""
    featured = data.copy()
    featured["LineValue"] = featured["Quantity"] * featured["UnitPrice"]
    featured["YearMonth"] = featured["InvoiceDate"].dt.to_period("M").astype("string")
    featured["DayOfWeek"] = featured["InvoiceDate"].dt.day_name()
    featured["Hour"] = featured["InvoiceDate"].dt.hour.astype("Int64")
    return featured


def create_customer_features(sales: pd.DataFrame) -> pd.DataFrame:
    """Summarize eligible positive sales for customers with an identifier."""
    identified = sales.dropna(subset=["CustomerID"]).copy()
    if identified.empty:
        return pd.DataFrame(
            columns=[
                "CustomerID",
                "TotalPurchaseValue",
                "OrderCount",
                "AverageOrderValue",
                "LastPurchaseDate",
                "RecencyDays",
                "CustomerSegment",
            ]
        )

    reference_date = sales["InvoiceDate"].max().normalize() + pd.Timedelta(days=1)
    customers = (
        identified.groupby("CustomerID", as_index=False)
        .agg(
            TotalPurchaseValue=("LineValue", "sum"),
            OrderCount=("InvoiceNo", "nunique"),
            LastPurchaseDate=("InvoiceDate", "max"),
        )
    )
    customers["AverageOrderValue"] = (
        customers["TotalPurchaseValue"] / customers["OrderCount"]
    )
    customers["RecencyDays"] = (
        reference_date - customers["LastPurchaseDate"].dt.normalize()
    ).dt.days
    # np.where demonstrates vectorized conditional feature creation.
    customers["CustomerSegment"] = np.where(
        customers["OrderCount"].eq(1), "One-time buyer", "Repeat buyer"
    )
    return customers[
        [
            "CustomerID",
            "TotalPurchaseValue",
            "OrderCount",
            "AverageOrderValue",
            "LastPurchaseDate",
            "RecencyDays",
            "CustomerSegment",
        ]
    ].sort_values("TotalPurchaseValue", ascending=False, ignore_index=True)

