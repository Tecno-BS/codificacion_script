# ⚡ Quick Start - Inicio Rápido

Guía simple usando UV directamente. Sin scripts complejos.

---

## 📦 **1. Instalar UV (solo primera vez)**

```powershell
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Luego reinicia PowerShell
```

Verifica:
```powershell
uv --version
```

---

## 🚀 **2. Instalar Dependencias**

```powershell
# En la raíz del proyecto
uv sync
```

Esto instalará todas las dependencias del backend y frontend automáticamente.

---

## ⚙️ **3. Configurar .env**

### Backend

```powershell
# Copiar el ejemplo
copy backend\.env.backend.example backend\.env.backend

# Editar (opcional)
notepad backend\.env.backend
```

**Para empezar, deja el modo MOCK:**
```bash
USE_GPT_MOCK=true
OPENAI_API_KEY=sk-test
```

### Frontend

```powershell
# Copiar el ejemplo
copy frontend\.env.frontend.example frontend\.env.frontend
```

---

## 🔧 **4. Ejecutar Backend**

```powershell
cd backend
uv run uvicorn cod_backend.main:app --reload --port 8000
```

✅ **Abrir:** http://localhost:8000/docs

---

## 🧪 **5. Ejecutar Tests**

```powershell
# En otra terminal (desde la raíz)
uv run pytest backend/tests/ -v
```

---

## 📝 **Comandos Principales**

### Desarrollo

```powershell
# Backend
cd backend
uv run uvicorn cod_backend.main:app --reload --port 8000

# Frontend (cuando esté listo)
cd frontend
uv run streamlit run src/cod_frontend/app.py

# Tests
uv run pytest backend/tests/ -v
```

### Gestión de Dependencias

```powershell
# Instalar/actualizar todo
uv sync

# Agregar paquete al backend
cd backend
uv add nombre-paquete

# Agregar paquete al frontend
cd frontend
uv add nombre-paquete

# Ver qué está instalado
uv pip list
```

### Calidad de Código

```powershell
# Formatear
uv run black backend frontend

# Linter
uv run ruff check backend frontend

# Tests con coverage
uv run pytest backend/tests/ --cov=cod_backend
```

---

## 🌐 **URLs del Backend**

| URL | Descripción |
|-----|-------------|
| http://localhost:8000 | Info de la API |
| http://localhost:8000/health | Health check |
| http://localhost:8000/docs | 📚 Swagger UI (Documentación interactiva) |

---

## 🐛 **Solución de Problemas**

### Backend no inicia

```powershell
# Verificar que existe .env
ls backend\.env.backend

# Si no existe, copiar el ejemplo
copy backend\.env.backend.example backend\.env.backend

# Reinstalar dependencias
uv sync
```

### Tests fallan

```powershell
# Verificar que backend está corriendo
curl http://localhost:8000/health
```

### Puerto 8000 ocupado

```powershell
# Ver qué proceso lo usa
netstat -ano | findstr :8000

# Matar el proceso (reemplaza <PID>)
taskkill /PID <PID> /F
```

### Importación falla

```powershell
# Asegúrate de estar en el directorio correcto
cd backend
uv run python -m cod_backend.main
```

---

## 📁 **Estructura Simple**

```
cod-script/
├── backend/                    # API REST (FastAPI)
│   ├── pyproject.toml         # Dependencias
│   ├── .env.backend           # Configuración
│   ├── src/cod_backend/
│   │   ├── main.py            # 🚀 App principal
│   │   ├── config.py
│   │   ├── api/
│   │   ├── core/
│   │   └── schemas/
│   └── tests/
│
├── frontend/                   # UI Web (Streamlit)
│   ├── pyproject.toml
│   ├── .env.frontend
│   └── src/cod_frontend/
│
└── pyproject.toml             # Workspace raíz
```

---

## ✅ **Checklist Rápido**

```powershell
# 1. Instalar dependencias
uv sync

# 2. Configurar .env
copy backend\.env.backend.example backend\.env.backend

# 3. Ejecutar backend
cd backend
uv run uvicorn cod_backend.main:app --reload --port 8000

# 4. Probar (en otra terminal)
uv run pytest backend/tests/ -v
```

---

**Eso es todo.** Comandos simples y directos con UV. 🎯

