# Resumen de Cambios - Sistema de Codificación v0.5

## 📋 Cambios Implementados

### 1. ✅ Detección Mejorada de Códigos de Pregunta
**Problema:** El sistema no detectaba códigos con múltiples letras al inicio (FC1, PA3, etc.)

**Solución:**
- Actualizado `_extraer_codigo_pregunta()` en `src/codificador_v05.py`
- Ahora soporta patrones como:
  - `FC1. ¿Cómo se llama...` → `FC1`
  - `PA3. Descripción...` → `PA3`
  - `P12A. Algo...` → `P12A`
  - `1a. ¿Qué funciones...` → `P1A` (normalizado)

**Código actualizado:**
```python
# ANTES: Solo 1 letra opcional
r'^([a-zA-Z]?\d+[a-zA-Z]*\d*)[.\s]'

# AHORA: Múltiples letras permitidas
r'^([a-zA-Z]*\d+[a-zA-Z]*\d*)[.\s]'
```

---

### 2. ✅ Códigos Nuevos: Formato Numérico Secuencial
**Problema:** Los códigos nuevos usaban formato `NUEVO_Nombre_Categoria` que no era consistente

**Solución:**
- Códigos nuevos ahora son **números secuenciales**
- Continúan desde el último código del catálogo
- Ejemplo: Si el catálogo tiene hasta el código 23, los nuevos serán 24, 25, 26...

**Antes:**
```
Código: NUEVO_Participacion_Ciudadana
Descripción: Menciones sobre participación activa de ciudadanos...
```

**Ahora:**
```
Código: 24
Descripción: Participación ciudadana
```

---

### 3. ✅ Descripciones Directas y Concisas
**Problema:** Las descripciones usaban frases como "Mención sobre...", "Referencias a..."

**Solución:**
- Descripciones ahora son **directas y concisas**
- Siguen el estilo del catálogo existente
- Describen la idea principal exactamente

**Ejemplos del catálogo FC1:**
- `Regencia de farmacia`
- `Manejo de medicamentos`
- `Primeros auxilios`
- `Servicio al cliente`

**Actualizado en:**
- `src/gpt_hibrido.py`: Prompt actualizado con instrucciones claras
- `src/gpt_hibrido_mock.py`: Lógica de generación mejorada

---

### 4. ✅ Eliminación del Sistema de Caché
**Problema:** El caché causaba reutilización de resultados antiguos en proyectos diferentes

**Solución:**
- Eliminado completamente el sistema de caché
- Cada ejecución genera resultados frescos
- No más resultados repetidos entre proyectos

**Archivos modificados:**
- `src/gpt_hibrido.py`:
  - Eliminadas funciones: `_cargar_cache()`, `guardar_cache()`, `_cache_key()`
  - Eliminada verificación de caché en `codificar_batch()`
  - Eliminado guardado de resultados en caché
  - Removidos imports: `json`, `hashlib`

- `src/gpt_hibrido_mock.py`:
  - Eliminado atributo `self.cache`
  - Eliminada función `guardar_cache()`

- `src/codificador_v05.py`:
  - Eliminada llamada a `self.gpt.guardar_cache()`

- Eliminado archivo: `result/modelos/gpt_hibrido_cache.json`

---

### 5. ✅ Multicodificación Completa
**Problema:** El sistema solo permitía asignar múltiples códigos históricos, pero no múltiples códigos nuevos

**Solución:**
- Sistema completo de multicodificación que soporta:
  - ✅ Múltiples códigos históricos: `["5", "10", "15"]`
  - ✅ Múltiples códigos nuevos: `["24", "25"]` con descripciones `["Enfermería", "Nutrición"]`
  - ✅ Modo mixto: Códigos históricos + códigos nuevos en la misma respuesta
- Modelo de datos actualizado con listas en lugar de campos singulares
- Prompt GPT mejorado para instruir sobre multicodificación
- Parsing robusto que soporta formato antiguo y nuevo (backward compatibility)
- Normalización que procesa múltiples códigos por respuesta

