"""
Simple backtest to evaluate system performance.
Conservative approach: monthly rebalancing only (per SYSTEM_RULES.md).
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from indicators import calculate_indicators
from market_state import classify_regime
from allocation import get_exposure, select_assets, allocate_cash
from universe import UNIVERSE, MARKET_INDICATOR


def load_historical_data(symbols: list[str], start_date: str, end_date: str) -> pd.DataFrame:
    """
    Load historical price data for backtesting with specific date range.
    
    Args:
        symbols: List of ticker symbols
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns:
        DataFrame with adjusted close prices
    """
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
    
    prices = prices.sort_index()
    return prices


def run_backtest(start_date: str, end_date: str, initial_capital: float = 10000):
    """
    Backtest the investment system with monthly rebalancing.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        initial_capital: Starting capital in USD
    
    Returns:
        Dict with backtest results
    """
    print("=" * 70)
    print("BACKTEST SIMULATION")
    print("=" * 70)
    print(f"Period: {start_date} to {end_date}")
    print(f"Initial capital: ${initial_capital:,.2f}")
    print(f"Rebalancing: Monthly (per SYSTEM_RULES.md)")
    print("=" * 70)
    print()
    
    # Load historical data (need extra lookback for indicators)
    # Need ~600 calendar days before start to ensure 250+ trading days for EMA200
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    lookback_start = start_dt - timedelta(days=600)
    
    # Load data from lookback start to backtest end
    prices = load_historical_data(
        UNIVERSE, 
        lookback_start.strftime("%Y-%m-%d"),
        end_dt.strftime("%Y-%m-%d")
    )
    
    # Filter to backtest period
    backtest_prices = prices[prices.index >= start_date]
    backtest_prices = backtest_prices[backtest_prices.index <= end_date]
    
    if len(backtest_prices) == 0:
        print("ERROR: No data available for backtest period")
        return None
    
    print(f"Loaded {len(backtest_prices)} trading days of data\n")
    
    # Get monthly rebalancing dates (first trading day of each month)
    monthly_dates = backtest_prices.resample('MS').first().index
    
    # Track portfolio over time
    portfolio_value = initial_capital
    cash = initial_capital
    holdings = {}  # {symbol: shares}
    
    portfolio_history = []
    transactions = []
    
    # Run simulation
    for i, rebalance_date in enumerate(monthly_dates):
        print(f"\n{'='*70}")
        print(f"REBALANCE #{i+1}: {rebalance_date.strftime('%Y-%m-%d')}")
        print(f"{'='*70}")
        
        # Get data up to this date for indicator calculation
        historical_data = prices[prices.index <= rebalance_date]
        
        if len(historical_data) < 200:
            print("Insufficient data for indicators, skipping...")
            continue
        
        # Calculate indicators
        indicators = calculate_indicators(historical_data)
        
        if MARKET_INDICATOR not in indicators:
            print("Market indicator not available, skipping...")
            continue
        
        # Classify regime
        market_data = indicators[MARKET_INDICATOR]
        regime, reason = classify_regime(market_data)
        
        print(f"Regime: {regime.value}")
        print(f"Reason: {reason}")
        
        # Get allocation
        target_exposure = get_exposure(regime)
        selected = select_assets(regime, indicators)
        
        print(f"Target exposure: {target_exposure:.0%}")
        print(f"Selected assets: {len(selected)}")
        
        # Calculate current portfolio value before rebalancing
        current_value = cash
        for symbol, shares in holdings.items():
            if symbol in indicators:
                current_value += shares * indicators[symbol]['price']
        
        portfolio_value = current_value
        print(f"Portfolio value: ${portfolio_value:,.2f}")
        
        # Rebalance portfolio
        # Sell all current holdings
        for symbol, shares in holdings.items():
            if symbol in indicators:
                sell_price = indicators[symbol]['price']
                cash += shares * sell_price
                transactions.append({
                    'date': rebalance_date,
                    'action': 'SELL',
                    'symbol': symbol,
                    'shares': shares,
                    'price': sell_price,
                    'value': shares * sell_price
                })
        
        holdings = {}
        
        # Calculate new positions
        if selected:
            equity_allocation = portfolio_value * target_exposure
            per_asset = equity_allocation / len(selected)
            
            print(f"\nBuying {len(selected)} assets at ${per_asset:,.2f} each:")
            
            for symbol, reason in selected:
                if symbol in indicators:
                    buy_price = indicators[symbol]['price']
                    shares = per_asset / buy_price
                    holdings[symbol] = shares
                    cash -= per_asset
                    
                    print(f"  {symbol}: {shares:.2f} shares @ ${buy_price:.2f}")
                    
                    transactions.append({
                        'date': rebalance_date,
                        'action': 'BUY',
                        'symbol': symbol,
                        'shares': shares,
                        'price': buy_price,
                        'value': per_asset
                    })
        
        print(f"\nCash after rebalance: ${cash:,.2f} ({(cash/portfolio_value):.1%})")
        
        # Track portfolio
        portfolio_history.append({
            'date': rebalance_date,
            'value': portfolio_value,
            'cash': cash,
            'regime': regime.value,
            'exposure': target_exposure,
            'num_positions': len(selected)
        })
    
    # Calculate final value
    final_date = backtest_prices.index[-1]
    final_prices = prices[prices.index <= final_date]
    final_indicators = calculate_indicators(final_prices)
    
    final_value = cash
    for symbol, shares in holdings.items():
        if symbol in final_indicators:
            final_value += shares * final_indicators[symbol]['price']
    
    # Calculate metrics
    total_return = (final_value - initial_capital) / initial_capital
    days = (backtest_prices.index[-1] - backtest_prices.index[0]).days
    years = days / 365.25
    annualized_return = (final_value / initial_capital) ** (1 / years) - 1 if years > 0 else 0
    
    # Print summary
    print("\n" + "=" * 70)
    print("BACKTEST RESULTS")
    print("=" * 70)
    print(f"Start date: {backtest_prices.index[0].strftime('%Y-%m-%d')}")
    print(f"End date: {backtest_prices.index[-1].strftime('%Y-%m-%d')}")
    print(f"Period: {days} days ({years:.2f} years)")
    print(f"\nInitial capital: ${initial_capital:,.2f}")
    print(f"Final value: ${final_value:,.2f}")
    print(f"Total return: {total_return:+.2%}")
    print(f"Annualized return: {annualized_return:+.2%}")
    print(f"\nRebalances executed: {len(monthly_dates)}")
    print(f"Total transactions: {len(transactions)}")
    print("=" * 70)
    
    return {
        'initial_capital': initial_capital,
        'final_value': final_value,
        'total_return': total_return,
        'annualized_return': annualized_return,
        'days': days,
        'years': years,
        'portfolio_history': portfolio_history,
        'transactions': transactions
    }


if __name__ == "__main__":
    # Run backtest from Jan 2025 to present
    results = run_backtest(
        start_date="2025-01-01",
        end_date=datetime.now().strftime("%Y-%m-%d"),
        initial_capital=10000
    )
