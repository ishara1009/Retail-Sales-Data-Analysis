# Verified findings

The original UCI `Online Retail.xlsx` workbook was processed successfully. The
figures below come from the generated report tables and were reconciled against
the eligible line-level sales total.

## Data quality and retention

- Raw rows: **541,909**; cleaned rows after configured exact-duplicate removal:
  **536,641**.
- There were **10,147 rows involved in exact-duplicate groups** and **5,268
  duplicate rows were removed** (one copy of each group was retained).
- Eligible sales lines: **524,878**; explicit C-prefixed cancellation lines:
  **9,251**; review-flagged lines: **11,763**. These outputs can overlap.
- The cleaned data contained **10,587 negative-quantity lines**, **2,512
  zero/negative-price lines**, and **421 unresolved missing descriptions**.

## Eligible positive sales

- Total eligible sales value: **GBP 10,642,110.80**.
- Unique orders: **19,960**; identified customers: **4,338**.
- Invoice-level average order value: **GBP 533.17**.
- Known-customer segments: **2,845 repeat buyers** and **1,493 one-time buyers**.
- The highest product sales values were associated with StockCodes `DOT`
  (GBP 206,248.77), `22423` (GBP 174,156.54), and `23843`
  (GBP 168,469.60).
- The United Kingdom dominated eligible sales value (GBP 9,001,744.09), so
  country comparisons should also be examined with the UK separated.

## Cancellations and outliers

- The **9,251** cancellation lines represented **3,836** cancellation invoices
  and had a signed line value of **GBP -893,979.73**. This is reported
  separately; eligible positive sales are not described as net revenue.
- IQR analysis flagged **27,111 Quantity** outliers and **42,624 LineValue**
  outliers. Removing LineValue outliers would reduce the displayed sales total
  to GBP 5,083,662.44, showing that unusual large lines have substantial
  influence. They remain in the default summary because a large wholesale order
  can be valid.

## Interpretation cautions

The dataset begins in December 2010 and ends part-way through December 2011.
For example, December 2011 is an incomplete period, so its total should not be
compared naively with full months. Sales value is not profit because cost data
is unavailable. Customer features use eligible positive sales and are not net
of refunds.

