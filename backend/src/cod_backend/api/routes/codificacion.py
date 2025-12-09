"""
Rutas de la API para codificación
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import FileResponse
from pathlib import Path
import asyncio
import shutil
from datetime import datetime, timedelta
import uuid
import time

from ...schemas.api_schemas import CodificacionRequest, CodificacionResponse
from ...core.codificador_nuevo import CodificadorNuevo
from ...utils import save_data
from ... import config
from .progress import crear_proceso, obtener_proceso, eliminar_proceso
from typing import Union

router = APIRouter()

# 🆕 MEJORA 2: Función de limpieza de archivos temporales
def limpiar_archivos_temporales(horas_antiguedad: int = 24):
    """
    Limpia archivos temporales más antiguos que el tiempo especificado.
    
    Args:
        horas_antiguedad: Archivos más antiguos que estas horas serán eliminados (default: 24)
    """
    temp_dir = Path("temp")
    if not temp_dir.exists():
        return
    
    tiempo_limite = time.time() - (horas_antiguedad * 3600)
    archivos_eliminados = 0
    espacio_liberado = 0
    
    try:
        for archivo in temp_dir.iterdir():
            if archivo.is_file():
                # Verificar antigüedad del archivo
                tiempo_modificacion = archivo.stat().st_mtime
                if tiempo_modificacion < tiempo_limite:
                    try:
                        tamaño = archivo.stat().st_size
                        archivo.unlink()
                        archivos_eliminados += 1
                        espacio_liberado += tamaño
                    except Exception as e:
                        # Si no se puede eliminar, continuar con el siguiente
                        continue
        
        if archivos_eliminados > 0:
            espacio_mb = espacio_liberado / (1024 * 1024)
            print(f"🧹 Limpieza automática: {archivos_eliminados} archivos eliminados ({espacio_mb:.2f} MB liberados)")
    except Exception as e:
        print(f"⚠️  Error en limpieza automática: {e}")


async def ejecutar_codificacion_con_progreso(
    proceso_id: str,
    codificador: CodificadorNuevo,
    ruta_respuestas: str,
    ruta_codigos: str | None,
    nombre_archivo: str
):
    """
    Ejecuta la codificación con actualización de progreso en tiempo real
    """
    try:
        controlador = obtener_proceso(proceso_id)
        if not controlador:
            return
        
        controlador.mensaje = "📤 Preparando archivos..."
        
        # Cargar datos para obtener el total (solo filas con respuesta no vacía)
        import pandas as pd
        df = pd.read_excel(ruta_respuestas)
        # Columna de respuestas asumida como segunda o tercera según estructura, pero
        # para el conteo simple usamos: cualquier fila donde haya algún valor no nulo en la segunda columna.
        if df.shape[1] >= 2:
            col_respuestas = df.columns[1]
            serie_respuestas = df[col_respuestas]
            total_respuestas = int(
                serie_respuestas.apply(
                    lambda v: isinstance(v, str) and v.strip() not in ["", "-", "--", "---"]
                ).sum()
            )
        else:
            total_respuestas = len(df)
        
        # Callback para actualizar progreso durante la codificación REAL
        def actualizar_progreso_real(progreso: float, mensaje: str):
            """
            Callback llamado por el codificador durante el procesamiento
            progreso: float de 0-1 (porcentaje real del codificador)
            mensaje: descripción del estado actual
            """
            # Verificar cancelación
            if controlador.cancelado:
                raise Exception("Proceso cancelado por el usuario")
            
            # Verificar si está pausado (bloquear hasta que se reanude)
            while controlador.pausado:
                import time
                time.sleep(0.5)
                if controlador.cancelado:
                    raise Exception("Proceso cancelado por el usuario")
            
            # Calcular respuestas procesadas basado en el progreso real
            respuestas_procesadas = int(progreso * total_respuestas)
            progreso_pct = progreso * 100
            
            # Extraer información de batch del mensaje
            # Formato: "🤖 Pregunta | Batch X/Y (Z/W respuestas)"
            import re
            batch_match = re.search(r'Batch (\d+)/(\d+)', mensaje)
            if batch_match:
                batch_actual = int(batch_match.group(1))
                total_batches = int(batch_match.group(2))
                controlador.batch_actual = batch_actual
                if total_batches > controlador.total_batches:
                    controlador.total_batches = total_batches
            
            # Extraer count de respuestas del mensaje
            # Formato: "... (X/Y respuestas)"
            resp_match = re.search(r'\((\d+)/(\d+) respuestas\)', mensaje)
            if resp_match:
                respuestas_procesadas = int(resp_match.group(1))
            
            # Actualizar estado del controlador
            controlador.actualizar(
                respuestas_procesadas=respuestas_procesadas,
                mensaje=mensaje
            )
            controlador.progreso_pct = progreso_pct
        
        # Ejecutar codificación REAL con callback de progreso
        resultados = await codificador.ejecutar_codificacion(
            ruta_respuestas=ruta_respuestas,
            ruta_codigos=ruta_codigos,
            progress_callback=actualizar_progreso_real
        )
        
        # Guardar resultados
        controlador.mensaje = "💾 Guardando resultados..."
        nombre_base = Path(nombre_archivo).stem
        # 🆕 MEJORA 1: Incluir proceso_id en el nombre para mayor unicidad
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_resultados = f"{nombre_base}_{proceso_id[:8]}_{timestamp}_resultados.xlsx"
        ruta_resultados = f"result/codificaciones/{archivo_resultados}"
        Path(ruta_resultados).parent.mkdir(parents=True, exist_ok=True)
        
        # 🆕 MEJORA: Guardar resultados y códigos nuevos en el mismo Excel con hojas diferentes
        import pandas as pd
        df_codigos_nuevos = getattr(codificador, "df_codigos_nuevos", None)
        with pd.ExcelWriter(ruta_resultados, engine='openpyxl') as writer:
            resultados.to_excel(writer, sheet_name='Resultados', index=False)
            if df_codigos_nuevos is not None and not df_codigos_nuevos.empty:
                df_codigos_nuevos.to_excel(writer, sheet_name='Códigos Nuevos', index=False)
        
        # Para compatibilidad con el frontend, los códigos nuevos están en la misma hoja
        ruta_codigos_nuevos = archivo_resultados if (df_codigos_nuevos is not None and not df_codigos_nuevos.empty) else None

        # Guardar nombres de archivos y métricas en el controlador para que el frontend
        # pueda mostrarlos al finalizar (vía SSE de progreso)
        controlador.archivo_resultados = Path(ruta_resultados).name
        if ruta_codigos_nuevos:
            controlador.archivo_codigos_nuevos = Path(ruta_resultados).name  # Mismo archivo, hoja diferente

        # Métricas generales (si el codificador las expone)
        stats = getattr(codificador, "stats", None)
        # Compatibilidad con el codificador híbrido anterior
        if stats is None:
            costo_total = 0.0
            if hasattr(codificador, "gpt") and hasattr(codificador.gpt, "costo_total"):
                costo_total = float(codificador.gpt.costo_total)
            stats = {
                "total_respuestas_codificadas": len(resultados),
                "total_codigos_nuevos": len(getattr(codificador, "codigos_nuevos", []) or []),
                "total_codigos_historicos": 0,
                "costo_total": costo_total,
            }
        controlador.stats = stats
        
        # Limpiar archivos temporales
        Path(ruta_respuestas).unlink(missing_ok=True)
        if ruta_codigos:
            Path(ruta_codigos).unlink(missing_ok=True)
        
        # Marcar como completado (100%)
        controlador.actualizar(
            respuestas_procesadas=total_respuestas,
            mensaje="✅ Codificación completada exitosamente"
        )
        controlador.progreso_pct = 100
        
        # Esperar un poco para que el frontend reciba el 100%
        await asyncio.sleep(1)
        
        # Eliminar el proceso después de completar
        eliminar_proceso(proceso_id)
        
    except Exception as e:
        import traceback
        print("❌ ERROR en ejecutar_codificacion_con_progreso:")
        traceback.print_exc()

        controlador = obtener_proceso(proceso_id)
        if controlador:
            controlador.mensaje = f"❌ Error interno: {str(e)}"
            controlador.cancelar()
        
        # Limpiar archivos temporales
        Path(ruta_respuestas).unlink(missing_ok=True)
        if ruta_codigos:
            Path(ruta_codigos).unlink(missing_ok=True)


@router.post("/codificar-upload", response_model=CodificacionResponse)
async def codificar_respuestas_upload(
    background_tasks: BackgroundTasks,
    archivo_respuestas: UploadFile = File(...),
    archivo_codigos: UploadFile = File(None),
    modelo: str = Form("gpt-5")
):
    """
    Codifica respuestas usando GPT Híbrido (upload directo de archivos)
    
    Args:
        archivo_respuestas: Archivo Excel con respuestas
        archivo_codigos: Archivo Excel con catálogo de códigos (opcional)
        modelo: Modelo GPT a utilizar
        
    Returns:
        Resultado de la codificación con proceso_id para seguimiento
    """
    try:
        # Crear carpeta temporal si no existe
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        # Generar timestamp para nombres únicos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Guardar archivo de respuestas
        nombre_respuestas = f"{timestamp}_{archivo_respuestas.filename}"
        ruta_respuestas = temp_dir / nombre_respuestas
        
        with ruta_respuestas.open("wb") as buffer:
            shutil.copyfileobj(archivo_respuestas.file, buffer)
        
        # Guardar archivo de códigos si existe
        ruta_codigos = None
        if archivo_codigos:
            nombre_codigos = f"{timestamp}_{archivo_codigos.filename}"
            ruta_codigos = temp_dir / nombre_codigos
            
            with ruta_codigos.open("wb") as buffer:
                shutil.copyfileobj(archivo_codigos.file, buffer)
        
        # Crear codificador (usando nuevo sistema)
        codificador = CodificadorNuevo(modelo=modelo)
        
        # Cargar datos para obtener el total de respuestas
        import pandas as pd
        df = pd.read_excel(ruta_respuestas)
        total_respuestas = len(df)
        
        # Crear proceso para tracking
        proceso_id = str(uuid.uuid4())
        batch_size = 20
        total_batches = (total_respuestas + batch_size - 1) // batch_size
        crear_proceso(proceso_id, total_respuestas, total_batches)
        
        # Ejecutar codificación en background con progreso
        background_tasks.add_task(
            ejecutar_codificacion_con_progreso,
            proceso_id,
            codificador,
            str(ruta_respuestas),
            str(ruta_codigos) if ruta_codigos else None,
            archivo_respuestas.filename
        )
        
        return CodificacionResponse(
            mensaje="Codificación iniciada",
            total_respuestas=total_respuestas,
            total_preguntas=0,  # Se actualizará después
            costo_total=0.0,  # Se actualizará después
            ruta_resultados="",  # Se generará después
            ruta_codigos_nuevos=None,
            proceso_id=proceso_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en codificación: {str(e)}")


@router.post("/extraer-datos-auxiliares")
async def extraer_datos_auxiliares(
    archivo_respuestas: UploadFile = File(...),
):
    """
    Extrae los datos auxiliares únicos de la columna B del archivo de respuestas.
    """
    try:
        import tempfile
        import pandas as pd
        
        # Guardar archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            shutil.copyfileobj(archivo_respuestas.file, tmp_file)
            tmp_path = tmp_file.name
        
        # Cargar archivo SIN headers (header=None) para leer todas las filas como datos
        df = pd.read_excel(tmp_path, header=None)
        
        # Verificar que tenga al menos 3 columnas (ID, Dato Auxiliar, Respuestas)
        if df.shape[1] < 3:
            raise HTTPException(status_code=400, detail="El archivo debe tener al menos 3 columnas (ID, Dato Auxiliar, Respuestas)")
        
        # Estructura del archivo:
        # Columna A (índice 0) = ID
        # Columna B (índice 1) = Dato Auxiliar
        # Columna C (índice 2) = Respuestas (primera fila es la pregunta)
        
        # Extraer columna B (índice 1) que contiene los datos auxiliares
        columna_auxiliar = df.iloc[:, 1]  # Columna B
        
        # Extraer valores únicos EXCLUYENDO la primera fila (índice 0) que contiene la pregunta
        # Filtrar NaN, valores vacíos y convertir a string
        datos_auxiliares = []
        for idx, valor in enumerate(columna_auxiliar):
            # Saltar la primera fila (índice 0)
            if idx == 0:
                continue
            if pd.notna(valor):
                valor_str = str(valor).strip()
                if valor_str and valor_str.lower() not in ['nan', 'none', '']:
                    datos_auxiliares.append(valor_str)
        
        # Eliminar duplicados y ordenar
        datos_auxiliares = sorted(list(set(datos_auxiliares)))
        
        # Debug: imprimir para verificar
        print(f"📊 Total de filas: {len(df)}")
        print(f"📊 Primeras 5 filas completas:")
        for i in range(min(5, len(df))):
            print(f"   Fila {i}: ID={df.iloc[i, 0]}, Auxiliar={df.iloc[i, 1]}, Respuesta={df.iloc[i, 2]}")
        print(f"📊 Columna B (Dato Auxiliar) - primeros 10 valores:")
        for i in range(min(10, len(columna_auxiliar))):
            print(f"   [{i}]: {columna_auxiliar.iloc[i]}")
        print(f"📊 Datos auxiliares únicos extraídos ({len(datos_auxiliares)}): {datos_auxiliares}")
        
        # Limpiar archivo temporal
        Path(tmp_path).unlink(missing_ok=True)
        
        return {
            "datos_auxiliares": sorted(list(set(datos_auxiliares))),  # Ordenar y eliminar duplicados
            "total": len(set(datos_auxiliares))
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al extraer datos auxiliares: {str(e)}")


@router.post("/codificar-nuevo-upload", response_model=CodificacionResponse)
async def codificar_respuestas_nuevo_upload(
    background_tasks: BackgroundTasks,
    archivo_respuestas: UploadFile = File(...),
    archivo_codigos: UploadFile = File(None),
    modelo: str = Form("gpt-5"),
    usar_dato_auxiliar: str = Form("false"),
    categorizacion_auxiliar: str = Form(None),
):
    """
    Nuevo endpoint de codificación que usa el grafo basado en LangGraph / LangChain.

    Reutiliza toda la infraestructura de procesos (progreso, pausa, cancelar,
    monitoreo, limpieza de temporales), solo cambia el motor de codificación.
    """
    try:
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        nombre_respuestas = f"{timestamp}_{archivo_respuestas.filename}"
        ruta_respuestas = temp_dir / nombre_respuestas
        with ruta_respuestas.open("wb") as buffer:
            shutil.copyfileobj(archivo_respuestas.file, buffer)

        ruta_codigos = None
        if archivo_codigos:
            nombre_codigos = f"{timestamp}_{archivo_codigos.filename}"
            ruta_codigos = temp_dir / nombre_codigos
            with ruta_codigos.open("wb") as buffer:
                shutil.copyfileobj(archivo_codigos.file, buffer)

        # 🆕 Procesar configuración de dato auxiliar
        config_auxiliar = None
        if usar_dato_auxiliar.lower() == "true" and categorizacion_auxiliar:
            import json
            try:
                categorizacion = json.loads(categorizacion_auxiliar)
                config_auxiliar = {
                    "usar": True,
                    "categorizacion": categorizacion
                }
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Error al parsear categorización de dato auxiliar")

        # Usar el nuevo codificador (grafo V3)
        codificador = CodificadorNuevo(modelo=modelo, config_auxiliar=config_auxiliar)

        # Cargar datos para total de respuestas (para progreso)
        import pandas as pd

        df = pd.read_excel(ruta_respuestas)
        if df.shape[1] >= 2:
            col_respuestas = df.columns[1]
            serie_respuestas = df[col_respuestas]
            total_respuestas = int(
                serie_respuestas.apply(
                    lambda v: isinstance(v, str) and v.strip() not in ["", "-", "--", "---"]
                ).sum()
            )
        else:
            total_respuestas = len(df)

        proceso_id = str(uuid.uuid4())
        batch_size = 10
        total_batches = (total_respuestas + batch_size - 1) // batch_size
        crear_proceso(proceso_id, total_respuestas, total_batches)

        background_tasks.add_task(
            ejecutar_codificacion_con_progreso,
            proceso_id,
            codificador,
            str(ruta_respuestas),
            str(ruta_codigos) if ruta_codigos else None,
            archivo_respuestas.filename,
        )

        return CodificacionResponse(
            mensaje="Codificación (nuevo sistema) iniciada",
            total_respuestas=total_respuestas,
            total_preguntas=0,
            costo_total=0.0,
            ruta_resultados="",
            ruta_codigos_nuevos=None,
            proceso_id=proceso_id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error en codificación (nuevo): {str(e)}"
        )


@router.post("/codificar", response_model=CodificacionResponse)
async def codificar_respuestas(request: CodificacionRequest):
    """
    Codifica respuestas usando GPT Híbrido (compatibilidad con rutas)
    
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
        
        # Crear codificador (usando nuevo sistema)
        codificador = CodificadorNuevo(modelo=request.modelo)
        
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
        
        # Exportar códigos nuevos (si existen)
        ruta_codigos_nuevos = None
        if hasattr(codificador, 'df_codigos_nuevos') and codificador.df_codigos_nuevos is not None and not codificador.df_codigos_nuevos.empty:
            from ...utils import save_data
            ruta_codigos_nuevos = f"result/codigos_nuevos/{timestamp}_codigos_nuevos.xlsx"
            Path(ruta_codigos_nuevos).parent.mkdir(parents=True, exist_ok=True)
            save_data(codificador.df_codigos_nuevos, ruta_codigos_nuevos)
        
        # Obtener estadísticas
        costo_total = 0.0
        if hasattr(codificador, 'stats') and codificador.stats:
            costo_total = codificador.stats.get('costo_total', 0.0)
        
        return CodificacionResponse(
            mensaje="Codificación completada exitosamente",
            total_respuestas=len(resultados),
            total_preguntas=1,  # El nuevo sistema procesa una pregunta a la vez
            costo_total=costo_total,
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
            {"id": "gpt-5", "nombre": "GPT-5", "recomendado": True},
            {"id": "gpt-4o-mini", "nombre": "GPT-4o Mini"},
            {"id": "gpt-4.1", "nombre": "GPT-4.1"},
        ]
    }


