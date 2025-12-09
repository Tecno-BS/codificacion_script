"""
Servicio para cálculo de costos y precios.
"""
from typing import Dict
from ....config import calcular_costo, obtener_precios


class PricingService:
    """
    Servicio para calcular costos de uso de LLM.
    """
    
    @staticmethod
    def calcular_costo_total(
        prompt_tokens: int,
        completion_tokens: int,
        modelo: str
    ) -> float:
        """
        Calcula el costo total basado en tokens y modelo.
        
        Args:
            prompt_tokens: Número de tokens de entrada
            completion_tokens: Número de tokens de salida
            modelo: Nombre del modelo
            
        Returns:
            Costo total en USD
        """
        return calcular_costo(prompt_tokens, completion_tokens, modelo)
    
    @staticmethod
    def obtener_precios_modelo(modelo: str) -> Dict[str, float]:
        """
        Obtiene los precios para un modelo específico.
        
        Args:
            modelo: Nombre del modelo
            
        Returns:
            Diccionario con precios de prompt y completion por 1K tokens
        """
        return obtener_precios(modelo)

