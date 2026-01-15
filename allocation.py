"""
Portfolio allocation logic.
Conservative approach: capital preservation > returns.
"""

from market_state import MarketRegime
from cash_instruments import CAUCIONES, MAX_CAUCIONES_TO_USE


def get_exposure(regime: MarketRegime) -> float:
    """
    Determine total portfolio exposure based on market regime.
    
    Conservative approach:
    - RISK_ON: 70% exposure (30% cash buffer)
    - NEUTRAL: 40% exposure (60% cash buffer)
    - RISK_OFF: 15% exposure (85% cash buffer)
    
    Args:
        regime: Current market regime
    
    Returns:
        Exposure percentage as decimal (0.7 = 70%)
    """
    exposure_map = {
        MarketRegime.RISK_ON: 0.70,
        MarketRegime.NEUTRAL: 0.40,
        MarketRegime.RISK_OFF: 0.15,
    }
    return exposure_map[regime]


def select_assets(regime: MarketRegime, indicators: dict) -> list[tuple[str, str]]:
    """
    Select assets based on simple, uniform rules.
    The market regime controls exposure, not asset preference.
    """
    from universe import UNIVERSE

    selected = []

    for symbol in UNIVERSE:
        data = indicators[symbol]

        # Core rule: only assets above EMA200
        if data["price"] > data["ema_200"]:
            selected.append((symbol, "Above EMA200"))

    return selected


def allocate_cash(cash_percentage: float, portfolio_value: float = 10000) -> list[tuple[str, float, float]]:
    """
    Distribute the cash portion among available cauciones.
    
    Rules:
    - Prefer shorter terms (higher liquidity)
    - Uniform distribution among selected cauciones
    - Only use the N shortest cauciones (defined in cash_instruments.py)
    
    Args:
        cash_percentage: Cash percentage (0.0 to 1.0)
        portfolio_value: Total portfolio value in USD (default 10,000 for example)
    
    Returns:
        List of tuples (caucion_name, amount_usd, annual_yield)
    """
    # Calculate total cash amount available
    total_cash = portfolio_value * cash_percentage
    
    # If no cash, return empty
    if total_cash <= 0:
        return []
    
    # Sort cauciones by term (already sorted in file, but be explicit)
    cauciones_sorted = sorted(CAUCIONES, key=lambda x: x["days"])
    
    # Select only the N shortest cauciones (liquidity first)
    selected_cauciones = cauciones_sorted[:MAX_CAUCIONES_TO_USE]
    
    # Uniform distribution of cash
    if not selected_cauciones:
        return []
    
    amount_per_caucion = total_cash / len(selected_cauciones)
    
    # Create list of allocations
    allocations = []
    for caucion in selected_cauciones:
        allocations.append((
            caucion["name"],
            amount_per_caucion,
            caucion["annual_yield"]
        ))
    
    return allocations
    """
    Select which assets to hold based on regime.
    
    Simple rules:
    - RISK_ON: Market ETFs + Mega caps above EMA200
    - NEUTRAL: Market ETFs above EMA200 + some defensive
    - RISK_OFF: Defensive assets only
    
    Args:
        regime: Current market regime
        indicators: Dict of indicator data per symbol
    
    Returns:
        List of tuples (symbol, reason)
    """
    from universe import MARKET_ETFS, DEFENSIVE_ETFS, MEGA_CAPS
    
    selected = []
    
    if regime == MarketRegime.RISK_ON:
        # Market ETFs
        for symbol in MARKET_ETFS:
            if indicators[symbol]['price'] > indicators[symbol]['ema_200']:
                selected.append((symbol, "Market ETF - strong trend"))
        
        # Mega caps above EMA200
        for symbol in MEGA_CAPS:
            if indicators[symbol]['price'] > indicators[symbol]['ema_200']:
                selected.append((symbol, "Mega cap - above EMA200"))
    
    elif regime == MarketRegime.NEUTRAL:
        # Market ETFs above EMA200
        for symbol in MARKET_ETFS:
            if indicators[symbol]['price'] > indicators[symbol]['ema_200']:
                selected.append((symbol, "Market ETF - above EMA200"))
        
        # Add one defensive asset
        selected.append((DEFENSIVE_ETFS[0], "Defensive allocation"))
    
    else:  # RISK_OFF
        # Defensive only
        for symbol in DEFENSIVE_ETFS:
            selected.append((symbol, "Defensive allocation"))
    
    return selected
