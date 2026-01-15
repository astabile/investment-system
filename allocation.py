"""
Portfolio allocation logic.
Conservative approach: capital preservation > returns.
"""

from market_state import MarketRegime


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
