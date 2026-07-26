"""
Reusable data loading, cleaning, and feature engineering utilities
for the Brent oil price change point analysis project.
"""

from typing import Optional
import pandas as pd
import numpy as np

from src.config import CONFIG

DEFAULT_ROLLING_WINDOW: int = CONFIG.data.rolling_volatility_window
DEFAULT_DATE_FORMAT: str = CONFIG.data.date_format


def load_price_data(filepath: str) -> pd.DataFrame:
    """
    Load raw Brent oil price data from CSV.

    Parameters
    ----------
    filepath : str
        Path to the raw price CSV file.

    Returns
    -------
    pd.DataFrame
        Raw dataframe with Date and Price columns.

    Raises
    ------
    FileNotFoundError
        If the file does not exist at the given path.
    ValueError
        If the expected columns are not present.
    """
    try:
        df: pd.DataFrame = pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Could not find data file at '{filepath}'. "
            "Check that the path is correct and the file has been downloaded."
        )

    required_cols = set(CONFIG.data.required_price_columns)
    if not required_cols.issubset(df.columns):
        raise ValueError(
            f"Expected columns {required_cols} not found in {filepath}. "
            f"Found columns: {list(df.columns)}"
        )

    return df


def clean_price_data(df: pd.DataFrame, date_format: str = DEFAULT_DATE_FORMAT) -> pd.DataFrame:
    """
    Parse dates, sort chronologically, and drop invalid rows.

    Parameters
    ----------
    df : pd.DataFrame
        Raw dataframe with Date and Price columns.
    date_format : str
        Expected strptime format for the Date column.

    Returns
    -------
    pd.DataFrame
        Cleaned dataframe, sorted by date, with no missing values.
    """
    df = df.copy()

    df["Date"] = pd.to_datetime(df["Date"], format=date_format, errors="coerce")
    if df["Date"].isna().any():
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

    n_before: int = len(df)
    df = df.dropna(subset=["Date", "Price"])
    n_after: int = len(df)
    if n_after < n_before:
        print(f"Warning: dropped {n_before - n_after} rows with invalid dates/prices.")

    df = df.sort_values("Date").drop_duplicates(subset="Date").reset_index(drop=True)
    return df


def add_log_returns(df: pd.DataFrame, price_col: str = "Price") -> pd.DataFrame:
    """
    Add log price and log return columns to the dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned price dataframe.
    price_col : str
        Name of the price column to use.

    Returns
    -------
    pd.DataFrame
        Dataframe with added 'Log_Price' and 'Log_Return' columns.
    """
    if price_col not in df.columns:
        raise ValueError(f"Column '{price_col}' not found in dataframe.")
    if (df[price_col] <= 0).any():
        raise ValueError("Price column contains non-positive values; cannot take log.")

    df = df.copy()
    df["Log_Price"] = np.log(df[price_col])
    df["Log_Return"] = df["Log_Price"].diff()
    return df


def add_rolling_volatility(
    df: pd.DataFrame,
    window: int = DEFAULT_ROLLING_WINDOW,
    col: str = "Log_Return",
) -> pd.DataFrame:
    """
    Add a rolling standard deviation (volatility) column.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing the column to compute rolling volatility on.
    window : int
        Rolling window size in days. Defaults to CONFIG.data.rolling_volatility_window.
    col : str
        Column to compute rolling std on.

    Returns
    -------
    pd.DataFrame
        Dataframe with an added 'Rolling_Volatility' column.
    """
    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found in dataframe.")

    df = df.copy()
    df["Rolling_Volatility"] = df[col].rolling(window=window).std()
    return df


def load_events(filepath: str) -> pd.DataFrame:
    """
    Load the curated events dataset.

    Parameters
    ----------
    filepath : str
        Path to events.csv.

    Returns
    -------
    pd.DataFrame
        Events dataframe with parsed Event_Date column.
    """
    try:
        events: pd.DataFrame = pd.read_csv(filepath, parse_dates=["Event_Date"])
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Could not find events file at '{filepath}'. "
            "Make sure data/events.csv has been created and committed."
        )
    return events