@router.post("/limpiar-temporales")
async def ejecutar_limpieza_temporales(horas_antiguedad: int = 24):
    """
    Ejecuta limpieza manual de archivos temporales.
    
    Args:
        horas_antiguedad: Archivos más antiguos que estas horas serán eliminados (default: 24)
    
    Returns:
        Resumen de la limpieza ejecutada
    """
    temp_dir = Path("temp")
    if not temp_dir.exists():
        return {
            "mensaje": "No hay carpeta temporal",
            "archivos_eliminados": 0,
            "espacio_liberado_mb": 0
        }
    
    tiempo_limite = time.time() - (horas_antiguedad * 3600)
    archivos_eliminados = 0
    espacio_liberado = 0
    
    try:
        for archivo in temp_dir.iterdir():
            if archivo.is_file():
                tiempo_modificacion = archivo.stat().st_mtime
                if tiempo_modificacion < tiempo_limite:
                    try:
                        tamaño = archivo.stat().st_size
                        archivo.unlink()
                        archivos_eliminados += 1
                        espacio_liberado += tamaño
                    except Exception as e:
                        continue
        
        espacio_mb = espacio_liberado / (1024 * 1024)
        return {
            "mensaje": "Limpieza completada",
            "archivos_eliminados": archivos_eliminados,
            "espacio_liberado_mb": round(espacio_mb, 2),
            "horas_antiguedad": horas_antiguedad
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en limpieza: {str(e)}")

