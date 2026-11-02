"""Flag unusual values with the interquartile-range method."""

import numpy as np
import pandas as pd

from retail_analysis.config import IQR_MULTIPLIER


def calculate_iqr_bounds(
    values: pd.Series, multiplier: float = IQR_MULTIPLIER
) -> dict[str, float | int]:
    """Calculate NumPy percentile-based IQR bounds for non-missing values."""
    usable = pd.to_numeric(values, errors="coerce").dropna().to_numpy()
    if usable.size == 0:
        raise ValueError("IQR bounds cannot be calculated from empty values.")
    q1, q3 = np.percentile(usable, [25, 75])
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    return {
        "Q1": float(q1),
        "Q3": float(q3),
        "IQR": float(iqr),
        "LowerBound": float(lower),
        "UpperBound": float(upper),
        "ZeroIQR": int(iqr == 0),
    }


def add_outlier_flags(
    sales: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Add separate Quantity and LineValue flags without dropping observations."""
    if sales.empty:
        raise ValueError("Outlier analysis requires at least one eligible sales row.")
    result = sales.copy()
    rows = []
    for column in ["Quantity", "LineValue"]:
        bounds = calculate_iqr_bounds(result[column])
        flag_name = f"{column}Outlier"
        result[flag_name] = result[column].lt(bounds["LowerBound"]) | result[column].gt(
            bounds["UpperBound"]
        )
        rows.append(
            {
                "Variable": column,
                **bounds,
                "OutlierCount": int(result[flag_name].sum()),
            }
        )
    return result, pd.DataFrame(rows)

