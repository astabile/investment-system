"""
Main entry point.
Run this to get today's analysis.
"""

from datetime import datetime
from universe import UNIVERSE, MARKET_INDICATOR
from data import load_prices
from indicators import calculate_indicators
from market_state import classify_regime
from allocation import get_exposure, select_assets, allocate_cash


def print_separator():
    print("=" * 70)


def print_section(title: str):
    print(f"\n{title}")
    print("-" * 70)


def main():
    print_separator()
    print(f"INVESTMENT SYSTEM DAILY ANALYSIS")
    print(f"Run date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_separator()
    
    # Load data
    print("\nLoading price data...")
    prices = load_prices(UNIVERSE)
    print(f"Loaded {len(prices)} days of data for {len(UNIVERSE)} assets")
    
    # Calculate indicators
    print("Calculating indicators...")
    indicators = calculate_indicators(prices)
    
    # Classify market regime
    print_section("MARKET REGIME")
    market_data = indicators[MARKET_INDICATOR]
    regime, reason = classify_regime(market_data)
    
    print(f"Regime: {regime.value}")
    print(f"Reason: {reason}")
    print(f"\nMarket indicator ({MARKET_INDICATOR}):")
    print(f"  Current price: ${market_data['price']:.2f}")
    print(f"  EMA 200: ${market_data['ema_200']:.2f}")
    print(f"  Volatility: {market_data['volatility']:.1%}")
    print(f"  1-day return: {market_data['return_1d']:+.2%}")
    print(f"  5-day return: {market_data['return_5d']:+.2%}")
    print(f"  20-day return: {market_data['return_20d']:+.2%}")
    
    # Portfolio allocation
    print_section("PORTFOLIO ALLOCATION")
    exposure = get_exposure(regime)
    print(f"Recommended exposure: {exposure:.0%}")
    print(f"Cash allocation: {(1-exposure):.0%}")
    
    # Asset selection
    print_section("RECOMMENDED HOLDINGS")
    selected_assets = select_assets(regime, indicators)
    
    if not selected_assets:
        print("No assets meet criteria. Stay in cash.")
    else:
        weight_per_asset = exposure / len(selected_assets)
        print(f"Equal weight per asset: {weight_per_asset:.1%} of portfolio")
        print()
        
        for symbol, reason in selected_assets:
            data = indicators[symbol]
            trend = "↑" if data['price'] > data['ema_200'] else "↓"
            print(f"{symbol:6s} {trend} ${data['price']:8.2f}  {reason}")
            print(f"       Return (1d/5d/20d): {data['return_1d']:+.1%} / {data['return_5d']:+.1%} / {data['return_20d']:+.1%}")
            print()
    
    # Cash / Cauciones allocation
    print_section("CASH ALLOCATION (CAUCIONES)")
    cash_percentage = 1 - exposure
    
    if cash_percentage > 0:
        # Use a default portfolio value of $10,000 for display purposes
        # User should adjust based on their actual portfolio size
        portfolio_value = 10000  # USD
        caucion_allocations = allocate_cash(cash_percentage, portfolio_value)
        
        print(f"Total cash: ${portfolio_value * cash_percentage:,.0f} ({cash_percentage:.0%} of portfolio)")
        print(f"Allocated across {len(caucion_allocations)} short-term instruments:\n")
        
        for name, amount, annual_yield in caucion_allocations:
            days = int(name.split("_")[1].replace("d", ""))
            print(f"{name:20s} → ${amount:8,.0f}  (Yield: {annual_yield:.2%}/year, {days}d)")
        
        print("\nNote: Cauciones provide liquidity and capital preservation.")
        print("      Yields are informational. Update rates manually in cash_instruments.py")
    else:
        print("No cash allocation (100% invested)")
    
    # Summary
    print_section("EXECUTION SUMMARY")
    caucion_allocations = allocate_cash(cash_percentage, 10000)
    print(f"Market regime: {regime.value}")
    print(f"Total exposure: {exposure:.0%}")
    print(f"Number of positions: {len(selected_assets)}")
    print(f"Weight per position: {weight_per_asset:.1%}" if selected_assets else "")
    print(f"Cash in cauciones: {cash_percentage:.0%} (across {len(caucion_allocations)} instruments)")
    print()
    print("This is an analysis tool, not a trading bot.")
    print("Review the data and execute manually if appropriate.")
    
    print_separator()


if __name__ == "__main__":
    main()
