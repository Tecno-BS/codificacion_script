"""
Sistema de progreso y control de codificación en tiempo real
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import Dict, Optional
import asyncio
import json
from datetime import datetime

router = APIRouter()

# Almacenamiento en memoria para el estado de los procesos
procesos_activos: Dict[str, Dict] = {}

class ControladorProceso:
    """Controlador para manejar el estado de un proceso de codificación"""
    
    def __init__(self, proceso_id: str):
        self.proceso_id = proceso_id
        self.pausado = False
        self.cancelado = False
        self.batch_actual = 0
        self.total_batches = 0
        self.respuestas_procesadas = 0
        self.total_respuestas = 0
        self.mensaje = "Iniciando..."
        self.progreso_pct = 0.0
        # Información adicional al finalizar
        self.archivo_resultados: str | None = None
        self.archivo_codigos_nuevos: str | None = None
        self.stats: dict | None = None
        
    def actualizar(
        self,
        batch_actual: Optional[int] = None,
        respuestas_procesadas: Optional[int] = None,
        mensaje: Optional[str] = None
    ):
        """Actualizar el estado del proceso"""
        if batch_actual is not None:
            self.batch_actual = batch_actual
        if respuestas_procesadas is not None:
            self.respuestas_procesadas = respuestas_procesadas
        if mensaje is not None:
            self.mensaje = mensaje
            
        # Calcular progreso
        if self.total_respuestas > 0:
            self.progreso_pct = (self.respuestas_procesadas / self.total_respuestas) * 100
    
    def pausar(self):
        """Pausar el proceso"""
        self.pausado = True
        
    def reanudar(self):
        """Reanudar el proceso"""
        self.pausado = False
        
    def cancelar(self):
        """Cancelar el proceso"""
        self.cancelado = True
        
    def to_dict(self):
        """Convertir a diccionario para enviar al frontend"""
        return {
            "proceso_id": self.proceso_id,
            "pausado": self.pausado,
            "cancelado": self.cancelado,
            "batch_actual": self.batch_actual,
            "total_batches": self.total_batches,
            "respuestas_procesadas": self.respuestas_procesadas,
            "total_respuestas": self.total_respuestas,
            "mensaje": self.mensaje,
            "progreso_pct": round(self.progreso_pct, 1),
            "timestamp": datetime.now().isoformat(),
            # Campos opcionales que pueden llenarse al finalizar
            "archivo_resultados": self.archivo_resultados,
            "archivo_codigos_nuevos": self.archivo_codigos_nuevos,
            "stats": self.stats,
        }


def crear_proceso(proceso_id: str, total_respuestas: int, total_batches: int) -> ControladorProceso:
    """Crear un nuevo proceso"""
    controlador = ControladorProceso(proceso_id)
    controlador.total_respuestas = total_respuestas
    controlador.total_batches = total_batches
    procesos_activos[proceso_id] = controlador
    return controlador


def obtener_proceso(proceso_id: str) -> Optional[ControladorProceso]:
    """Obtener un proceso existente"""
    return procesos_activos.get(proceso_id)


def eliminar_proceso(proceso_id: str):
    """Eliminar un proceso completado"""
    if proceso_id in procesos_activos:
        del procesos_activos[proceso_id]


@router.get("/progreso/{proceso_id}")
async def stream_progreso(proceso_id: str):
    """
    Stream de progreso en tiempo real usando Server-Sent Events (SSE)
    """
    async def event_generator():
        controlador = obtener_proceso(proceso_id)
        
        if not controlador:
            # Proceso no encontrado
            yield f"data: {json.dumps({'error': 'Proceso no encontrado'})}\n\n"
            return
        
        # Enviar actualizaciones cada 500ms
        while not controlador.cancelado:
            # Enviar estado actual
            data = controlador.to_dict()
            yield f"data: {json.dumps(data)}\n\n"
            
            # Si el proceso está completado (100%), enviar y cerrar
            if controlador.progreso_pct >= 100:
                await asyncio.sleep(0.5)
                yield f"data: {json.dumps({'completado': True, **data})}\n\n"
                break
            
            # Esperar antes de la siguiente actualización
            await asyncio.sleep(0.5)
        
        # Si fue cancelado
        if controlador.cancelado:
            yield f"data: {json.dumps({'cancelado': True, **controlador.to_dict()})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Deshabilitar buffering en nginx
        }
    )


@router.post("/control/{proceso_id}/pausar")
async def pausar_proceso(proceso_id: str):
    """Pausar un proceso de codificación"""
    controlador = obtener_proceso(proceso_id)
    
    if not controlador:
        return {"error": "Proceso no encontrado"}
    
    controlador.pausar()
    return {"mensaje": "Proceso pausado", "estado": controlador.to_dict()}


@router.post("/control/{proceso_id}/reanudar")
async def reanudar_proceso(proceso_id: str):
    """Reanudar un proceso pausado"""
    controlador = obtener_proceso(proceso_id)
    
    if not controlador:
        return {"error": "Proceso no encontrado"}
    
    controlador.reanudar()
    return {"mensaje": "Proceso reanudado", "estado": controlador.to_dict()}


@router.post("/control/{proceso_id}/cancelar")
async def cancelar_proceso(proceso_id: str):
    """Cancelar un proceso de codificación"""
    controlador = obtener_proceso(proceso_id)
    
    if not controlador:
        return {"error": "Proceso no encontrado"}
    
    controlador.cancelar()
    return {"mensaje": "Proceso cancelado", "estado": controlador.to_dict()}


@router.get("/control/{proceso_id}/estado")
async def obtener_estado(proceso_id: str):
    """Obtener el estado actual de un proceso"""
    controlador = obtener_proceso(proceso_id)
    
    if not controlador:
        return {"error": "Proceso no encontrado"}
    
    return controlador.to_dict()


@router.get("/monitoreo")
async def obtener_monitoreo():
    """
    🆕 MEJORA 3: Obtiene información de monitoreo de procesos activos.
    
    Returns:
        Información sobre procesos activos, pausados, cancelados, etc.
    """
    procesos = list(procesos_activos.values())
    
    # Contar por estado
    activos = sum(1 for p in procesos if not p.pausado and not p.cancelado and p.progreso_pct < 100)
    pausados = sum(1 for p in procesos if p.pausado)
    cancelados = sum(1 for p in procesos if p.cancelado)
    completados = sum(1 for p in procesos if p.progreso_pct >= 100)
    
    # Calcular estadísticas
    total_respuestas = sum(p.total_respuestas for p in procesos)
    respuestas_procesadas = sum(p.respuestas_procesadas for p in procesos)
    progreso_promedio = sum(p.progreso_pct for p in procesos) / len(procesos) if procesos else 0
    
    # Lista de procesos con información básica
    lista_procesos = [
        {
            "proceso_id": p.proceso_id,
            "estado": "completado" if p.progreso_pct >= 100 else "cancelado" if p.cancelado else "pausado" if p.pausado else "activo",
            "progreso_pct": round(p.progreso_pct, 1),
            "respuestas": f"{p.respuestas_procesadas}/{p.total_respuestas}",
            "batches": f"{p.batch_actual}/{p.total_batches}",
            "mensaje": p.mensaje
        }
        for p in procesos
    ]
    
    return {
        "resumen": {
            "total_procesos": len(procesos),
            "activos": activos,
            "pausados": pausados,
            "cancelados": cancelados,
            "completados": completados
        },
        "estadisticas": {
            "total_respuestas": total_respuestas,
            "respuestas_procesadas": respuestas_procesadas,
            "progreso_promedio": round(progreso_promedio, 1)
        },
        "procesos": lista_procesos,
        "timestamp": datetime.now().isoformat()
    }

