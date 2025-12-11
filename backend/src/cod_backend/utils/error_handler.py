"""
Utilidades para manejo de errores mejorado
"""
import traceback
from typing import Optional, Dict, Any


def obtener_mensaje_error_descriptivo(error: Exception, contexto: Optional[str] = None) -> str:
    """
    Obtiene un mensaje de error descriptivo a partir de una excepción.
    
    Args:
        error: La excepción capturada
        contexto: Contexto adicional sobre dónde ocurrió el error
        
    Returns:
        Mensaje de error descriptivo y útil para el usuario
    """
    tipo_error = type(error).__name__
    mensaje_base = str(error)
    
    # Mensajes más descriptivos según el tipo de error
    mensajes_mejorados = {
        "ValueError": mensaje_base,
        "FileNotFoundError": f"Archivo no encontrado: {mensaje_base}",
        "PermissionError": f"Error de permisos: {mensaje_base}",
        "KeyError": f"Clave no encontrada: {mensaje_base}",
        "IndexError": f"Índice fuera de rango: {mensaje_base}",
        "TypeError": f"Error de tipo: {mensaje_base}",
        "AttributeError": f"Atributo no encontrado: {mensaje_base}",
        "JSONDecodeError": f"Error al parsear JSON: {mensaje_base}",
        "HTTPException": mensaje_base,  # Ya tiene un mensaje descriptivo
        "RuntimeError": mensaje_base,
    }
    
    # Obtener mensaje mejorado o usar el mensaje base
    mensaje = mensajes_mejorados.get(tipo_error, mensaje_base)
    
    # Agregar contexto si está disponible
    if contexto:
        mensaje = f"{contexto}: {mensaje}"
    
    # Si el mensaje está vacío, usar el tipo de error
    if not mensaje:
        mensaje = f"Error de tipo {tipo_error}"
    
    return mensaje


def obtener_traceback_completo(error: Exception) -> str:
    """
    Obtiene el traceback completo de una excepción como string.
    
    Args:
        error: La excepción capturada
        
    Returns:
        Traceback completo como string
    """
    return "".join(traceback.format_exception(type(error), error, error.__traceback__))


def formatear_error_para_frontend(
    error: Exception,
    contexto: Optional[str] = None,
    incluir_traceback: bool = False
) -> Dict[str, Any]:
    """
    Formatea un error para enviarlo al frontend de manera estructurada.
    
    Args:
        error: La excepción capturada
        contexto: Contexto adicional sobre dónde ocurrió el error
        incluir_traceback: Si incluir el traceback completo (útil para debugging)
        
    Returns:
        Diccionario con información del error formateada
    """
    mensaje = obtener_mensaje_error_descriptivo(error, contexto)
    
    resultado = {
        "mensaje": mensaje,
        "tipo": type(error).__name__,
    }
    
    if incluir_traceback:
        resultado["traceback"] = obtener_traceback_completo(error)
    
    return resultado


def extraer_mensaje_error_principal(error: Exception) -> str:
    """
    Extrae el mensaje principal de un error, incluso si está anidado.
    
    Args:
        error: La excepción capturada
        
    Returns:
        Mensaje principal del error
    """
    mensaje = str(error)
    
    # Si el error tiene un mensaje anidado, intentar extraerlo
    if hasattr(error, "__cause__") and error.__cause__:
        mensaje_causa = str(error.__cause__)
        if mensaje_causa and mensaje_causa != mensaje:
            mensaje = f"{mensaje}: {mensaje_causa}"
    
    # Limpiar mensajes muy largos o con información técnica innecesaria
    if len(mensaje) > 500:
        mensaje = mensaje[:500] + "..."
    
    return mensaje

