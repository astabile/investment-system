"""
Technical indicators.
Simple, deterministic calculations.
"""

import pandas as pd
import numpy as np


def ema(prices: pd.Series, period: int) -> pd.Series:
    """
    Exponential Moving Average.
    
    Args:
        prices: Price series
        period: EMA period
    
    Returns:
        EMA series
    """
    return prices.ewm(span=period, adjust=False).mean()


def simple_return(prices: pd.Series, periods: int = 1) -> pd.Series:
    """
    Simple percentage returns.
    
    Args:
        prices: Price series
        periods: Number of periods for return calculation
    
    Returns:
        Return series as decimal (0.05 = 5%)
    """
    return prices.pct_change(periods=periods)


def volatility(prices: pd.Series, window: int = 20) -> pd.Series:
    """
    Rolling volatility (standard deviation of returns).
    
    Args:
        prices: Price series
        window: Rolling window size
    
    Returns:
        Annualized volatility series
    """
    returns = simple_return(prices, periods=1)
    # Annualize: multiply by sqrt(252) for daily data
    return returns.rolling(window=window).std() * np.sqrt(252)


def calculate_indicators(prices: pd.DataFrame) -> dict:
    """
    Calculate all indicators for the given price data.

    Returns indicators for the latest available day only.
    Returns data is informational (not used for decisions).
    """
    indicators = {}

    for symbol in prices.columns:
        price_series = prices[symbol].dropna()

        # Require sufficient data
        if len(price_series) < 200:
            continue

        vol_series = volatility(price_series, 20)
        ema_series = ema(price_series, 200)

        # Skip if indicators are not available yet
        if pd.isna(vol_series.iloc[-1]) or pd.isna(ema_series.iloc[-1]):
            continue

        indicators[str(symbol)] = {
            "price": price_series.iloc[-1],
            "ema_200": ema_series.iloc[-1],
            "return_1d": simple_return(price_series, 1).iloc[-1],
            "return_5d": simple_return(price_series, 5).iloc[-1],
            "return_20d": simple_return(price_series, 20).iloc[-1],
            "volatility": vol_series.iloc[-1],
        }

    return indicators
