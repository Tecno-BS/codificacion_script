import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys
from pathlib import Path
from io import BytesIO


#Agregar directorio src
sys.path.append(str(Path(__file__).parent.parent / "src"))

from codificador import SemanticCoder
from evaluador import EvaluadorCodificacion
from config import *

#Configuración página
st.set_page_config(
    page_title="Codificación Automatizada - BS",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    st.title("Codificación Automatizada - BS")
    st.markdown("---")

    configuracion_sidebar()

    col1, col2 = st.columns([2,1])

    with col1:
        st.header("Cargar archivos")
        archivos = cargar_archivos()

        if archivos: 

            st.header("Ejecutar codificación")
            if st.button("Ejecutar codificación", type="primary"):
                ejecutar_codificacion(archivos)
            
    with col2:
        st.header("Estado del sistema")
        mostrar_estado()


#Configuración barra lateral
def configuracion_sidebar():
    st.sidebar.title("Configuración")
    st.sidebar.subheader("Cargar archivos")
    archivos = st.sidebar.file_uploader("Cargar archivos", type=["xlsx", "csv"], accept_multiple_files=True)

    st.sidebar.subheader("Configuración GPT")

    # Mostrar modo actual
    if USE_GPT_MOCK:
        st.sidebar.success("Modo Mock activado (sin costo real)")
    else:
        st.sidebar.warning("Modo Real activado (consumirá créditos)")

    usar_gpt = st.sidebar.checkbox("Usar GPT para casos difíciles", value=True)
    modelo_gpt = st.sidebar.selectbox(
        "Modelo GPT",
        ["gpt-4o-mini", "gpt-4o"],
        index=0
    )
    presupuesto_max = st.sidebar.slider(
        "Presupuesto máximo (USD)",
        0.0, 50.0, 10.0
    )

    st.session_state.usar_gpt = usar_gpt
    st.session_state.modelo_gpt = modelo_gpt
    st.session_state.presupuesto_max = presupuesto_max
    
    if 'gpt_costo_total' in st.session_state:
        st.metric("Costo GPT Total", f"${st.session_state.gpt_costo_total:.4f}")

    return archivos

#Configuración principal
def configuracion_principal():
    st.subheader("Configuración")
    
    st.sidebar.subheader("Parametros de similitud")
    umbral = st.sidebar.slider("Umbral de similitud", min_value=0.0, max_value=1.0, value=UMBRAL_SIMILITUD, step=0.5, help="Umbral de similitud para la codificación")

    top_k = st.sidebar.slider(
        "Top candidatos",
        min_value=1,
        max_value=10,
        value=TOP_CANDIDATOS,
        help="Número de códigos candidatos para la codificación"
    )

    #Guardar datos durante la sesión
    st.session_state.umbral = umbral
    st.session_state.top_k = top_k


#Interfaz para cargar archivos
def cargar_archivos():
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Archivo de respuestas")
        archivo_respuestas = st.file_uploader(
            "Selecciona archivo de respuestas",
            type=["xlsx", "csv"],
            help="Archivo de respuestas a codificar"
        )
    
    with col2:
        st.subheader("Archivo de codigos anteriores")

        archivo_codigos = st.file_uploader(
            "Selecciona archivo de codigos anteriores (opcional)",
            type=["xlsx", "csv"],
            help="Archivo de codigos anteriores (opcional)"
        )
    
    if archivo_respuestas:
        st.success("Archivo de respuestas cargado correctamente")

    #Mostrar preview del archivo
        try:
            df = pd.read_excel(archivo_respuestas) if archivo_respuestas.name.endswith('.xlsx') else pd.read_csv(archivo_respuestas)
            st.subheader("Vista previa del archivo")
            st.dataframe(df.head(), use_container_width=True)
            st.info(f"Total de filas: {len(df)}")
        except Exception as e:
            st.error(f"Error al leer archivo: {e}")

    return {
        'respuestas': archivo_respuestas,
        'codigos': archivo_codigos
    } if archivo_respuestas else None

#Ejecutar codificación
def ejecutar_codificacion(archivos):
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    ruta_respuestas = temp_dir / archivos['respuestas'].name
    with open(ruta_respuestas, "wb") as f:
        f.write(archivos['respuestas'].getbuffer())
    
    ruta_codigos = None
    if archivos['codigos']:
        ruta_codigos = temp_dir / archivos['codigos'].name
        with open(ruta_codigos, "wb") as f:
            f.write(archivos['codigos'].getbuffer())

    #Mostrar progreso
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.text("Inicializando codificación...")

        progress_bar.progress(10)

        codificador = SemanticCoder()

        status_text.text("Procesando respuestas...")
        progress_bar.progress(30)

        # Ejecutar codificación
        status_text.text("Ejecutando codificación...")
        progress_bar.progress(60)

        resultados = codificador.ejecutar_codificacion(
            ruta_respuestas=str(ruta_respuestas),
            ruta_codigos=str(ruta_codigos) if ruta_codigos else None
        )


        #Generar resultados
        status_text.text("Generando resultados...")
        progress_bar.progress(80)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_resultados = f"result/codificaciones/resultados_{timestamp}.xlsx"

        # Guardado robusto usando el método del codificador (normaliza datos y maneja errores)
        try:
            codificador.guardar_resultados(resultados, ruta_resultados)
            st.success(f"Archivo guardado: {ruta_resultados}")
        except Exception as e:
            st.error("Error al guardar el Excel")
            st.exception(e)
            return

        progress_bar.progress(100)
        status_text.text("Codificación completada")

        mostrar_resultados(resultados, ruta_resultados)

        # No eliminar el archivo guardado para permitir inspección desde disco
        # ruta_resultados.unlink()
        if ruta_codigos:
            ruta_codigos.unlink()
    except Exception as e:
        st.error(f"Error durante la codificación: {e}")
        progress_bar.progress(0)

def mostrar_resultados(resultados, ruta_resultados):
    st.header("Descargar resultados")
    # Solo ofrecer descarga, sin vista previa ni gráficos
    try:
        excel_bytes = df_a_excel_bytes(resultados)
        st.download_button(
            label="📥 Descargar Excel (.xlsx)",
            data=excel_bytes,
            file_name=f"codificacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.info(f"Archivo también guardado en: {ruta_resultados}")
    except Exception as e:
        st.error("Error preparando el archivo para descarga")
        st.exception(e)

def generar_graficos(resultados):
    # Vista de gráficos deshabilitada por solicitud: solo descarga
    return

def mostrar_estado():
    """Mostrar estado del sistema"""
    st.metric("Estado", "🟢 Activo")
    st.metric("Modelo", st.session_state.get('modelo', 'distilbert-base-multilingual-cased'))
    
    # Información del sistema
    st.subheader("ℹ️ Información del Sistema")
    st.info("""
    **Versión:** 0.2
    **Modelo:** DistilBERT Multilingüe
    **Idioma:** Español
    **Formato:** Excel/CSV
    """)

def preparar_para_streamlit(df: pd.DataFrame) -> pd.DataFrame:
    dfo = df.copy()

    # 1) Columnas de códigos: forzar a string (evita mezcla int/str)
    codigo_cols = [c for c in dfo.columns if c.endswith('_codigo')]
    for c in codigo_cols:
        dfo[c] = dfo[c].astype(str)  # incluso NaN -> "nan" (luego limpiamos)
        dfo[c] = dfo[c].replace({'nan': ''})  # limpia "nan" visibles

    # 2) Columnas de similitud: forzar a float
    sim_cols = [c for c in dfo.columns if c.endswith('_similitud')]
    for c in sim_cols:
        dfo[c] = pd.to_numeric(dfo[c], errors='coerce')

    # 3) Columnas de candidatos: asegurar string
    cand_cols = [c for c in dfo.columns if c.endswith('_candidatos')]
    for c in cand_cols:
        dfo[c] = dfo[c].astype(str)

    return dfo


def df_a_excel_bytes(df: pd.DataFrame) -> bytes:
    dfx = preparar_para_streamlit(df) 
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        dfx.to_excel(writer, index=False, sheet_name="Codificacion")
    buffer.seek(0)
    return buffer.getvalue()

if __name__ == "__main__":
    main()

