"""Normalize transaction fields and apply explicit cleaning rules."""

import pandas as pd

from retail_analysis.config import REMOVE_EXACT_DUPLICATES
from retail_analysis.validation import validate_required_columns


def _clean_identifier(series: pd.Series) -> pd.Series:
    """Strip identifiers while preserving missing values as pd.NA."""
    cleaned = series.astype("string").str.strip()
    # Excel commonly reads CustomerID as a float because the column has blanks.
    cleaned = cleaned.str.replace(r"\.0$", "", regex=True)
    return cleaned.mask(cleaned.eq(""), pd.NA)


def _fill_known_descriptions(data: pd.DataFrame) -> pd.Series:
    """Fill a missing description only for an unambiguous StockCode mapping."""
    known = data.dropna(subset=["StockCode", "Description"])
    description_counts = known.groupby("StockCode")["Description"].nunique()
    unambiguous_codes = description_counts[description_counts == 1].index
    description_map = (
        known[known["StockCode"].isin(unambiguous_codes)]
        .drop_duplicates("StockCode")
        .set_index("StockCode")["Description"]
    )
    return data["Description"].fillna(data["StockCode"].map(description_map))


def clean_transactions(
    data: pd.DataFrame,
    remove_exact_duplicates: bool = REMOVE_EXACT_DUPLICATES,
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Normalize values, add review flags, and optionally remove exact duplicates."""
    validate_required_columns(data)
    cleaned = data.copy()
    duplicate_candidates = int(cleaned.duplicated(keep=False).sum())
    duplicate_rows_removed = 0

    if remove_exact_duplicates:
        before = len(cleaned)
        cleaned = cleaned.drop_duplicates().copy()
        duplicate_rows_removed = before - len(cleaned)

    for column in ["InvoiceNo", "StockCode", "CustomerID"]:
        cleaned[column] = _clean_identifier(cleaned[column])

    cleaned["Description"] = cleaned["Description"].astype("string").str.strip()
    cleaned["Description"] = cleaned["Description"].mask(
        cleaned["Description"].eq(""), pd.NA
    )
    cleaned["Country"] = cleaned["Country"].astype("string").str.strip()
    cleaned["Country"] = cleaned["Country"].mask(cleaned["Country"].eq(""), pd.NA)

    original_quantity = cleaned["Quantity"].copy()
    original_price = cleaned["UnitPrice"].copy()
    original_date = cleaned["InvoiceDate"].copy()
    cleaned["Quantity"] = pd.to_numeric(cleaned["Quantity"], errors="coerce")
    cleaned["UnitPrice"] = pd.to_numeric(cleaned["UnitPrice"], errors="coerce")
    cleaned["InvoiceDate"] = pd.to_datetime(
        cleaned["InvoiceDate"], errors="coerce", format="mixed"
    )

    cleaned["InvalidQuantity"] = original_quantity.notna() & cleaned["Quantity"].isna()
    cleaned["InvalidUnitPrice"] = original_price.notna() & cleaned["UnitPrice"].isna()
    cleaned["InvalidDate"] = original_date.notna() & cleaned["InvoiceDate"].isna()
    cleaned["IsCancellation"] = cleaned["InvoiceNo"].str.upper().str.startswith(
        "C", na=False
    )
    cleaned["NegativeQuantity"] = cleaned["Quantity"].lt(0).fillna(False)
    cleaned["ZeroQuantity"] = cleaned["Quantity"].eq(0).fillna(False)
    cleaned["ZeroOrNegativePrice"] = cleaned["UnitPrice"].le(0).fillna(False)

    cleaned["Description"] = _fill_known_descriptions(cleaned)
    cleaned["MissingDescription"] = cleaned["Description"].isna()

    cleaned["NeedsReview"] = (
        cleaned["InvoiceNo"].isna()
        | cleaned["StockCode"].isna()
        | cleaned["Quantity"].isna()
        | cleaned["UnitPrice"].isna()
        | cleaned["InvoiceDate"].isna()
        | cleaned["InvalidQuantity"]
        | cleaned["InvalidUnitPrice"]
        | cleaned["InvalidDate"]
        | cleaned["NegativeQuantity"]
        | cleaned["ZeroQuantity"]
        | cleaned["ZeroOrNegativePrice"]
        | cleaned["MissingDescription"]
    )

    stats = {
        "input_rows": len(data),
        "duplicate_candidates": duplicate_candidates,
        "duplicate_rows_removed": duplicate_rows_removed,
        "output_rows": len(cleaned),
    }
    return cleaned.reset_index(drop=True), stats


def split_transaction_sets(
    cleaned: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create overlapping sales, cancellation, and review datasets."""
    sales_mask = (
        cleaned["Quantity"].gt(0)
        & cleaned["UnitPrice"].gt(0)
        & ~cleaned["IsCancellation"]
        & cleaned["InvoiceDate"].notna()
    )
    sales = cleaned.loc[sales_mask].copy()
    cancellations = cleaned.loc[cleaned["IsCancellation"]].copy()
    flagged = cleaned.loc[cleaned["NeedsReview"]].copy()
    if sales.empty:
        raise ValueError(
            "No usable sales records remain after applying positive quantity, positive "
            "price, non-cancellation, and valid-date rules."
        )
    return sales, cancellations, flagged

