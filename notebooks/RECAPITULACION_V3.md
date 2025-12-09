# 📋 Recapitulación: Grafo V3 - Evaluación Booleana Exhaustiva

## 🎯 Objetivo Principal

Implementar un sistema de codificación de respuestas abiertas usando **LangGraph** que:
- Evalúa **TODOS** los códigos históricos explícitamente (no solo busca coincidencias)
- Identifica **gaps de cobertura** (qué conceptos NO están cubiertos)
- Captura casos **mixtos** (respuestas que necesitan códigos históricos + nuevos)
- Genera códigos nuevos con **especificidad correcta** y **unicidad**

## 🏗️ Arquitectura del Grafo

### Flujo del Proceso

```
START
  ↓
preparar_batch  ← [LOOP: toma siguiente grupo de respuestas]
  ↓
validar  → Filtrar respuestas basura
  ↓
evaluar_catalogo  → Evaluar TODOS los códigos (True/False + confianza)
  ↓
identificar_conceptos  → Detectar gaps (qué NO está cubierto)
  ↓
justificar  → Explicar decisiones
  ↓
ensamblar  → Combinar resultados
  ↓
finalizar  → Incrementar batch_actual
  ↓
¿Hay más batches?
  ├─ SÍ → volver a preparar_batch
  └─ NO → END
```

### Nodos del Grafo

1. **`preparar_batch`**: Toma el siguiente grupo de respuestas según `batch_size`
2. **`validar`**: Filtra respuestas basura (vacías, incomprensibles)
3. **`evaluar_catalogo`**: Evalúa **TODOS** los códigos históricos con True/False + confianza
4. **`identificar_conceptos`**: Detecta qué conceptos NO están cubiertos y genera códigos nuevos
5. **`justificar`**: Genera justificaciones breves para cada decisión
6. **`ensamblar`**: Combina resultados y determina la decisión final (histórico/mixto/nuevo/rechazar)
7. **`finalizar`**: Incrementa el contador de batch

## 🔑 Características Clave

### 1. Evaluación Booleana Exhaustiva

**Problema en V2:** Si encuentra 1 código histórico, NO genera nuevos → Pierde conceptos

**Solución en V3:**
- Evalúa **CADA código** del catálogo para **CADA respuesta**
- Retorna `aplica: True/False` + `confianza: 0.0-1.0`
- Permite múltiples códigos por respuesta
- Solo aplica códigos con confianza >= 0.7

### 2. Detección de Gaps

- Si una respuesta tiene códigos históricos aplicables → analiza qué falta
- Si NO tiene códigos históricos → genera códigos para TODA la respuesta
- Captura casos **mixtos**: respuestas que necesitan históricos + nuevos

### 3. Códigos Secuenciales Globales

- Contador global `proximo_codigo_nuevo` persiste durante toda la ejecución
- Los códigos nuevos son **secuenciales entre batches**
- Si hay catálogo histórico → empieza desde `max(codigo_historico) + 1`
- Si NO hay catálogo → empieza desde 1

### 4. Reglas de Especificidad (aligned con `gpt_hibrido.py`)

- **Nivel de especificidad CRÍTICO**: General pero claro (no demasiado específico)
- **Agrupa bajo el MISMO código** si comparten idea central
- **Crea códigos SEPARADOS** solo si son temas realmente distintos
- **CADA código debe ser ÚNICO**: un código = un concepto específico
- **NO usa frases** como "Mención sobre...", "Referencias a..."

### 5. Códigos Especiales (90-98)

Siempre disponibles:
- 90: Ninguno
- 91: No Recuerda
- 92: No Sabe
- 93: No Responde
- 94: Cualquiera
- 95: Todos
- 96: No Aplica
- 97: Ningún Otro
- 98: Nada

## 📊 Formato de Entrada

### Archivo de Respuestas
- **Columna 1**: ID (numérico)
- **Columna 2**: Respuesta abierta (texto)

### Archivo de Catálogo (opcional)
- **Hoja**: Debe coincidir con el nombre de la pregunta
- **Columnas**: `COD` (numérico), `TEXTO` (descripción)

## 📤 Formato de Salida

### Excel con 2 hojas:

**Hoja 1: Resultados**
- `ID`: ID extraído del archivo original
- `[nombre_pregunta]`: Columna con el nombre exacto de la pregunta del archivo original
- `Códigos asignados`: Códigos numéricos separados por `;` (históricos y nuevos)

**Hoja 2: Códigos Nuevos** (solo si hay códigos nuevos)
- `COD`: ID numérico del código nuevo
- `TEXTO`: Descripción del código nuevo

## 🔧 Configuración

```python
ARCHIVO_RESPUESTAS = Path("temp/respuestas.xlsx")
USAR_CATALOGO_HISTORICO = True/False
ARCHIVO_CATALOGO = Path("result/modelos/catalogo.xlsx")
MAX_RESPUESTAS = None  # o número límite
BATCH_SIZE = 10
MODELO_GPT = "gpt-5"  # o "gpt-4o", "gpt-4o-mini", "gpt-4-turbo"
```

## 📝 Esquemas Pydantic

1. **`ResultadoValidacion`**: Validación de respuestas (válida/inválida)
2. **`ResultadoEvaluacion`**: Evaluación booleana de códigos históricos
3. **`ResultadoCobertura`**: Análisis de gaps y conceptos nuevos
4. **`ResultadoJustificacion`**: Justificaciones breves

## 🚀 Estado del Grafo

```python
class EstadoCodificacionV3(TypedDict):
    pregunta: str
    modelo_gpt: str
    batch_size: int
    respuestas: List[Dict]
    catalogo: List[Dict]
    batch_actual: int
    batch_respuestas: List[Dict]
    codificaciones: List[Dict]
    validaciones_batch: List[Dict]
    evaluaciones_batch: List[Dict]
    cobertura_batch: List[Dict]
    justificaciones_batch: List[Dict]
    proximo_codigo_nuevo: int  # Contador global de códigos nuevos
```

## ✅ Ventajas sobre V2

1. **No pierde conceptos**: Evalúa todos los códigos, no se detiene al encontrar el primero
2. **Captura casos mixtos**: Respuestas que necesitan históricos + nuevos
3. **Mejor especificidad**: Reglas alineadas con `gpt_hibrido.py`
4. **Códigos secuenciales**: Mantiene secuencia global entre batches
5. **Códigos especiales**: Siempre disponibles (90-98)

## 🔄 Próximos Pasos para Backend

1. **Migrar nodos a funciones del backend**
2. **Adaptar carga de datos** (usar rutas del backend)
3. **Integrar con API de codificación** existente
4. **Mantener streaming de progreso** (SSE)
5. **Exportar resultados** en el formato correcto

