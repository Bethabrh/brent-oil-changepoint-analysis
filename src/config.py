"""
Central configuration for the Brent oil change point analysis project.
Consolidates magic numbers and settings into named, typed constants.
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass(frozen=True)
class DataConfig:
    """Settings for data loading and feature engineering."""
    date_format: str = "%d-%b-%y"
    rolling_volatility_window: int = 30
    required_price_columns: Tuple[str, str] = ("Date", "Price")


@dataclass(frozen=True)
class MCMCConfig:
    """Settings for PyMC Bayesian change point sampling."""
    draws: int = 1500
    tune: int = 1500
    chains: int = 2
    target_accept: float = 0.9
    random_seed: int = 42
    cores: int = 1


@dataclass(frozen=True)
class EventWindow:
    """A focused date window used for windowed change point detection."""
    start_date: str
    end_date: str
    label: str


@dataclass(frozen=True)
class ProjectConfig:
    """Top-level project configuration bundling all sub-configs."""
    data: DataConfig = field(default_factory=DataConfig)
    mcmc: MCMCConfig = field(default_factory=MCMCConfig)
    event_windows: Dict[str, EventWindow] = field(default_factory=lambda: {
        "gulf_war": EventWindow("1989-01-01", "1992-12-31", "Gulf War"),
        "financial_crisis": EventWindow("2007-06-01", "2009-06-30", "Global Financial Crisis"),
        "opec_2014": EventWindow("2014-06-01", "2015-12-31", "2014 OPEC Non-Cut"),
        "covid": EventWindow("2019-09-01", "2020-09-30", "COVID / Price War"),
        "russia_ukraine": EventWindow("2021-09-01", "2022-09-30", "Russia-Ukraine War"),
    })
    dataset_start_date: str = "1987-05-20"
    dataset_end_date: str = "2022-09-30"


# Singleton instance used throughout the project
CONFIG = ProjectConfig()