# ⚡ Guía Rápida: Experimentar con Datos Reales

## 🎯 Objetivo

Probar LangGraph con **tus archivos Excel reales** antes de llevarlo a producción.

---

## 🚀 Pasos (5 minutos)

### **1. Abrir el notebook**

```bash
cd notebooks
jupyter lab 03_experimentacion_real.ipynb
```

---

### **2. Configurar (Celda 5)**

```python
# Edita estas variables:
ARCHIVO_RESPUESTAS = project_root / "temp" / "3255.xlsx"  # 👈 Tu archivo
PREGUNTA_A_CODIFICAR = "P6"  # 👈 Tu pregunta

USAR_CATALOGO_HISTORICO = True  # 👈 True o False
MAX_RESPUESTAS = 20  # 👈 Empieza con pocas
MODELO_GPT = "gpt-4o-mini"  # 👈 Más barato
```

---

### **3. Ejecutar todo**

```
Menú → Run → Run All Cells
```

O ejecuta celda por celda con `Shift + Enter`.

---

### **4. Revisar resultados**

Al final verás:

- ✅ Resumen de decisiones (histórico, nuevo, mixto, rechazar)
- ✅ Lista de códigos nuevos generados
- ✅ Ejemplos de codificaciones
- ✅ Gráfico de distribución
- ✅ Archivo Excel exportado en `notebooks/`

---

## 🔬 Experimentos Sugeridos

### **Experimento 1: Con vs. Sin Catálogo**

**Primera ejecución:**
```python
USAR_CATALOGO_HISTORICO = True
MAX_RESPUESTAS = 20
```

**Segunda ejecución:**
```python
USAR_CATALOGO_HISTORICO = False
MAX_RESPUESTAS = 20
```

Luego usa la celda 21 para comparar:
```python
comparar_resultados(
    "notebooks/resultados_P6_con_catalogo_TIMESTAMP.xlsx",
    "notebooks/resultados_P6_sin_catalogo_TIMESTAMP.xlsx"
)
```

---

### **Experimento 2: Diferentes Modelos**

```python
# Más barato, más rápido
MODELO_GPT = "gpt-4o-mini"

# Más preciso, más caro
MODELO_GPT = "gpt-4o"
```

---

### **Experimento 3: Tamaño de Batch**

```python
# Más llamadas, más contexto por llamada
BATCH_SIZE = 5

# Menos llamadas, menos contexto
BATCH_SIZE = 20
```

---

## 💰 Control de Costos

| Configuración | Respuestas | Costo Estimado |
|---------------|------------|----------------|
| Prueba rápida | 10-20 | ~$0.01-0.02 |
| Validación | 50-100 | ~$0.05-0.10 |
| Completo | 200+ | ~$0.20+ |

**Modelo:** gpt-4o-mini (10x más barato que gpt-4)

---

## ✅ Checklist Post-Experimento

Después de ejecutar, revisa:

- [ ] **¿Los códigos históricos fueron bien reutilizados?**
- [ ] **¿Los códigos nuevos son específicos y no redundantes?**
- [ ] **¿Las justificaciones tienen sentido?**
- [ ] **¿Hay multicodificación apropiada?**
- [ ] **¿El tiempo de ejecución es aceptable?**
- [ ] **¿El costo justifica el beneficio?**

---

## 🐛 Problemas Comunes

### **Error: "Columna 'P6' no encontrada"**
```python
# En celda 6, verás las columnas disponibles:
print(f"Columnas disponibles: {list(df.columns)}")
# Cambia PREGUNTA_A_CODIFICAR a una columna existente
```

### **Error: "Archivo no encontrado"**
```python
# Verifica la ruta:
ARCHIVO_RESPUESTAS = project_root / "ruta" / "correcta.xlsx"
print(f"Existe: {ARCHIVO_RESPUESTAS.exists()}")
```

### **Error: "OPENAI_API_KEY no configurada"**
```bash
# Edita .env en la raíz del proyecto
OPENAI_API_KEY=sk-...
```

---

## 📊 Interpretar Resultados

### **Decisiones:**
- **historico**: ✅ Reutilizó códigos existentes
- **nuevo**: 🆕 Generó códigos emergentes
- **mixto**: 🔀 Combinó ambos
- **rechazar**: ❌ Respuesta inválida

### **Códigos Nuevos:**
- `N1, N2, N3...`: Códigos generados secuencialmente
- Si ves muchos códigos nuevos con catálogo → GPT no encontró match
- Si ves pocos códigos únicos sin catálogo → Buena normalización

---

## 🎓 Próximos Pasos

1. ✅ Ejecuta con 20 respuestas para validar
2. ✅ Revisa manualmente 10-15 codificaciones
3. ✅ Compara con/sin catálogo
4. ✅ Ajusta prompts si es necesario
5. ✅ Ejecuta con más datos (50, 100, 200)
6. ✅ Decide si migrar a producción

---

## 🚀 ¿Te gustó el resultado?

Entonces es hora de:

1. **Integrar** este flujo en tu backend FastAPI
2. **Agregar** streaming para progreso en tiempo real
3. **Implementar** checkpointing para recuperación
4. **Desplegar** a producción

Consulta `notebooks/02_langgraph_codificacion.ipynb` (celda final) para el plan de migración.

---

¡Feliz experimentación! 🎉

