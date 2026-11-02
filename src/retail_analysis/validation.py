"""Validate columns and describe data-quality issues."""

import pandas as pd

from retail_analysis.config import REQUIRED_COLUMNS


def validate_required_columns(data: pd.DataFrame) -> None:
    """Raise a helpful error when expected UCI columns are missing."""
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(
            "Required columns are missing: " + ", ".join(missing) + ". "
            "Check that you downloaded the original UCI Online Retail workbook."
        )


def data_quality_report(data: pd.DataFrame, stage: str) -> pd.DataFrame:
    """Return one row per column with type and missing-value information."""
    row_count = len(data)
    missing_count = data.isna().sum()
    report = pd.DataFrame(
        {
            "Stage": stage,
            "Column": data.columns,
            "DataType": data.dtypes.astype(str).values,
            "RowCount": row_count,
            "MissingCount": missing_count.values,
            "MissingPercent": (
                missing_count.div(row_count).mul(100).round(2).values
                if row_count
                else 0.0
            ),
        }
    )
    return report


def issue_counts(data: pd.DataFrame) -> pd.DataFrame:
    """Count cleaning flags when present, plus exact duplicate candidates."""
    counts = {"ExactDuplicateCandidates": int(data.duplicated(keep=False).sum())}
    flag_columns = [
        "InvalidDate",
        "InvalidQuantity",
        "InvalidUnitPrice",
        "ZeroQuantity",
        "NegativeQuantity",
        "ZeroOrNegativePrice",
        "IsCancellation",
        "MissingDescription",
        "NeedsReview",
    ]
    for column in flag_columns:
        if column in data.columns:
            counts[column] = int(data[column].fillna(False).sum())
    return pd.DataFrame({"Issue": counts.keys(), "Count": counts.values()})

