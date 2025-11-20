"""
Rutas de la API para codificación
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pathlib import Path
import asyncio

from ...schemas.api_schemas import CodificacionRequest, CodificacionResponse
from ...core import CodificadorHibridoV05
from ...utils import save_data
from ... import config

router = APIRouter()


@router.post("/codificar", response_model=CodificacionResponse)
async def codificar_respuestas(request: CodificacionRequest):
    """
    Codifica respuestas usando GPT Híbrido
    
    Args:
        request: Solicitud con rutas de archivos y modelo
        
    Returns:
        Resultado de la codificación con rutas a archivos generados
    """
    try:
        # Validar que los archivos existen
        if not Path(request.ruta_respuestas).exists():
            raise HTTPException(status_code=404, detail=f"Archivo de respuestas no encontrado: {request.ruta_respuestas}")
        
        if request.ruta_codigos and not Path(request.ruta_codigos).exists():
            raise HTTPException(status_code=404, detail=f"Archivo de códigos no encontrado: {request.ruta_codigos}")
        
        # Crear codificador
        codificador = CodificadorHibridoV05(modelo=request.modelo)
        
        # Ejecutar codificación
        resultados = await codificador.ejecutar_codificacion(
            ruta_respuestas=request.ruta_respuestas,
            ruta_codigos=request.ruta_codigos
        )
        
        # Guardar resultados
        timestamp = Path(request.ruta_respuestas).stem
        ruta_resultados = f"result/codificaciones/{timestamp}_resultados.xlsx"
        Path(ruta_resultados).parent.mkdir(parents=True, exist_ok=True)
        save_data(resultados, ruta_resultados)
        
        # Exportar códigos nuevos
        ruta_codigos_nuevos = codificador.exportar_catalogo_nuevos(nombre_proyecto=timestamp)
        
        return CodificacionResponse(
            mensaje="Codificación completada exitosamente",
            total_respuestas=len(resultados),
            total_preguntas=len(codificador.mapeo_columnas),
            costo_total=codificador.gpt.costo_total,
            ruta_resultados=ruta_resultados,
            ruta_codigos_nuevos=ruta_codigos_nuevos
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en codificación: {str(e)}")


@router.get("/resultados/{filename}")
async def descargar_resultados(filename: str):
    """
    Descarga archivo de resultados
    """
    ruta = Path(f"result/codificaciones/{filename}")
    
    if not ruta.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileResponse(
        path=str(ruta),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/codigos-nuevos/{filename}")
async def descargar_codigos_nuevos(filename: str):
    """
    Descarga archivo de códigos nuevos
    """
    ruta = Path(f"result/codigos_nuevos/{filename}")
    
    if not ruta.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return FileResponse(
        path=str(ruta),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@router.get("/modelos")
async def listar_modelos():
    """
    Lista modelos GPT disponibles
    """
    return {
        "modelos": [
            {"id": "gpt-4o-mini", "nombre": "GPT-4o Mini", "recomendado": True},
            {"id": "gpt-4o", "nombre": "GPT-4o"},
            {"id": "gpt-4.1", "nombre": "GPT-4.1"},
            {"id": "gpt-3.5-turbo", "nombre": "GPT-3.5 Turbo"},
        ]
    }

