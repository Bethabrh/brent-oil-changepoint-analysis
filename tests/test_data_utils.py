"""
Unit tests for src/data_utils.py
Run with: pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import pandas as pd
import numpy as np

from src.data_utils import (
    load_price_data,
    clean_price_data,
    add_log_returns,
    add_rolling_volatility,
    load_events,
)


# ---------- Fixtures ----------

@pytest.fixture
def sample_raw_df():
    """A small, valid raw price dataframe matching the expected format."""
    return pd.DataFrame({
        'Date': ['20-May-87', '21-May-87', '22-May-87', '25-May-87'],
        'Price': [18.63, 18.45, 18.55, 18.60],
    })


@pytest.fixture
def sample_clean_df():
    """A small, already-cleaned dataframe with datetime dates."""
    return pd.DataFrame({
        'Date': pd.to_datetime(['1987-05-20', '1987-05-21', '1987-05-22', '1987-05-25']),
        'Price': [18.63, 18.45, 18.55, 18.60],
    })


@pytest.fixture
def tmp_csv_file(tmp_path, sample_raw_df):
    """Write a sample CSV to a temp file and return its path."""
    filepath = tmp_path / "test_prices.csv"
    sample_raw_df.to_csv(filepath, index=False)
    return str(filepath)


# ---------- load_price_data ----------

class TestLoadPriceData:
    def test_loads_valid_file(self, tmp_csv_file):
        df = load_price_data(tmp_csv_file)
        assert len(df) == 4
        assert 'Date' in df.columns
        assert 'Price' in df.columns

    def test_raises_on_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_price_data('nonexistent_file_xyz.csv')

    def test_raises_on_missing_columns(self, tmp_path):
        bad_df = pd.DataFrame({'WrongCol': [1, 2, 3]})
        filepath = tmp_path / "bad.csv"
        bad_df.to_csv(filepath, index=False)
        with pytest.raises(ValueError, match="Expected columns"):
            load_price_data(str(filepath))


# ---------- clean_price_data ----------

class TestCleanPriceData:
    def test_parses_dates_correctly(self, sample_raw_df):
        result = clean_price_data(sample_raw_df)
        assert pd.api.types.is_datetime64_any_dtype(result['Date'])

    def test_sorts_chronologically(self):
        unsorted_df = pd.DataFrame({
            'Date': ['22-May-87', '20-May-87', '21-May-87'],
            'Price': [18.55, 18.63, 18.45],
        })
        result = clean_price_data(unsorted_df)
        dates = result['Date'].tolist()
        assert dates == sorted(dates)

    def test_drops_duplicate_dates(self):
        dup_df = pd.DataFrame({
            'Date': ['20-May-87', '20-May-87', '21-May-87'],
            'Price': [18.63, 18.70, 18.45],
        })
        result = clean_price_data(dup_df)
        assert result['Date'].duplicated().sum() == 0
        assert len(result) == 2

    def test_drops_missing_prices(self):
        df_with_nan = pd.DataFrame({
            'Date': ['20-May-87', '21-May-87', '22-May-87'],
            'Price': [18.63, np.nan, 18.55],
        })
        result = clean_price_data(df_with_nan)
        assert len(result) == 2
        assert result['Price'].isna().sum() == 0


# ---------- add_log_returns ----------

class TestAddLogReturns:
    def test_adds_expected_columns(self, sample_clean_df):
        result = add_log_returns(sample_clean_df)
        assert 'Log_Price' in result.columns
        assert 'Log_Return' in result.columns

    def test_first_row_return_is_nan(self, sample_clean_df):
        result = add_log_returns(sample_clean_df)
        assert pd.isna(result['Log_Return'].iloc[0])

    def test_log_return_calculation_is_correct(self, sample_clean_df):
        result = add_log_returns(sample_clean_df)
        expected = np.log(18.45) - np.log(18.63)
        assert abs(result['Log_Return'].iloc[1] - expected) < 1e-10

    def test_raises_on_missing_price_column(self, sample_clean_df):
        df = sample_clean_df.drop(columns=['Price'])
        with pytest.raises(ValueError, match="not found"):
            add_log_returns(df)

    def test_raises_on_non_positive_prices(self):
        df = pd.DataFrame({
            'Date': pd.to_datetime(['1987-05-20', '1987-05-21']),
            'Price': [18.63, -5.0],
        })
        with pytest.raises(ValueError, match="non-positive"):
            add_log_returns(df)


# ---------- add_rolling_volatility ----------

class TestAddRollingVolatility:
    def test_adds_expected_column(self, sample_clean_df):
        df = add_log_returns(sample_clean_df)
        result = add_rolling_volatility(df, window=2)
        assert 'Rolling_Volatility' in result.columns

    def test_raises_on_missing_column(self, sample_clean_df):
        with pytest.raises(ValueError, match="not found"):
            add_rolling_volatility(sample_clean_df, col='Nonexistent_Col')

    def test_window_size_affects_nan_count(self, sample_clean_df):
        df = add_log_returns(sample_clean_df)
        result_small = add_rolling_volatility(df.copy(), window=2)
        result_large = add_rolling_volatility(df.copy(), window=3)
        # Larger window -> more leading NaNs
        assert result_large['Rolling_Volatility'].isna().sum() >= result_small['Rolling_Volatility'].isna().sum()


# ---------- load_events ----------

class TestLoadEvents:
    def test_loads_valid_events_file(self, tmp_path):
        events_df = pd.DataFrame({
            'Event_ID': [1, 2],
            'Event_Date': ['1990-08-02', '2020-03-08'],
            'Event_Name': ['Test Event 1', 'Test Event 2'],
        })
        filepath = tmp_path / "events.csv"
        events_df.to_csv(filepath, index=False)

        result = load_events(str(filepath))
        assert len(result) == 2
        assert pd.api.types.is_datetime64_any_dtype(result['Event_Date'])

    def test_raises_on_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_events('nonexistent_events_xyz.csv')