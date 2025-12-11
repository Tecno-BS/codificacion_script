"""
Estado del grafo de codificación.
"""
from typing import TypedDict, Dict, List, Any, Optional


class EstadoCodificacion(TypedDict):
    """Estado completo del grafo de codificación."""
    pregunta: str
    modelo_gpt: str
    batch_size: int
    respuestas: List[Dict[str, Any]]
    catalogo: List[Dict[str, Any]]
    catalogo_por_categoria: Dict[str, List[Dict[str, Any]]]  # Catálogo agrupado por categoría
    batch_actual: int
    batch_respuestas: List[Dict[str, Any]]
    codificaciones: List[Dict[str, Any]]
    validaciones_batch: List[Dict[str, Any]]
    evaluaciones_batch: List[Dict[str, Any]]
    cobertura_batch: List[Dict[str, Any]]
    proximo_codigo_nuevo: int
    respuestas_especiales: Dict[int, int]
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    # Configuración de dato auxiliar
    config_auxiliar: Optional[Dict[str, Any]]  # {"usar": bool, "categorizacion": {"negativas": [], "neutrales": [], "positivas": []}}

