# 📓 Notebooks de Experimentación - LangChain + LangGraph

Esta carpeta contiene notebooks Jupyter para **experimentar con LangChain y LangGraph** antes de migrar el código a producción.

---

## 📚 Notebooks Disponibles

### 1. **`01_langgraph_intro.ipynb`** 
🎯 **Introducción a LangGraph**

- Conceptos básicos: estados, nodos, aristas
- Ejemplo 1: Grafo simple (sin LLM)
- Ejemplo 2: Grafo con GPT (análisis de texto)
- Ejemplo 3: Transiciones condicionales (Conjetura de Collatz)

**Duración**: ~15 minutos  
**Costo API**: ~$0.01 (Ejemplo 2)

---

### 2. **`02_langgraph_codificacion.ipynb`**
🏗️ **Aplicar LangGraph a tu sistema de codificación**

- Análisis de tu flujo actual
- Diseño del grafo de estados
- Implementación de nodos clave:
  - Cargar datos
  - Preparar batches
  - Codificar con GPT
  - Normalizar códigos
  - Exportar a Excel
- Comparación con tu código actual

**Duración**: ~30 minutos  
**Costo API**: ~$0.02-0.05 (5 respuestas de prueba)

---

### 3. **`03_experimentacion_real.ipynb`**
🧪 **Experimentar con tus datos reales**

- Cargar archivos Excel reales
- Probar CON y SIN catálogo histórico
- Control de costos (limitar respuestas)
- Exportar resultados
- Comparar configuraciones
- Visualizaciones

**Duración**: ~5-15 minutos  
**Costo API**: ~$0.02-0.10 (20-50 respuestas con gpt-4o-mini)

⚠️ **ESTE NOTEBOOK SÍ CONSUME API** - configurable

---

### 4. **`04_langgraph_streaming.ipynb`** (Próximamente)
📡 **Progreso en tiempo real**

- Server-Sent Events (SSE)
- Actualizar frontend en vivo
- Checkpointing para recuperación

---

## 🚀 Cómo Ejecutar

### **Opción 1: Jupyter Lab (Recomendado)**

```bash
# Desde la raíz del proyecto
cd notebooks

# Activar entorno virtual
..\codificacion_env\Scripts\activate  # Windows
# source ../codificacion_env/bin/activate  # Linux/Mac

# Instalar dependencias (si no las tienes)
pip install langchain langchain-openai langgraph jupyter ipython

# Lanzar Jupyter Lab
jupyter lab
```

Esto abrirá tu navegador en `http://localhost:8888`.

---

### **Opción 2: VS Code con extensión Jupyter**

1. Abre VS Code en la carpeta del proyecto
2. Instala la extensión **Jupyter** (Microsoft)
3. Abre cualquier `.ipynb`
4. Selecciona el kernel `codificacion_env`
5. Ejecuta celda por celda con `Shift+Enter`

---

### **Opción 3: Google Colab** (si no quieres instalar nada local)

1. Sube el notebook a Google Drive
2. Abre con Google Colab
3. Agrega al inicio:
   ```python
   !pip install langchain langchain-openai langgraph python-dotenv
   
   # Configurar API key
   import os
   os.environ["OPENAI_API_KEY"] = "tu-api-key-aqui"
   ```

---

## ⚙️ Configuración

### **1. Verificar `.env`**

Asegúrate de tener tu API key configurada:

```env
OPENAI_API_KEY=sk-...
```

### **2. Instalar Dependencias**

```bash
# Con uv (recomendado)
uv sync

# O con pip
pip install -r requirements.txt
pip install langchain langchain-openai langgraph jupyter
```

---

## 📖 Orden Sugerido

Si eres nuevo en LangGraph, sigue este orden:

1. ✅ **`01_langgraph_intro.ipynb`** - Aprende los conceptos básicos
2. ✅ **`02_langgraph_codificacion.ipynb`** - Aplica a tu caso de uso
3. ⭐ **`03_experimentacion_real.ipynb`** - Prueba con TUS datos reales
4. 🔜 **`04_langgraph_streaming.ipynb`** - Agrega progreso en tiempo real

**Si ya conoces LangGraph**, ve directo al **notebook 3** para experimentar con tus datos.

---

## 💡 Consejos

### **Para ahorrar costos de API:**
- Los notebooks tienen secciones comentadas para llamadas a GPT
- Descomenta solo cuando estés listo
- Usa `batch_size` pequeño para pruebas (ej: 3)

### **Para debugging:**
- Ejecuta celda por celda (no "Run All")
- Inspecciona el estado después de cada nodo
- Usa `print()` libremente para entender el flujo

### **Para experimentar:**
- Crea copias de los notebooks (ej: `02_mi_experimento.ipynb`)
- Modifica prompts, parámetros, lógica
- Prueba diferentes modelos (`gpt-4o-mini`, `gpt-4o`)

---

## 🐛 Problemas Comunes

### **Error: `ModuleNotFoundError: No module named 'langgraph'`**
```bash
pip install langgraph
```

### **Error: `OPENAI_API_KEY not found`**
- Verifica que `.env` esté en la raíz del proyecto
- Recarga con `load_dotenv()`

### **Jupyter no encuentra el kernel**
```bash
python -m ipykernel install --user --name=codificacion_env
```

---

## 📊 Siguiente Paso

Una vez que te sientas cómodo con los notebooks:

1. **Decide** si quieres migrar a LangGraph en producción
2. **Crea** una rama de desarrollo:
   ```bash
   git checkout -b feature/langgraph-migration
   ```
3. **Migra** gradualmente:
   - Fase 1: Nodos básicos
   - Fase 2: Streaming SSE
   - Fase 3: Checkpointing
   - Fase 4: Observabilidad (LangSmith)

---

## 🤝 ¿Preguntas?

Si tienes dudas mientras experimentas, recuerda:

- Cada nodo es una **función pura** (entrada → salida)
- El estado fluye **secuencialmente** entre nodos
- Las aristas condicionales permiten **bucles y ramificaciones**
- LangGraph es **ideal para workflows complejos** con múltiples pasos

---

¡Feliz experimentación! 🚀


