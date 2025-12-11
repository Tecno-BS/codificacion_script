"""
Utilidades para detectar y manejar categorías de códigos.
"""
from typing import Optional
from ...utils import normalizar_texto


def detectar_categoria_desde_texto(texto: str) -> Optional[str]:
    """
    Detecta automáticamente la categoría basándose en el texto del marcador.
    
    Busca palabras clave como "negativa", "neutral", "positiva" en el texto,
    sin importar el formato (1-2 Negativas, 3-Neutras, 4-5 Positivas, etc.).
    
    Retorna: "negativas", "neutrales", "positivas", o None si no se detecta.
    """
    texto_normalizado = normalizar_texto(texto)
    
    # Palabras clave para cada categoría (en singular y plural)
    palabras_negativas = ["negativa", "negativas", "negativo", "negativos"]
    palabras_neutrales = ["neutral", "neutrales", "neutra", "neutras"]
    palabras_positivas = ["positiva", "positivas", "positivo", "positivos"]
    
    # Buscar coincidencias
    for palabra in palabras_negativas:
        if palabra in texto_normalizado:
            return "negativas"
    
    for palabra in palabras_neutrales:
        if palabra in texto_normalizado:
            return "neutrales"
    
    for palabra in palabras_positivas:
        if palabra in texto_normalizado:
            return "positivas"
    
    return None

