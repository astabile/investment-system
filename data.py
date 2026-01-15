"""
Data loading from Yahoo Finance.
Daily data only. One source of truth.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def load_prices(symbols: list[str], lookback_days: int = 400) -> pd.DataFrame:
    """
    Load daily adjusted close prices for given symbols.

    We intentionally over-fetch calendar days to guarantee
    sufficient trading days for long indicators (EMA200).
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)

    data = yf.download(
        symbols,
        start=start_date,
        end=end_date,
        progress=False,
        auto_adjust=True,
    )

    # Normalize output
    if len(symbols) == 1:
        prices = pd.DataFrame({symbols[0]: data["Close"]})
    else:
        prices = data["Close"]

    # Sort and keep as-is (cleaning happens downstream)
    prices = prices.sort_index()

    return prices
