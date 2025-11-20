"""
Configuración del Backend - Sistema de Codificación Automatizada
"""
import os
from pathlib import Path

# Cargar variables de entorno desde .env.backend
try:
    from dotenv import load_dotenv
    # Cargar .env.backend desde la raíz del workspace
    backend_env = Path(__file__).parent.parent.parent.parent / ".env.backend"
    if backend_env.exists():
        load_dotenv(backend_env)
    else:
        # Fallback a .env.backend en la carpeta backend
        backend_env_local = Path(__file__).parent.parent.parent / ".env.backend"
        if backend_env_local.exists():
            load_dotenv(backend_env_local)
except ImportError:
    print("[WARNING] python-dotenv no instalado, usando variables de entorno del sistema")

# ============================================
# CONFIGURACIÓN DE OPENAI
# ============================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GPT_TEMPERATURE = 0.1
GPT_MAX_TOKENS = 350
GPT_TOP_K = 5
GPT_BATCH_SIZE = 20
MAX_CHARS_TEXTO = 500
PRESUPUESTO_USD_MAX = 10.0

# ============================================
# MULTICODIFICACIÓN
# ============================================

HABILITAR_MULTICODIGO = True
UMBRAL_MULTICODIGO = 0.95
SEPARADOR_CODIGOS = ";"

AUXILIARES_POR_PREGUNTA = {
    "P12A": {"col_aux": "P12", "normalizar": True}
}

AUXILIARES_CANONICOS = {
    "favorable": "favorable",
    "regular": "regular",
    "poco favorable": "poco favorable",
    "poco favoral": "poco favorable",
    "desfavorable": "poco favorable",
    "nada favorable": "poco favorable"
}

# ============================================
# CACHE DE GPT
# ============================================

GPT_CACHE_ENABLED = True
GPT_CACHE_FILE = "result/modelos/gpt_cache.json"

# ============================================
# PARÁMETROS DE CODIFICACIÓN
# ============================================

UMBRAL_SIMILITUD = 0.85  # Aumentado para mayor precisión (era 0.75)
TOP_CANDIDATOS = 8  # Más candidatos para GPT (era 5)
MAX_CODIGOS = 3  # Máximo de códigos por respuesta

# ============================================
# MODELO DE EMBEDDINGS (LEGACY - No usado en v0.5+)
# ============================================

# EMBEDDING_MODEL = "distilbert-base-multilingual-cased"  # Ya no se usa

# ============================================
# PARÁMETROS DE LIMPIEZA DE RESPUESTAS
# ============================================

NO_ACCENT = True  # Tildes
NO_SPECIAL_CHARS = True  # Caracteres especiales
TO_LOWER = True  # Minúsculas

# ============================================
# RUTAS (relativas a la raíz del proyecto)
# ============================================

# Obtener la raíz del proyecto (cod-script/)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RUTA_DATOS_RAW = str(PROJECT_ROOT / "data" / "raw")
RUTA_DATA_PROCESSED = str(PROJECT_ROOT / "data" / "processed")
RUTA_RESULTADOS = str(PROJECT_ROOT / "result")

# ============================================
# MODO MOCK (DESARROLLO)
# ============================================

USE_GPT_MOCK = os.getenv("USE_GPT_MOCK", "true").lower() == "true"

# ============================================
# INICIALIZAR CLIENTE OPENAI
# ============================================

OPENAI_AVAILABLE = False
OPENAI_CLIENT = None

if not USE_GPT_MOCK and OPENAI_API_KEY:
    try:
        from openai import OpenAI
        OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY)
        OPENAI_AVAILABLE = True
        print("[REAL] Modo producción activado - Se consumirá API real de OpenAI")
        print(f"[REAL] API Key configurada: {OPENAI_API_KEY[:7]}...{OPENAI_API_KEY[-4:]}")
    except ImportError:
        print("[ERROR] Biblioteca 'openai' no instalada. Instala: pip install openai")
        USE_GPT_MOCK = True
    except Exception as e:
        print(f"[ERROR] No se pudo inicializar cliente OpenAI: {e}")
        USE_GPT_MOCK = True

if USE_GPT_MOCK:
    print("[MOCK] Modo desarrollo activado - No se consumirá API real de OpenAI")
