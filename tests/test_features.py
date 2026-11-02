"""Tests for transaction and customer feature calculations."""

import pandas as pd

from retail_analysis.features import add_transaction_features, create_customer_features


def featured_sales() -> pd.DataFrame:
    sales = pd.DataFrame(
        {
            "InvoiceNo": ["100", "100", "101", "200"],
            "StockCode": ["A", "B", "C", "A"],
            "Description": ["A", "B", "C", "A"],
            "Quantity": [2, 1, 4, 1],
            "InvoiceDate": pd.to_datetime(
                [
                    "2021-01-01 10:00",
                    "2021-01-01 10:00",
                    "2021-01-05 11:00",
                    "2021-01-10 00:00",
                ]
            ),
            "UnitPrice": [5.0, 3.0, 2.0, 7.0],
            "CustomerID": ["1", "1", "1", "2"],
            "Country": ["UK"] * 4,
        }
    )
    return add_transaction_features(sales)


def test_line_value_is_quantity_times_unit_price() -> None:
    sales = featured_sales()
    assert sales["LineValue"].tolist() == [10.0, 3.0, 8.0, 7.0]


def test_unique_orders_and_average_order_value() -> None:
    customers = create_customer_features(featured_sales()).set_index("CustomerID")
    assert customers.loc["1", "OrderCount"] == 2
    assert customers.loc["1", "TotalPurchaseValue"] == 21.0
    assert customers.loc["1", "AverageOrderValue"] == 10.5
    assert customers.loc["1", "CustomerSegment"] == "Repeat buyer"


def test_recency_uses_day_after_latest_eligible_sale() -> None:
    customers = create_customer_features(featured_sales()).set_index("CustomerID")
    assert customers.loc["1", "RecencyDays"] == 6
    assert customers.loc["2", "RecencyDays"] == 1

