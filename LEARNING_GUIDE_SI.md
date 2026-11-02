# Retail Sales Data Analysis — සිංහල ඉගෙනුම් මාර්ගෝපදේශය

මෙම project එකේ අරමුණ UCI Online Retail data භාවිතයෙන් Python data
analysis ක්‍රියාවලිය මුල සිට අගට සරලව ඉගෙන ගැනීමයි. Excel file එකේ එක් row
එකක් සම්පූර්ණ order එකක් නොව **invoice line item** එකකි. එකම InvoiceNo එකට
rows කිහිපයක් තිබිය හැක.

## Data ගමන් කරන ආකාරය

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

`flagged` record එකක් අනිවාර්යයෙන්ම ඉවත් කරන්නේ නැහැ. උදාහරණයක් ලෙස විශාල
wholesale order එක IQR outlier එකක් වුවත් සැබෑ sale එකක් විය හැක. එසේම
cancellation එකක් සහ negative quantity ඇති සෑම line එකක්ම එකම අදහස නොවේ.

## Python files වල කාර්යය

- `config.py`: project-relative paths, required columns, weekday order සහ
  duplicate setting තබයි.
- `data_loader.py`: `pd.read_excel(..., engine="openpyxl")` මගින් original file
  එක කියවා CSV tables save කරයි.
- `validation.py`: columns අඩුද කියා පරීක්ෂා කර data types, missing counts සහ
  percentages report කරයි.
- `cleaning.py`: identifiers clean කිරීම, numbers/dates parse කිරීම,
  descriptions ආරක්ෂිතව fill කිරීම සහ review flags නිර්මාණය කරයි.
- `outliers.py`: `np.percentile()` භාවිතයෙන් Q1, Q3, IQR සහ bounds ගණනය කර
  Quantity/LineValue flags වෙන වෙනම එකතු කරයි.
- `features.py`: transaction calendar features සහ customer summaries සාදයි.
- `analysis.py`: business metrics සහ groupby/pivot summary tables සාදයි.
- `visualization.py`: Matplotlib figure සහ Seaborn charts PNG ලෙස save කරයි.
- `pipeline.py`: ඉහත පියවර නිවැරදි පිළිවෙළට run කර outputs reconcile කරයි.

## වැදගත් functions

| Function | Input | Output |
|---|---|---|
| `load_retail_data` | Excel path | raw DataFrame |
| `clean_transactions` | raw DataFrame, duplicate Boolean | cleaned DataFrame, statistics |
| `split_transaction_sets` | cleaned DataFrame | sales, cancellations, flagged |
| `add_transaction_features` | transaction rows | LineValue සහ date features සමඟ rows |
| `create_customer_features` | eligible sales | එක් CustomerID එකකට summary row එකක් |
| `calculate_iqr_bounds` | numeric Series | Q1, Q3, IQR, lower/upper bounds |
| `add_outlier_flags` | eligible sales | flagged sales, threshold table |
| `run_pipeline` | local workbook | සියලු CSV, table සහ chart outputs |

## Pandas සහ NumPy මූලික අදහස්

- `data.loc[mask]`: Boolean condition එකකට ගැළපෙන rows filter කරයි.
- `pd.to_numeric(..., errors="coerce")`: parse කළ නොහැකි value එක `NaN` කරයි;
  එය පසුව flag කළ හැක.
- `pd.to_datetime(..., errors="coerce")`: invalid date එක `NaT` කරයි.
- `groupby(...).agg(...)`: එකම customer/product/invoice එකට අදාළ rows
  summary එකකට එකතු කරයි.
- `pivot_table(...)`: weekday × hour වැනි දෙමාන summary table එකක් සාදයි.
- `nunique()`: duplicate invoice lines තිබුණත් unique orders ගණන් කරයි.
- `np.percentile(values, [25, 75])`: Q1 සහ Q3 ලබාගෙන IQR ගණනය කරයි.
- `np.where(condition, A, B)`: loop එකක් නැතිව segment label තෝරයි.
- `plt.figure(...)`: Matplotlib canvas එක සාදයි; `sns.barplot()` වැනි Seaborn
  function එක එහි readable statistical chart එක අඳියි.
- `plt.close()`: chart save කළ පසු memory නිදහස් කරයි.

## Missing values සහ outliers වෙනස් ඇයි?

