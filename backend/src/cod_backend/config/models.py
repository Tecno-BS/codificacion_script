"""
Configuración de modelos de LLM.
"""
from typing import Dict


def supports_temperature(model: str) -> bool:
    """
    Detecta si el modelo permite modificar temperature.
    
    GPT-5 y O1 no permiten modificar temperature (usan 1 por defecto).
    Otros modelos sí permiten temperature.
    
    Args:
        model: Nombre del modelo
        
    Returns:
        True si el modelo soporta modificar temperature, False en caso contrario
    """
    model_lower = model.lower()
    # GPT-5 y O1 no permiten modificar temperature
    if 'gpt-5' in model_lower or 'gpt-6' in model_lower:
        return False
    if model_lower.startswith('o1'):
        return False
    # Otros modelos sí permiten temperature
    return True


def get_default_temperature(model: str) -> float:
    """
    Obtiene la temperature por defecto para un modelo.
    
    Args:
        model: Nombre del modelo
        
    Returns:
        Temperature por defecto (0.1 para modelos que lo soportan, 1.0 para otros)
    """
    if supports_temperature(model):
        return 0.1
    return 1.0