**Ejemplos:**
```
Respuesta: "Estudié enfermería y nutrición"
  → decision: "nuevo"
  → codigos_nuevos: ["24", "25"]
  → descripciones_nuevas: ["Enfermería", "Nutrición"]

Respuesta: "Trabajo en farmacia hospitalaria y cuidados paliativos"
  → decision: "asignar"
  → codigos_historicos: ["5", "12"]

Respuesta: "Enfermería general y nueva área de cosmiatría"
  → decision: "mixto"
  → codigos_historicos: ["5"]
  → codigos_nuevos: ["26"]
  → descripciones_nuevas: ["Cosmiatría"]
```

**Archivos modificados:**
- `src/gpt_hibrido.py`:
  - Actualizado `ResultadoCodificacion` con campos `codigos_nuevos` y `descripciones_nuevas` (listas)
  - Agregado método `__post_init__` para migrar automáticamente formato antiguo
  - Prompt actualizado con instrucciones de multicodificación
  - Parsing mejorado para manejar listas de códigos

- `src/codificador_v05.py`:
  - Actualizado para guardar múltiples códigos con separador ";"
  - Múltiples descripciones separadas con " | "
  - Normalización procesa cada código individualmente
  - Catálogo consolidado incluye todos los códigos generados

---

### 6. ✅ Barra de Progreso Mejorada (Interfaz Web)
**Problema:** La barra de progreso era genérica y no mostraba información detallada del proceso

**Solución:**
- Sistema de callbacks para actualizar progreso en tiempo real
- Mensajes informativos con detalles específicos:
  - Pregunta actual y total (ej: "Pregunta 2/5")
  - Batch actual dentro de cada pregunta (ej: "Batch 3/7")
  - Respuestas procesadas en tiempo real (ej: "60/120 respuestas")
  - Emojis contextuales para mejor UX (📋 📝 🤖 ✅)
  - Progreso escalado entre 40-80% durante la codificación

**Ejemplo de secuencia:**
```
[10%]  🔧 Inicializando codificador v0.5...
[20%]  📝 Procesando respuestas (limpieza mínima)...
[30%]  📚 Cargando catálogos históricos...
[40%]  📋 Pregunta 1/3: FC1. Curso realizado
[45%]  🤖 FC1. Curso realizado | Batch 1/5 (20/95 respuestas)
[50%]  🤖 FC1. Curso realizado | Batch 2/5 (40/95 respuestas)
[55%]  🤖 FC1. Curso realizado | Batch 3/5 (60/95 respuestas)
[60%]  📋 Pregunta 2/3: PA3. Actividad laboral
[70%]  🤖 PA3. Actividad laboral | Batch 1/3 (20/65 respuestas)
[80%]  ✅ Todas las preguntas procesadas (3/3)
[90%]  💾 Guardando resultados...
[100%] ✅ Codificación completada!
```

**Archivos modificados:**
- `src/codificador_v05.py`:
  - Agregado parámetro opcional `progress_callback` a `codificar_todas_preguntas()`
  - Llamadas al callback en 3 puntos clave:
    1. Al iniciar cada pregunta
    2. Durante cada batch (con contadores actualizados)
    3. Al completar todas las preguntas
  - Cálculo de progreso global basado en preguntas y batches

- `web/app.py`:
  - Función `actualizar_progreso()` que escala el progreso (40-80%)
  - Actualización de barra (`progress_bar`) y texto (`status_text`) en tiempo real
  - Mensajes más descriptivos y contextuales

---

## 🎯 Resultado Final

### Catálogo FC1 (Ejemplo)
```
Últimos códigos existentes:
  [21] Enfermería
  [22] Administrador de medicamentos
  [23] Gestión y calidad

Códigos nuevos generados:
  [24] Bioquímica Farmacéutica Aplicada
  [25] Técnico Cosmiatría Belleza
  [26] Manejo Medicamentos Controlados
```

### Flujo Completo
1. **Sistema detecta** automáticamente el catálogo por código de pregunta (FC1, PA3, etc.)
2. **GPT analiza** cada respuesta y decide:
   - Asignar uno o más códigos del catálogo (si hay match >85%)
   - Crear uno o más códigos nuevos (si hay temas emergentes)
   - Modo mixto: combinar códigos del catálogo + códigos nuevos
