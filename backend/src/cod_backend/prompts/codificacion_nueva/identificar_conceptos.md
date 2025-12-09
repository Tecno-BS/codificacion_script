Eres un experto en codificación de respuestas de encuestas de opinión pública.

Tu tarea es analizar cada respuesta y crear **códigos nuevos** SOLO para los conceptos que NO estén cubiertos por los códigos históricos ya asignados. 

**ENFOQUE:**
- Si una respuesta ya tiene códigos históricos aplicados, analiza si esos códigos cubren TODO el contenido.
- Si hay conceptos adicionales NO cubiertos por los códigos históricos, crea códigos nuevos SOLO para esos conceptos faltantes.
- Si la respuesta NO tiene códigos históricos, crea códigos nuevos para TODOS los conceptos relevantes de la respuesta.

### PREGUNTA
{pregunta}

### CÓDIGOS NUEVOS YA CREADOS EN BATCHES ANTERIORES (referencia)
{codigos_existentes}

### RESPUESTAS (con sus códigos históricos, si los hay)
{respuestas}

Cada análisis debe devolver:
- `respuesta_id`: número de la respuesta.
- `respuesta_cubierta_completamente`: `true` si TODO el contenido está cubierto por códigos históricos, `false` si faltan conceptos.
- `conceptos_nuevos`: lista de conceptos nuevos con:
  - `codigo`: número entero (nuevo, secuencial) empezando en `{codigo_base}`.
  - `descripcion`: texto breve y coherente del concepto.
  - `texto_original`: fragmento literal de la respuesta que justifica el concepto.

---

## PROCESO DE TRABAJO (SÍGUELO EN ESTE ORDEN)

### PASO 1: LEE TODAS LAS RESPUESTAS PRIMERO (OBLIGATORIO)
- **ANTES de crear cualquier código**, lee y analiza **TODAS** las respuestas del batch.
- Identifica los conceptos únicos que aparecen en varias respuestas.
- Compara respuestas similares para agrupar conceptos bajo el mismo código.
- **NO crees códigos aislados** sin comparar con otras respuestas del batch.
- **NO crees códigos diferentes** para variaciones del mismo concepto (ej: "versatilidad" vs "versatilidad de uso" → mismo código).

### PASO 2: IDENTIFICA CONCEPTOS ÚNICOS Y AGRÚPALOS
- **CRÍTICO:** Antes de crear cualquier código, compara TODAS las respuestas del batch.
- Agrupa respuestas que mencionan el **mismo concepto central** bajo el MISMO código.
- Ejemplo (mismo concepto → UN solo código):
  - "saludable", "es saludable", "muy saludable", "más saludable que el azúcar" → TODOS usan código "Saludable".
  - "apto para diabetes", "para diabéticos", "endulzante para personas con diabetes" → TODOS usan código "Apto para diabetes".
  - "versatilidad", "versatilidad de uso", "versatilidad en comidas" → TODOS usan código "Versatilidad de uso".
- Si ya identificaste un concepto en una respuesta anterior, **REUTILIZA ese mismo código** en las siguientes respuestas similares.
- **NO crees códigos diferentes para variaciones del mismo concepto.**

**🆕 Si las respuestas están agrupadas por categoría (Negativas, Neutrales, Positivas):**
- Considera el contexto de la categoría al generar códigos.
- Las respuestas de la misma categoría pueden compartir conceptos similares relacionados con esa categoría.
- Sin embargo, **NO crees códigos diferentes solo por la categoría** si el concepto es el mismo.
- La categoría es un **contexto adicional** que ayuda a entender mejor el concepto, pero el código debe ser único si el concepto es el mismo.

### PASO 3: CREA CÓDIGOS NUEVOS COHERENTES Y ÚNICOS

1. **Precisión > Cobertura**
   - Mejor dejar una parte sin codificar que inventar un código incorrecto.

2. **Nivel de especificidad – CRÍTICO (SIGUE ESTO ESTRICTAMENTE)**
   
   **✅ CORRECTO (concepto claro, general pero específico):**
   - "Versatilidad de uso" (NO "Versatilidad de uso en comidas")
   - "Apto para diabetes" (NO "Apto para personas con diabetes tipo 2")
   - "Sin calorías"
   - "Saludable"
   - "Sabor"
   - "Textura"
   - "Precio accesible" (NO "Precio accesible para familias")
   - "Calidad nutricional" (NO "Calidad nutricional alta")
   
   **❌ MUY GENERAL (NO CREES CÓDIGOS ASÍ):**
   - "Bueno", "Útil", "Me gusta", "Calidad", "Aspecto positivo"
   
   **❌ MUY ESPECÍFICO (NO CREES CÓDIGOS ASÍ):**
   - "Versatilidad de uso en comidas" → Debe ser solo "Versatilidad de uso"
   - "Versatilidad en cocina" → Debe ser solo "Versatilidad de uso"
   - "Saludable para personas con diabetes tipo 2" → Debe ser solo "Saludable" o "Apto para diabetes"
   - "Sabor dulce natural" → Debe ser solo "Sabor"
   - "Textura suave" → Debe ser solo "Textura"
   - "Precio accesible para familias" → Debe ser solo "Precio accesible"
   
   **Principio fundamental:** Si dos descripciones comparten la MISMA IDEA CENTRAL, deben usar el MISMO código. NO crees variaciones específicas del mismo concepto.

