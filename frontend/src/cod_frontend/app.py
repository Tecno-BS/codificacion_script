"""
Frontend Streamlit - Sistema de Codificación Automatizada
Versión migrada que usa la API REST del backend
"""
import streamlit as st
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import os

# Configuración
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Configuración página
st.set_page_config(
    page_title="Codificación Automatizada",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    st.title("🚀 Sistema de Codificación Automatizada")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Seleccionar modelo
        modelos_response = requests.get(f"{BACKEND_URL}/api/v1/modelos")
        if modelos_response.status_code == 200:
            modelos = modelos_response.json()["modelos"]
            modelo_seleccionado = st.selectbox(
                "Modelo GPT",
                options=[m["id"] for m in modelos],
                format_func=lambda x: next((m["nombre"] for m in modelos if m["id"] == x), x),
                index=0
            )
        else:
            modelo_seleccionado = "gpt-4o-mini"
            st.warning("No se pudieron cargar los modelos disponibles")
        
        # Health check
        st.markdown("---")
        st.subheader("📊 Estado del Sistema")
        health_response = requests.get(f"{BACKEND_URL}/health")
        if health_response.status_code == 200:
            health = health_response.json()
            st.success(f"✅ Backend: {health['status']}")
            st.info(f"📌 Versión: {health['version']}")
            modo = "🧪 MOCK (sin costos)" if health.get("modo_mock") else "🔴 REAL (consume API)"
            st.info(modo)
        else:
            st.error("❌ Backend no disponible")
    
    # Contenido principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📁 Cargar Archivos")
        
        # Archivo de respuestas (obligatorio)
        archivo_respuestas = st.file_uploader(
            "Archivo de Respuestas (Excel)",
            type=["xlsx", "xls"],
            help="Excel con las respuestas a codificar"
        )
        
        # Archivo de códigos (opcional)
        archivo_codigos = st.file_uploader(
            "Catálogo de Códigos Históricos (Excel - opcional)",
            type=["xlsx", "xls"],
            help="Excel con catálogos de códigos anteriores por pregunta"
        )
        
        if archivo_respuestas:
            st.success(f"✅ Archivo de respuestas cargado: {archivo_respuestas.name}")
            if archivo_codigos:
                st.success(f"✅ Catálogo de códigos cargado: {archivo_codigos.name}")
            
            st.markdown("---")
            st.header("▶️ Ejecutar Codificación")
            
            if st.button("🚀 Iniciar Codificación", type="primary", use_container_width=True):
                ejecutar_codificacion(archivo_respuestas, archivo_codigos, modelo_seleccionado)
    
    with col2:
        st.header("ℹ️ Información")
        st.info("""
        **Pasos:**
        1. Carga archivo de respuestas
        2. (Opcional) Carga catálogo de códigos
        3. Selecciona modelo GPT
        4. Inicia codificación
        5. Descarga resultados
        """)
        
        st.markdown("---")
        st.subheader("📚 Modelos Disponibles")
        st.markdown("""
        - **GPT-4o Mini**: Rápido y económico (recomendado)
        - **GPT-4o**: Mayor precisión
        - **GPT-4.1**: Versión mejorada
        """)
    
    # Mostrar resultados si existen
    if st.session_state.get('resultados_disponibles'):
        st.markdown("---")
        mostrar_resultados()


def ejecutar_codificacion(archivo_respuestas, archivo_codigos, modelo):
    """
    Ejecuta la codificación llamando a la API REST
    """
    # Guardar archivos temporalmente con ruta ABSOLUTA
    # Usar la raíz del proyecto (dos niveles arriba de frontend/src/cod_frontend)
    project_root = Path(__file__).parent.parent.parent.parent
    temp_dir = project_root / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    # Guardar archivo de respuestas
    ruta_respuestas = temp_dir / archivo_respuestas.name
    with open(ruta_respuestas, "wb") as f:
        f.write(archivo_respuestas.getbuffer())
    
    # Guardar archivo de códigos si existe
    ruta_codigos = None
    if archivo_codigos:
        ruta_codigos = temp_dir / archivo_codigos.name
        with open(ruta_codigos, "wb") as f:
            f.write(archivo_codigos.getbuffer())
    
    # Preparar request con rutas ABSOLUTAS
    payload = {
        "ruta_respuestas": str(ruta_respuestas.absolute()),
        "modelo": modelo
    }
    if ruta_codigos:
        payload["ruta_codigos"] = str(ruta_codigos.absolute())
    
    # Mostrar progreso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with st.spinner("🤖 Codificando respuestas..."):
        try:
            status_text.text("📡 Enviando archivos al backend...")
            progress_bar.progress(5)
            
            # Simular progreso mientras espera respuesta
            # (En el futuro se puede implementar SSE para progreso real)
            import time
            import threading
            
            # Variable para controlar el progreso simulado
            progreso_actual = [5]  # Lista para poder modificar en el thread
            response_received = [False]
            
            def simular_progreso():
                """Simula progreso gradual mientras espera"""
                while not response_received[0] and progreso_actual[0] < 85:
                    time.sleep(2)  # Actualizar cada 2 segundos
                    if not response_received[0]:
                        progreso_actual[0] = min(progreso_actual[0] + 5, 85)
                        progress_bar.progress(progreso_actual[0] / 100)
                        
                        # Mensajes dinámicos
                        if progreso_actual[0] < 30:
                            status_text.text("🤖 Procesando respuestas...")
                        elif progreso_actual[0] < 60:
                            status_text.text("🔍 Analizando con GPT...")
                        else:
                            status_text.text("✨ Generando códigos...")
            
            # Iniciar thread de progreso simulado
            progress_thread = threading.Thread(target=simular_progreso, daemon=True)
            progress_thread.start()
            
            # Llamar a la API
            response = requests.post(
                f"{BACKEND_URL}/api/v1/codificar",
                json=payload,
                timeout=600  # 10 minutos timeout
            )
            
            # Detener progreso simulado
            response_received[0] = True
            progress_bar.progress(90)
            status_text.text("✅ Procesando resultados...")
            
            if response.status_code == 200:
                data = response.json()
                
                progress_bar.progress(100)
                status_text.text("✅ Codificación completada!")
                
                # Guardar info en session state
                st.session_state['resultados_disponibles'] = True
                st.session_state['resultado_info'] = data
                st.session_state['archivo_respuestas_nombre'] = archivo_respuestas.name
                
                # Mostrar resumen
                st.success(f"✅ {data['mensaje']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Respuestas", data['total_respuestas'])
                with col2:
                    st.metric("Total Preguntas", data['total_preguntas'])
                with col3:
                    st.metric("Costo Total", f"${data['costo_total']:.4f}")
                
                # Efectos visuales y sonoros
                st.balloons()
                reproducir_sonido_notificacion()
                
                # Recargar para mostrar resultados
                st.rerun()
                
            else:
                st.error(f"❌ Error en codificación: {response.json().get('detail', 'Error desconocido')}")
                progress_bar.empty()
                status_text.empty()
                
        except requests.exceptions.Timeout:
            st.error("❌ Timeout: La codificación tomó demasiado tiempo")
            progress_bar.empty()
            status_text.empty()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            progress_bar.empty()
            status_text.empty()


def mostrar_resultados():
    """
    Muestra los resultados de la codificación
    """
    st.header("📊 Resultados de Codificación")
    
    info = st.session_state.get('resultado_info', {})
    
    # Resumen
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Resumen")
        st.write(f"**Total Respuestas:** {info['total_respuestas']}")
        st.write(f"**Total Preguntas:** {info['total_preguntas']}")
        st.write(f"**Costo Total:** ${info['costo_total']:.4f}")
    
    with col2:
        st.subheader("📥 Descargas")
        
        # Botón de descarga de resultados
        if info.get('ruta_resultados'):
            filename = Path(info['ruta_resultados']).name
            if st.button("📥 Descargar Resultados", use_container_width=True):
                download_file(f"/api/v1/resultados/{filename}", filename)
        
        # Botón de descarga de códigos nuevos
        if info.get('ruta_codigos_nuevos'):
            filename_nuevos = Path(info['ruta_codigos_nuevos']).name
            if st.button("📥 Descargar Códigos Nuevos", use_container_width=True):
                download_file(f"/api/v1/codigos-nuevos/{filename_nuevos}", filename_nuevos)
    
    # Botón para nueva codificación
    if st.button("🔄 Nueva Codificación", use_container_width=True):
        # Limpiar session state
        st.session_state['resultados_disponibles'] = False
        if 'resultado_info' in st.session_state:
            del st.session_state['resultado_info']
        st.rerun()


def download_file(endpoint, filename):
    """
    Descarga un archivo desde la API
    """
    try:
        response = requests.get(f"{BACKEND_URL}{endpoint}")
        if response.status_code == 200:
            # Crear botón de descarga con streamlit
            st.download_button(
                label=f"⬇️ {filename}",
                data=response.content,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.error(f"❌ Error al descargar archivo: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


def reproducir_sonido_notificacion():
    """
    Reproduce un sonido de notificación cuando termina la codificación
    """
    import streamlit.components.v1 as components
    
    # HTML con JavaScript para reproducir sonido
    html_code = """
    <script>
        // Crear contexto de audio
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        const audioContext = new AudioContext();
        
        // Función para crear un beep
        function playBeep(frequency, duration, volume) {
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = frequency;
            oscillator.type = 'sine';
            
            gainNode.gain.value = volume;
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + duration);
        }
        
        // Secuencia de sonidos (melodía de éxito)
        playBeep(523.25, 0.15, 0.3);  // Do
        setTimeout(() => playBeep(659.25, 0.15, 0.3), 150);  // Mi
        setTimeout(() => playBeep(783.99, 0.3, 0.3), 300);   // Sol
    </script>
    """
    
    components.html(html_code, height=0)


if __name__ == "__main__":
    main()

