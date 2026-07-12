

import pandas as pd
import numpy as np


def load_price_data(filepath: str) -> pd.DataFrame:
    
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Could not find data file at '{filepath}'. "
            "Check that the path is correct and the file has been downloaded."
        )

    required_cols = {"Date", "Price"}
    if not required_cols.issubset(df.columns):
        raise ValueError(
            f"Expected columns {required_cols} not found in {filepath}. "
            f"Found columns: {list(df.columns)}"
        )

    return df


def clean_price_data(df: pd.DataFrame) -> pd.DataFrame:
    """Parse dates, sort chronologically, and drop invalid rows."""
    df = df.copy()

    df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%y", errors="coerce")
    if df["Date"].isna().any():
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

    n_before = len(df)
    df = df.dropna(subset=["Date", "Price"])
    n_after = len(df)
    if n_after < n_before:
        print(f"Warning: dropped {n_before - n_after} rows with invalid dates/prices.")

    df = df.sort_values("Date").drop_duplicates(subset="Date").reset_index(drop=True)
    return df


def add_log_returns(df: pd.DataFrame, price_col: str = "Price") -> pd.DataFrame:
    """Add Log_Price and Log_Return columns."""
    if price_col not in df.columns:
        raise ValueError(f"Column '{price_col}' not found in dataframe.")
    if (df[price_col] <= 0).any():
        raise ValueError("Price column contains non-positive values; cannot take log.")

    df = df.copy()
    df["Log_Price"] = np.log(df[price_col])
    df["Log_Return"] = df["Log_Price"].diff()
    return df


def add_rolling_volatility(df: pd.DataFrame, window: int = 30, col: str = "Log_Return") -> pd.DataFrame:
    """Add a Rolling_Volatility column (rolling std dev)."""
    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found in dataframe.")

    df = df.copy()
    df["Rolling_Volatility"] = df[col].rolling(window=window).std()
    return df


def load_events(filepath: str) -> pd.DataFrame:
    """Load the curated events dataset with parsed dates."""
    try:
        events = pd.read_csv(filepath, parse_dates=["Event_Date"])
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Could not find events file at '{filepath}'. "
            "Make sure data/events.csv has been created and committed."
        )
    return events