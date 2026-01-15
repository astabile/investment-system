"""
Fixed income instruments for the cash portion.
Cauciones are the default parking for uninvested capital.
"""

# List of available cauciones (ordered by term)
# Annual yield is estimated and must be updated manually
CAUCIONES = [
    {"name": "Caucion_1d_USD", "days": 1, "annual_yield": 0.10},
    {"name": "Caucion_2d_USD", "days": 2, "annual_yield": 0.12},
    {"name": "Caucion_5d_USD", "days": 5, "annual_yield": 0.15},
    {"name": "Caucion_7d_USD", "days": 7, "annual_yield": 0.18},
]

# Rule: always prefer shorter terms to maintain liquidity
# Allocation is uniform among the shortest available cauciones
MAX_CAUCIONES_TO_USE = 3  # Limit the number of instruments to use
