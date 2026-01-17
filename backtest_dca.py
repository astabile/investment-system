"""
Backtest with Dollar Cost Averaging (monthly capital injections).
Simulates regular monthly contributions per SYSTEM_RULES.md #11.
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from indicators import calculate_indicators
from market_state import classify_regime
from allocation import get_exposure, select_assets
from universe import UNIVERSE, MARKET_INDICATOR


def load_historical_data(symbols: list[str], start_date: str, end_date: str) -> pd.DataFrame:
    """Load historical price data for backtesting."""
    data = yf.download(
        symbols,
        start=start_date,
        end=end_date,
        progress=False,
        auto_adjust=True,
    )
    
    if len(symbols) == 1:
        prices = pd.DataFrame({symbols[0]: data["Close"]})
    else:
        prices = data["Close"]
    
    prices = prices.sort_index()
    return prices


def run_backtest_with_dca(
    start_date: str,
    end_date: str,
    initial_capital: float = 10000,
    monthly_injection: float = 1000,
    injection_day: int = 5
):
    """
    Backtest with monthly capital injections (Dollar Cost Averaging).
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        initial_capital: Starting capital
        monthly_injection: Amount to add each month
        injection_day: Day of month to add capital (default 5th)
    """
    print("=" * 70)
    print("BACKTEST WITH MONTHLY CAPITAL INJECTIONS (DCA)")
    print("=" * 70)
    print(f"Period: {start_date} to {end_date}")
    print(f"Initial capital: ${initial_capital:,.2f}")
    print(f"Monthly injection: ${monthly_injection:,.2f} on day {injection_day}")
    print(f"Rebalancing: Monthly (per SYSTEM_RULES.md)")
    print("=" * 70)
    print()
    
    # Load data
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    lookback_start = start_dt - timedelta(days=600)
    
    prices = load_historical_data(
        UNIVERSE,
        lookback_start.strftime("%Y-%m-%d"),
        end_dt.strftime("%Y-%m-%d")
    )
    
    backtest_prices = prices[prices.index >= start_date]
    backtest_prices = backtest_prices[backtest_prices.index <= end_date]
    
    if len(backtest_prices) == 0:
        print("ERROR: No data available")
        return None
    
    print(f"Loaded {len(backtest_prices)} trading days\n")
    
    # Initialize portfolio
    cash = initial_capital
    holdings = {}
    total_injected = initial_capital
    
    # Get monthly rebalancing dates
    monthly_dates = backtest_prices.resample('MS').first().index
    
    portfolio_history = []
    injection_count = 0
    
    # Simulation
    for i, rebalance_date in enumerate(monthly_dates):
        print(f"\n{'='*70}")
        print(f"MONTH {i+1}: {rebalance_date.strftime('%Y-%m-%d')}")
        print(f"{'='*70}")
        
        # Add monthly capital injection (except first month)
        if i > 0:
            # Find trading day closest to injection_day
            month_start = rebalance_date
            target_injection_date = month_start.replace(day=min(injection_day, 28))
            
            # Add capital
            cash += monthly_injection
            total_injected += monthly_injection
            injection_count += 1
            
            print(f"💵 Capital injection: ${monthly_injection:,.2f}")
            print(f"   Total injected so far: ${total_injected:,.2f}")
        
        # Get historical data
        historical_data = prices[prices.index <= rebalance_date]
        
        if len(historical_data) < 200:
            print("Insufficient data, skipping...")
            continue
        
        # Calculate indicators
        indicators = calculate_indicators(historical_data)
        
        if MARKET_INDICATOR not in indicators:
            print("Market indicator unavailable, skipping...")
            continue
        
        # Classify regime
        market_data = indicators[MARKET_INDICATOR]
        regime, reason = classify_regime(market_data)
        
        print(f"\nRegime: {regime.value}")
        print(f"Reason: {reason}")
        
        # Get allocation
        target_exposure = get_exposure(regime)
        selected = select_assets(regime, indicators)
        
        # Calculate current portfolio value
        current_value = cash
        for symbol, shares in holdings.items():
            if symbol in indicators:
                current_value += shares * indicators[symbol]['price']
        
        portfolio_value = current_value
        
        print(f"Portfolio value: ${portfolio_value:,.2f}")
        print(f"Unrealized gain: ${portfolio_value - total_injected:+,.2f} ({((portfolio_value/total_injected)-1)*100:+.2f}%)")
        
        # Rebalance: sell all
        for symbol, shares in holdings.items():
            if symbol in indicators:
                cash += shares * indicators[symbol]['price']
        holdings = {}
        
        # Buy new positions
        if selected:
            equity_allocation = portfolio_value * target_exposure
            per_asset = equity_allocation / len(selected)
            
            print(f"\nTarget exposure: {target_exposure:.0%}")
            print(f"Buying {len(selected)} assets at ${per_asset:,.2f} each:")
            
            for symbol, reason in selected:
                if symbol in indicators:
                    buy_price = indicators[symbol]['price']
                    shares = per_asset / buy_price
                    holdings[symbol] = shares
                    cash -= per_asset
                    print(f"  {symbol}: {shares:.2f} shares @ ${buy_price:.2f}")
        
        print(f"\nCash: ${cash:,.2f} ({(cash/portfolio_value):.1%})")
        
        portfolio_history.append({
            'date': rebalance_date,
            'value': portfolio_value,
            'cash': cash,
            'total_injected': total_injected,
            'gain': portfolio_value - total_injected,
            'regime': regime.value
        })
    
    # Final value
    final_date = backtest_prices.index[-1]
    final_prices = prices[prices.index <= final_date]
    final_indicators = calculate_indicators(final_prices)
    
    final_value = cash
    for symbol, shares in holdings.items():
        if symbol in final_indicators:
            final_value += shares * final_indicators[symbol]['price']
    
    # Calculate metrics
    total_gain = final_value - total_injected
    gain_percentage = (final_value / total_injected - 1) * 100
    
    # Average return on capital deployed
    days = (backtest_prices.index[-1] - backtest_prices.index[0]).days
    years = days / 365.25
    
    # Print summary
    print("\n" + "=" * 70)
    print("FINAL RESULTS WITH DCA")
    print("=" * 70)
    print(f"Period: {backtest_prices.index[0].strftime('%Y-%m-%d')} to {backtest_prices.index[-1].strftime('%Y-%m-%d')}")
    print(f"Duration: {days} days ({years:.2f} years)")
    print(f"\n💰 CAPITAL:")
    print(f"   Initial: ${initial_capital:,.2f}")
    print(f"   Monthly injections: {injection_count} x ${monthly_injection:,.2f}")
    print(f"   Total injected: ${total_injected:,.2f}")
    print(f"\n📈 RESULTS:")
    print(f"   Final value: ${final_value:,.2f}")
    print(f"   Total gain: ${total_gain:+,.2f}")
    print(f"   Gain on capital: {gain_percentage:+.2f}%")
    print(f"\n🎯 COMPARISON:")
    print(f"   Money you put in: ${total_injected:,.2f}")
    print(f"   Money you have now: ${final_value:,.2f}")
    print(f"   Profit from investing: ${total_gain:,.2f}")
    print("=" * 70)
    
    return {
        'initial_capital': initial_capital,
        'total_injected': total_injected,
        'final_value': final_value,
        'total_gain': total_gain,
        'gain_percentage': gain_percentage,
        'injection_count': injection_count,
        'portfolio_history': portfolio_history
    }


if __name__ == "__main__":
    # Run DCA backtest for 2025
    results = run_backtest_with_dca(
        start_date="2025-01-01",
        end_date=datetime.now().strftime("%Y-%m-%d"),
        initial_capital=10000,
        monthly_injection=1000,
        injection_day=5
    )
