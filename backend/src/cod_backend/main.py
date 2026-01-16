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

# Si PUBLIC_ACCESS está configurado, permitir acceso desde cualquier origen
public_access = os.getenv("PUBLIC_ACCESS", "false").lower() == "true"

if public_access:
    # Modo público: permitir acceso desde cualquier origen
    # Usamos allow_origin_regex con una regex que permite cualquier URL HTTP/HTTPS
    # También incluimos explícitamente los orígenes comunes por si la regex falla
    print("MODO PUBLICO ACTIVADO: El servidor acepta conexiones desde cualquier origen")
    
    # Obtener la IP del servidor si está disponible
    server_ip = os.getenv("SERVER_IP", "192.168.2.4")
    server_domain = os.getenv("SERVER_DOMAIN", "codificacion-automatizada.brandstratx.sas.corp")
    
    # Lista de orígenes comunes que siempre permitimos
    common_origins = [
        f"http://{server_ip}:3000",
        f"http://{server_domain}:3000",
        f"http://localhost:3000",
        f"http://127.0.0.1:3000",
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=common_origins,
        allow_origin_regex=r"https?://.*",
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
else:
    # Modo por defecto: solo localhost
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
    print("Ejecutando limpieza automática de archivos temporales...")
    codificacion.limpiar_archivos_temporales(horas_antiguedad=24)
    print("Servidor iniciado correctamente")


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

def run(host="0.0.0.0", port=8000, reload=None):
    """Función para ejecutar el servidor
    
    Args:
        host: Dirección IP donde escuchar (default: "0.0.0.0" para todas las interfaces)
        port: Puerto donde escuchar (default: 8000)
        reload: Activar auto-reload (default: None, se detecta automáticamente)
    """
    import os
    
    # Detectar si estamos en modo desarrollo o producción
    if reload is None:
        reload = os.getenv("ENVIRONMENT", "development") != "production"
    
    # Obtener configuración desde variables de entorno si están disponibles
    host = os.getenv("HOST", host)
    port = int(os.getenv("PORT", port))
    
    print(f"🚀 Iniciando servidor en http://{host}:{port}")
    print(f"📚 Documentación disponible en http://{host}:{port}/docs")
    
    uvicorn.run(
        "cod_backend.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run()
