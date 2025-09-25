#Configuraciones de la aplicación
import os 

# Configuración de OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"  # Cambié a 4o-mini (más barato y eficiente)
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
    "poco favoral": "poco favorable",  # Variante común
    "desfavorable": "poco favorable",
    "nada favorable": "poco favorable"
}



# Cache de GPT
GPT_CACHE_ENABLED = True
GPT_CACHE_FILE = "result/modelos/gpt_cache.json"


#Parámetros de asignación de códigos
UMBRAL_SIMILITUD = 0.75
TOP_CANDIDATOS = 5 
MAX_CODIGOS = 3

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

# Configuración de modo mock
USE_GPT_MOCK = os.getenv("USE_GPT_MOCK", "true").lower() == "true"

# Logging para modo mock
if USE_GPT_MOCK:
    print("🤖 MODO MOCK ACTIVADO - No se consumirá API real de OpenAI")
else:
    print("⚠️ MODO REAL ACTIVADO - Se consumirá API real de OpenAI")



