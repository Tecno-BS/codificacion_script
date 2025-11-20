# Frontend Streamlit - Codificación Automatizada

Frontend web para el Sistema de Codificación Automatizada con GPT.

## 🚀 Uso

### Ejecutar Frontend

```bash
cd frontend
uv run streamlit run src/cod_frontend/app.py
```

El frontend estará disponible en: **http://localhost:8501**

### Requisitos

- Backend corriendo en `http://localhost:8000`
- Archivo `.env.frontend` configurado

## 📝 Configuración

Crear archivo `.env.frontend`:

```bash
BACKEND_URL=http://localhost:8000
FRONTEND_PORT=8501
```

## 🎯 Funcionalidades

- ✅ Carga de archivos Excel (respuestas y catálogos)
- ✅ Selección de modelo GPT
- ✅ Codificación automática via API REST
- ✅ Descarga de resultados
- ✅ Descarga de catálogo de códigos nuevos
- ✅ Health check del backend
- ✅ Progreso en tiempo real

## 📊 Flujo de Trabajo

1. **Cargar archivos:**
   - Archivo de respuestas (obligatorio)
   - Catálogo de códigos históricos (opcional)

2. **Seleccionar modelo:**
   - GPT-4o Mini (recomendado, económico)
   - GPT-4o (mayor precisión)
   - GPT-4.1 (versión mejorada)

3. **Iniciar codificación:**
   - Click en "Iniciar Codificación"
   - Esperar procesamiento

4. **Descargar resultados:**
   - Excel con codificaciones
   - Catálogo de códigos nuevos

## 🔧 Desarrollo

### Estructura

```
frontend/
├── src/cod_frontend/
│   ├── __init__.py
│   └── app.py              # Aplicación Streamlit
├── pyproject.toml          # Dependencias
└── README.md
```

### Agregar Dependencias

```bash
cd frontend
uv add nombre-paquete
```

## 📚 Documentación API

El frontend consume la API REST del backend:

- `POST /api/v1/codificar` - Codificar respuestas
- `GET /api/v1/modelos` - Listar modelos
- `GET /api/v1/resultados/{filename}` - Descargar resultados
- `GET /api/v1/codigos-nuevos/{filename}` - Descargar códigos nuevos
- `GET /health` - Health check

Ver documentación completa: http://localhost:8000/docs

## 🆚 Diferencias con Frontend Legacy

**Frontend nuevo (migrado):**
- ✅ Usa API REST (desacoplado del backend)
- ✅ Más simple (260 líneas vs 689)
- ✅ Sin imports directos del codificador
- ✅ Comunicación HTTP
- ✅ Más fácil de escalar

**Frontend legacy (`web/app.py`):**
- ❌ Importa codificador directamente
- ❌ Acoplado al backend
- ❌ Más complejo
- ✅ Mantiene todas las funcionalidades originales

El frontend legacy se mantiene en `web/app.py` por compatibilidad.

## 🐛 Solución de Problemas

### Backend no disponible

```bash
# Verificar que el backend está corriendo
curl http://localhost:8000/health
```

### Timeout en codificación

- Archivos muy grandes pueden tardar varios minutos
- El timeout está configurado a 10 minutos
- Ver progreso en los logs del backend

### Error al descargar archivos

- Verificar que los archivos se generaron correctamente
- Ver carpetas `result/codificaciones/` y `result/codigos_nuevos/`





