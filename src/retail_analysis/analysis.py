"""Calculate business summaries from eligible sales."""

import pandas as pd

from retail_analysis.config import WEEKDAY_ORDER


def invoice_values(sales: pd.DataFrame) -> pd.DataFrame:
    """Aggregate invoice lines into order values."""
    return (
        sales.groupby("InvoiceNo", as_index=False)
        .agg(InvoiceValue=("LineValue", "sum"), InvoiceDate=("InvoiceDate", "min"))
    )


def key_metrics(sales: pd.DataFrame) -> pd.DataFrame:
    """Return the main sales metrics, with average value computed per invoice."""
    orders = invoice_values(sales)
    metrics = {
        "TotalEligibleSalesGBP": sales["LineValue"].sum(),
        "UniqueOrders": sales["InvoiceNo"].nunique(),
        "IdentifiedCustomers": sales["CustomerID"].nunique(),
        "AverageOrderValueGBP": orders["InvoiceValue"].mean(),
    }
    return pd.DataFrame({"Metric": metrics.keys(), "Value": metrics.values()})


def monthly_sales(sales: pd.DataFrame) -> pd.DataFrame:
    return sales.groupby("YearMonth", as_index=False)["LineValue"].sum()


def top_products(sales: pd.DataFrame, by: str = "LineValue", n: int = 10) -> pd.DataFrame:
    """Group products by StockCode and use one description only as a label."""
    descriptions = (
        sales.dropna(subset=["Description"])
        .drop_duplicates("StockCode")
        .set_index("StockCode")["Description"]
    )
    grouped = sales.groupby("StockCode", as_index=False).agg(
        Quantity=("Quantity", "sum"), LineValue=("LineValue", "sum")
    )
    grouped["Description"] = grouped["StockCode"].map(descriptions)
    return grouped.nlargest(n, by).reset_index(drop=True)


def top_countries(sales: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        sales.groupby("Country", dropna=False, as_index=False)["LineValue"]
        .sum()
        .nlargest(n, "LineValue")
        .reset_index(drop=True)
    )


def weekday_hour_sales(sales: pd.DataFrame) -> pd.DataFrame:
    table = sales.pivot_table(
        index="DayOfWeek", columns="Hour", values="LineValue", aggfunc="sum"
    )
    return table.reindex(WEEKDAY_ORDER)


def customer_segment_counts(customers: pd.DataFrame) -> pd.DataFrame:
    return (
        customers["CustomerSegment"]
        .value_counts()
        .rename_axis("CustomerSegment")
        .reset_index(name="CustomerCount")
    )


def cancellation_summary(cancellations: pd.DataFrame) -> pd.DataFrame:
    """Report explicit C-prefixed cancellations and their signed line values."""
    values = cancellations.copy()
    values["SignedLineValue"] = values["Quantity"] * values["UnitPrice"]
    return pd.DataFrame(
        {
            "Metric": ["CancellationLines", "CancellationInvoices", "SignedLineValueGBP"],
            "Value": [
                len(values),
                values["InvoiceNo"].nunique(),
                values["SignedLineValue"].sum(),
            ],
        }
    )


def outlier_influence(sales: pd.DataFrame) -> pd.DataFrame:
    """Compare default totals with totals after excluding flagged line-value outliers."""
    return pd.DataFrame(
        {
            "Summary": ["All eligible sales", "Excluding LineValue IQR outliers"],
            "SalesValueGBP": [
                sales["LineValue"].sum(),
                sales.loc[~sales["LineValueOutlier"], "LineValue"].sum(),
            ],
            "RowCount": [len(sales), int((~sales["LineValueOutlier"]).sum())],
        }
    )

