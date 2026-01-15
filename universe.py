"""
Asset universe definition.
Small, fixed set of liquid assets.
"""

UNIVERSE = [
    "SPY",   # S&P 500
    "QQQ",   # Nasdaq 100
    "AAPL",  # Apple
    "MSFT",  # Microsoft
    "GLD",   # Gold
    "TLT",   # Long-term Treasuries
]

# Primary market indicator (used for regime classification)
MARKET_INDICATOR = "SPY"
