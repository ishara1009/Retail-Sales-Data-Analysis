# Retail Sales Data Analysis — Learning Guide

This project teaches a complete Python data-analysis workflow using the UCI
Online Retail dataset. Each row in the Excel file is an **invoice line item**,
not necessarily a complete order. Several rows can share the same InvoiceNo.

## How data moves through the project

```text
Online Retail.xlsx
        ↓ load + validate
raw DataFrame
        ↓ normalize + flags
cleaned_transactions.csv
        ├── eligible positive sales → sales_transactions.csv
        ├── C-prefixed invoices → cancellation_transactions.csv
        └── review flags → flagged_transactions.csv
                    ↓ features + IQR + groupby
customer_features.csv + report tables + charts
```

A `flagged` record is not removed automatically. For example, a large wholesale
order can be a valid sale even if it is an IQR outlier. A cancellation and every
line with a negative quantity also do not necessarily mean the same thing.

## Purpose of each Python file

- `config.py`: Stores project-relative paths, required columns, weekday order,
  and the duplicate-removal setting.
- `data_loader.py`: Reads the original file with
  `pd.read_excel(..., engine="openpyxl")` and saves CSV tables.
- `validation.py`: Checks for missing columns and reports data types, missing
  counts, and missing percentages.
- `cleaning.py`: Cleans identifiers, parses numbers and dates, safely fills
  descriptions, and creates review flags.
- `outliers.py`: Uses `np.percentile()` to calculate Q1, Q3, IQR, and bounds,
  then adds separate Quantity and LineValue flags.
- `features.py`: Creates transaction calendar features and customer summaries.
- `analysis.py`: Produces business metrics and groupby/pivot summary tables.
- `visualization.py`: Creates Matplotlib figures and Seaborn charts and saves
  them as PNG files.
- `pipeline.py`: Runs all stages in the correct order and reconciles outputs.

## Important functions

| Function | Input | Output |
|---|---|---|
| `load_retail_data` | Excel path | Raw DataFrame |
| `clean_transactions` | Raw DataFrame and duplicate Boolean | Cleaned DataFrame and statistics |
| `split_transaction_sets` | Cleaned DataFrame | Sales, cancellations, and flagged rows |
| `add_transaction_features` | Transaction rows | Rows with LineValue and date features |
| `create_customer_features` | Eligible sales | One summary row per CustomerID |
| `calculate_iqr_bounds` | Numeric Series | Q1, Q3, IQR, and lower/upper bounds |
| `add_outlier_flags` | Eligible sales | Flagged sales and threshold table |
| `run_pipeline` | Local workbook | All CSV, table, and chart outputs |

## Core Pandas and NumPy operations

- `data.loc[mask]`: Filters rows that match a Boolean condition.
- `pd.to_numeric(..., errors="coerce")`: Converts values that cannot be parsed
  to `NaN`, allowing the code to flag them later.
- `pd.to_datetime(..., errors="coerce")`: Converts invalid dates to `NaT`.
- `groupby(...).agg(...)`: Combines rows for the same customer, product, or
  invoice into a summary.
- `pivot_table(...)`: Builds a two-dimensional summary such as weekday × hour.
- `nunique()`: Counts unique orders even when an invoice has several lines.
- `np.percentile(values, [25, 75])`: Returns Q1 and Q3 for the IQR calculation.
- `np.where(condition, A, B)`: Selects a segment label without a Python loop.
- `plt.figure(...)`: Creates a Matplotlib canvas; a Seaborn function such as
  `sns.barplot()` draws a readable statistical chart on it.
- `plt.close()`: Releases figure memory after the chart has been saved.

## Why missing values and outliers need different decisions

A missing CustomerID means the customer is unknown. If the sales information is
otherwise valid, the row can remain in overall sales analysis, but it cannot be
used for customer-level analysis. Filling it with a mean or mode would invent a
false customer identity.

An outlier is a value far from the other observations; it is not a missing
value. A high Quantity may represent a real wholesale order. Therefore, the
project flags outliers and compares their influence instead of removing them
from default totals. If the IQR is zero, the report sets `ZeroIQR=1`, indicating
that the middle 50% of values are identical.

## Invoice lines and orders

`LineValue = Quantity × UnitPrice` is the value of one invoice line. To find an
order value, all lines with the same `InvoiceNo` must be summed. Average Order
Value is calculated as the mean of invoice totals, not the mean of line values.

## Ten interview questions and answers

1. **Why is CustomerID converted to a string?** — It is an identifier rather
   than a mathematical quantity, and string handling preserves missing values.
2. **Why are anonymous sales retained?** — Quantity, price, and date can still
   contribute to valid business totals even when the customer is unknown.
3. **How is a cancellation identified?** — The code checks whether InvoiceNo
   starts with `C`, case-insensitively.
4. **Is every negative quantity a cancellation?** — No. A negative line without
   a C prefix may be another correction, so it is flagged separately.
5. **Why can removing exact duplicates be risky?** — Two legitimate scanned
   lines can look identical, so the decision is controlled by a setting.
6. **What is the IQR method?** — It calculates the distance between Q1 and Q3
   and flags values outside the 1.5 × IQR bounds.
7. **Are outliers removed from the default total?** — No. They may be valid
   wholesale orders, so only a separate influence comparison is produced.
8. **Why is today's date not used for recency?** — The fixed reference date is
   one day after the latest eligible sale, making the result reproducible.
9. **Why is sales value not called profit?** — Product cost data is unavailable,
   so profit cannot be calculated.
10. **Why is a missing month not filled with zero?** — Missing data is not proof
    of zero sales, and the first or last reporting periods may be incomplete.

## Five practical exercises

1. Set `REMOVE_EXACT_DUPLICATES=False` and examine the changes in duplicate
   reporting and sales totals.
2. Filter one StockCode and plot its Quantity and LineValue history.
3. Compare monthly eligible sales for the UK and non-UK countries.
4. Change the IQR multiplier from 1.5 to 3.0 and explain the change in counts.
5. Use `customer_features.csv` to find the ten customers with the highest
   AverageOrderValue and interpret their OrderCount values.

Run notebooks `01` through `05` in order. Before opening them, run
`python -m pip install -e .` from the project root.

