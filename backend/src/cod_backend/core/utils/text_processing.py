"""
Utilidades para procesamiento y normalización de texto.
"""
import re
from typing import Optional


def normalizar_texto(texto: str) -> str:
    """
    Normaliza un texto para comparación (minúsculas, sin acentos básicos, sin espacios extra).
    
    Args:
        texto: Texto a normalizar
        
    Returns:
        Texto normalizado
    """
    if not texto:
        return ""
    
    # Convertir a minúsculas
    texto = texto.lower()
    
    # Remover espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    
    # Remover acentos básicos (simplificado)
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n', 'ü': 'u'
    }
    for old, new in replacements.items():
        texto = texto.replace(old, new)
    
    return texto.strip()


def son_conceptos_similares(desc1: str, desc2: str, umbral_similitud: float = 0.85) -> bool:
    """
    Determina si dos conceptos son similares basándose en normalización y comparación.
    
    Args:
        desc1: Primera descripción
        desc2: Segunda descripción
        umbral_similitud: Umbral de similitud (0.0-1.0)
        
    Returns:
        True si los conceptos son similares, False en caso contrario
    """
    norm1 = normalizar_texto(desc1)
    norm2 = normalizar_texto(desc2)
    
    if not norm1 or not norm2:
        return False
    
    # Comparación simple: si son iguales después de normalizar
    if norm1 == norm2:
        return True
    
    # Comparación por inclusión (si uno contiene al otro)
    if norm1 in norm2 or norm2 in norm1:
        return True
    
    # Comparación por palabras comunes (simplificado)
    palabras1 = set(norm1.split())
    palabras2 = set(norm2.split())
    
    if not palabras1 or not palabras2:
        return False
    
    interseccion = palabras1.intersection(palabras2)
    union = palabras1.union(palabras2)
    
    if not union:
        return False
    
    similitud = len(interseccion) / len(union)
    return similitud >= umbral_similitud


def detectar_codigo_especial(texto: str) -> Optional[int]:
    """
    Detecta si una respuesta contiene un código especial (NS, NC, etc.).
    
    Args:
        texto: Texto de la respuesta
        
    Returns:
        Código especial si se detecta, None en caso contrario
    """
    if not texto:
        return None
    
    texto_upper = texto.strip().upper()
    
    # Códigos especiales comunes
    codigos_especiales = {
        "NS": 98,  # No sabe
        "NC": 99,  # No contesta
        "NO SABE": 98,
        "NO CONTESTA": 99,
        "N/A": 97,
        "NA": 97,
    }
    
    return codigos_especiales.get(texto_upper)

