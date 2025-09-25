"""
Sistema de Codificación Semántica Inteligente

Un sistema híbrido que combina embeddings semánticos con GPT
para mejorar la precisión y consistencia en la codificación
de respuestas abiertas de encuestas.

Módulos principales:
- config: Configuraciones del sistema
- utils: Funciones auxiliares
- embeddings: Generación de embeddings semánticos
- codificador: Lógica principal de codificación
- evaluador: Evaluación y métricas
- main: Interfaz de línea de comandos
"""

# Importar clases principales
from codificador import SemanticCoder
from evaluador import EvaluatorCodification
from embeddings import GenerateEmbeddings

# Importar configuraciones
from config import *

# Importar funciones auxiliares
from utils import (
    clean_text,
    load_data,
    save_data,
    verify_codes
)

# Metadatos del paquete
__version__ = "1.0.0"
__author__ = "Ivan"
__email__ = "a.tecno@brandstrat.co"
__description__ = "Sistema de Codificación Semántica Inteligente"

# Lista de clases y funciones exportadas
__all__ = [
    # Clases principales
    "SemanticCoder",
    "EvaluatorCodification", 
    "GenerateEmbeddings",
    
    # Funciones auxiliares
    "clean_text",
    "load_data",
    "save_data",
    "verify_codes",
    
    # Configuraciones
    "UMBRAL_SIMILITUD",
    "TOP_CANDIDATOS",
    "MAX_CODIGOS",
    "EMBEDDING_MODEL",
    "NO_ACCENT",
    "NO_SPECIAL_CHARS",
    "TO_LOWER",
    "RUTA_DATA_RAW",
    "RUTA_DATA_PROCESSED",
    "RUTA_RESULTADOS",
    "BATCH_SIZE",
    "MAX_LONGITUD_TEXT"
]