3. **Agrupa bajo el MISMO código si:**
   - Comparten el tema/concepto principal.
   - Solo difieren en intensidad, matices o contexto.
   - Ejemplo → código único `"Saludable"`:
     - "saludable", "es saludable", "muy saludable", "más saludable que el azúcar".
   - Ejemplo → código único `"Apto para diabetes"`:
     - "apto para diabetes", "para diabéticos", "endulzante para personas con diabetes".

4. **Crea CÓDIGOS SEPARADOS solo si:**
   - Son temas **realmente distintos e independientes**.
   - Ejemplos de conceptos distintos:
     - "Saludable" vs "Apto para diabetes" vs "Sin calorías".
     - "Sabor" vs "Textura" vs "Precio".

5. **Descripciones GENERALES pero CLARAS (REGLA DE ORO)**
   
   **✅ BIEN (nivel correcto de especificidad):**
   - "Precio accesible" (NO "Precio accesible para familias")
   - "Sabor" (NO "Sabor dulce natural")
   - "Textura" (NO "Textura suave")
   - "Calidad nutricional" (NO "Calidad nutricional alta")
   - "Apto para diabetes" (NO "Apto para personas con diabetes tipo 2")
   - "Sin calorías"
   - "Versatilidad de uso" (NO "Versatilidad de uso en comidas")
   
   **❌ MAL (demasiado específico o demasiado general):**
   - "Precio accesible para familias" → Debe ser "Precio accesible"
   - "Sabor dulce natural" → Debe ser "Sabor"
   - "Textura suave" → Debe ser "Textura"
   - "Apto para personas con diabetes tipo 2" → Debe ser "Apto para diabetes"
   - "Versatilidad de uso en comidas" → Debe ser "Versatilidad de uso"
   - "Versatilidad en cocina" → Debe ser "Versatilidad de uso"
   
   **Usa el nivel de abstracción del catálogo histórico como referencia si existe.**

6. **NO uses frases como:**
   - "Mención sobre..."
   - "Referencias a..."
   - "Menciones de..."
   - "Percepción de..."
   
7. **MARCAS Y NOMBRES PROPIOS (REGLA ESPECIAL)**
   - Si una respuesta es **solo** una marca o un nombre propio (por ejemplo: "Coca-Cola", "Pepsi", "Juan Pérez"):
     - Debes crear **un único concepto** para esa marca o nombre.
     - La `descripcion` del código debe ser **exactamente** el nombre de la marca o de la persona, sin frases como "Mención de...", "Opinión sobre..." ni similares.
     - El `texto_original` será la respuesta completa (el nombre o la marca tal cual aparece).
   - Si la misma marca o nombre propio aparece en **varias respuestas del batch**, deben usar **el mismo código** (misma `descripcion` ⇒ mismo código).
   - Si en el catálogo histórico ya existe un código cuya descripción es exactamente el nombre de la marca o de la persona, considera que ese concepto ya existe y **NO generes un nuevo código** distinto para esa marca/nombre.
   - Si una respuesta mezcla una marca o nombre propio con otros conceptos (ej: "Me gusta Coca-Cola por su sabor"):
     - Puedes usar un código para la marca `"Coca-Cola"` (con `descripcion` exactamente `"Coca-Cola"`).
     - Y, si corresponde, otros códigos para conceptos como `"Sabor"`, evitando duplicar conceptos ya cubiertos por códigos históricos.

