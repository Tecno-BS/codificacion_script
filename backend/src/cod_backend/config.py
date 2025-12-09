"""
Configuración del Backend - Sistema de Codificación Automatizada

Este archivo mantiene compatibilidad con código antiguo que importa desde .config
Reexporta todo desde el nuevo módulo config/
"""
# Reexportar todo desde los submódulos de config/
from .config.pricing import PRECIOS_POR_1K, obtener_precios, calcular_costo
from .config.models import supports_temperature, get_default_temperature
from .config.settings import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    GPT_TEMPERATURE,
    GPT_MAX_TOKENS,
    GPT_TOP_K,
    GPT_BATCH_SIZE,
    MAX_CHARS_TEXTO,
    PRESUPUESTO_USD_MAX,
    HABILITAR_MULTICODIGO,
    UMBRAL_MULTICODIGO,
    SEPARADOR_CODIGOS,
    AUXILIARES_POR_PREGUNTA,
    AUXILIARES_CANONICOS,
    GPT_CACHE_ENABLED,
    GPT_CACHE_FILE,
    UMBRAL_SIMILITUD,
    TOP_CANDIDATOS,
    MAX_CODIGOS,
    NO_ACCENT,
    NO_SPECIAL_CHARS,
    TO_LOWER,
    RUTA_DATOS_RAW,
    RUTA_DATA_PROCESSED,
    RUTA_RESULTADOS,
    USE_GPT_MOCK,
    OPENAI_AVAILABLE,
    OPENAI_CLIENT,
    PROJECT_ROOT,
)
