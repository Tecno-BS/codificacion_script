"""
Schemas Pydantic para la API REST
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class CodificacionRequest(BaseModel):
    """Request para codificación"""
    ruta_respuestas: str = Field(..., description="Ruta al archivo Excel de respuestas")
    ruta_codigos: Optional[str] = Field(None, description="Ruta al archivo Excel de códigos históricos (opcional)")
    modelo: str = Field("gpt-4o-mini", description="Modelo GPT a usar")


class CodificacionResponse(BaseModel):
    """Response de codificación"""
    mensaje: str
    total_respuestas: int
    total_preguntas: int
    costo_total: float
    ruta_resultados: Optional[str] = None
    ruta_codigos_nuevos: Optional[str] = None


class HealthResponse(BaseModel):
    """Response de health check"""
    status: str
    version: str
    modo_mock: bool
    openai_disponible: bool

