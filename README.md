# Conservative Investment Analysis System

A minimal, rule-based system for conservative portfolio management.

## Philosophy

- **Simplicity over sophistication**: One screen per file, no frameworks
- **Rules over prediction**: Deterministic logic, no ML/AI
- **Capital preservation > returns**: Conservative exposure levels
- **Manual execution**: Analysis tool, not a trading bot

## System Design

### Components

```
universe.py      - Asset universe (ETFs + mega caps)
data.py          - Yahoo Finance data loading
indicators.py    - EMA, returns, volatility
market_state.py  - Regime classification
allocation.py    - Exposure and asset selection
run.py           - Main entry point
```

### Market Regimes

The system classifies market conditions into three regimes based on SPY:

**RISK_ON** (70% exposure)
- Price > EMA 200
- Volatility < 20%
- Holds: Market ETFs + Mega caps (if above EMA)

**NEUTRAL** (40% exposure)
- Price > EMA 200
- Volatility 20-30%
- Holds: Market ETFs (above EMA) + Defensive

**RISK_OFF** (15% exposure)
- Price < EMA 200 OR Volatility > 30%
- Holds: Defensive only (TLT, GLD)

### Indicators

- **EMA 200**: Trend direction (price above/below)
- **Returns**: 1-day, 5-day, 20-day performance
- **Volatility**: 20-day rolling, annualized

### Asset Universe

**Market ETFs**
- SPY (S&P 500)
- QQQ (Nasdaq 100)

**Defensive ETFs**
- TLT (20+ Year Treasury)
- GLD (Gold)

**Mega Caps**
- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Alphabet)

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install yfinance pandas numpy
```

## Usage

```bash
python run.py
```

The system will:
1. Load latest price data
2. Calculate indicators
3. Classify market regime
4. Recommend exposure level
5. Select assets to hold
6. Print human-readable summary

## Output Example

```
======================================================================
INVESTMENT SYSTEM DAILY ANALYSIS
Run date: 2026-01-14 10:30:00
======================================================================

Loading price data...
Loaded 250 days of data for 7 assets
Calculating indicators...

MARKET REGIME
----------------------------------------------------------------------
Regime: RISK_ON
Reason: Price above EMA200 (+5.2%), low volatility (12.5%)

Market indicator (SPY):
  Current price: $475.32
  EMA 200: $452.18
  Volatility: 12.5%
  1-day return: +0.45%
  5-day return: +2.10%
  20-day return: +5.80%

PORTFOLIO ALLOCATION
----------------------------------------------------------------------
Recommended exposure: 70%
Cash allocation: 30%

RECOMMENDED HOLDINGS
----------------------------------------------------------------------
Equal weight per asset: 14.0% of portfolio

SPY    ↑ $475.32  Market ETF - strong trend
       Return (1d/5d/20d): +0.5% / +2.1% / +5.8%

QQQ    ↑ $412.15  Market ETF - strong trend
       Return (1d/5d/20d): +0.7% / +3.2% / +8.1%

AAPL   ↑ $225.50  Mega cap - above EMA200
       Return (1d/5d/20d): +1.2% / +4.5% / +12.3%

MSFT   ↑ $415.80  Mega cap - above EMA200
       Return (1d/5d/20d): +0.8% / +2.8% / +9.2%

GOOGL  ↑ $175.30  Mega cap - above EMA200
       Return (1d/5d/20d): +0.6% / +3.1% / +10.5%

EXECUTION SUMMARY
----------------------------------------------------------------------
Market regime: RISK_ON
Total exposure: 70%
Number of positions: 5
Weight per position: 14.0%

This is an analysis tool, not a trading bot.
Review the data and execute manually if appropriate.
======================================================================
```

## Extending the System

The system is designed to be easily modifiable:

### Add new assets
Edit `universe.py` to add symbols to the appropriate category.

### Adjust regime thresholds
Edit `market_state.py` to change EMA or volatility thresholds.

### Change exposure levels
Edit `allocation.py` to adjust exposure percentages.

### Add new indicators
Add functions to `indicators.py` following the existing pattern.

## Limitations

- Daily data only (no intraday)
- No automated trading
- No backtesting (yet)
- No portfolio optimization
- No transaction cost modeling
- No tax considerations
- Fixed universe (no screening)

## Currency

All logic uses USD as the base currency. No forex handling needed.

## Data Source

Yahoo Finance via `yfinance` library. Free, no API key required.

## Disclaimer

This is a personal analysis tool, not financial advice. The system is designed for conservative, long-term investing. Always do your own research and understand the risks before investing.
