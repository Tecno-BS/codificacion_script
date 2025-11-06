import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys
from pathlib import Path
from io import BytesIO
import asyncio
import streamlit.components.v1 as components


# Agregar directorio src
sys.path.append(str(Path(__file__).parent.parent / "src"))

from codificador_v05 import CodificadorHibridoV05
from evaluador import EvaluadorCodificacion
from config import USE_GPT_MOCK, OPENAI_MODEL
from contexto import ContextoProyecto
from extractor_contexto import ExtractorContexto

# Configuración página
st.set_page_config(
    page_title="Codificación Híbrida - BS",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    st.title("🚀 Sistema de Codificación Automatizada")
    st.markdown("---")

    configuracion_sidebar()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📁 Cargar Archivos")
        archivos = cargar_archivos()

        if archivos: 
            # Capturar contexto del proyecto (opcional) - TEMPORALMENTE DESACTIVADO
            # contexto = capturar_contexto()
            contexto = ContextoProyecto()  # Contexto vacío por ahora
            
            st.header("▶️ Ejecutar Codificación")
            if st.button("🚀 Iniciar Codificación", type="primary", use_container_width=True):
                # Limpiar resultados anteriores
                keys_to_clear = [
                    'resultados', 'ruta_resultados', 'ruta_codigos_nuevos', 
                    'codificador', 'codificacion_completada',
                    'excel_bytes_resultados', 'excel_bytes_codigos_nuevos'
                ]
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                ejecutar_codificacion(archivos, contexto)
            
    with col2:
        st.header("📊 Estado del Sistema")
        mostrar_estado()
    
    # MOSTRAR RESULTADOS SI EXISTEN EN SESSION_STATE
    if st.session_state.get('codificacion_completada', False):
        st.markdown("---")
        
        # Botón para limpiar resultados y empezar de nuevo
        col_limpiar1, col_limpiar2 = st.columns([3, 1])
        with col_limpiar2:
            if st.button("🔄 Nueva Codificación", use_container_width=True):
                keys_to_clear = [
                    'resultados', 'ruta_resultados', 'ruta_codigos_nuevos', 
                    'codificador', 'codificacion_completada',
                    'excel_bytes_resultados', 'excel_bytes_codigos_nuevos'
                ]
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        mostrar_resultados(
            st.session_state.resultados,
            st.session_state.ruta_resultados,
            st.session_state.ruta_codigos_nuevos,
            st.session_state.codificador
        )


def reproducir_sonido_notificacion():
    """Reproduce un sonido de notificación cuando termina la codificación"""
    # Verificar si el usuario quiere sonido
    if not st.session_state.get('notificacion_sonido', True):
        return
    
    # HTML con JavaScript para reproducir sonido
    html_code = """
    <script>
        // Crear contexto de audio
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        // Función para crear un beep
        function playBeep(frequency, duration, volume) {
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = frequency;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(volume, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + duration);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + duration);
        }
        
        // Secuencia de notificación: 3 beeps cortos
        playBeep(800, 0.15, 0.3);  // Primera nota
        setTimeout(() => playBeep(1000, 0.15, 0.3), 200);  // Segunda nota
        setTimeout(() => playBeep(1200, 0.25, 0.3), 400);  // Tercera nota (más larga)
        
        console.log("🔔 Notificación sonora reproducida");
    </script>
    """
    components.html(html_code, height=0)


def configuracion_sidebar():
    """Configuración en barra lateral"""
    st.sidebar.title("⚙️ Configuración")

    # Modo GPT
    st.sidebar.subheader("🤖 Modo de Operación")
    if USE_GPT_MOCK:
        st.sidebar.success("✅ Modo MOCK activado")
        st.sidebar.info("Sin costos - Ideal para desarrollo y pruebas")
        # En modo MOCK, usar el modelo por defecto
        if 'modelo_gpt' not in st.session_state:
            st.session_state.modelo_gpt = OPENAI_MODEL
    else:
        st.sidebar.warning("⚡ Modo REAL activado")
        
        # Selector de modelo
        modelos_disponibles = [
            "gpt-4o-mini",
            "gpt-4.1",
            "gpt-5"
        ]
        
        # Obtener modelo por defecto
        modelo_default = OPENAI_MODEL if OPENAI_MODEL in modelos_disponibles else "gpt-4o-mini"
        default_index = modelos_disponibles.index(modelo_default)
        
        modelo_seleccionado = st.sidebar.selectbox(
            "🎯 Modelo GPT",
            modelos_disponibles,
            index=default_index,
            help="Selecciona el modelo según tu necesidad de precisión vs. costo"
        )
        st.session_state.modelo_gpt = modelo_seleccionado
        
        # Mostrar info del modelo
        if "gpt-5" in modelo_seleccionado:
            st.sidebar.info("💎 **GPT-5**: Máxima precisión y razonamiento avanzado")
            st.sidebar.warning("⚠️ Costo estimado: ~$5-15 por 1M tokens")
            st.sidebar.caption("🔸 Temperature fija = 1 | max_completion_tokens = 8000")
        elif "gpt-4.1" in modelo_seleccionado:
            st.sidebar.info("🔸 **GPT-4.1**: Equilibrio calidad-costo óptimo")
            st.sidebar.info("⚡ Costo estimado: ~$3-12 por 1M tokens")
            st.sidebar.caption("🔸 Temperature = 0.1 | max_tokens = 4000")
        else:  # gpt-4o-mini
            st.sidebar.info("⚡ **GPT-4o-mini**: Económico y rápido")
            st.sidebar.success("💰 Costo estimado: ~$0.15-0.60 por 1M tokens")
            st.sidebar.caption("🔸 Temperature = 0.1 | max_tokens = 4000")
    
    st.sidebar.info("Se consumirá API de OpenAI")
    
    # Costo acumulado
    if 'gpt_costo_total' in st.session_state:
        st.sidebar.metric("💵 Costo Total Sesión", f"${st.session_state.gpt_costo_total:.4f}")
    
    st.sidebar.markdown("---")
    
    # Preferencias
    st.sidebar.subheader("🔔 Notificaciones")
    notificacion_sonido = st.sidebar.checkbox(
        "🔊 Sonido al terminar",
        value=st.session_state.get('notificacion_sonido', True),
        help="Reproducir un sonido cuando termine la codificación"
    )
    st.session_state.notificacion_sonido = notificacion_sonido
    
    st.sidebar.markdown("---")
    
    # Información del sistema
    st.sidebar.subheader("ℹ️ Información")
    
    # Mostrar modelo seleccionado dinámicamente
    modelo_actual = st.session_state.get('modelo_gpt', OPENAI_MODEL)
    
    st.sidebar.info("""
**Versión:** v0.5 Híbrida

**Características:**
- ✅ 100% Genérico
- ✅ Sin embeddings
- ✅ GPT directo
- ✅ Detección automática
- ✅ Códigos históricos + nuevos

**Modelo:** {model}
    """.format(model=modelo_actual))


def cargar_archivos():
    """Interfaz para cargar archivos"""
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Archivo de Respuestas")
        archivo_respuestas = st.file_uploader(
            "Selecciona Excel con respuestas",
            type=["xlsx", "xls"],
            help="Excel con columnas de preguntas abiertas"
        )
        
        if archivo_respuestas:
            st.success("✅ Archivo cargado")
            try:
                df = pd.read_excel(archivo_respuestas)
                
                with st.expander("👁️ Vista previa"):
                    st.dataframe(df.head(10), use_container_width=True)
                
                st.info(f"📊 **{len(df)}** respuestas | **{len(df.columns)}** columnas")
                
                # Detectar preguntas potenciales
                columnas_texto = [c for c in df.columns if df[c].dtype == 'object']
                st.caption(f"🔍 Detectadas **{len(columnas_texto)}** columnas de texto")
                
            except Exception as e:
                st.error(f"❌ Error al leer archivo: {e}")
    
    with col2:
        st.subheader("📚 Catálogo de Códigos (Opcional)")
        archivo_codigos = st.file_uploader(
            "Selecciona Excel con códigos históricos",
            type=["xlsx", "xls"],
            help="Excel con hojas nombradas por pregunta, columnas: COD y TEXTO"
        )
        
        if archivo_codigos:
            st.success("✅ Catálogo cargado")
            try:
                with pd.ExcelFile(archivo_codigos) as xls:
                    hojas = xls.sheet_names
                    st.info(f"📑 **{len(hojas)}** catálogos encontrados")
                    
                    with st.expander("📋 Hojas disponibles"):
                        for hoja in hojas:
                            df_hoja = pd.read_excel(xls, sheet_name=hoja)
                            if 'COD' in df_hoja.columns and 'TEXTO' in df_hoja.columns:
                                st.success(f"✅ **{hoja}**: {len(df_hoja)} códigos")
                            else:
                                st.warning(f"⚠️ **{hoja}**: Sin formato válido")
            except Exception as e:
                st.error(f"❌ Error al leer catálogo: {e}")
        else:
            st.info("ℹ️ Sin catálogo → Modo **generación de códigos**")

    return {
        'respuestas': archivo_respuestas,
        'codigos': archivo_codigos
    } if archivo_respuestas else None


# ========================================================================
# FUNCIONALIDAD DE CONTEXTO - TEMPORALMENTE DESACTIVADA
# ========================================================================
# def capturar_contexto():
#     """
#     Captura el contexto del proyecto (opcional) - EXTRACCION AUTOMATICA
#     """
#     st.subheader("📝 Contexto del Proyecto (Opcional)")
#     st.markdown("**Sube un documento** y el sistema extraerá automáticamente el contexto:")
#     st.caption("✅ Soporta: Word (`.docx`, `.doc`), PDF (`.pdf`), Texto (`.txt`), Excel (`.xlsx`, `.xls`)")
#     
#     # Opción para forzar GPT en extracción de contexto
#     if USE_GPT_MOCK:
#         usar_gpt_extraccion = st.checkbox(
#             "🤖 Usar GPT para extracción inteligente (recomendado, ~$0.001 por doc)",
#             value=True,
#             help="GPT puede extraer contexto de documentos con formato libre. Regex solo funciona con formato estructurado."
#         )
#         st.session_state.forzar_gpt_contexto = usar_gpt_extraccion
#         
#         if not usar_gpt_extraccion:
#             st.warning("⚠️ Modo regex: El documento debe tener formato estructurado (ej: 'Objetivo: ...')")
#     
#     # File uploader para documento de contexto
#     archivo_contexto = st.file_uploader(
#         "📄 Subir Documento de Contexto",
#         type=['txt', 'docx', 'doc', 'pdf', 'xlsx', 'xls'],
#         help="Sube el instructivo, briefing o documento con información del proyecto. El sistema extraerá automáticamente: antecedentes, objetivo, grupo objetivo, etc.",
#         key="uploader_contexto"
#     )
#     
#     contexto = ContextoProyecto.vacio()
#     
#     if archivo_contexto:
#         try:
#             # Guardar temporalmente
#             temp_dir = Path("temp")
#             temp_dir.mkdir(exist_ok=True)
#             ruta_temp = temp_dir / archivo_contexto.name
#             
#             with open(ruta_temp, "wb") as f:
#                 f.write(archivo_contexto.getbuffer())
#             
#             # Extraer contexto automáticamente
#             with st.spinner("🔍 Extrayendo contexto del documento..."):
#                 # Siempre usar GPT para extracción de contexto (más preciso)
#                 # Costo: ~$0.001 por documento (muy bajo)
#                 usar_gpt_contexto = not USE_GPT_MOCK or st.session_state.get('forzar_gpt_contexto', True)
#                 extractor = ExtractorContexto(usar_gpt=usar_gpt_contexto)
#                 contexto = extractor.extraer_desde_archivo(str(ruta_temp))
#             
#             # Limpiar archivo temporal
#             ruta_temp.unlink()
#             
#             # Mostrar contexto extraído
#             if contexto.tiene_contexto():
#                 st.success("✅ Contexto extraído exitosamente")
#                 
#                 with st.expander("👁️ Ver Contexto Extraído", expanded=True):
#                     col1, col2 = st.columns(2)
#                     
#                     with col1:
#                         if contexto.nombre_proyecto:
#                             st.markdown(f"**Proyecto:** {contexto.nombre_proyecto}")
#                         if contexto.cliente:
#                             st.markdown(f"**Cliente:** {contexto.cliente}")
#                         if contexto.antecedentes:
#                             st.markdown(f"**Antecedentes:**")
#                             st.caption(contexto.antecedentes[:200] + "..." if len(contexto.antecedentes) > 200 else contexto.antecedentes)
#                     
#                     with col2:
#                         if contexto.objetivo:
#                             st.markdown(f"**Objetivo:**")
#                             st.caption(contexto.objetivo[:200] + "..." if len(contexto.objetivo) > 200 else contexto.objetivo)
#                         if contexto.grupo_objetivo:
#                             st.markdown(f"**Grupo Objetivo:**")
#                             st.caption(contexto.grupo_objetivo[:200] + "..." if len(contexto.grupo_objetivo) > 200 else contexto.grupo_objetivo)
#                 
#                 # Opción de editar manualmente
#                 editar = st.checkbox("✏️ Editar contexto manualmente", value=False)
#                 
#                 if editar:
#                     st.markdown("---")
#                     col1, col2 = st.columns(2)
#                     
#                     with col1:
#                         contexto.nombre_proyecto = st.text_input("Nombre Proyecto", value=contexto.nombre_proyecto)
#                         contexto.cliente = st.text_input("Cliente", value=contexto.cliente)
#                         contexto.antecedentes = st.text_area("Antecedentes", value=contexto.antecedentes, height=100)
#                     
#                     with col2:
#                         contexto.objetivo = st.text_area("Objetivo", value=contexto.objetivo, height=100)
#                         contexto.grupo_objetivo = st.text_area("Grupo Objetivo", value=contexto.grupo_objetivo, height=100)
#                         contexto.notas_adicionales = st.text_area("Notas", value=contexto.notas_adicionales, height=100)
#             else:
#                 st.warning("⚠️ No se pudo extraer contexto del documento")
#                 
#                 if USE_GPT_MOCK and not st.session_state.get('forzar_gpt_contexto', True):
#                     st.info("💡 **Sugerencia:** Activa el checkbox '🤖 Usar GPT para extracción inteligente' arriba para extraer contexto de documentos con formato libre")
#                 else:
#                     st.info("💡 El documento puede estar vacío o no contener información relevante. Puedes editar manualmente usando el checkbox '✏️ Editar contexto manualmente'")
#                 
#         except ImportError as e:
#             st.error(f"❌ Error: Biblioteca faltante para procesar este formato")
#             st.info("💡 **Solución:** Instala las dependencias necesarias:")
#             st.code("pip install python-docx PyPDF2")
#             st.caption(f"Detalles técnicos: {e}")
#         except ValueError as e:
#             error_msg = str(e)
#             st.error(f"❌ Error al procesar documento")
#             
#             # Mostrar mensaje de error detallado
#             if "tiene extensión .doc pero es formato .docx" in error_msg:
#                 st.warning("⚠️ **Problema detectado:** Tu archivo tiene extensión `.doc` pero internamente es formato `.docx` moderno")
#                 
#                 st.markdown("### 🔧 Soluciones:")
#                 
#                 col1, col2 = st.columns(2)
#                 
#                 with col1:
#                     st.markdown("**Opción 1: Renombrar (Rápido)**")
#                     st.info("Renombra tu archivo de `.doc` a `.docx` y súbelo de nuevo")
#                     st.caption("Ejemplo: `archivo.doc` → `archivo.docx`")
#                 
#                 with col2:
#                     st.markdown("**Opción 2: Convertir a texto**")
#                     st.info("Abre el archivo en Word y guárdalo como `.txt`")
#                     st.caption("Archivo → Guardar como → Formato: Texto plano (.txt)")
#                 
#                 st.markdown("**Opción 3: Usar script de conversión**")
#                 st.code(f'python convertir_doc_a_docx.py "{archivo_contexto.name}"')
#                 st.caption("Este script convierte automáticamente el archivo")
#             else:
#                 st.error(f"{error_msg}")
#                 st.info("💡 Formatos soportados: DOCX, DOC, PDF, TXT, XLSX, XLS")
#         except Exception as e:
#             st.error(f"❌ Error al procesar documento: {e}")
#             st.info("💡 Verifica que el archivo no esté corrupto y sea legible")
#             with st.expander("🔍 Detalles técnicos (para desarrolladores)"):
#                 import traceback
#                 st.code(traceback.format_exc())
#     else:
#         st.info("ℹ️ Sin documento de contexto - La codificación funcionará normalmente")
#     
#     return contexto
# ========================================================================


def ejecutar_codificacion(archivos, contexto: ContextoProyecto):
    """Ejecutar proceso de codificación"""
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    # Guardar archivos temporales
    ruta_respuestas = temp_dir / archivos['respuestas'].name
    with open(ruta_respuestas, "wb") as f:
        f.write(archivos['respuestas'].getbuffer())
    
    ruta_codigos = None
    if archivos['codigos']:
        ruta_codigos = temp_dir / archivos['codigos'].name
        with open(ruta_codigos, "wb") as f:
            f.write(archivos['codigos'].getbuffer())

    # Barra de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        # 1. Inicializar (con contexto)
        status_text.text("🔧 Inicializando codificador...")
        progress_bar.progress(10)

        # Obtener modelo seleccionado (o usar default)
        modelo_gpt = st.session_state.get('modelo_gpt', OPENAI_MODEL)
        codificador = CodificadorHibridoV05(contexto=contexto, modelo=modelo_gpt)
        
        if contexto.tiene_contexto():
            st.info(f"📝 Contexto: {contexto.resumen_corto()}")

        # 2. Procesar respuestas
        status_text.text("📝 Procesando respuestas (limpieza mínima)...")
        progress_bar.progress(20)
        
        if not codificador.procesar_respuestas(str(ruta_respuestas)):
            st.error("❌ Error al procesar respuestas")
            return

        # 3. Cargar catálogos
        if ruta_codigos:
            status_text.text("📚 Cargando catálogos históricos...")
            progress_bar.progress(30)
            codificador.cargar_catalogos(str(ruta_codigos))
        else:
            st.info("ℹ️ Modo generación pura (sin catálogos)")

        # 4. Codificar con GPT
        status_text.text("🤖 Iniciando codificación con GPT...")
        progress_bar.progress(40)
        
        # Callback para actualizar progreso
        def actualizar_progreso(progreso: float, mensaje: str):
            # Escalar progreso entre 40% y 80% (reservando inicio y fin para otras tareas)
            progreso_escalado = 0.40 + (progreso * 0.40)
            progress_bar.progress(progreso_escalado)
            status_text.text(mensaje)
        
        # Ejecutar codificación async con callback
        resultados = asyncio.run(
            codificador.codificar_todas_preguntas(progress_callback=actualizar_progreso)
        )
        
        progress_bar.progress(80)
        status_text.text("📊 Procesando resultados finales...")

        # 5. Guardar resultados
        status_text.text("💾 Guardando resultados...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_proyecto = Path(archivos['respuestas'].name).stem
        ruta_resultados = f"result/codificaciones/resultados_{nombre_proyecto}_{timestamp}.xlsx"

        codificador.guardar_resultados(resultados, ruta_resultados)
        
        # 6. Exportar códigos nuevos
        ruta_codigos_nuevos = codificador.exportar_catalogo_nuevos(
            nombre_proyecto=nombre_proyecto
        )

        progress_bar.progress(100)
        status_text.text("✅ Codificación completada!")

        # GUARDAR TODO EN SESSION_STATE para persistir entre recargas
        st.session_state.gpt_costo_total = codificador.gpt.costo_total
        st.session_state.resultados = resultados
        st.session_state.ruta_resultados = ruta_resultados
        st.session_state.ruta_codigos_nuevos = ruta_codigos_nuevos
        st.session_state.codificador = codificador
        st.session_state.codificacion_completada = True

        # Reproducir notificación sonora
        st.success("🎉 ¡Codificación completada con éxito!")
        reproducir_sonido_notificacion()
        st.balloons()  # Efecto visual adicional

        # Limpiar archivos temporales
        ruta_respuestas.unlink()
        if ruta_codigos:
            ruta_codigos.unlink()

    except Exception as e:
        st.error(f"❌ Error durante la codificación: {e}")
        import traceback
        st.code(traceback.format_exc())
        progress_bar.progress(0)


def mostrar_resultados(resultados, ruta_resultados, ruta_codigos_nuevos, codificador):
    """Mostrar resultados de la codificación"""
    st.header("✅ Codificación Completada")
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Respuestas", len(resultados))
    
    with col2:
        total_preguntas = len(codificador.mapeo_columnas)
        st.metric("❓ Preguntas Procesadas", total_preguntas)
    
    with col3:
        total_nuevos = len(codificador.codigos_nuevos)
        st.metric("🆕 Códigos Nuevos", total_nuevos)
    
    with col4:
        costo = codificador.gpt.costo_total
        st.metric("💰 Costo Total", f"${costo:.4f}")
    
    st.markdown("---")
    
    # Descargas
    st.subheader("📥 Descargar Resultados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Resultados de Codificación**")
        try:
            # Generar bytes solo una vez y guardar en session_state
            if 'excel_bytes_resultados' not in st.session_state:
                st.session_state.excel_bytes_resultados = df_a_excel_bytes(resultados)
            
            # Generar nombre de archivo dinámico con pregunta y modelo
            preguntas = list(codificador.mapeo_columnas.values())
            pregunta_principal = preguntas[0] if preguntas else "codificacion"
            modelo_actual = st.session_state.get('modelo_gpt', 'gpt')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Limpiar nombre de pregunta para usar en archivo (máximo 30 caracteres)
            pregunta_limpia = ''.join(c for c in pregunta_principal if c.isalnum() or c in ' _-')[:30]
            pregunta_limpia = pregunta_limpia.replace(' ', '_')
            
            nombre_archivo = f"{pregunta_limpia}_{modelo_actual}_{timestamp}.xlsx"
            
            st.download_button(
                        label="⬇️ Descargar Resultados (.xlsx)",
                        data=st.session_state.excel_bytes_resultados,
                file_name=nombre_archivo,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="download_resultados"
                )
            st.caption(f"💾 También guardado en: `{ruta_resultados}`")
        except Exception as e:
            st.error(f"❌ Error preparando descarga: {e}")
    
    with col2:
        if ruta_codigos_nuevos:
            st.markdown("**🆕 Catálogo de Códigos Nuevos**")
            try:
                # Leer archivo solo una vez y guardar en session_state
                if 'excel_bytes_codigos_nuevos' not in st.session_state:
                    with open(ruta_codigos_nuevos, "rb") as f:
                        st.session_state.excel_bytes_codigos_nuevos = f.read()
                
                st.download_button(
                    label="⬇️ Descargar Códigos Nuevos (.xlsx)",
                    data=st.session_state.excel_bytes_codigos_nuevos,
                    file_name=f"codigos_nuevos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="download_codigos_nuevos"
                )
                st.caption(f"💾 También guardado en: `{ruta_codigos_nuevos}`")
            except Exception as e:
                st.error(f"❌ Error preparando descarga: {e}")
        else:
            st.info("ℹ️ No se generaron códigos nuevos")

    
    # Vista previa
    st.markdown("---")
    st.subheader("👁️ Vista Previa de Resultados")
    
    with st.expander("Ver primeras 20 filas"):
        st.dataframe(resultados.head(20), use_container_width=True)
    
    # Estadísticas por pregunta
    st.markdown("---")
    st.subheader("📈 Estadísticas por Pregunta")
    
    for columna, pregunta in codificador.mapeo_columnas.items():
        with st.expander(f"📋 {pregunta}"):
            col1, col2, col3 = st.columns(3)
            
            # Contar decisiones
            col_decision = f"{pregunta}_decision"
            if col_decision in resultados.columns:
                decisiones = resultados[col_decision].value_counts()
                
                with col1:
                    st.metric("✅ Asignados", decisiones.get('asignar', 0))
                
                with col2:
                    st.metric("🆕 Nuevos", decisiones.get('nuevo', 0))
                
                with col3:
                    st.metric("❌ Rechazados", decisiones.get('rechazar', 0))
                
                # Gráfico
                if len(decisiones) > 0:
                    fig = px.pie(
                        values=decisiones.values,
                        names=decisiones.index,
                        title=f"Distribución de Decisiones - {pregunta}"
                    )
                    st.plotly_chart(fig, use_container_width=True)


def mostrar_estado():
    """Mostrar estado del sistema"""
    # Estado
    st.metric("Estado", "🟢 Activo")
    
    # Modo
    if USE_GPT_MOCK:
        st.metric("Modo", "🧪 MOCK")
    else:
        st.metric("Modo", "⚡ REAL")
    
    # Modelo - Mostrar el seleccionado dinámicamente
    modelo_actual = st.session_state.get('modelo_gpt', OPENAI_MODEL)
    st.metric("Modelo GPT", modelo_actual)
    


def df_a_excel_bytes(df: pd.DataFrame) -> bytes:
    """Convertir DataFrame a bytes de Excel"""
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Codificacion")
    buffer.seek(0)
    return buffer.getvalue()


if __name__ == "__main__":
    main()
