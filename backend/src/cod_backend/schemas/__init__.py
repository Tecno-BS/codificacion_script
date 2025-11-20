"""
Schemas Pydantic para la API
"""
from .gpt_schemas import (
    RespuestaInput,
    Catalogo,
    CodigoHistorico,
    ResultadoCodificacion,
)

__all__ = [
    "RespuestaInput",
    "Catalogo",
    "CodigoHistorico",
    "ResultadoCodificacion",
]
