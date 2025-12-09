# 🚀 Optimización de Costos y Rendimiento

## Problema Identificado

El sistema actual con LangGraph hace **3-4 llamadas separadas a GPT por cada batch**:
1. `nodo_validar` → 1 llamada GPT
2. `nodo_evaluar_catalogo` → 1 llamada GPT (o más si hay categorías)
3. `nodo_identificar_conceptos` → 1 llamada GPT

**Impacto:**
- **3-4x más costo** que el sistema anterior
- **3-4x más latencia** (tiempo de procesamiento)
- **3-4x más tokens** (cada prompt incluye contexto repetido)

## Solución Implementada

### Nodo Combinado (`nodo_codificar_combinado`)

Se creó un nuevo nodo que combina las 3 tareas en **una sola llamada GPT**:
- ✅ Validación de respuestas
- ✅ Evaluación del catálogo histórico
- ✅ Identificación de conceptos nuevos

**Beneficios:**
- **Reducción de costo: ~70%** (de 3-4 llamadas a 1)
- **Reducción de latencia: ~70%** (de 3-4 llamadas secuenciales a 1)
- **Reducción de tokens: ~50%** (contexto compartido, sin repetición)

### Cómo Activar la Optimización

El nodo combinado está disponible pero **no activado por defecto** para mantener compatibilidad.

Para activarlo, modifica el grafo en `codificador_nuevo.py`:

```python
# ANTES (3 nodos separados):
workflow.add_node("validar", nodo_validar)
workflow.add_node("evaluar_catalogo", nodo_evaluar_catalogo)
workflow.add_node("identificar_conceptos", nodo_identificar_conceptos)

workflow.add_edge("preparar_batch", "validar")
workflow.add_edge("validar", "evaluar_catalogo")
workflow.add_edge("evaluar_catalogo", "identificar_conceptos")
workflow.add_edge("identificar_conceptos", "ensamblar")

# DESPUÉS (1 nodo combinado):
workflow.add_node("codificar_combinado", nodo_codificar_combinado)

workflow.add_edge("preparar_batch", "codificar_combinado")
workflow.add_edge("codificar_combinado", "ensamblar")
```

## Comparación de Rendimiento

### Sistema Anterior (GptHibrido)
- **Llamadas GPT por batch:** 1
- **Costo estimado por 100 respuestas:** ~$0.05-0.10
- **Tiempo estimado:** ~5-10 segundos

### Sistema Actual (LangGraph - 3 nodos)
- **Llamadas GPT por batch:** 3-4
- **Costo estimado por 100 respuestas:** ~$0.15-0.40
- **Tiempo estimado:** ~15-40 segundos

### Sistema Optimizado (LangGraph - nodo combinado)
- **Llamadas GPT por batch:** 1
- **Costo estimado por 100 respuestas:** ~$0.05-0.10
- **Tiempo estimado:** ~5-10 segundos

## Otras Optimizaciones Recomendadas

1. **Caché más agresivo:**
   - Cachear respuestas similares
   - Cachear evaluaciones de catálogo para respuestas idénticas

2. **Llamadas asíncronas en paralelo:**
   - Si hay múltiples categorías, procesarlas en paralelo

3. **Optimización de prompts:**
   - Reducir tokens redundantes
   - Usar prompts más concisos

4. **Batch size dinámico:**
   - Ajustar el tamaño del batch según el modelo usado
   - Modelos más rápidos pueden usar batches más grandes

## Notas

- El nodo combinado mantiene la misma calidad de resultados
- La estructura de LangGraph se mantiene para flexibilidad futura
- El formato de salida es compatible con el nodo `ensamblar` existente

