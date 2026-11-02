"""Run the complete retail analysis in an easy-to-follow order."""

import pandas as pd

from retail_analysis.analysis import (
    cancellation_summary,
    customer_segment_counts,
    invoice_values,
    key_metrics,
    monthly_sales,
    outlier_influence,
    top_countries,
    top_products,
    weekday_hour_sales,
)
from retail_analysis.cleaning import clean_transactions, split_transaction_sets
from retail_analysis.config import PROCESSED_DIR, TABLES_DIR
from retail_analysis.data_loader import load_retail_data, save_table
from retail_analysis.features import add_transaction_features, create_customer_features
from retail_analysis.outliers import add_outlier_flags
from retail_analysis.validation import data_quality_report, issue_counts
from retail_analysis.visualization import create_all_charts


def run_pipeline() -> None:
    """Load, clean, feature, analyse, export, and visualize the real dataset."""
    print("1/7 Loading the original workbook...")
    raw = load_retail_data()
    before_quality = data_quality_report(raw, "Before cleaning")

    print("2/7 Cleaning and classifying transaction lines...")
    cleaned, duplicate_stats = clean_transactions(raw)
    after_quality = data_quality_report(cleaned, "After cleaning")
    sales, cancellations, flagged = split_transaction_sets(cleaned)

    print("3/7 Creating transaction and customer features...")
    cleaned = add_transaction_features(cleaned)
    sales = add_transaction_features(sales)
    cancellations = add_transaction_features(cancellations)
    flagged = add_transaction_features(flagged)
    sales, thresholds = add_outlier_flags(sales)
    customers = create_customer_features(sales)

    print("4/7 Saving processed datasets...")
    save_table(cleaned, PROCESSED_DIR / "cleaned_transactions.csv")
    save_table(sales, PROCESSED_DIR / "sales_transactions.csv")
    save_table(cancellations, PROCESSED_DIR / "cancellation_transactions.csv")
    save_table(flagged, PROCESSED_DIR / "flagged_transactions.csv")
    save_table(customers, PROCESSED_DIR / "customer_features.csv")

    print("5/7 Saving quality and business summary tables...")
    quality = pd.concat([before_quality, after_quality], ignore_index=True)
    retention = pd.DataFrame(
        {
            "Dataset": ["Raw", "Cleaned", "Eligible sales", "Cancellations", "Flagged"],
            "RowCount": [len(raw), len(cleaned), len(sales), len(cancellations), len(flagged)],
        }
    )
    duplicate_table = pd.DataFrame(
        {"Metric": duplicate_stats.keys(), "Value": duplicate_stats.values()}
    )
    tables = {
        "data_quality_report.csv": quality,
        "issue_counts.csv": issue_counts(cleaned),
        "retention_counts.csv": retention,
        "duplicate_handling.csv": duplicate_table,
        "outlier_thresholds.csv": thresholds,
        "key_metrics.csv": key_metrics(sales),
        "monthly_sales.csv": monthly_sales(sales),
        "top_products_quantity.csv": top_products(sales, by="Quantity"),
        "top_products_value.csv": top_products(sales, by="LineValue"),
        "top_countries_value.csv": top_countries(sales),
        "weekday_hour_sales.csv": weekday_hour_sales(sales).reset_index(),
        "customer_segments.csv": customer_segment_counts(customers),
        "invoice_values.csv": invoice_values(sales),
        "cancellation_summary.csv": cancellation_summary(cancellations),
        "outlier_influence.csv": outlier_influence(sales),
    }
    for filename, table in tables.items():
        save_table(table, TABLES_DIR / filename)

    # Reconciliation: grouped monthly sales must equal line-level eligible sales.
    total = sales["LineValue"].sum()
    monthly_total = tables["monthly_sales.csv"]["LineValue"].sum()
    if not abs(total - monthly_total) < 0.01:
        raise RuntimeError("Sales reconciliation failed: monthly totals do not match.")

    print("6/7 Creating charts...")
    create_all_charts(before_quality, sales, customers)
    print("7/7 Complete. Outputs are in data/processed and reports/.")


if __name__ == "__main__":
    run_pipeline()

