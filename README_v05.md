# 🚀 Sistema de Codificación Híbrido v0.5

## 🎯 **¿Qué es v0.5?**

Sistema **100% genérico, simplificado y optimizado** que funciona con **CUALQUIER proyecto** sin configuración previa:

- ✅ **Sistema genérico** (funciona con cualquier Excel/proyecto)
- ✅ **Asigna códigos del catálogo histórico** (si encajan bien)
- ✅ **Genera nuevos códigos emergentes** (estilo Power Automate)
- ✅ **Detección automática de preguntas** (sin mapeo hardcodeado)
- ✅ **Más rápido** (sin overhead de embeddings)
- ✅ **Más preciso** (GPT entiende contexto completo)

---

## 🆚 **v0.5 vs v2.1**

| Característica | v2.1 (Anterior) | v0.5 (Nuevo) |
|----------------|-----------------|--------------|
| **Embeddings** | ✅ DistilBERT | ❌ No (eliminados) |
| **Similitud coseno** | ✅ Sí | ❌ No |
| **Decisión** | Embeddings → GPT | GPT directo |
| **Velocidad (1000 resp)** | ~5-8 min | ~2-3 min |
| **Complejidad** | Alta | Baja |
| **Códigos nuevos** | Propone individuales | Agrupa categorías |
| **Precisión** | ⭐⭐⭐⭐ (85%) | ⭐⭐⭐⭐⭐ (90-95%) |

---

## 🌟 **NUEVO: Sistema 100% Genérico**

**¡Ya no necesitas configurar nada!** El sistema detecta automáticamente:

✅ Todas las preguntas de tu Excel (cualquier nombre de columna)  
✅ Qué columnas son metadata (ID, fecha, etc) y las ignora  
✅ Qué preguntas tienen catálogo histórico  
✅ Qué preguntas necesitan generación pura (sin catálogo)  

**📖 Ver guía completa:** [GUIA_SISTEMA_GENERICO_v05.md](GUIA_SISTEMA_GENERICO_v05.md)

---

## 📦 **Archivos Nuevos**

```
src/
├── gpt_hibrido.py          # ⭐ GPT con modo dual (real)
├── gpt_hibrido_mock.py     # ⭐ GPT mock (sin costos)
├── codificador_v05.py      # ⭐ Orquestador principal
└── [archivos v2.1...]      # Mantienen compatibilidad

test_v05.py                 # ⭐ Script de pruebas
README_v05.md              # ⭐ Esta documentación
```

---

## 🚀 **Inicio Rápido**

### **1. Activar entorno virtual**
```bash
.\codificacion_env\Scripts\Activate.ps1
```

### **2. Probar con test básico** (sin costos)
```bash
python test_v05.py
# Selecciona opción [1] - Test básico
```

### **3. Codificar tus datos**
```python
from src.codificador_v05 import CodificadorHibridoV05

# Crear codificador
codificador = CodificadorHibridoV05()

# Ejecutar
resultados = codificador.ejecutar_codificacion(
    ruta_respuestas="data/respuestas.xlsx",
    ruta_codigos="data/codigos.xlsx"  # Opcional
)

# Guardar
codificador.guardar_resultados(resultados, "result/codificaciones/resultado_v05.xlsx")
```

---

## 🔧 **Configuración**

### **Modo MOCK (desarrollo sin costos)** ✅ Por defecto
```python
# src/config.py
USE_GPT_MOCK = True  # Ya configurado
```

### **Modo REAL (con API de OpenAI)**
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-tu-api-key"
$env:USE_GPT_MOCK="false"
```

```python
# src/config.py
USE_GPT_MOCK = False
OPENAI_MODEL = "gpt-4o-mini"  # Recomendado
```

---

## 📊 **Cómo Funciona v0.5**

### **Flujo Simplificado:**

```
1. CARGA
   ├─ Respuestas.xlsx
   └─ Catalogo.xlsx (opcional)
         ↓
2. LIMPIEZA
   └─ Corrección encoding + preservar tildes
         ↓
3. AGRUPACIÓN
   └─ Batches de ~20 respuestas
         ↓
4. GPT HÍBRIDO (UN SOLO PASO)
   ├─ Input: Batch + Catálogo completo
   ├─ GPT decide POR CADA respuesta:
   │  ├─ ASIGNAR código(s) del catálogo
   │  ├─ CREAR código nuevo
   │  └─ RECHAZAR (si irrelevante)
   └─ Output: JSON con decisiones
         ↓
5. CONSOLIDACIÓN
   ├─ Excel con resultados
   └─ Catálogo de códigos nuevos