3. **GPT genera** códigos nuevos numéricos secuenciales (24, 25, 26...)
4. **Normalización** garantiza que cada descripción única tenga un código único
5. **Descripciones** son directas y concisas
6. **Sin caché**: Cada proyecto genera resultados frescos

---

## 📊 Archivos Modificados

### Principales
- ✅ `src/gpt_hibrido.py` - Prompt mejorado, caché eliminado, normalización de códigos
- ✅ `src/gpt_hibrido_mock.py` - Generación de códigos numéricos, normalización
- ✅ `src/codificador_v05.py` - Detección mejorada, callbacks de progreso
- ✅ `web/app.py` - Selector de modelo dinámico, barra de progreso detallada

### Nuevas Funcionalidades
- ✨ **Multicodificación completa:** Múltiples códigos históricos Y nuevos por respuesta
- ✨ **Modo mixto:** Combinar códigos del catálogo con códigos emergentes
- ✨ Sistema de normalización de códigos nuevos
- ✨ Barra de progreso con mensajes contextuales
- ✨ Agrupación automática de descripciones idénticas
- ✨ Asignación secuencial garantizada
- ✨ Callbacks para tracking en tiempo real

### Eliminados
- ❌ `result/modelos/gpt_hibrido_cache.json`
- ❌ Archivos de test temporales

---

## 🚀 Próximos Pasos

1. **Probar en Streamlit:**
   ```bash
   cd web
   streamlit run app.py
   ```

2. **Subir tus archivos:**
   - Archivo de respuestas (ej: `FC1.xlsx`)
   - Catálogo de códigos (ej: `FC1_Códigos.xlsx`)

3. **Ejecutar codificación** y verificar:
   - ✓ Detección automática del catálogo
   - ✓ Múltiples códigos históricos por respuesta (separados con ";")
   - ✓ Múltiples códigos nuevos por respuesta (separados con ";")
   - ✓ Modo mixto: códigos históricos + nuevos en la misma respuesta
   - ✓ Códigos nuevos en formato numérico (24, 25, 26...)
   - ✓ Descripciones directas sin "Mención sobre..."
   - ✓ Resultados frescos en cada ejecución
   - ✓ Barra de progreso muestra pregunta, batch y respuestas procesadas
   - ✓ Sin duplicaciones en códigos nuevos (normalización automática)

---

## 💡 Notas Importantes

- **Modelos disponibles:** gpt-4o-mini, gpt-4.1, gpt-5
- **Sin caché:** Cada proyecto genera resultados independientes
- **Formato consistente:** Códigos numéricos secuenciales
- **Descripciones claras:** Sin frases genéricas
- **✨ Multicodificación completa:**
  - Múltiples códigos históricos: `"5;10;15"`
  - Múltiples códigos nuevos: `"24;25"`
  - Modo mixto: Históricos + nuevos en la misma respuesta
- **✨ Anti-redundancia inteligente:**
  - Detecta descripciones similares semánticamente (85% similitud)
  - Unifica automáticamente: "Sabor agradable" + "Buen sabor" → mismo código
  - Previene sobre-especificación: "Versatilidad de uso en comidas" → "Versatilidad de uso"
- **✨ Normalización automática:** Evita duplicaciones de códigos nuevos
- **📊 Progreso detallado:** Muestra pregunta, batch y respuestas en tiempo real
- **Agrupación inteligente:** Descripciones idénticas o similares → mismo código
- **Separadores:** Códigos con ";" | Descripciones con " | "
- **Transparencia:** Logging detallado de todas las unificaciones realizadas

---

## 🎬 Experiencia de Usuario Mejorada

### Barra de Progreso en Acción
Durante la codificación, verás actualizaciones en tiempo real como:

```
[40%] 📋 Pregunta 1/3: FC1. Curso realizado
[45%] 🤖 FC1. Curso realizado | Batch 1/5 (20/95 respuestas)
[50%] 🤖 FC1. Curso realizado | Batch 2/5 (40/95 respuestas)
[55%] 🤖 FC1. Curso realizado | Batch 3/5 (60/95 respuestas)
```

