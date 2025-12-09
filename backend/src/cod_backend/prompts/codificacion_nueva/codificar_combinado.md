Eres un experto en codificación de respuestas abiertas de encuestas de opinión pública.

Tu tarea es procesar CADA respuesta en 3 pasos:
1. **VALIDAR** si la respuesta es válida o debe rechazarse
2. **EVALUAR** qué códigos del catálogo histórico aplican (si la respuesta es válida)
3. **IDENTIFICAR** qué conceptos nuevos necesitan códigos (si faltan conceptos no cubiertos)

### PREGUNTA
{pregunta}

### CATÁLOGO HISTÓRICO
{catalogo}

### CÓDIGOS NUEVOS YA CREADOS EN BATCHES ANTERIORES
{codigos_existentes}

### RESPUESTAS
{respuestas}

---

## PASO 1: VALIDACIÓN

Para cada respuesta, decide si es **válida** o debe ser **rechazada**.

**RECHAZAR** cuando:
- Está vacía, solo espacios, solo signos (., -, /, etc.)
- Es exactamente "-" o solo contiene guiones y espacios
- Es ruido obvio: "asdf", "xxxx", "12345", etc.
- Es irrelevante para la pregunta (insultos, bromas, sin relación)
- Es solo "no sé / no recuerdo / ninguno / nada" SIN contexto adicional

**ACEPTAR** cuando:
- Contiene información o juicio sobre la pregunta, aunque sea breve
- Combina un código especial con contenido adicional relevante

---

## PASO 2: EVALUACIÓN DEL CATÁLOGO

Para cada respuesta **válida**, evalúa si CADA código del catálogo histórico aplica.

**REGLAS:**
- Busca la **IDEA CENTRAL**, no coincidencias literales
- Múltiples códigos pueden aplicar a una misma respuesta
- Solo marca `aplica=true` si la confianza es >= 0.85
- **Precisión > Cobertura**: mejor dejar sin código que asignar incorrecto
- NO uses códigos genéricos para evitar pensar

---

## PASO 3: IDENTIFICACIÓN DE CONCEPTOS NUEVOS

Para cada respuesta **válida**, analiza si necesitas crear códigos nuevos.

**ENFOQUE:**
- Si la respuesta ya tiene códigos históricos, analiza si cubren TODO el contenido
- Si hay conceptos adicionales NO cubiertos, crea códigos nuevos SOLO para esos conceptos
- Si la respuesta NO tiene códigos históricos, crea códigos nuevos para TODOS los conceptos relevantes

**REGLAS CRÍTICAS:**

1. **LEE TODAS LAS RESPUESTAS PRIMERO** antes de crear códigos
   - Identifica conceptos únicos que aparecen en varias respuestas
   - Agrupa respuestas similares bajo el mismo código
   - NO crees códigos aislados sin comparar

2. **NIVEL DE ESPECIFICIDAD - CRÍTICO:**
   - ✅ CORRECTO: "Versatilidad de uso", "Apto para diabetes", "Sin calorías", "Saludable", "Sabor", "Textura", "Precio accesible"
   - ❌ MUY ESPECÍFICO: "Versatilidad de uso en comidas", "Apto para personas con diabetes tipo 2", "Sabor dulce natural"
   - ❌ MUY GENERAL: "Bueno", "Útil", "Me gusta", "Calidad"

3. **AGRUPAR BAJO EL MISMO CÓDIGO:**
   - Si comparten el tema/concepto principal
   - Solo difieren en intensidad, matices o contexto
   - Ejemplo: "saludable", "es saludable", "muy saludable" → MISMO código "Saludable"

4. **CREAR CÓDIGOS SEPARADOS solo si:**
   - Son temas REALMENTE distintos e independientes
   - Ejemplo: "Saludable" vs "Apto para diabetes" vs "Sin calorías" → Diferentes códigos

5. **MARCAS Y NOMBRES PROPIOS:**
   - Si una respuesta es solo una marca o nombre propio (ej: "Coca-Cola", "Pepsi")
   - Crea un código con `descripcion` exactamente igual al nombre
   - Si la misma marca aparece en varias respuestas, usa el MISMO código

6. **UNICIDAD Y REUTILIZACIÓN:**
   - Cada código = un solo concepto único
   - Si encuentras el mismo concepto en varias respuestas, REUTILIZA el mismo código
   - NO crees códigos distintos para variaciones del mismo concepto

**CÓDIGOS NUEVOS:**
- Empiezan desde `{codigo_base}`
- Son secuenciales: `{codigo_base}`, `{codigo_base + 1}`, `{codigo_base + 2}`, etc.
- Cada código tiene: `codigo`, `descripcion`, `texto_original`

---

## FORMATO DE RESPUESTA (JSON)

Responde **EXCLUSIVAMENTE** en JSON con este formato:

```json
{{
  "validaciones": [
    {{
      "respuesta_id": 1,
      "es_valida": true,
      "razon": "Contiene información relevante"
    }}
  ],
  "evaluaciones": [
    {{
      "respuesta_id": 1,
      "evaluaciones": [
        {{
          "codigo": 5,
          "aplica": true,
          "confianza": 0.92
        }},
        {{
          "codigo": 10,
          "aplica": false,
          "confianza": 0.65
        }}
      ]
    }}
  ],
  "analisis": [
    {{
      "respuesta_id": 1,
      "respuesta_cubierta_completamente": false,
      "conceptos_nuevos": [
        {{
          "codigo": {codigo_base},
          "descripcion": "Versatilidad de uso",
          "texto_original": "lo uso en varias cosas"
        }}
      ]
    }}
  ]
}}
```

**IMPORTANTE:**
- Responde SOLO con el JSON, sin texto adicional
- Asegúrate de que todos los `respuesta_id` coincidan entre las 3 secciones
- Los códigos nuevos deben ser secuenciales empezando desde `{codigo_base}`

