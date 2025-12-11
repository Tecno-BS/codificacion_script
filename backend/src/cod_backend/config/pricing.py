"""
Configuración de precios por modelo de OpenAI.

Precios convertidos desde precios por 1M tokens de OpenAI (divididos por 1000).
Fuente: https://openai.com/api/pricing/ (actualizado 2025)
"""
from typing import Dict

# Precios por modelo (USD por 1K tokens)
PRECIOS_POR_1K: Dict[str, Dict[str, float]] = {
    "gpt-5": {
        "prompt": 0.005,      # $5.00 por 1M tokens → $0.005 por 1K tokens
        "completion": 0.015,  # $15.00 por 1M tokens → $0.015 por 1K tokens
    },
    "gpt-4.1": {
        "prompt": 0.003,      # $3.00 por 1M tokens → $0.003 por 1K tokens
        "completion": 0.012,  # $12.00 por 1M tokens → $0.012 por 1K tokens
    },
    "gpt-4o": {
        "prompt": 0.0025,     # $2.50 por 1M tokens → $0.0025 por 1K tokens
        "completion": 0.01,   # $10.00 por 1M tokens → $0.01 por 1K tokens
    },
    "gpt-4o-mini": {
        "prompt": 0.00015,   # $0.150 por 1M tokens → $0.00015 por 1K tokens
        "completion": 0.0006, # $0.600 por 1M tokens → $0.0006 por 1K tokens
    }
}


def obtener_precios(modelo: str) -> Dict[str, float]:
    """
    Obtiene los precios para un modelo específico.
    
    Args:
        modelo: Nombre del modelo (ej: "gpt-5", "gpt-4o-mini")
        
    Returns:
        Diccionario con precios de prompt y completion por 1K tokens
    """
    return PRECIOS_POR_1K.get(
        modelo, 
        PRECIOS_POR_1K.get("gpt-5", {"prompt": 0.0, "completion": 0.0})
    )


def calcular_costo(prompt_tokens: int, completion_tokens: int, modelo: str) -> float:
    """
    Calcula el costo total basado en tokens y modelo.
    
    Args:
        prompt_tokens: Número de tokens de entrada
        completion_tokens: Número de tokens de salida
        modelo: Nombre del modelo
        
    Returns:
        Costo total en USD
    """
    precios = obtener_precios(modelo)
    costo_total = (
        (prompt_tokens / 1000.0) * precios["prompt"]
        + (completion_tokens / 1000.0) * precios["completion"]
    )
    return costo_total

