"""Tests for explicit transaction-cleaning decisions."""

import pandas as pd

from retail_analysis.cleaning import clean_transactions, split_transaction_sets
from retail_analysis.features import add_transaction_features, create_customer_features


def sample_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "InvoiceNo": ["100", "101", "C102", "103", "100"],
            "StockCode": ["A", "B", "C", "D", "A"],
            "Description": ["Item A", "Item B", "Item C", "Item D", "Item A"],
            "Quantity": [2, 1, -1, -3, 2],
            "InvoiceDate": pd.to_datetime(
                ["2021-01-01", "2021-01-02", "2021-01-03", "2021-01-04", "2021-01-01"]
            ),
            "UnitPrice": [5.0, 4.0, 4.0, 2.0, 5.0],
            "CustomerID": [pd.NA, "22", "22", "23", pd.NA],
            "Country": ["UK"] * 5,
        }
    )


def test_anonymous_sale_retained_but_not_customer_feature() -> None:
    cleaned, _ = clean_transactions(sample_data())
    sales, _, _ = split_transaction_sets(cleaned)
    sales = add_transaction_features(sales)
    customers = create_customer_features(sales)
    assert sales["CustomerID"].isna().any()
    assert not customers["CustomerID"].isna().any()
    assert set(customers["CustomerID"]) == {"22"}


def test_cancellation_excluded_and_negative_quantity_flagged() -> None:
    cleaned, _ = clean_transactions(sample_data())
    sales, cancellations, flagged = split_transaction_sets(cleaned)
    assert "C102" in set(cancellations["InvoiceNo"])
    assert "C102" not in set(sales["InvoiceNo"])
    assert cleaned.loc[cleaned["InvoiceNo"].eq("103"), "NegativeQuantity"].all()
    assert "103" in set(flagged["InvoiceNo"])


def test_duplicate_setting_is_respected() -> None:
    kept, kept_stats = clean_transactions(sample_data(), remove_exact_duplicates=False)
    removed, removed_stats = clean_transactions(sample_data(), remove_exact_duplicates=True)
    assert len(kept) == 5
    assert len(removed) == 4
    assert kept_stats["duplicate_rows_removed"] == 0
    assert removed_stats["duplicate_rows_removed"] == 1

