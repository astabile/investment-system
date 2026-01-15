"""
Market regime classification.
Simple rules, no prediction.
"""

from enum import Enum


class MarketRegime(Enum):
    RISK_ON = "RISK_ON"
    NEUTRAL = "NEUTRAL"
    RISK_OFF = "RISK_OFF"


def classify_regime(indicator_data: dict) -> tuple[MarketRegime, str]:
    """
    Classify market regime based on SPY indicators.
    
    Rules:
    - RISK_ON: Price > EMA200 AND volatility < 0.20
    - RISK_OFF: Price < EMA200 OR volatility > 0.30
    - NEUTRAL: Everything else
    
    Args:
        indicator_data: Dict with 'price', 'ema_200', 'volatility'
    
    Returns:
        Tuple of (MarketRegime, explanation string)
    """
    price = indicator_data['price']
    ema_200 = indicator_data['ema_200']
    vol = indicator_data['volatility']
    
    above_ema = price > ema_200
    price_vs_ema_pct = ((price / ema_200) - 1) * 100
    
    # RISK_OFF conditions (most conservative)
    if not above_ema:
        reason = f"Price below EMA200 ({price_vs_ema_pct:+.1f}%)"
        return MarketRegime.RISK_OFF, reason
    
    if vol > 0.30:
        reason = f"High volatility ({vol:.1%})"
        return MarketRegime.RISK_OFF, reason
    
    # RISK_ON conditions (most aggressive)
    if above_ema and vol < 0.20:
        reason = f"Price above EMA200 ({price_vs_ema_pct:+.1f}%), low volatility ({vol:.1%})"
        return MarketRegime.RISK_ON, reason
    
    # NEUTRAL (everything else)
    reason = f"Price above EMA200 ({price_vs_ema_pct:+.1f}%), moderate volatility ({vol:.1%})"
    return MarketRegime.NEUTRAL, reason
