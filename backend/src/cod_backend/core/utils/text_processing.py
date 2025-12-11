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


def normalizar_marca_nombre(texto: str) -> str:
    """
    Normaliza un nombre de marca o nombre propio para comparación.
    Preserva mayúsculas iniciales y caracteres especiales importantes.
    
    Args:
        texto: Nombre de marca o nombre propio
        
    Returns:
        Nombre normalizado (sin espacios extra, con mayúsculas iniciales)
    """
    if not texto:
        return ""
    
    # Remover espacios al inicio y final
    texto = texto.strip()
    
    # Normalizar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    
    # Capitalizar palabras (preservar mayúsculas en medio de palabras como "McDonald's")
    palabras = texto.split()
    palabras_normalizadas = []
    for palabra in palabras:
        # Si la palabra tiene mayúsculas en medio (ej: "McDonald's", "iPhone"), preservarla
        if any(c.isupper() for c in palabra[1:]):
            palabras_normalizadas.append(palabra)
        else:
            # Capitalizar normalmente
            palabras_normalizadas.append(palabra.capitalize())
    
    return " ".join(palabras_normalizadas)


def es_marca_o_nombre_propio(texto: str) -> bool:
    """
    Detecta si un texto parece ser una marca o nombre propio.
    
    Criterios:
    - Es corto (menos de 50 caracteres)
    - No contiene verbos comunes
    - Puede contener mayúsculas en medio
    - No contiene puntuación de oración (., !, ?) excepto al final
    
    Args:
        texto: Texto a evaluar
        
    Returns:
        True si parece ser una marca o nombre propio
    """
    if not texto:
        return False
    
    texto_limpio = texto.strip()
    
    # Debe ser relativamente corto
    if len(texto_limpio) > 50:
        return False
    
    # No debe contener verbos comunes de opinión
    verbos_comunes = [
        "me gusta", "me encanta", "prefiero", "opino", "creo", "pienso",
        "es bueno", "es malo", "tiene", "hace", "puede", "debe"
    ]
    texto_lower = texto_limpio.lower()
    for verbo in verbos_comunes:
        if verbo in texto_lower:
            return False
    
    # No debe contener puntuación de oración en medio (solo al final)
    texto_sin_final = texto_limpio[:-1] if texto_limpio and texto_limpio[-1] in ".,!?" else texto_limpio
    if any(p in texto_sin_final for p in ".,!?"):
        return False
    
    # Si tiene mayúsculas en medio o es todo mayúsculas, probablemente es marca/nombre
    tiene_mayusculas_medio = any(c.isupper() for c in texto_limpio[1:-1] if texto_limpio)
    es_todo_mayusculas = texto_limpio.isupper() and len(texto_limpio) > 1
    
    # Si es muy corto (1-3 palabras) y no tiene verbos, probablemente es marca/nombre
    palabras = texto_limpio.split()
    es_corto = len(palabras) <= 3
    
    return (tiene_mayusculas_medio or es_todo_mayusculas or es_corto) and len(palabras) > 0


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