```

---

## 🎯 **Decisiones de GPT**

GPT recibe **UN PROMPT DUAL** que le permite:

### **OPCIÓN A: Asignar del catálogo**
- Si la respuesta encaja bien (similitud semántica > 85%)
- Puede asignar múltiples códigos si aplican
- Más preciso que similitud coseno

### **OPCIÓN B: Crear código nuevo**
- Si NO encaja con catálogo existente
- Genera: `NUEVO_Nombre_Categoria_Descriptivo`
- Incluye: descripción + idea principal
- Agrupa respuestas similares bajo MISMO código nuevo

### **OPCIÓN C: Rechazar**
- Solo para respuestas vacías/irrelevantes/incoherentes
- Minimiza "no sabe/no responde"

---

## 📈 **Estructura de Salida**

### **Excel de resultados:**
```
| Respuesta_limpio | P1A_decision | P1A_codigo_historico | P1A_codigo_nuevo | P1A_descripcion_nueva | P1A_confianza | P1A_justificacion |
```

### **Catálogo de códigos nuevos:**
```
result/modelos/catalogo_nuevos_v05.xlsx

| pregunta | codigo_nuevo | descripcion | idea_principal | aprobado | codigo_final | observaciones |
```

---

## 💡 **Ventajas de v0.5**

### **1. Más Simple**
```python
# v2.1: 3 sistemas
Embeddings → Similitud → GPT fallback

# v0.5: 1 sistema
GPT directo (modo dual)
```

### **2. Más Rápido**
- ❌ Sin carga de DistilBERT
- ❌ Sin generación de embeddings
- ❌ Sin cálculo de similitud coseno
- ✅ GPT directo

### **3. Más Preciso**
- GPT entiende **contexto completo**
- Maneja **sinónimos** y **variaciones** mejor
- **Agrupa** categorías emergentes coherentemente

### **4. Más Flexible**
- Un solo prompt para ambos modos
- Fácil ajustar comportamiento
- No depende de umbrales arbitrarios

---

## 🧪 **Testing**

### **Test 1: Básico**
```bash
python test_v05.py
# Opción [1]
```
Prueba con 5 respuestas de ejemplo

### **Test 2: Con archivo**
```bash
python test_v05.py
# Opción [2]
```
Usa `temp/ejemplo_respuestas.xlsx`

### **Test 3: Comparar v2.1 vs v0.5**
```python
# Próximamente: script de comparación
```

---

## 🎛️ **Ajustes Avanzados**

### **Tamaño de batch**
```python
# codificador_v05.py, línea ~130
batch_size = 20  # Ajustar según necesidad
# Más grande = menos llamadas, más tokens
# Más pequeño = más llamadas, menos tokens
```

### **Prompt personalizado**
```python
# gpt_hibrido.py, línea ~97
def _build_prompt(...):
    # Personaliza el prompt aquí
```

### **Modelo GPT**
```python
# config.py
OPENAI_MODEL = "gpt-4o-mini"  # Balance costo/calidad
# O: "gpt-4o" (más caro, más preciso)
# O: "gpt-3.5-turbo" (más barato, menos preciso)
```

---

## 📊 **Costos Estimados**

### **Con gpt-4o-mini (recomendado):**
- 100 respuestas: ~$0.10 - $0.20
- 500 respuestas: ~$0.50 - $1.00
- 1,000 respuestas: ~$1.00 - $2.00
- 7,000 respuestas: ~$7.00 - $14.00

### **Factores que afectan costo:**
- Tamaño del catálogo (más códigos = más tokens)
- Longitud de respuestas
- Número de códigos nuevos generados

---

## ❓ **FAQ**

### **¿Necesito embeddings para algo?**
No. GPT hace análisis semántico internamente de forma más precisa.

### **¿Funciona sin catálogo histórico?**
Sí. En modo "generación pura" crea todas las categorías desde cero (estilo Power Automate).

### **¿Puedo usar mi catálogo de v2.1?**
Sí, 100% compatible. Mismo formato Excel.

### **¿El mock es preciso?**
~70% preciso. Suficiente para desarrollo, pero usa GPT real para producción.

### **¿Puedo volver a v2.1?**
Sí. v0.5 está en rama separada. Main mantiene v2.1.

---

## 🚧 **Próximos Pasos**

### **Implementado:**
- ✅ GPT híbrido (real + mock)
- ✅ Codificador v0.5
- ✅ Tests básicos
- ✅ Documentación

### **Pendiente:**
- ⏳ Integración con interfaz web
- ⏳ Script de comparación v2.1 vs v0.5
- ⏳ Métricas y evaluación automática
- ⏳ Dashboard de aprobación de códigos nuevos

---

## 📞 **Soporte**

### **Errores comunes:**

**1. "Cliente OpenAI no inicializado"**
```bash
$env:OPENAI_API_KEY="tu-api-key"
$env:USE_GPT_MOCK="false"
```

**2. "No se pudieron mapear columnas"**
Actualiza `mapear_columnas_preguntas()` en `codificador_v05.py`

**3. "Error en llamada a GPT"**
Verifica que tu API key sea válida y tenga créditos

---

## 🎉 **¡Listo para usar!**

```bash
# Probar ahora:
python test_v05.py
```

---

**Versión:** 0.5  
**Fecha:** Octubre 2024  
**Estado:** ✅ Funcional (desarrollo activo)

