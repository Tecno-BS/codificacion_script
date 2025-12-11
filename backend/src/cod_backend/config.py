"""
Configuración del Backend - Sistema de Codificación Automatizada

Este archivo mantiene compatibilidad con código antiguo que importa desde .config
Reexporta todo desde el nuevo módulo config/
"""
# Reexportar todo desde los submódulos de config/
from .config.pricing import PRECIOS_POR_1K, obtener_precios, calcular_costo
from .config.models import supports_temperature
from .config.settings import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    PROJECT_ROOT,
)
