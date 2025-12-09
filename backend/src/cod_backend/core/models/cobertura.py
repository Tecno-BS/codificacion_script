"""
Modelos Pydantic para análisis de cobertura y conceptos nuevos.
"""
from pydantic import BaseModel
from typing import List


class ConceptoNuevo(BaseModel):
    """Concepto nuevo identificado que no está cubierto por códigos históricos."""
    codigo: int
    descripcion: str
    texto_original: str


class AnalisisCobertura(BaseModel):
    """Análisis de cobertura para una respuesta específica."""
    respuesta_id: int
    respuesta_cubierta_completamente: bool
    conceptos_nuevos: List[ConceptoNuevo]


class ResultadoCobertura(BaseModel):
    """Resultado completo de análisis de cobertura de un batch de respuestas."""
    analisis: List[AnalisisCobertura]

