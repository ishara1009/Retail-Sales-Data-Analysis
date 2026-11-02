# Retail Sales Data Analysis

A beginner-friendly Python project for cleaning, exploring, and visualizing the
[UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail).
It answers practical sales questions while keeping each function readable
enough to explain in an internship interview. Each source row is an **invoice
line item**; several rows may belong to one order.

## Learning coverage

| Topic | Where it is practised |
|---|---|
| NumPy | Percentile-based IQR bounds and `np.where` segmentation |
| Pandas | Loading, cleaning, filtering, grouping, pivot tables, CSV output |
| Matplotlib | Figure creation, labels, sizing, and saving |
| Seaborn | Bar, line, histogram, box, and heatmap charts |
| Data Cleaning | `cleaning.py` rules and before/after reports |
| Missing Values | Missing reports, identifier preservation, safe description fill |
| Outlier Detection | Separate Quantity and LineValue IQR flags |
| EDA | Business summary tables and five ordered notebooks |
| Feature Engineering | Transaction and customer features |
| Data Visualization | Eight saved charts in `reports/figures/` |

## Dataset setup

Download the original workbook from the official UCI page and place it at:

```text
data/raw/Online Retail.xlsx
```

The pipeline never edits this file. See [data/README.md](data/README.md) for
attribution and the dataset's CC BY 4.0 license. The repository's MIT license
applies only to the original project code.

## Installation

Python 3.10 or newer is recommended.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Run the project

```bash
python -m retail_analysis.pipeline
python -m pytest
jupyter notebook
```

Run notebooks `01` through `05` in order. They import the installed package, so
run `pip install -e .` first.

## Project structure

```text
data/                 Original input and generated processed CSVs
notebooks/            Five ordered learning notebooks
src/retail_analysis/  Reusable cleaning and analysis functions
reports/figures/      Generated charts
reports/tables/       Generated quality and business tables
tests/                Small synthetic unit tests
LEARNING_GUIDE_SI.md  Beginner-friendly learning and interview guide
```

## Cleaning rules

- Identifiers are strings; missing identifiers stay missing and never become
  the literal text `"nan"`.
- Whitespace is stripped and dates/numbers are parsed with invalid values
  converted to missing and flagged.
- A missing description is filled only if its StockCode has exactly one known
  description. CustomerID is never invented or imputed.
- Anonymous eligible lines remain in sales analysis but are excluded from
  customer features.
- An invoice starting with `C` (case-insensitive) is a cancellation. A negative
  quantity is inspected separately because not every negative line necessarily
  has the same meaning.
- Zero/negative prices, invalid values, negative quantities, and unresolved
  descriptions are flagged for review.
- Exact duplicates are counted first. `REMOVE_EXACT_DUPLICATES` in `config.py`
  controls removal; it defaults to `True`. Identical lines can sometimes be
  legitimate, so this decision is always reported.
- IQR outliers are flagged, not automatically removed. Large wholesale orders
  can be valid business activity.

The sales, cancellation, and flagged outputs may overlap. A flagged line is not
automatically excluded, and a cancellation is not the same as every negative
quantity line.

## Metric definitions

- **Eligible sales value:** `Quantity × UnitPrice` for positive-quantity,
  positive-price, non-cancellation lines with a valid date. Currency is GBP.
- **Unique orders:** unique InvoiceNo values among eligible sales.
- **Average order value:** mean of invoice-level totals, not mean line value.
- **Customer features:** eligible positive sales for known CustomerID values;
  they are not net of refunds.
- **Recency:** days from the customer's last purchase to one day after the
  latest eligible sales date, making results deterministic.
- **Cancellation value:** signed `Quantity × UnitPrice`, reported separately.

Sales value is not called profit because product cost is unavailable, and it is
not called net revenue because refunds are separate.

## Outputs

- `data/processed/`: cleaned, sales, cancellation, flagged, and customer CSVs.
- `reports/tables/`: quality, retention, outlier, metric, and EDA tables.
- `reports/figures/`: eight PNG charts created by Matplotlib and Seaborn.

## Limitations

- Customer behaviour excludes anonymous transactions.
- Eligible sales are not adjusted for refunds or costs.
- IQR flags indicate unusual values, not errors.
- The source period starts and ends part-way through calendar periods. Missing
  months are not inserted as zero, and incomplete months should not be compared
  naively with full months.
- Descriptions are labels; StockCode is the product grouping key.
- Identifier correlations are intentionally avoided because their numeric-like
  values have no meaningful scale.
- Findings in `reports/findings.md` are tied to the verified original workbook
  run; rerun the pipeline if the input or cleaning setting changes.

