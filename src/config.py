#Configuraciones de la aplicación
import os 

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("[WARNING] python-dotenv no instalado, usando variables de entorno del sistema")

# Configuración de OpenAI (leer del entorno)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Permitir elegir modelo desde .env 
GPT_TEMPERATURE = 0.1
GPT_MAX_TOKENS = 350
GPT_TOP_K = 5
GPT_BATCH_SIZE = 20
MAX_CHARS_TEXTO = 500
PRESUPUESTO_USD_MAX = 10.0 

# Multicodificación
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

# Cache de GPT
GPT_CACHE_ENABLED = True
GPT_CACHE_FILE = "result/modelos/gpt_cache.json"


#Parámetros de asignación de códigos
UMBRAL_SIMILITUD = 0.85  # Aumentado para mayor precisión (era 0.75)
TOP_CANDIDATOS = 8  # Más candidatos para GPT (era 5)
MAX_CODIGOS = 3  # Máximo de códigos por respuesta

#Modelo para realizar los embeddings
EMBEDDING_MODEL = "distilbert-base-multilingual-cased"

#Parametros de limpieza de respuestas
NO_ACCENT = True #Tildes
NO_SPECIAL_CHARS = True #Caracteres especiales
TO_LOWER = True #Minusculas


#Rutas
RUTA_DATOS_RAW = "data/raw/"
RUTA_DATA_PROCESSED = "data/processed/"
RUTA_RESULTADOS = "result/"

# Configuración de modo mock (leer del entorno)
USE_GPT_MOCK = os.getenv("USE_GPT_MOCK", "true").lower() == "true"

# Inicializar cliente OpenAI si está disponible y no es modo MOCK
OPENAI_AVAILABLE = False
OPENAI_CLIENT = None

if not USE_GPT_MOCK and OPENAI_API_KEY:
    try:
        from openai import OpenAI
        OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY)
        OPENAI_AVAILABLE = True
        print("[REAL] Modo produccion activado - Se consumira API real de OpenAI")
        print(f"[REAL] API Key configurada: {OPENAI_API_KEY[:7]}...{OPENAI_API_KEY[-4:]}")
    except ImportError:
        print("[ERROR] Biblioteca 'openai' no instalada. Instala: pip install openai")
        USE_GPT_MOCK = True
    except Exception as e:
        print(f"[ERROR] No se pudo inicializar cliente OpenAI: {e}")
        USE_GPT_MOCK = True

if USE_GPT_MOCK:
    print("[MOCK] Modo desarrollo activado - No se consumira API real de OpenAI")



