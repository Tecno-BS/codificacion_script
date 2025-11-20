"""
FastAPI Application - Sistema de Codificación Automatizada
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .api.routes import codificacion
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

# Configurar CORS (permitir acceso desde frontend Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Streamlit local
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== RUTAS ==========

# Incluir rutas de codificación
app.include_router(codificacion.router, prefix="/api/v1", tags=["codificacion"])


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
    return HealthResponse(
        status="ok",
        version="0.8.0",
        modo_mock=config.USE_GPT_MOCK,
        openai_disponible=config.OPENAI_AVAILABLE
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
