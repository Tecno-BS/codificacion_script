# 🎓 Cómo Usar Estos Notebooks

## 🎯 Objetivo

Estos notebooks te permiten **experimentar con LangChain y LangGraph** de forma interactiva antes de integrar el código a tu aplicación de producción.

---

## 📝 Pasos Rápidos

### **1. Activar entorno virtual**

```bash
# Desde la carpeta notebooks/
cd C:\Users\ivan\Documents\cod-script\notebooks

# Activar entorno (Windows)
..\codificacion_env\Scripts\activate

# Verificar que estés en el entorno correcto
which python  # Debería apuntar a codificacion_env
```

---

### **2. Instalar dependencias**

```bash
# Opción A: Con uv (desde la raíz del proyecto)
cd ..
uv sync

# Opción B: Con pip (si no tienes uv)
pip install langchain langchain-openai langgraph jupyter ipython
```

---

### **3. Lanzar Jupyter**

```bash
# Desde la carpeta notebooks/
jupyter lab

# O si prefieres el clásico:
jupyter notebook
```

Esto abrirá tu navegador en `http://localhost:8888/`.

---

### **4. Ejecutar notebooks**

1. **Abre** `01_langgraph_intro.ipynb`
2. **Ejecuta** celda por celda con `Shift + Enter`
3. **Observa** los resultados en cada paso
4. **Experimenta** modificando el código

---

## 📚 Orden Recomendado

```
01_langgraph_intro.ipynb
     ↓
02_langgraph_codificacion.ipynb
     ↓
03_langgraph_streaming.ipynb (próximamente)
```

---

## 💰 Control de Costos

Para evitar gastos innecesarios de API:

### **En `01_langgraph_intro.ipynb`:**
- ✅ Ejemplo 1: Sin costo (sin LLM)
- 💰 Ejemplo 2: ~$0.005 (1 llamada a GPT-4o-mini)
- ✅ Ejemplo 3: Sin costo (solo lógica)

### **En `02_langgraph_codificacion.ipynb`:**
- Celdas con GPT están **comentadas** por defecto
- Descomenta solo cuando estés listo
- Usa `batch_size=3` para pruebas pequeñas
- Costo estimado: ~$0.02-0.05 (5 respuestas)

---

## 🔍 Tips de Experimentación

### **1. Crea copias de los notebooks**
```bash
cp 02_langgraph_codificacion.ipynb 02_mi_prueba.ipynb
```

### **2. Usa prints para debugging**
```python
print(f"Estado actual: {state}")
print(f"Batch procesado: {len(batch)}")
```

### **3. Prueba diferentes modelos**
```python
# Más barato
modelo_gpt = "gpt-4o-mini"

# Más preciso (más caro)
modelo_gpt = "gpt-4o"
```

### **4. Modifica los prompts**
Los prompts están en las celdas de los nodos. Experimenta con diferentes instrucciones.

---

## 🎨 Visualizar Grafos

Si quieres ver gráficos del flujo:

```bash
# Instalar graphviz
# Windows: descarga desde https://graphviz.org/download/
# Linux: sudo apt install graphviz
# Mac: brew install graphviz

pip install pygraphviz
```

Luego en el notebook:
```python
from IPython.display import Image, display
display(Image(app.get_graph().draw_mermaid_png()))
```

---

## ❓ Problemas Comunes

### **Error: Kernel not found**
```bash
# Instalar kernel de Jupyter
python -m ipykernel install --user --name=codificacion_env --display-name="Python (codificacion_env)"
```

### **Error: ModuleNotFoundError**
```bash
# Asegúrate de estar en el entorno correcto
which python

# Reinstala la dependencia
pip install <nombre-del-paquete>
```

### **Notebook se traba**
- **Reinicia el kernel**: Menú → Kernel → Restart Kernel
- **Verifica** que no haya bucles infinitos
- **Revisa** las llamadas a API (timeouts)

---

## 📤 Exportar Resultados

### **A Python Script:**
```bash
jupyter nbconvert --to python 02_langgraph_codificacion.ipynb
```

### **A HTML (para compartir):**
```bash
jupyter nbconvert --to html 02_langgraph_codificacion.ipynb
```

---

## 🚀 Migrar a Producción

Cuando estés listo para llevar tu código a la aplicación:

1. **Extrae** las funciones de los nodos
2. **Crea** archivo `backend/src/cod_backend/core/langgraph_nodes.py`
3. **Define** el grafo en `backend/src/cod_backend/core/langgraph_workflow.py`
4. **Actualiza** el endpoint de la API
5. **Prueba** con tests unitarios

---

## 🎓 Recursos Adicionales

- [Documentación LangChain](https://python.langchain.com/)
- [Documentación LangGraph](https://langchain-ai.github.io/langgraph/)
- [LangSmith (Observabilidad)](https://smith.langchain.com/)
- [Ejemplos de LangGraph](https://github.com/langchain-ai/langgraph/tree/main/examples)

---

¡Feliz aprendizaje! 🎉

Si tienes preguntas, revisa los comentarios en los notebooks o consulta la documentación oficial.


