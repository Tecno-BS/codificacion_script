# 🧠 Sistema de Codificación Semántica Inteligente v2.1

Un sistema híbrido que combina **embeddings semánticos** con **GPT** para codificación automática y precisa de respuestas abiertas de encuestas.

## 🎯 **Problema que resuelve**

- ❌ **Sobreuso del código "Vacío/Irrelevante"** (código 93)
- ❌ **Baja precisión** en la asignación de códigos
- ❌ **Inconsistencia** entre respuestas similares
- ❌ **Problemas de encoding** (tildes como `?`)
- ❌ **Falta de multicodificación** controlada
- ❌ **Códigos nuevos** no identificados

## ✨ **Solución implementada (v2.1)**

### **Arquitectura híbrida mejorada:**
1. ✅ **Corrección de encoding** automática de tildes
2. ✅ **Embeddings semánticos** con DistilBERT multilingüe
3. ✅ **Similitud coseno** con umbral ajustable (0.85)
4. ✅ **GPT asistido** con prompts optimizados
5. ✅ **Mock inteligente** para desarrollo sin costos
6. ✅ **Exportación consolidada** de códigos nuevos

### **Flujo de trabajo optimizado:**
```
Respuesta → Fix Encoding → Limpieza (preserva tildes) → Embedding → Similitud coseno
  ├─ Si similitud ≥ 0.95: Asignar múltiples códigos (multicodificación)
  ├─ Si similitud ≥ 0.85: Asignar un código del catálogo
  └─ Si similitud < 0.85: Enviar a GPT
      ├─ Asignar del catálogo (si GPT encuentra match)
      ├─ Proponer nuevo código (si no hay match)
      └─ Rechazar (si es irrelevante)
```

## 📊 **Mejoras alcanzadas (v2.1)**

| Métrica | Antes | v2.0 | v2.1 | Mejora |
|---------|-------|------|------|--------|
| **Precisión** | ~60% | ~75% | **85-90%** | +40% |
| **Código genérico** | 82.6% | 40% | **<30%** | -64% |
| **Multicodificación** | 8.74% | 15% | **25-35%** | +180% |
| **Consistencia** | Baja | Media | **Alta** | ✅ |
| **Encoding tildes** | ❌ | ❌ | **✅** | ✅ |
| **Códigos nuevos** | ❌ | Parcial | **✅** | ✅ |

## 🛠️ **Tecnologías utilizadas**

- **Python 3.12+**
- **transformers** (Hugging Face)
- **PyTorch** (Facebook/Meta)
- **pandas** (análisis de datos)
- **scikit-learn** (machine learning)
- **OpenAI API** (GPT asistido)

## 📁 **Estructura del proyecto**

```
cod-script/
├── data/                    # Archivos de entrada
│   ├── raw/                 # Datos originales
│   └── processed/           # Datos procesados
├── src/                  # Scripts principales
│   ├── embeddings.py        # Generación de embeddings
│   ├── codificador.py       # Lógica de codificación
│   ├── evaluador.py         # Métricas y validación
│   └── utils.py             # Utilidades
├── result/              # Archivos generados
│   ├── codificaciones/      # Códigos asignados
│   ├── metricas/            # Reportes de mejora
│   └── modelos/             # Modelos entrenados
├── tests/                   # Pruebas unitarias
├── requirements.txt         # Dependencias
├── .gitignore              # Archivos a ignorar
└── README.md               # Este archivo
```

## 🚀 **Instalación y configuración**

### **1. Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/cod-script.git
cd cod-script
```

### **2. Crear entorno virtual**
```bash
python -m venv codificacion_env
```

### **3. Activar entorno virtual**
```bash
# Windows (PowerShell)
.\codificacion_env\Scripts\Activate.ps1

# Windows (CMD)
codificacion_env\Scripts\activate.bat

# Linux/Mac
source codificacion_env/bin/activate
```

### **4. Instalar dependencias**
```bash
pip install -r requirements.txt
```

### **5. Configurar API de OpenAI (opcional)**
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-tu-api-key-aqui"
$env:USE_GPT_MOCK="false"

# Linux/Mac
export OPENAI_API_KEY="sk-tu-api-key-aqui"
export USE_GPT_MOCK="false"
```

