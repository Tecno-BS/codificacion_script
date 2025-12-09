"""
Modelos Pydantic del sistema de codificación.
"""
from .validacion import ValidacionItem, ResultadoValidacion
from .evaluacion import EvaluacionCodigo, EvaluacionRespuesta, ResultadoEvaluacion
from .cobertura import ConceptoNuevo, AnalisisCobertura, ResultadoCobertura

__all__ = [
    "ValidacionItem",
    "ResultadoValidacion",
    "EvaluacionCodigo",
    "EvaluacionRespuesta",
    "ResultadoEvaluacion",
    "ConceptoNuevo",
    "AnalisisCobertura",
    "ResultadoCobertura",
]

