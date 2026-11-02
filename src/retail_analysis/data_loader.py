"""Read the source workbook and save generated tables."""

from pathlib import Path

import pandas as pd

from retail_analysis.config import RAW_DATA_PATH


def load_retail_data(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the original Excel workbook without modifying it."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {path}. Download 'Online Retail.xlsx' from "
            "https://archive.ics.uci.edu/dataset/352/online+retail and place it there."
        )
    try:
        return pd.read_excel(path, engine="openpyxl")
    except Exception as exc:
        raise RuntimeError(f"Could not read the Excel dataset at {path}: {exc}") from exc


def save_table(data: pd.DataFrame, path: Path, index: bool = False) -> None:
    """Create the parent folder and save a DataFrame as CSV."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=index)

