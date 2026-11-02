"""Create and save the project charts with Matplotlib and Seaborn."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from retail_analysis.analysis import invoice_values, weekday_hour_sales
from retail_analysis.config import FIGURES_DIR


def _save(path: Path) -> None:
    """Apply a tidy layout, save the current figure, and release its memory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def create_all_charts(
    before_quality: pd.DataFrame,
    sales: pd.DataFrame,
    customers: pd.DataFrame,
    output_dir: Path = FIGURES_DIR,
) -> None:
    """Generate all eight requested charts."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", palette="deep")

    missing = before_quality.sort_values("MissingPercent", ascending=False)
    plt.figure(figsize=(10, 5))
    sns.barplot(data=missing, x="MissingPercent", y="Column", color="#4C72B0")
    plt.title("Missing Values in Raw Data")
    plt.xlabel("Missing values (%)")
    plt.ylabel("Column")
    _save(output_dir / "01_missing_values.png")

    monthly = sales.groupby("YearMonth", as_index=False)["LineValue"].sum()
    plt.figure(figsize=(11, 5))
    sns.lineplot(data=monthly, x="YearMonth", y="LineValue", marker="o")
    plt.title("Monthly Eligible Sales Value")
    plt.xlabel("Month (reporting periods may be incomplete)")
    plt.ylabel("Sales value (GBP)")
    plt.xticks(rotation=45)
    _save(output_dir / "02_monthly_sales.png")

    product_labels = sales["StockCode"].astype(str)
    product_sales = (
        sales.assign(ProductLabel=product_labels)
        .groupby("ProductLabel", as_index=False)["LineValue"]
        .sum()
        .nlargest(10, "LineValue")
        .sort_values("LineValue")
    )
    plt.figure(figsize=(10, 6))
    sns.barplot(data=product_sales, x="LineValue", y="ProductLabel", color="#55A868")
    plt.title("Top 10 Products by Eligible Sales Value")
    plt.xlabel("Sales value (GBP)")
    plt.ylabel("StockCode")
    _save(output_dir / "03_top_products_value.png")

    country_sales = (
        sales.groupby("Country", dropna=False, as_index=False)["LineValue"]
        .sum()
        .nlargest(10, "LineValue")
        .sort_values("LineValue")
    )
    plt.figure(figsize=(10, 6))
    sns.barplot(data=country_sales, x="LineValue", y="Country", color="#C44E52")
    plt.title("Top 10 Countries by Eligible Sales Value")
    plt.xlabel("Sales value (GBP)")
    plt.ylabel("Country")
    _save(output_dir / "04_top_countries_value.png")

    orders = invoice_values(sales)
    plt.figure(figsize=(10, 5))
    # A log x-axis keeps common small orders visible beside a few very large ones.
    sns.histplot(orders["InvoiceValue"], bins=50, log_scale=True)
    plt.title("Invoice Value Distribution (Log Scale)")
    plt.xlabel("Invoice value (GBP, logarithmic scale)")
    plt.ylabel("Invoice count")
    _save(output_dir / "05_invoice_value_distribution.png")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sns.boxplot(y=sales["Quantity"], ax=axes[0], color="#8172B2")
    axes[0].set_title("Eligible Sales Quantity")
    axes[0].set_ylabel("Quantity")
    sns.boxplot(y=sales["LineValue"], ax=axes[1], color="#CCB974")
    axes[1].set_title("Eligible Sales Line Value")
    axes[1].set_ylabel("Line value (GBP)")
    _save(output_dir / "06_quantity_line_value_boxplots.png")

    heatmap_data = weekday_hour_sales(sales)
    plt.figure(figsize=(12, 6))
    sns.heatmap(heatmap_data, cmap="YlGnBu", fmt=".0f")
    plt.title("Eligible Sales by Weekday and Hour")
    plt.xlabel("Hour of day")
    plt.ylabel("Weekday")
    _save(output_dir / "07_weekday_hour_heatmap.png")

    segments = (
        customers["CustomerSegment"]
        .value_counts()
        .rename_axis("CustomerSegment")
        .reset_index(name="CustomerCount")
    )
    plt.figure(figsize=(8, 5))
    sns.barplot(data=segments, x="CustomerSegment", y="CustomerCount", color="#64B5CD")
    plt.title("One-time vs Repeat Customers")
    plt.xlabel("Customer segment")
    plt.ylabel("Customer count")
    _save(output_dir / "08_customer_segments.png")

