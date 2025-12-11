"""
FastAPI Application - Sistema de Codificación Automatizada
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .api.routes import codificacion, progress
from .schemas.api_schemas import HealthResponse
from . import config

# Crear aplicación FastAPI
app = FastAPI(
    title="Codificación Automatizada API",
    version="0.8.0",
    description="API REST para codificación automatizada de respuestas con GPT",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS (permitir acceso desde frontend)
# En producción, usar variables de entorno para los orígenes permitidos
import os
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
if os.getenv("ENVIRONMENT") == "production":
    # En producción, agregar el dominio real
    production_domain = os.getenv("PRODUCTION_DOMAIN", "")
    if production_domain:
        cors_origins.extend([
            f"https://{production_domain}",
            f"http://{production_domain}",
        ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== RUTAS ==========

# Incluir rutas de codificación
app.include_router(codificacion.router, prefix="/api/v1", tags=["codificacion"])

# Incluir rutas de progreso
app.include_router(progress.router, prefix="/api/v1", tags=["progreso"])


# ========== EVENTOS DE INICIO ==========

@app.on_event("startup")
async def startup_event():
    """Ejecuta tareas al iniciar el servidor"""
    # 🆕 MEJORA 2: Limpieza automática de archivos temporales al inicio
    print("🧹 Ejecutando limpieza automática de archivos temporales...")
    codificacion.limpiar_archivos_temporales(horas_antiguedad=24)
    print("✅ Servidor iniciado correctamente")


# ========== ENDPOINTS BASE ==========

@app.get("/")
async def root():
    """Endpoint raíz - Información básica de la API"""
    return {
        "nombre": "Codificación Automatizada API",
        "version": "0.8.0",
        "descripcion": "API REST para codificación con GPT",
        "documentacion": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check - Verificar que la API está funcionando"""
    # Verificar si OpenAI está disponible
    openai_disponible = config.OPENAI_API_KEY is not None and config.OPENAI_API_KEY != ""
    
    return HealthResponse(
        status="ok",
        version="0.8.0",
        modo_mock=False,  # Ya no usamos modo mock
        openai_disponible=openai_disponible
    )


# ========== MANEJO DE ERRORES ==========

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de errores"""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )


# ========== FUNCIÓN PARA EJECUTAR ==========

def run():
    """Función para ejecutar el servidor"""
    uvicorn.run(
        "cod_backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload en desarrollo
        log_level="info"
    )


if __name__ == "__main__":
    run()