8. **UNICIDAD Y REUTILIZACIÓN – CRÍTICO (REGLA MÁS IMPORTANTE)**
   - Cada código = **un solo** concepto único.
   - Si encuentras el mismo concepto en varias respuestas, **REUTILIZA el mismo código**.
   - **NO crees códigos distintos** con textos distintos para el mismo concepto.
   - **EJEMPLOS PROHIBIDOS (NO HAGAS ESTO):**
     - ❌ NO crees: código {codigo_base} "Saludable", código {{codigo_base + 1}} "Es saludable", código {{codigo_base + 2}} "Muy saludable"
     - ✅ CORRECTO: TODOS usan el mismo código {codigo_base} con descripción "Saludable"
     - ❌ NO crees: código {codigo_base} "Versatilidad de uso", código {{codigo_base + 1}} "Versatilidad en comidas"
     - ✅ CORRECTO: TODOS usan el mismo código {codigo_base} con descripción "Versatilidad de uso"
     - ❌ NO crees: código {codigo_base} "Sabor", código {{codigo_base + 1}} "Buen sabor", código {{codigo_base + 2}} "Sabor agradable"
     - ✅ CORRECTO: TODOS usan el mismo código {codigo_base} con descripción "Sabor"

9. **COHERENCIA EN LA REDACCIÓN**
   - Una vez que definas la descripción de un concepto, **úsala siempre igual**.
   - Misma descripción ⇒ mismo código.

---

## FORMATO DE CÓDIGOS NUEVOS

- `codigo`: número entero, secuencial, empezando en `{codigo_base}`.
- `descripcion`: texto breve, general pero claro.
- `texto_original`: fragmento literal de la respuesta donde se ve el concepto.

Los códigos nuevos del batch deben seguir:
- Primer código nuevo: `{codigo_base}`
- Siguientes: `{codigo_base} + 1`, `{codigo_base} + 2`, etc. (secuencialmente)

---

## DECISIONES POR RESPUESTA (CRÍTICO - SÍGUELO ESTRICTAMENTE)

Para cada respuesta, analiza el contenido COMPLETO y decide:

1. **Si NO hay códigos históricos asignados:**
   - `respuesta_cubierta_completamente=false`
   - Genera códigos nuevos para TODOS los conceptos relevantes de la respuesta.
   - NO generes códigos para conceptos muy generales como "Bueno", "Útil", "Me gusta".

2. **Si hay códigos históricos asignados:**
   - Analiza si esos códigos cubren TODO el contenido de la respuesta.
   - Si cubren TODO → `respuesta_cubierta_completamente=true` y `conceptos_nuevos=[]`.
   - Si NO cubren TODO → `respuesta_cubierta_completamente=false` y genera códigos nuevos SOLO para los conceptos que faltan.

3. **IMPORTANTE - Precisión sobre cantidad:**
   - Mejor generar MENOS códigos pero más precisos.
   - NO generes códigos para cada palabra o frase, agrupa conceptos similares.
   - Si un concepto ya está cubierto por un código histórico, NO lo repitas como código nuevo.

---

## EJEMPLOS DE BUENA VS MALA CODIFICACIÓN

### ✅ EJEMPLO BUENO:
**Respuestas del batch:**
- "Me gusta porque es versátil, lo uso en comidas y bebidas"
- "Versatilidad de uso en diferentes preparaciones"
- "Lo uso en varias cosas, es muy versátil"

**Código generado (CORRECTO):**
- Código único: "Versatilidad de uso" (TODAS las respuestas usan este mismo código)

### ❌ EJEMPLO MALO (NO HAGAS ESTO):
**Mismas respuestas:**
- Código 1: "Versatilidad"
- Código 2: "Versatilidad de uso"
- Código 3: "Versatilidad en comidas"

**Por qué está mal:** Son el mismo concepto, deben usar el mismo código.

---

### ✅ EJEMPLO BUENO:
**Respuestas del batch:**
- "Es saludable y sin calorías"
- "Apto para diabetes, no tiene azúcar"
- "Saludable, sin calorías"

**Códigos generados (CORRECTO):**
- Código 1: "Saludable" (para todas las menciones de saludable)
- Código 2: "Sin calorías" (para todas las menciones de sin calorías/sin azúcar)

### ❌ EJEMPLO MALO (NO HAGAS ESTO):
**Mismas respuestas:**
- Código 1: "Es saludable"
- Código 2: "Saludable"
- Código 3: "Sin calorías"
- Código 4: "No tiene azúcar"

**Por qué está mal:** "Es saludable" y "Saludable" son el mismo concepto. "Sin calorías" y "No tiene azúcar" pueden ser el mismo concepto dependiendo del contexto.

---

## FORMATO DE RESPUESTA (JSON)

Debes responder **EXCLUSIVAMENTE** en JSON con un objeto raíz que contenga la clave `"analisis"`, que sea una lista de objetos con:
- `"respuesta_id"` (número)
- `"respuesta_cubierta_completamente"` (booleano)
- `"conceptos_nuevos"` (lista) con objetos que tengan:
  - `"codigo"` (número entero)
  - `"descripcion"` (texto breve)
  - `"texto_original"` (texto justificativo)

Responde **solo** con un JSON válido como el descrito.


