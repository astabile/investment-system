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
universe.py         - Asset universe (ETFs + mega caps)
data.py             - Yahoo Finance data loading
indicators.py       - EMA, returns, volatility
market_state.py     - Regime classification
allocation.py       - Exposure and asset selection
cash_instruments.py - Caucion definitions for cash allocation
run.py              - Main entry point (daily analysis)
backtest.py         - Historical backtesting (lump sum)
backtest_dca.py     - Historical backtesting (dollar cost averaging)
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

### Cash Management (Cauciones)

The system automatically allocates the cash portion (non-invested capital) across short-term money market instruments called **cauciones**.

**Key Principles:**
- Cash never sits idle - it's allocated to cauciones for capital preservation
- Cauciones are treated as risk-free parking, not investment assets
- Preference for shorter-term instruments (higher liquidity)
- Distribution is uniform across the 3 shortest-term cauciones available
- Yields are informational and must be updated manually

**Available Instruments:**
Defined in `cash_instruments.py`:
- Caucion 1-day USD
- Caucion 2-day USD
- Caucion 5-day USD
- Caucion 7-day USD

**Conservative Approach:**
- RISK_ON: 30% in cauciones
- NEUTRAL: 60% in cauciones
- RISK_OFF: 85% in cauciones

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install yfinance pandas numpy
```

## Usage

### Daily Analysis

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

### Backtesting

Test the system with historical data to validate performance:

**Lump Sum Strategy:**
```bash
python backtest.py
```

Simulates investing a single amount upfront with monthly rebalancing.

**Dollar Cost Averaging (DCA):**
```bash
python backtest_dca.py
```

Simulates starting with initial capital and adding fixed monthly contributions.

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

CASH ALLOCATION (CAUCIONES)
----------------------------------------------------------------------
Total cash: $3,000 (30% of portfolio)
Allocated across 3 short-term instruments:

Caucion_1d_USD       → $   1,000  (Yield: 10.00%/year, 1d)
Caucion_2d_USD       → $   1,000  (Yield: 12.00%/year, 2d)
Caucion_5d_USD       → $   1,000  (Yield: 15.00%/year, 5d)

Note: Cauciones provide liquidity and capital preservation.
      Yields are informational. Update rates manually in cash_instruments.py

EXECUTION SUMMARY
----------------------------------------------------------------------
Market regime: RISK_ON
Total exposure: 70%
Number of positions: 5
Weight per position: 14.0%
Cash in cauciones: 30% (across 3 instruments)

This is an analysis tool, not a trading bot.
Review the data and execute manually if appropriate.
======================================================================
```

## Backtesting Results

The system has been validated with historical data from 2021-2025:

### 5-Year Performance (2021-2025)

**Lump Sum Strategy** ($69,000 invested upfront):
- Final value: $96,653
- Total return: +40.08%
- Annualized: +6.99%/year

**Dollar Cost Averaging** ($10k initial + $1k/month):
- Total invested: $69,000 (over 5 years)
- Final value: $87,343
- Total gain: $18,343
- Return on capital: +26.58%

### Year-by-Year Returns

| Year | Return | Market Condition | System Behavior |
|------|--------|------------------|-----------------|
| 2021 | +18.78% | Bull market | RISK_ON all year |
| 2022 | -13.01% | Bear market | RISK_OFF 9/12 months |
| 2023 | +7.01% | Recovery | 5 regime switches |
| 2024 | +12.92% | Bull market | RISK_ON all year |
| 2025 | +13.06% | Strong growth | Mostly RISK_ON |

**Key Findings:**
- System survived 2022 bear market with 13% loss vs 18% for S&P 500
- Conservative 30-85% cash buffer protected capital during downturns
- Automatic defensive positioning during market stress
- Consistent 7-13% returns in non-crisis years
- Both strategies profitable over full cycle

**5-Year Compound:**
- Started with $10k lump sum in 2021
- Would have $14,117 by 2026
- Total return: +41.17%
- Average: ~7.1% CAGR through bull and bear markets

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

### Update caucion rates
Edit `cash_instruments.py` to:
- Update annual yields (should be done weekly or monthly)
- Add or remove caucion instruments
- Adjust `MAX_CAUCIONES_TO_USE` to change diversification

## Limitations

- Daily data only (no intraday)
- No automated trading
- No portfolio optimization (equal weight only)
- No transaction cost modeling in backtests
- No tax considerations
- No slippage modeling
- Fixed universe (no dynamic screening)
- Backtest data limited by Yahoo Finance availability

## Currency

All logic uses USD as the base currency. No forex handling needed.

## Data Source

Yahoo Finance via `yfinance` library. Free, no API key required.

## Disclaimer

This is a personal analysis tool, not financial advice. The system is designed for conservative, long-term investing. Always do your own research and understand the risks before investing.