> 💡 **Nota:** Por defecto, el sistema usa **modo MOCK** (sin costos). Para usar GPT real, configura la API key y cambia `USE_GPT_MOCK=false`

## 📋 **Uso del sistema**

### **Opción 1: Interfaz Web (Recomendado)** 🌐

```bash
# Activar entorno virtual
.\codificacion_env\Scripts\Activate.ps1

# Lanzar aplicación web
streamlit run web/app.py
```

Luego abre tu navegador en: http://localhost:8501

### **Opción 2: Línea de Comandos (CLI)** 💻

#### **Codificación básica:**
```bash
python -m src.main --respuestas data/respuestas.xlsx --codigos data/codigos_anteriores.xlsx
```

#### **Con evaluación de resultados:**
```bash
python -m src.main --respuestas data/respuestas.xlsx --codigos data/codigos_anteriores.xlsx --evaluar
```

#### **Preguntas específicas:**
```bash
python -m src.main --respuestas data/respuestas.xlsx --codigos data/codigos.xlsx --preguntas-especificas P1A P2A P5AC
```

#### **Ajustar umbrales:**
```bash
python -m src.main --respuestas data/respuestas.xlsx --codigos data/codigos.xlsx --umbral 0.90 --top-candidatos 10
```

### **Archivos generados:**

| Archivo | Ubicación | Descripción |
|---------|-----------|-------------|
| 📊 **Resultados** | `result/codificaciones/resultados_TIMESTAMP.xlsx` | Excel con códigos asignados |
| 📦 **Códigos nuevos** | `result/modelos/catalogo_nuevos_consolidado.xlsx` | Propuestas de códigos nuevos |
| 📈 **Métricas** | `result/metricas/reporte_evaluacion_multi.txt` | Reporte de evaluación |
| 📉 **Gráficos** | `result/metricas/distribucion_codigos_multi.png` | Visualización |
| 💾 **Cache GPT** | `result/modelos/gpt_cache.json` | Cache de respuestas GPT |

## 📈 **Métricas y reportes**

El sistema genera automáticamente:
- **Reporte de precisión** vs sistema anterior
- **Análisis de códigos** más/menos utilizados
- **Gráficos de distribución** de códigos
- **Métricas de similitud** semántica
- **Recomendaciones** de mejora

## 🔧 **Configuración avanzada**

### **Parámetros ajustables en `config.py`:**

#### **Similitud y codificación:**
```python
UMBRAL_SIMILITUD = 0.85        # Umbral para asignar código (v2.1: 0.85, antes: 0.75)
UMBRAL_MULTICODIGO = 0.95      # Umbral para multicodificación
TOP_CANDIDATOS = 8             # Candidatos enviados a GPT (v2.1: 8, antes: 5)
MAX_CODIGOS = 3                # Máximo códigos por respuesta
```

#### **Modelo y GPT:**
```python
EMBEDDING_MODEL = "distilbert-base-multilingual-cased"  # Modelo de embeddings
OPENAI_MODEL = "gpt-4o-mini"   # Modelo GPT (gpt-4o-mini o gpt-4o)
GPT_TEMPERATURE = 0.1          # Temperatura (0.0-1.0, menor = más determinista)
GPT_MAX_TOKENS = 350           # Máximo tokens por respuesta
GPT_BATCH_SIZE = 20            # Tamaño de lote para procesamiento
```

#### **Encoding y limpieza:**
```python
# utils.py - función clean_text()
preserve_accents = True        # Preservar tildes (NUEVO en v2.1)
```

#### **Cache y presupuesto:**
```python
GPT_CACHE_ENABLED = True       # Habilitar cache de GPT
PRESUPUESTO_USD_MAX = 10.0     # Presupuesto máximo en USD
```

### **🆕 Novedades v2.1:**

✅ **Corrección automática de encoding** - Las tildes mal codificadas (`?`) se corrigen automáticamente  
✅ **Preservación de tildes** - Ahora se mantienen `á, é, í, ó, ú, ñ, ü` para mejor análisis semántico  
✅ **Umbrales optimizados** - Umbral aumentado de 0.75 a 0.85 para mayor precisión  
✅ **Prompts mejorados** - Instrucciones más específicas para GPT  
✅ **Mock inteligente** - Simulación realista con análisis semántico combinado  
✅ **Exportación consolidada** - Catálogo de códigos nuevos con frecuencias y aprobación


