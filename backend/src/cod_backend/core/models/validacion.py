"""
Modelos Pydantic para validación de respuestas.
"""
from pydantic import BaseModel
from typing import List


class ValidacionItem(BaseModel):
    """Item individual de validación de una respuesta."""
    respuesta_id: int
    es_valida: bool
    razon: str


class ResultadoValidacion(BaseModel):
    """Resultado completo de validación de un batch de respuestas."""
    validaciones: List[ValidacionItem]

