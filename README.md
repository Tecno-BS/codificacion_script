# 🚀 Sistema de Codificación Automatizada v1.0

Sistema de codificación automatizada de respuestas abiertas usando GPT, con arquitectura moderna separada entre backend (FastAPI) y frontend (Next.js + React).

## 📋 Tabla de Contenidos

- [Arquitectura](#-arquitectura)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Desarrollo](#-desarrollo)
- [Testing](#-testing)
- [Estructura del Proyecto](#-estructura-del-proyecto)

---

## 🏗️ Arquitectura

```
┌─────────────────────┐      HTTP/REST     ┌─────────────────────┐
│   FRONTEND          │ ◄─────────────────► │   BACKEND (API)     │
│   (Next.js/React)   │      JSON          │   (FastAPI)         │
│                     │                     │                     │
│  • UI moderna       │                     │  • Endpoints REST   │
│  • TypeScript       │                     │  • Lógica negocio   │
│  • Modo oscuro      │                     │  • GPT integration  │
│  • Upload directo   │                     │  • Procesamiento    │
└─────────────────────┘                     └─────────────────────┘
```

**Ventajas:**
- ✅ Frontend y backend desacoplados
- ✅ UI profesional y moderna con Next.js
- ✅ TypeScript para type-safety
- ✅ Escalabilidad independiente
- ✅ Testing más fácil
- ✅ API documentada automáticamente (Swagger)
- ✅ Deploy simplificado (Vercel, Docker, etc.)

---

## 🔧 Requisitos

- **Python:** 3.11 o superior
- **UV:** Gestor de paquetes y entornos virtuales
- **OpenAI API Key:** (opcional, puede usar modo MOCK)

---

## 📦 Instalación

### 1. Instalar UV (solo primera vez)

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Reinicia la terminal y verifica:
```bash
uv --version
```

### 2. Instalar Dependencias

```bash
# Desde la raíz del proyecto
uv sync
```

### 3. Configurar .env

**Backend:**
```bash
# backend/.env.backend
USE_GPT_MOCK=true
OPENAI_API_KEY=sk-test-mock-key
OPENAI_MODEL=gpt-4o-mini
BACKEND_PORT=8000
```

**Frontend:**
```bash
# cod-frontend/.env.local
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=QCoder
NEXT_PUBLIC_APP_VERSION=1.0.0
```

---

## 🚀 Uso

### Ejecutar Backend

```bash
cd backend
uv run uvicorn cod_backend.main:app --reload --port 8000
```

Disponible en:
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs 📚
- **Health:** http://localhost:8000/health

### Ejecutar Frontend (Next.js)

```bash
cd cod-frontend
npm install  # Solo primera vez
npm run dev
```

Disponible en: **http://localhost:3000** 🎨

> **Nota:** El frontend antiguo (Streamlit en `frontend/`) está deprecado. Usa el nuevo frontend en `cod-frontend/`.

### Ejecutar Tests

```bash
uv run pytest backend/tests/ -v
```

---

## 🧪 Testing

```bash
# Tests
uv run pytest backend/tests/ -v

# Con coverage
uv run pytest backend/tests/ --cov=cod_backend

# Health check manual
curl http://localhost:8000/health
```

---

## 📁 Estructura del Proyecto

```
cod-script/
├── pyproject.toml                 # Configuración raíz del workspace
├── uv.lock                        # Lock file de dependencias
├── .python-version                # Versión de Python (3.12)
│
├── backend/                       # 🔧 Backend API (FastAPI)
│   ├── pyproject.toml            # Dependencias del backend
│   ├── .env.backend              # Variables de entorno (no en git)
│   ├── .env.backend.example      # Ejemplo de configuración
│   ├── src/
│   │   └── cod_backend/
│   │       ├── __init__.py
│   │       ├── main.py           # Aplicación FastAPI
│   │       ├── config.py         # Configuración
│   │       ├── api/              # Endpoints REST
│   │       │   ├── __init__.py
│   │       │   └── routes/
│   │       │       └── __init__.py
│   │       ├── core/             # Lógica de negocio
│   │       │   └── __init__.py
│   │       └── schemas/          # Modelos Pydantic
│   │           └── __init__.py
│   └── tests/
│       ├── __init__.py
│       └── test_api.py           # Tests de la API
│
├── frontend/                      # 🎨 Frontend Web (Streamlit)
│   ├── pyproject.toml            # Dependencias del frontend
│   ├── .env.frontend             # Variables de entorno (no en git)
│   ├── .env.frontend.example     # Ejemplo de configuración
│   ├── src/
│   │   └── cod_frontend/
│   │       └── __init__.py
│   └── tests/
│       └── __init__.py
│
├── src/                           # 📦 Código legacy (temporal)
│   └── ... (código actual a migrar)
│
├── web/                           # 📦 UI legacy (temporal)
│   └── ... (código actual a migrar)
│
├── data/                          # 📊 Datos de entrada
├── result/                        # 📈 Resultados y reportes
└── README.md                      # Este archivo
```

---

## 🔄 Migración desde v0.5

Este proyecto está en proceso de migración de una arquitectura monolítica (v0.5) a una arquitectura separada (v0.6).

**Estado actual:**
- ✅ **FASE 1 COMPLETADA:** Estructura de carpetas y FastAPI básico
- ⏳ **FASE 2 EN PROGRESO:** Migrar lógica de negocio a backend API
- ⏳ **FASE 3 PENDIENTE:** Refactorizar frontend para consumir API
- ⏳ **FASE 4 PENDIENTE:** Testing completo

**Código legacy:**
- `src/` - Lógica de negocio actual (a migrar a `backend/src/cod_backend/core/`)
- `web/` - UI Streamlit actual (a migrar a `frontend/src/cod_frontend/`)

---

## 📚 Comandos Útiles

```bash
# Gestión de dependencias
uv sync                          # Instalar/actualizar todo
cd backend && uv add <paquete>   # Agregar al backend
cd frontend && uv add <paquete>  # Agregar al frontend
uv pip list                      # Ver instalados

# Calidad de código
uv run black backend frontend           # Formatear
uv run ruff check backend frontend      # Linter
```

---

## 📖 Documentación API

Una vez iniciado el backend, la documentación interactiva está disponible en:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🐛 Solución de Problemas

```bash
# Backend no inicia
uv sync                           # Reinstalar dependencias
ls backend\.env.backend           # Verificar que existe .env

# Tests fallan
curl http://localhost:8000/health # Verificar backend corriendo

# Puerto ocupado
netstat -ano | findstr :8000      # Ver qué proceso usa el puerto
taskkill /PID <PID> /F            # Matar proceso
```

---

## 🚀 Despliegue en Producción

Para desplegar el proyecto en un servidor Windows Server, consulta las siguientes guías:

- **📘 Despliegue Manual (Recomendado)**: [`DEPLOYMENT_MANUAL_WINDOWS_SERVER.md`](DEPLOYMENT_MANUAL_WINDOWS_SERVER.md)
  - Guía paso a paso sin scripts automatizados
  - Instrucciones detalladas para cada configuración
  - Ideal para entender cada paso del proceso

- **⚡ Despliegue con Scripts**: [`DEPLOYMENT_WINDOWS_SERVER.md`](DEPLOYMENT_WINDOWS_SERVER.md)
  - Scripts automatizados de PowerShell
  - Más rápido pero requiere ejecutar scripts

- **📋 Guía Rápida**: [`QUICK_START_DEPLOYMENT.md`](QUICK_START_DEPLOYMENT.md)
  - Resumen de pasos esenciales
  - Checklist de verificación