Missing CustomerID එකක් කියන්නේ customer කවුදැයි නොදන්නා බවයි. Sale value එක
හරි නම් එය overall sales analysis එකේ තබා ගත හැකි නමුත් customer analysis එකේ
භාවිත කළ නොහැක. එයට mean/mode ID එකක් දැමීම අසත්‍ය customer කෙනෙක් නිර්මාණය
කිරීමකි.

Outlier එකක් කියන්නේ අනෙක් values වලට වඩා දුරින් ඇති value එකකි; missing value
එකක් නොවේ. විශාල Quantity එක wholesale order එකක් විය හැකි නිසා default totals
වලින් එය ඉවත් නොකර, flag කර එහි බලපෑම වෙනම compare කරයි. IQR zero නම් values
මැද 50% එකම වන බව report එකේ `ZeroIQR=1` ලෙස පෙන්වයි.

## Invoice lines සහ orders

`LineValue = Quantity × UnitPrice` යනු line එකක value එකයි. Order value ලබා
ගැනීමට එකම `InvoiceNo` ඇති lines sum කළ යුතුයි. Average Order Value ගණනය
කරන්නේ invoice totals වල mean එක ලෙසයි; line values වල mean එක නොවේ.

## Interview ප්‍රශ්න 10ක් සහ කෙටි පිළිතුරු

1. **CustomerID string එකක් කරන්නේ ඇයි?** — එය ගණිතමය ප්‍රමාණයක් නොව
   identifier එකක් නිසා සහ missing value ආරක්ෂා කිරීමටයි.
2. **Anonymous sales ඉවත් නොකරන්නේ ඇයි?** — customer කවුදැයි නොදැනුණත් sale
   එකේ quantity, price සහ date business totals සඳහා ප්‍රයෝජනවත් නිසායි.
3. **Cancellation හඳුනාගන්නේ කොහොමද?** — InvoiceNo එක `C` අකුරෙන් ආරම්භදැයි
   case-insensitive ලෙස බලයි.
4. **Negative quantity සියල්ල cancellation ද?** — නැහැ. C-prefix නැති negative
   line වෙනත් correction එකක් විය හැකි නිසා වෙනම flag කරයි.
5. **Exact duplicates remove කිරීම අවදානම් ඇයි?** — සමාන භාණ්ඩ දෙවරක් scan
   කළ සැබෑ lines දෙකක් ද එකම විය හැකි නිසා setting එක configurable කරයි.
6. **IQR method එක කුමක්ද?** — Q1/Q3 අතර දුර IQR ලෙස ගෙන 1.5×IQR පිටත values
   flag කිරීමයි.
7. **Outliers default total එකෙන් ඉවත් කළාද?** — නැහැ; business-valid wholesale
   orders විය හැකි නිසා influence comparison එකක් පමණක් කරයි.
8. **Recency අද දිනයෙන් නොගන්නේ ඇයි?** — run කරන දවස අනුව result වෙනස් නොවීමට
   latest eligible sale එකෙන් දින එකක් පසු fixed reference එක භාවිත කරයි.
9. **Sales value එක profit නොවන්නේ ඇයි?** — product cost data නොමැති නිසා profit
   ගණනය කළ නොහැක.
10. **Missing month එක zero ලෙස නොදමන්නේ ඇයි?** — data නැති බව zero sales බවට
    සාක්ෂියක් නොවන නිසා සහ first/last periods incomplete විය හැකි නිසායි.

## Practical exercises 5ක්

1. `REMOVE_EXACT_DUPLICATES=False` කර duplicate report සහ totals වෙනස්වීම බලන්න.
2. එක් StockCode එකක් filter කර Quantity සහ LineValue history එක plot කරන්න.
3. UK සහ non-UK eligible sales monthly groupby දෙකක් compare කරන්න.
4. IQR multiplier 1.5 සිට 3.0 කර outlier counts වෙනස්වීම පැහැදිලි කරන්න.
5. `customer_features.csv` භාවිතයෙන් highest AverageOrderValue customers 10 දෙනා
   සොයා OrderCount සමඟ interpret කරන්න.

Notebook `01` සිට `05` දක්වා පිළිවෙළින් run කරන්න. ඒවා run කිරීමට පෙර
`python -m pip install -e .` ක්‍රියාත්මක කළ යුතුයි.

