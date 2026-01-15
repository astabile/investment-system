"""
Instrumentos de renta fija para la porción de efectivo.
Las cauciones son el parking por defecto para capital no invertido.
"""

# Lista de cauciones disponibles (ordenadas por plazo)
# El rendimiento anual es estimado y debe actualizarse manualmente
CAUCIONES = [
    {"name": "Caucion_1d_USD", "days": 1, "annual_yield": 0.10},
    {"name": "Caucion_2d_USD", "days": 2, "annual_yield": 0.12},
    {"name": "Caucion_5d_USD", "days": 5, "annual_yield": 0.15},
    {"name": "Caucion_7d_USD", "days": 7, "annual_yield": 0.18},
]

# Regla: siempre preferir plazos más cortos para mantener liquidez
# La asignación es uniforme entre las cauciones más cortas disponibles
MAX_CAUCIONES_TO_USE = 3  # Limitar la cantidad de instrumentos a usar