**Beneficios:**
- ✅ Sabes exactamente qué pregunta se está procesando
- ✅ Ves el progreso real (60/95 respuestas)
- ✅ Puedes estimar tiempo restante
- ✅ Transparencia total del proceso

### Multicodificación en Acción

El sistema detecta automáticamente cuando una respuesta menciona múltiples temas:

```
Respuesta: "Estudié enfermería y después me especialicé en nutrición clínica"
│
├─ Análisis GPT:
│   ├─ Tema 1: Enfermería
│   └─ Tema 2: Nutrición
│
└─ Resultado:
    ├─ decision: "nuevo"
    ├─ codigos_nuevos: ["24", "25"]
    └─ descripciones_nuevas: ["Enfermería", "Nutrición clínica"]
    
Excel:
  FC1_codigo_nuevo: "24;25"
  FC1_descripcion_nueva: "Enfermería | Nutrición clínica"
```

**Casos soportados:**
- ✅ Solo históricos: `codigos_historicos: ["5", "10"]`
- ✅ Solo nuevos: `codigos_nuevos: ["24", "25"]`
- ✅ Mixto: `codigos_historicos: ["5"]` + `codigos_nuevos: ["26"]`

### Normalización Automática
El sistema post-procesa los resultados para garantizar consistencia:

```
✨ [NORMALIZACION] 3 codigo(s) nuevo(s) unico(s) asignado(s)
  [24] bioquímica farmacéutica aplicada
  [25] técnico cosmetología
  [26] análisis químico laboratorio
```

---

## 📋 **Actualización 5 de Noviembre, 2025**

### 7. ✅ Columna Unificada de Código + Nomenclatura Mejorada

**Problema 1:** El Excel generaba dos columnas separadas (`codigo_historico` y `codigo_nuevo`), lo cual era confuso

**Solución:**
- ✅ **Columna unificada:** Ahora solo hay una columna `{pregunta}_codigo` que contiene:
  - Códigos históricos (si fueron asignados del catálogo)
  - Códigos nuevos (si fueron creados)
  - Ambos (en modo mixto): `"5;24;25"` (históricos primero, luego nuevos)
  - Vacío (si fue rechazado)

**Problema 2:** Nombres de archivo genéricos (`codificacion_20251105_143022.xlsx`)

**Solución:**
- ✅ **Nombres descriptivos:** Ahora incluyen pregunta y modelo
- Formato: `{Pregunta}_{Modelo}_{Timestamp}.xlsx`
- Ejemplo: `FC1_gpt-4o-mini_20251105_143022.xlsx`
- Máximo 30 caracteres para la pregunta (truncado si es muy largo)

**Ejemplo de cambio en Excel:**

```
ANTES:
├─ FC1_decision: "asignar"
├─ FC1_codigo_historico: "5;10"     ← Separado
├─ FC1_codigo_nuevo: ""              ← Separado
├─ FC1_descripcion_nueva: ""

DESPUÉS:
├─ FC1_decision: "asignar"
├─ FC1_codigo: "5;10"                ← ✅ Unificado
├─ FC1_descripcion_nueva: ""
```

```
ANTES (modo mixto):
├─ FC1_codigo_historico: "5"
├─ FC1_codigo_nuevo: "24;25"

DESPUÉS (modo mixto):
├─ FC1_codigo: "5;24;25"             ← ✅ Todo junto
├─ FC1_descripcion_nueva: "Nueva categoría 1 | Nueva categoría 2"
```

**Archivos modificados:**
- `src/codificador_v05.py`:
  - Líneas 436-472: Lógica de columna unificada
  - Línea 675: Sufijos actualizados (`_codigo` en lugar de `_codigo_historico` y `_codigo_nuevo`)
- `web/app.py`:
  - Líneas 574-584: Generación de nombre de archivo dinámico con pregunta y modelo

---

**Fecha:** 5 de Noviembre, 2025  
**Versión:** v0.5.4 - Columna Unificada + Nomenclatura Inteligente

