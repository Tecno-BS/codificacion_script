# 🧠 Sistema de Codificación Semántica Inteligente

Un sistema híbrido que combina **embeddings semánticos** con **GPT** para mejorar la precisión y consistencia en la codificación de respuestas abiertas de encuestas.

## 🎯 **Problema que resuelve**

- **Sobreuso del código "Vacío/Irrelevante"** (código 93)
- **Baja precisión** en la asignación de códigos
- **Inconsistencia** entre respuestas similares
- **Falta de multicodificación** controlada

## 🚀 **Solución implementada**

### **Arquitectura híbrida:**
1. **Embeddings semánticos** con `transformers` + `torch`
2. **Similitud coseno** para encontrar códigos candidatos
3. **GPT asistido** para decisiones finales
4. **Validación cruzada** entre respuestas similares
5. **Aprendizaje continuo** con retroalimentación

### **Flujo de trabajo:**
```
Respuesta → Embedding → Similitud → Códigos candidatos → GPT → Código final
```

## 📊 **Mejoras esperadas**

| Métrica | Antes | Después |
|---------|-------|---------|
| **Precisión** | ~60% | 85-90% |
| **Código 93** | 82.6% | <30% |
| **Multicodificación** | 8.74% | 25-35% |
| **Consistencia** | Baja | Alta |

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

## 📋 **Uso del sistema**

### **1. Preparar datos**
```bash
# Colocar archivos en datos/raw/
# - respuestas.xlsx (respuestas de encuesta)
# - codigos_historicos.xlsx (catálogo de códigos)
```

### **2. Ejecutar codificación**
```bash
python codigo/codificador.py --entrada datos/raw/respuestas.xlsx --codigos datos/raw/codigos_historicos.xlsx
```

### **3. Evaluar resultados**
```bash
python codigo/evaluador.py --resultados resultados/codificaciones/
```

## 📈 **Métricas y reportes**

El sistema genera automáticamente:
- **Reporte de precisión** vs sistema anterior
- **Análisis de códigos** más/menos utilizados
- **Gráficos de distribución** de códigos
- **Métricas de similitud** semántica
- **Recomendaciones** de mejora

## 🔧 **Configuración avanzada**

### **Parámetros ajustables:**
- **Umbral de similitud**: 0.75 (por defecto)
- **Top códigos candidatos**: 5 (por defecto)
- **Modelo de embeddings**: `distilbert-base-multilingual-cased`
- **Máximo de códigos**: 3 por respuesta

### **Archivo de configuración:**
```python
# config.py
UMBRAL_SIMILITUD = 0.75
TOP_CANDIDATOS = 5
MODELO_EMBEDDINGS = "distilbert-base-multilingual-cased"
MAX_CODIGOS = 3
```


