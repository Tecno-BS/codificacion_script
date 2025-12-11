"""
Configuración del Backend - Sistema de Codificación Automatizada

Solo contiene las configuraciones realmente utilizadas en el código actual.
"""
import os
from pathlib import Path

# Cargar variables de entorno desde .env.backend
try:
    from dotenv import load_dotenv
    # Cargar .env.backend desde la raíz del workspace
    backend_env = Path(__file__).parent.parent.parent.parent.parent / ".env.backend"
    if backend_env.exists():
        load_dotenv(backend_env)
    else:
        # Fallback a .env.backend en la carpeta backend
        backend_env_local = Path(__file__).parent.parent.parent.parent / ".env.backend"
        if backend_env_local.exists():
            load_dotenv(backend_env_local)
except ImportError:
    print("[WARNING] python-dotenv no instalado, usando variables de entorno del sistema")

# ============================================
# CONFIGURACIÓN DE OPENAI
# ============================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ============================================
# RUTAS (relativas a la raíz del proyecto)
# ============================================

# Obtener la raíz del proyecto (cod-script/)
# Estructura: cod-script/backend/src/cod_backend/config/settings.py
# Necesitamos subir 5 niveles: config -> cod_backend -> src -> backend -> cod-script
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
