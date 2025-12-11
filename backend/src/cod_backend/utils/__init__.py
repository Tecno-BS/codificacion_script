"""
Utilidades del backend - Paquete de utilidades
"""
# Reexportar funciones de error_handler
from .error_handler import (
    obtener_mensaje_error_descriptivo,
    obtener_traceback_completo,
    formatear_error_para_frontend,
    extraer_mensaje_error_principal,
)

# Importar funciones del módulo data_utils.py del nivel superior
from ..data_utils import (
    save_data,
    load_data,
    clean_text,
    clean_text_for_gpt,
    fix_encoding_issues,
    verify_codes,
)

__all__ = [
    # Error handling
    "obtener_mensaje_error_descriptivo",
    "obtener_traceback_completo",
    "formatear_error_para_frontend",
    "extraer_mensaje_error_principal",
    # Data utilities (si están disponibles)
    "save_data",
    "load_data",
    "clean_text",
    "clean_text_for_gpt",
    "fix_encoding_issues",
    "verify_codes",
]

