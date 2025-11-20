"""
Schemas Pydantic para el sistema GPT Híbrido
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class RespuestaInput(BaseModel):
    """Representa una respuesta a codificar"""
    id: str = Field(..., description="ID único de la respuesta")
    texto: str = Field(..., description="Texto de la respuesta")
    pregunta: str = Field(..., description="Pregunta asociada")


class CodigoHistorico(BaseModel):
    """Representa un código del catálogo histórico"""
    codigo: str = Field(..., description="Código del catálogo")
    descripcion: str = Field(..., description="Descripción del código")


class Catalogo(BaseModel):
    """Representa el catálogo de códigos históricos"""
    pregunta: str = Field(..., description="Pregunta del catálogo")
    codigos: List[CodigoHistorico] = Field(default_factory=list, description="Lista de códigos")

    model_config = {
        # Para aceptar también dict con 'codigo' y 'descripcion'
        "populate_by_name": True
    }


class ResultadoCodificacion(BaseModel):
    """Resultado de codificación para una respuesta"""
    respuesta_id: str = Field(..., description="ID de la respuesta codificada")
    decision: str = Field(..., description="Decisión: asignar, nuevo, mixto, rechazar")
    codigos_historicos: List[str] = Field(default_factory=list, description="Códigos del catálogo asignados")
    codigo_nuevo: Optional[str] = Field(None, description="Código nuevo (singular, compatibilidad)")
    descripcion_nueva: Optional[str] = Field(None, description="Descripción nueva (singular, compatibilidad)")
    idea_principal: Optional[str] = Field(None, description="Idea principal extraída")
    confianza: float = Field(..., description="Nivel de confianza (0-1)")
    justificacion: str = Field(..., description="Justificación de la decisión")
    # Nuevos campos para multicodificación completa
    codigos_nuevos: List[str] = Field(default_factory=list, description="Múltiples códigos nuevos")
    descripciones_nuevas: List[str] = Field(default_factory=list, description="Múltiples descripciones nuevas")

    def model_post_init(self, __context) -> None:
        """Normalizar campos después de inicialización (similar a __post_init__)"""
        # Si codigos_nuevos está vacío pero hay codigo_nuevo, migrar
        if not self.codigos_nuevos and self.codigo_nuevo:
            self.codigos_nuevos = [self.codigo_nuevo]
        
        # Si descripciones_nuevas está vacío pero hay descripcion_nueva, migrar
        if not self.descripciones_nuevas and self.descripcion_nueva:
            self.descripciones_nuevas = [self.descripcion_nueva]

