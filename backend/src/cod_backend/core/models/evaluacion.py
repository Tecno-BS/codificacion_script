"""
Modelos Pydantic para evaluación de catálogo histórico.
"""
from pydantic import BaseModel
from typing import List


class EvaluacionCodigo(BaseModel):
    """Evaluación de un código histórico para una respuesta."""
    codigo: int
    aplica: bool
    confianza: float


class EvaluacionRespuesta(BaseModel):
    """Evaluación de todos los códigos para una respuesta."""
    respuesta_id: int
    evaluaciones: List[EvaluacionCodigo]


class ResultadoEvaluacion(BaseModel):
    """Resultado completo de evaluación de un batch de respuestas."""
    evaluaciones: List[EvaluacionRespuesta]

