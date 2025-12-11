"""
Utilidades para el proceso de codificación.
"""
from .batch_size import calcular_batch_size_optimo
from .categoria import detectar_categoria_desde_texto

__all__ = [
    "calcular_batch_size_optimo",
    "detectar_categoria_desde_texto",
]

