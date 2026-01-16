# Sistema de Codificación Automatizada

Sistema web para la codificación automatizada de respuestas abiertas de encuestas usando inteligencia artificial (GPT de OpenAI). Permite procesar grandes volúmenes de respuestas de texto libre y asignarles códigos estructurados de manera automática.

## Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Despliegue](#despliegue)
- [Acceso a la Aplicación](#acceso-a-la-aplicación)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Solución de Problemas](#solución-de-problemas)

---

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

1. **Python 3.11 o superior**
   - Descarga desde: https://www.python.org/downloads/
   - Durante la instalación, marca la opción "Add Python to PATH"

2. **uv** (gestor de paquetes Python)
   - Instalación en Windows (PowerShell):
     ```powershell
     powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
     ```
   - O descarga desde: https://github.com/astral-sh/uv/releases
   - **Nota:** Si no puedes instalar uv, puedes usar pip tradicional (ver sección alternativa más abajo)

3. **Node.js 18 o superior y npm**
   - Descarga desde: https://nodejs.org/
   - npm se instala automáticamente con Node.js

4. **Clave de API de OpenAI**
   - Obtén una clave desde: https://platform.openai.com/api-keys
   - Necesitarás una cuenta de OpenAI con créditos disponibles

5. **Git** (opcional, solo si clonas el repositorio)
   - Descarga desde: https://git-scm.com/downloads

### Verificar Instalaciones

Abre CMD (Símbolo del sistema) y verifica que todo esté instalado:

```cmd
python --version
uv --version
node --version
npm --version
```

Deberías ver versiones como:
- Python 3.11.x o superior
- uv 0.x.x o superior
- Node.js v18.x.x o superior
- npm 9.x.x o superior

---

## Instalación

### Paso 1: Obtener el Código

Si tienes el código en una carpeta local, navega hasta ella:

```cmd
cd C:\Apps\CodificacionAutomatizada
```

Si necesitas clonar desde un repositorio:

```cmd
git clone [URL_DEL_REPOSITORIO]
cd CodificacionAutomatizada
```

### Paso 2: Instalar Dependencias del Backend

1. Navega a la raíz del proyecto (donde está el archivo `uv.lock`):

```cmd
cd C:\Apps\CodificacionAutomatizada
```

2. Sincroniza las dependencias con uv (esto crea el entorno virtual automáticamente):

```cmd
uv sync
```

Este comando:
- Crea el entorno virtual automáticamente
- Instala todas las dependencias del proyecto
- Sincroniza las versiones según `uv.lock`

3. Activa el entorno virtual creado por uv:

```cmd
uv venv
```

O si prefieres activarlo manualmente, el entorno virtual se crea en `.venv`:

```cmd
.venv\Scripts\activate
```

Verás que el prompt cambia a `(.venv)` indicando que el entorno está activo.

4. Verifica la instalación:

```cmd
uv run python -c "import fastapi; print('FastAPI instalado correctamente')"
```

O si activaste el entorno virtual manualmente:

```cmd
python -c "import fastapi; print('FastAPI instalado correctamente')"
```

**Nota:** Con `uv`, puedes ejecutar comandos Python directamente sin activar el entorno virtual usando `uv run`:

```cmd
uv run python -m uvicorn cod_backend.main:app --host 0.0.0.0 --port 8000
```

#### Alternativa: Si no tienes uv instalado

Si prefieres usar pip tradicional en lugar de uv:

1. Navega a la carpeta del backend:

```cmd
cd backend
```

2. Crea un entorno virtual de Python:

```cmd
python -m venv venv
```

3. Activa el entorno virtual:

```cmd
venv\Scripts\activate
```

4. Instala las dependencias:

```cmd
pip install -e .
```

### Paso 3: Instalar Dependencias del Frontend

1. Abre una nueva ventana de CMD (mantén el backend corriendo en la otra)

2. Navega a la carpeta del frontend:

```cmd
cd C:\Apps\CodificacionAutomatizada\frontend
```

3. Instala las dependencias de Node.js:

```cmd
npm install
```

Esto puede tardar varios minutos la primera vez. Verás que se descargan muchos paquetes.

4. Verifica la instalación:

```cmd
npm list next
```

---

## Configuración

### Configurar la Clave de API de OpenAI

El backend necesita la clave de API de OpenAI para funcionar. Tienes dos opciones:

#### Opción 1: Variable de Entorno del Sistema (Recomendado)

1. Abre el Panel de Control de Windows
2. Ve a "Sistema" > "Configuración avanzada del sistema"
3. Haz clic en "Variables de entorno"
4. En "Variables del sistema", haz clic en "Nueva"
5. Nombre de la variable: `OPENAI_API_KEY`
6. Valor de la variable: `sk-tu-clave-aqui` (reemplaza con tu clave real)
7. Haz clic en "Aceptar" en todas las ventanas
8. **Reinicia CMD** para que los cambios surtan efecto

#### Opción 2: Archivo .env.backend

1. En la raíz del proyecto (C:\Apps\CodificacionAutomatizada), crea un archivo llamado `.env.backend`

2. Abre el archivo con un editor de texto y agrega:

```
OPENAI_API_KEY=sk-tu-clave-aqui
```

Reemplaza `sk-tu-clave-aqui` con tu clave real de OpenAI.

3. Guarda el archivo

### Verificar la Configuración

Abre CMD, activa el entorno virtual del backend y verifica:

```cmd
cd C:\Apps\CodificacionAutomatizada\backend
venv\Scripts\activate
python -c "import os; print('API Key configurada:', 'Sí' if os.getenv('OPENAI_API_KEY') else 'No')"
```

---

## Despliegue

### Iniciar el Backend

**Opción 1: Usando uv (Recomendado)**

1. Abre CMD y navega a la raíz del proyecto:

```cmd
cd C:\Apps\CodificacionAutomatizada
```

2. Configura la variable de entorno para acceso público (opcional):

```cmd
set PUBLIC_ACCESS=true
```

Si solo quieres acceso local, omite este paso.

3. Inicia el servidor usando uv:

```cmd
cd backend\src
uv run python -m uvicorn cod_backend.main:app --host 0.0.0.0 --port 8000
```

**Opción 2: Activando el entorno virtual manualmente**

1. Abre CMD y navega a la raíz del proyecto:

```cmd
cd C:\Apps\CodificacionAutomatizada
```

2. Activa el entorno virtual creado por uv:

```cmd
.venv\Scripts\activate
```

3. Navega al directorio src:

```cmd
cd backend\src
```

4. Configura la variable de entorno para acceso público (opcional):

```cmd
set PUBLIC_ACCESS=true
```

5. Inicia el servidor:

```cmd
python -m uvicorn cod_backend.main:app --host 0.0.0.0 --port 8000
```

Verás mensajes como:
```
INFO:     Started server process
INFO:     Waiting for application startup.
MODO PUBLICO ACTIVADO: El servidor acepta conexiones desde cualquier origen
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Mantén esta ventana abierta.** El servidor debe seguir corriendo.

### Iniciar el Frontend

1. Abre una **nueva ventana de CMD** (no cierres la del backend)

2. Navega al directorio del frontend:

```cmd
cd C:\Apps\CodificacionAutomatizada\frontend
```

3. Configura la URL del backend:

```cmd
set NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Si el backend está en otro servidor, reemplaza `localhost` con la IP del servidor.

4. Para desarrollo (con recarga automática):

```cmd
npm run dev
```

O para producción (más rápido, sin recarga):

```cmd
npm run build
npm start
```

Verás mensajes como:
```
  ▲ Next.js 16.0.8
  - Local:        http://localhost:3000
  - Ready in 2.3s
```

**Mantén esta ventana abierta también.**

---

## Acceso a la Aplicación

Una vez que ambos servidores estén corriendo:

### Acceso Local

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Documentación del Backend:** http://localhost:8000/docs

### Acceso desde Otros Equipos en la Red

Si configuraste `PUBLIC_ACCESS=true` y el backend está escuchando en `0.0.0.0`:

1. Obtén la IP de tu servidor:

```cmd
ipconfig
```

Busca la dirección IPv4 que no sea 127.0.0.1 (generalmente algo como 192.168.x.x)

2. Accede desde otros equipos usando:
   - **Frontend:** http://[TU_IP]:3000
   - **Backend:** http://[TU_IP]:8000

3. **Importante:** Asegúrate de que el firewall de Windows permita conexiones en los puertos 3000 y 8000.

### Configurar el Firewall (si es necesario)

Si otros equipos no pueden acceder, abre los puertos en el firewall:

1. Abre "Firewall de Windows Defender" desde el Panel de Control
2. Haz clic en "Configuración avanzada"
3. Haz clic en "Reglas de entrada" > "Nueva regla"
4. Selecciona "Puerto" > Siguiente
5. Selecciona "TCP" y especifica los puertos "3000,8000" > Siguiente
6. Selecciona "Permitir la conexión" > Siguiente
7. Marca todos los perfiles > Siguiente
8. Dale un nombre (ej: "Codificacion Automatizada") > Finalizar

---

## Estructura del Proyecto

```
CodificacionAutomatizada/
├── backend/                 # Backend API (FastAPI)
│   ├── src/
│   │   └── cod_backend/    # Código fuente del backend
│   ├── venv/               # Entorno virtual de Python
│   ├── temp/               # Archivos temporales
│   ├── result/             # Resultados generados
│   └── pyproject.toml      # Dependencias del backend
│
├── frontend/               # Frontend web (Next.js)
│   ├── app/                # Páginas de Next.js
│   ├── components/          # Componentes React
│   ├── hooks/              # Custom hooks
│   ├── node_modules/       # Dependencias de Node.js
│   └── package.json        # Dependencias del frontend
│
└── notebooks/              # Jupyter notebooks de experimentación
```

---

## Solución de Problemas

### Error: "No module named 'cod_backend'"

**Problema:** Estás ejecutando el backend desde el directorio incorrecto.

**Solución:**
```cmd
cd C:\Apps\CodificacionAutomatizada\backend\src
uv run python -m uvicorn cod_backend.main:app --host 0.0.0.0 --port 8000
```

O si activaste el entorno virtual:
```cmd
cd C:\Apps\CodificacionAutomatizada
.venv\Scripts\activate
cd backend\src
python -m uvicorn cod_backend.main:app --host 0.0.0.0 --port 8000
```

### Error: "ModuleNotFoundError: No module named 'langgraph'"

**Problema:** Las dependencias del backend no están instaladas.

**Solución:**
```cmd
cd C:\Apps\CodificacionAutomatizada
uv sync
```

Esto sincronizará todas las dependencias según el archivo `uv.lock`.

### Error: "OPENAI_API_KEY not found"

**Problema:** La clave de API no está configurada.

**Solución:**
1. Verifica que creaste la variable de entorno `OPENAI_API_KEY` o el archivo `.env.backend`
2. Si usaste variable de entorno, **reinicia CMD** después de crearla
3. Verifica con:
```cmd
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

### Error: "Cannot find module 'next'"

**Problema:** Las dependencias del frontend no están instaladas.

**Solución:**
```cmd
cd C:\Apps\CodificacionAutomatizada\frontend
npm install
```

### Error de CORS: "Access-Control-Allow-Origin header is missing"

**Problema:** El backend no está configurado para permitir conexiones desde el frontend.

**Solución:**
1. Asegúrate de que el backend esté corriendo con `PUBLIC_ACCESS=true`:
```cmd
set PUBLIC_ACCESS=true
python -m uvicorn cod_backend.main:app --host 0.0.0.0 --port 8000
```

2. Verifica que `NEXT_PUBLIC_BACKEND_URL` esté configurado correctamente en el frontend:
```cmd
set NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### El frontend no se conecta al backend

**Problema:** La URL del backend está mal configurada o el backend no está corriendo.

**Solución:**
1. Verifica que el backend esté corriendo (deberías ver mensajes en la consola)
2. Abre http://localhost:8000/health en el navegador, debería responder con JSON
3. Verifica que `NEXT_PUBLIC_BACKEND_URL` esté configurado antes de iniciar el frontend
4. Si cambiaste la variable, **reconstruye el frontend**:
```cmd
cd C:\Apps\CodificacionAutomatizada\frontend
set NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
npm run build
npm start
```

### Puerto 8000 o 3000 ya está en uso

**Problema:** Otro proceso está usando esos puertos.

**Solución:**
1. Encuentra qué proceso está usando el puerto:
```cmd
netstat -ano | findstr :8000
netstat -ano | findstr :3000
```

2. Termina el proceso o usa otros puertos:
   - Para backend: `--port 8001`
   - Para frontend: modifica `package.json` o usa `npm run dev -- -p 3001`

### El entorno virtual no se activa

**Problema:** Puede ser un problema de permisos o la ruta está mal.

**Solución:**
1. Si usas uv, el entorno virtual está en `.venv` en la raíz del proyecto:
```cmd
cd C:\Apps\CodificacionAutomatizada
.venv\Scripts\activate
```

2. Si no existe `.venv`, sincroniza las dependencias:
```cmd
uv sync
```

3. Verifica que existe la carpeta:
```cmd
dir .venv
```

4. Intenta activarlo con la ruta completa:
```cmd
C:\Apps\CodificacionAutomatizada\.venv\Scripts\activate.bat
```

5. **Alternativa:** Usa `uv run` sin necesidad de activar el entorno:
```cmd
cd C:\Apps\CodificacionAutomatizada\backend\src
uv run python -m uvicorn cod_backend.main:app --host 0.0.0.0 --port 8000
```

---

## Comandos Útiles

### Backend

```cmd
# Navegar a la raíz del proyecto
cd C:\Apps\CodificacionAutomatizada

# Sincronizar dependencias (crea/actualiza entorno virtual)
uv sync

# Opción 1: Usar uv run (no necesitas activar el entorno)
cd backend\src
set PUBLIC_ACCESS=true
uv run python -m uvicorn cod_backend.main:app --host 0.0.0.0 --port 8000 --reload

# Opción 2: Activar entorno virtual manualmente
.venv\Scripts\activate
cd backend\src
set PUBLIC_ACCESS=true
python -m uvicorn cod_backend.main:app --host 0.0.0.0 --port 8000 --reload

# Verificar que el servidor responde
curl http://localhost:8000/health
```

### Frontend

```cmd
# Instalar dependencias
cd C:\Apps\CodificacionAutomatizada\frontend
npm install

# Modo desarrollo (con recarga automática)
set NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
npm run dev

# Construir para producción
set NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
npm run build

# Iniciar en modo producción
npm start

# Limpiar caché y reinstalar
rmdir /s /q node_modules
del package-lock.json
npm install
```

---

## Próximos Pasos

Una vez que tengas el sistema funcionando:

1. **Explora la documentación del API:** http://localhost:8000/docs
2. **Prueba con un archivo pequeño:** Sube un Excel con 10-20 respuestas para probar
3. **Revisa los resultados:** Los archivos generados se guardan en `backend/result/`
4. **Consulta los logs:** Si hay errores, revisa la consola donde corre el backend

---

## Soporte

Si encuentras problemas que no están cubiertos en esta guía:

1. Revisa los mensajes de error en las consolas (backend y frontend)
2. Verifica que todas las dependencias estén instaladas correctamente
3. Asegúrate de que la clave de API de OpenAI sea válida y tenga créditos
4. Consulta la documentación de FastAPI: https://fastapi.tiangolo.com/
5. Consulta la documentación de Next.js: https://nextjs.org/docs

---

## Notas Importantes

- **Con uv, no necesitas activar el entorno virtual** si usas `uv run` para ejecutar comandos
- **El entorno virtual con uv está en `.venv`** en la raíz del proyecto (no en `backend/venv`)
- **No cierres las ventanas de CMD** donde están corriendo los servidores
- **La clave de API de OpenAI es sensible:** No la compartas ni la subas a repositorios públicos
- **Los archivos temporales** se limpian automáticamente después de 24 horas
- **El procesamiento puede tardar** dependiendo del número de respuestas y el modelo GPT usado
- **Si usas `uv sync`**, las dependencias se sincronizan automáticamente según `uv.lock` para garantizar versiones consistentes

---

**Última actualización:** Diciembre 2024

