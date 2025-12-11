"""
Utilidades para calcular el tamaño óptimo de batches.
"""


def calcular_batch_size_optimo(
    total_respuestas: int,
    tamanio_catalogo: int = 0,
    modelo: str = "gpt-4o-mini"
) -> int:
    """
    Calcula un batch_size óptimo basado en el tamaño de los datos.
    
    Para modelos con contexto grande (gpt-4o, gpt-4-turbo): batch_size más grande
    Para modelos con contexto limitado (gpt-4o-mini): batch_size más conservador
    
    Args:
        total_respuestas: Número total de respuestas a procesar
        tamanio_catalogo: Número de códigos en el catálogo histórico
        modelo: Modelo GPT a usar
        
    Returns:
        batch_size recomendado (entre 5 y 20)
    """
    # Modelos con contexto grande pueden manejar batches más grandes
    modelos_grandes = ["gpt-4o", "gpt-4-turbo", "gpt-4", "o1"]
    es_modelo_grande = any(m in modelo.lower() for m in modelos_grandes)
    
    # Batch size base según el modelo
    if es_modelo_grande:
        batch_base = 15  # Modelos grandes pueden manejar más
    else:
        batch_base = 10  # Modelos pequeños más conservador
    
    # Ajustar según el tamaño del catálogo
    # Catálogos muy grandes reducen el espacio disponible para respuestas
    if tamanio_catalogo > 100:
        batch_base = max(5, batch_base - 3)
    elif tamanio_catalogo > 50:
        batch_base = max(7, batch_base - 2)
    
    # Para datasets muy grandes (1000+), mantener batch_size razonable
    # para evitar que los códigos existentes crezcan demasiado
    if total_respuestas > 1000:
        batch_base = min(batch_base, 12)  # Limitar a 12 para datasets grandes
    
    return batch_base

