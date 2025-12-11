# Guía de Despliegue Manual - Windows Server

Esta guía te llevará paso a paso para desplegar el proyecto manualmente en un servidor Windows Server, sin usar scripts automatizados.

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Preparación del Servidor](#preparación-del-servidor)
3. [Instalación de Dependencias](#instalación-de-dependencias)
4. [Configuración del Backend](#configuración-del-backend)
5. [Configuración del Frontend](#configuración-del-frontend)
6. [Configuración de IIS](#configuración-de-iis)
7. [Configuración de Servicios de Windows](#configuración-de-servicios-de-windows)
8. [Configuración de Variables de Entorno](#configuración-de-variables-de-entorno)
9. [Configuración de Logs](#configuración-de-logs)
10. [Configuración de Seguridad](#configuración-de-seguridad)
11. [Configuración de HTTPS](#configuración-de-https)
12. [Verificación y Pruebas](#verificación-y-pruebas)

---

## 1. Requisitos Previos

### Hardware Mínimo Recomendado
- **CPU**: 4 cores o más
- **RAM**: 8 GB mínimo (16 GB recomendado)
- **Disco**: 50 GB libres (SSD recomendado)
- **Red**: Conexión estable a Internet

### Software Requerido
- Windows Server 2019 o superior
- PowerShell 5.1 o superior
- Acceso de administrador al servidor

---

## 2. Preparación del Servidor

### 2.1 Crear Estructura de Directorios

Abre PowerShell como Administrador y ejecuta:

```powershell
# Crear directorio principal
New-Item -ItemType Directory -Path "C:\Apps\CodificacionAutomatizada" -Force
New-Item -ItemType Directory -Path "C:\Apps\CodificacionAutomatizada\backend" -Force
New-Item -ItemType Directory -Path "C:\Apps\CodificacionAutomatizada\frontend" -Force
New-Item -ItemType Directory -Path "C:\Apps\CodificacionAutomatizada\logs" -Force
New-Item -ItemType Directory -Path "C:\Apps\CodificacionAutomatizada\backups" -Force

# Crear directorios para datos
New-Item -ItemType Directory -Path "C:\Apps\CodificacionAutomatizada\backend\result" -Force
New-Item -ItemType Directory -Path "C:\Apps\CodificacionAutomatizada\backend\result\codificaciones" -Force
New-Item -ItemType Directory -Path "C:\Apps\CodificacionAutomatizada\backend\result\codigos_nuevos" -Force
New-Item -ItemType Directory -Path "C:\Apps\CodificacionAutomatizada\backend\temp" -Force
```

### 2.2 Copiar Archivos del Proyecto

1. Copia todo el contenido de la carpeta `backend/` a `C:\Apps\CodificacionAutomatizada\backend\`
2. Copia todo el contenido de la carpeta `frontend/` a `C:\Apps\CodificacionAutomatizada\frontend\`

---

## 3. Instalación de Dependencias

### 3.1 Instalar Python 3.11+

1. Descarga Python 3.11+ desde [python.org/downloads](https://www.python.org/downloads/)
2. Ejecuta el instalador
3. Durante la instalación, marca:
   - ✅ "Add Python to PATH"
   - ✅ "Install for all users"
4. Verifica la instalación:

```powershell
python --version
# Debe mostrar: Python 3.11.x o superior
```

### 3.2 Instalar UV (Gestor de Paquetes Python)

Abre PowerShell y ejecuta:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

Cierra y vuelve a abrir PowerShell, luego verifica:

```powershell
uv --version
```

### 3.3 Instalar Node.js 18+ LTS

1. Descarga Node.js LTS desde [nodejs.org](https://nodejs.org/)
2. Ejecuta el instalador con configuración por defecto
3. Verifica:

```powershell
node --version
npm --version
```

### 3.4 Habilitar IIS y Características Necesarias

Abre PowerShell como Administrador y ejecuta:

```powershell
# Habilitar IIS
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServer
Enable-WindowsOptionalFeature -Online -FeatureName IIS-CommonHttpFeatures
Enable-WindowsOptionalFeature -Online -FeatureName IIS-HttpErrors
Enable-WindowsOptionalFeature -Online -FeatureName IIS-ApplicationInit
Enable-WindowsOptionalFeature -Online -FeatureName IIS-HealthAndDiagnostics
Enable-WindowsOptionalFeature -Online -FeatureName IIS-HttpLogging
Enable-WindowsOptionalFeature -Online -FeatureName IIS-Security
Enable-WindowsOptionalFeature -Online -FeatureName IIS-RequestFiltering
Enable-WindowsOptionalFeature -Online -FeatureName IIS-Performance
Enable-WindowsOptionalFeature -Online -FeatureName IIS-HttpCompressionStatic
Enable-WindowsOptionalFeature -Online -FeatureName IIS-HttpCompressionDynamic
```

**Reinicia el servidor después de habilitar IIS.**

### 3.5 Instalar URL Rewrite Module

1. Descarga desde: [iis.net/downloads/microsoft/url-rewrite](https://www.iis.net/downloads/microsoft/url-rewrite)
2. Ejecuta el instalador
3. Sigue las instrucciones del asistente

### 3.6 Instalar Application Request Routing (ARR)

1. Descarga desde: [iis.net/downloads/microsoft/application-request-routing](https://www.iis.net/downloads/microsoft/application-request-routing)
2. Ejecuta el instalador
3. Sigue las instrucciones del asistente

### 3.7 Instalar NSSM (Non-Sucking Service Manager)

1. Descarga desde: [nssm.cc/download](https://nssm.cc/download)
2. Extrae el archivo ZIP
3. Copia `nssm.exe` (de la carpeta `win64` o `win32` según tu sistema) a `C:\Windows\System32\` o a una carpeta en tu PATH

---

## 4. Configuración del Backend

### 4.1 Crear Entorno Virtual

Abre PowerShell y ejecuta:

```powershell
cd C:\Apps\CodificacionAutomatizada\backend

# Crear entorno virtual
uv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar dependencias
uv pip install -e .
```

### 4.2 Crear Archivo de Configuración

Crea el archivo `C:\Apps\CodificacionAutomatizada\backend\.env.backend` con el siguiente contenido:

```env
# OpenAI Configuration
OPENAI_API_KEY=tu_clave_api_de_openai_aqui
OPENAI_MODEL=gpt-4o-mini

# Server Configuration
HOST=127.0.0.1
PORT=8000
WORKERS=4

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# CORS (Producción)
CORS_ORIGINS=http://localhost:3000,https://tu-dominio.com
PRODUCTION_DOMAIN=tu-dominio.com
```

**Importante**: Reemplaza `tu_clave_api_de_openai_aqui` y `tu-dominio.com` con tus valores reales.

### 4.3 Crear Archivo de Configuración de Logging

Crea el archivo `C:\Apps\CodificacionAutomatizada\backend\logging_prod.json`:

```json
{
  "version": 1,
  "disable_existing_loggers": false,
  "formatters": {
    "default": {
      "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
      "datefmt": "%Y-%m-%d %H:%M:%S"
    },
    "detailed": {
      "format": "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s",
      "datefmt": "%Y-%m-%d %H:%M:%S"
    }
  },
  "handlers": {
    "file": {
      "class": "logging.handlers.RotatingFileHandler",
      "level": "INFO",
      "formatter": "detailed",
      "filename": "C:\\Apps\\CodificacionAutomatizada\\logs\\backend.log",
      "maxBytes": 10485760,
      "backupCount": 10,
      "encoding": "utf-8"
    },
    "error_file": {
      "class": "logging.handlers.RotatingFileHandler",
      "level": "ERROR",
      "formatter": "detailed",
      "filename": "C:\\Apps\\CodificacionAutomatizada\\logs\\backend_errors.log",
      "maxBytes": 10485760,
      "backupCount": 10,
      "encoding": "utf-8"
    },
    "console": {
      "class": "logging.StreamHandler",
      "level": "INFO",
      "formatter": "default",
      "stream": "ext://sys.stdout"
    }
  },
  "loggers": {
    "uvicorn": {
      "level": "INFO",
      "handlers": ["file", "console"],
      "propagate": false
    },
    "uvicorn.error": {
      "level": "ERROR",
      "handlers": ["error_file", "console"],
      "propagate": false
    },
    "cod_backend": {
      "level": "INFO",
      "handlers": ["file", "error_file"],
      "propagate": false
    }
  },
  "root": {
    "level": "INFO",
    "handlers": ["file", "console"]
  }
}
```

### 4.4 Probar que el Backend Funciona

Abre PowerShell y ejecuta:

```powershell
cd C:\Apps\CodificacionAutomatizada\backend
.\venv\Scripts\Activate.ps1

# Probar que puede importar el módulo
python -c "from cod_backend.main import app; print('Backend OK')"
```

Si no hay errores, el backend está configurado correctamente.

---

## 5. Configuración del Frontend

### 5.1 Instalar Dependencias

Abre PowerShell y ejecuta:

```powershell
cd C:\Apps\CodificacionAutomatizada\frontend

# Instalar dependencias
npm ci --production
```

### 5.2 Crear Archivo de Configuración de Producción

Crea el archivo `C:\Apps\CodificacionAutomatizada\frontend\.env.production`:

```env
NEXT_PUBLIC_BACKEND_URL=https://tu-dominio.com/api
NODE_ENV=production
```

**Importante**: Reemplaza `tu-dominio.com` con tu dominio real.

### 5.3 Compilar el Frontend

Abre PowerShell y ejecuta:

```powershell
cd C:\Apps\CodificacionAutomatizada\frontend

# Compilar para producción
npm run build
```

Esto creará la carpeta `.next` con los archivos compilados.

### 5.4 Verificar la Compilación

```powershell
# Verificar que existe .next
Test-Path "C:\Apps\CodificacionAutomatizada\frontend\.next"
# Debe retornar: True
```

---

## 6. Configuración de IIS

### 6.1 Abrir IIS Manager

1. Presiona `Win + R`
2. Escribe `inetmgr` y presiona Enter
3. Se abrirá el Administrador de IIS

### 6.2 Crear Application Pool

1. En el panel izquierdo, expande el servidor
2. Haz clic derecho en **Application Pools**
3. Selecciona **Add Application Pool...**
4. Configura:
   - **Name**: `CodificacionAutomatizadaAppPool`
   - **.NET CLR version**: **No Managed Code**
   - **Managed pipeline mode**: **Integrated**
5. Haz clic en **OK**

### 6.3 Configurar Application Pool

1. Selecciona `CodificacionAutomatizadaAppPool`
2. Haz clic en **Advanced Settings...** (panel derecho)
3. Configura:
   - **Start Mode**: `AlwaysRunning`
   - **Idle Timeout**: `00:00:00` (deshabilitar timeout)
4. Haz clic en **OK**

### 6.4 Crear Sitio Web

1. En el panel izquierdo, haz clic derecho en **Sites**
2. Selecciona **Add Website...**
3. Configura:
   - **Site name**: `CodificacionAutomatizada`
   - **Application pool**: `CodificacionAutomatizadaAppPool`
   - **Physical path**: `C:\Apps\CodificacionAutomatizada\frontend`
   - **Binding**:
     - **Type**: `http`
     - **IP address**: `All Unassigned`
     - **Port**: `80`
     - **Host name**: `tu-dominio.com` (o déjalo vacío para localhost)
4. Haz clic en **OK**

### 6.5 Crear web.config

Crea el archivo `C:\Apps\CodificacionAutomatizada\frontend\web.config`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <!-- Proxy requests to /api/* to backend -->
        <rule name="Backend API Proxy" stopProcessing="true">
          <match url="^api/(.*)" />
          <action type="Rewrite" url="http://127.0.0.1:8000/{R:1}" />
          <serverVariables>
            <set name="HTTP_X_FORWARDED_PROTO" value="https" />
            <set name="HTTP_X_FORWARDED_HOST" value="{HTTP_HOST}" />
          </serverVariables>
        </rule>
        
        <!-- Next.js routing -->
        <rule name="Next.js Routes" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/" />
        </rule>
      </rules>
    </rewrite>
    
    <!-- Configuración de compresión -->
    <httpCompression>
      <dynamicTypes>
        <add mimeType="application/json" enabled="true" />
        <add mimeType="application/javascript" enabled="true" />
        <add mimeType="text/css" enabled="true" />
      </dynamicTypes>
    </httpCompression>
    
    <!-- Headers de seguridad -->
    <httpProtocol>
      <customHeaders>
        <add name="X-Content-Type-Options" value="nosniff" />
        <add name="X-Frame-Options" value="DENY" />
        <add name="X-XSS-Protection" value="1; mode=block" />
        <add name="Referrer-Policy" value="strict-origin-when-cross-origin" />
      </customHeaders>
    </httpProtocol>
    
    <!-- Configuración de errores -->
    <httpErrors errorMode="DetailedLocalOnly" />
    
    <!-- Configuración de caché estática -->
    <staticContent>
      <clientCache cacheControlMode="UseMaxAge" cacheControlMaxAge="365.00:00:00" />
    </staticContent>
  </system.webServer>
</configuration>
```

### 6.6 Habilitar Application Request Routing

1. En IIS Manager, selecciona el servidor (nombre del servidor en la parte superior)
2. Haz doble clic en **Application Request Routing Cache**
3. Haz clic en **Server Proxy Settings...** (panel derecho)
4. Marca **Enable proxy**
5. Haz clic en **Apply**

### 6.7 Configurar Request Filtering

1. Selecciona el sitio `CodificacionAutomatizada`
2. Haz doble clic en **Request Filtering**
3. Haz clic en **Edit Feature Settings...** (panel derecho)
4. Configura:
   - **Maximum allowed content length**: `52428800` (50 MB en bytes)
5. Haz clic en **OK**

---

## 7. Configuración de Servicios de Windows

### 7.1 Crear Servicio para el Backend

Abre PowerShell como Administrador y ejecuta:

```powershell
# Crear servicio
nssm install CodificacionBackend "C:\Apps\CodificacionAutomatizada\backend\venv\Scripts\python.exe" "-m uvicorn cod_backend.main:app --host 127.0.0.1 --port 8000 --workers 4 --log-level info --log-config C:\Apps\CodificacionAutomatizada\backend\logging_prod.json"

# Configurar directorio de trabajo
nssm set CodificacionBackend AppDirectory "C:\Apps\CodificacionAutomatizada\backend"

# Configurar usuario (recomendado: NETWORK SERVICE)
nssm set CodificacionBackend ObjectName "NT AUTHORITY\NETWORK SERVICE"

# Configurar reinicio automático
nssm set CodificacionBackend AppExit Default Restart
nssm set CodificacionBackend AppRestartDelay 5000

# Configurar logs del servicio
nssm set CodificacionBackend AppStdout "C:\Apps\CodificacionAutomatizada\logs\backend_service.log"
nssm set CodificacionBackend AppStderr "C:\Apps\CodificacionAutomatizada\logs\backend_service_errors.log"
```

### 7.2 Iniciar el Servicio

```powershell
# Iniciar servicio
Start-Service CodificacionBackend

# Verificar estado
Get-Service CodificacionBackend
# Debe mostrar: Running
```

### 7.3 Verificar que el Servicio Funciona

Abre un navegador y visita:

```
http://127.0.0.1:8000/api/v1/health
```

Deberías ver una respuesta JSON con el estado del backend.

---

## 8. Configuración de Variables de Entorno

### 8.1 Variables de Entorno del Sistema (Opcional)

Si prefieres usar variables de entorno del sistema en lugar del archivo `.env.backend`:

1. Presiona `Win + R`
2. Escribe `sysdm.cpl` y presiona Enter
3. Ve a la pestaña **Advanced**
4. Haz clic en **Environment Variables...**
5. En **System variables**, haz clic en **New...**
6. Agrega:
   - **Variable name**: `OPENAI_API_KEY`
   - **Variable value**: `tu_clave_api_aqui`
7. Repite para otras variables si es necesario
8. Haz clic en **OK** en todas las ventanas
9. **Reinicia el servicio** para que tome las nuevas variables:

```powershell
Restart-Service CodificacionBackend
```

---

## 9. Configuración de Logs

### 9.1 Verificar que los Logs se Están Generando

```powershell
# Ver logs del backend
Get-Content "C:\Apps\CodificacionAutomatizada\logs\backend.log" -Tail 20

# Ver logs de errores
Get-Content "C:\Apps\CodificacionAutomatizada\logs\backend_errors.log" -Tail 20

# Ver logs del servicio
Get-Content "C:\Apps\CodificacionAutomatizada\logs\backend_service.log" -Tail 20
```

### 9.2 Configurar Rotación de Logs (Opcional)

Puedes crear una tarea programada en Windows para limpiar logs antiguos:

1. Abre **Task Scheduler** (Programador de tareas)
2. Crea una nueva tarea básica
3. Configura para ejecutarse diariamente a las 2 AM
4. Acción: Ejecutar script PowerShell:

```powershell
$logPath = "C:\Apps\CodificacionAutomatizada\logs"
$maxAge = 30  # días

Get-ChildItem -Path $logPath -File | Where-Object {
    $_.LastWriteTime -lt (Get-Date).AddDays(-$maxAge)
} | Remove-Item -Force
```

---

## 10. Configuración de Seguridad

### 10.1 Configurar Firewall de Windows

Abre PowerShell como Administrador:

```powershell
# Permitir tráfico HTTP/HTTPS
New-NetFirewallRule -DisplayName "Codificacion HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "Codificacion HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# Bloquear acceso directo al backend (solo localhost)
New-NetFirewallRule -DisplayName "Bloquear Backend Externo" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Block
```

### 10.2 Verificar Permisos de Archivos

Asegúrate de que el usuario del servicio tenga permisos:

```powershell
# Otorgar permisos al directorio
$acl = Get-Acl "C:\Apps\CodificacionAutomatizada"
$permission = "NT AUTHORITY\NETWORK SERVICE", "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission
$acl.SetAccessRule($accessRule)
Set-Acl "C:\Apps\CodificacionAutomatizada" $acl
```

---

## 11. Configuración de HTTPS

### 11.1 Obtener Certificado SSL

**Opción A: Certificado Let's Encrypt (Gratis)**

1. Descarga win-acme desde: [win-acme.com](https://www.win-acme.com/)
2. Ejecuta `wacs.exe`
3. Sigue las instrucciones para obtener un certificado

**Opción B: Certificado Comercial**

1. Obtén un certificado SSL de un proveedor comercial
2. Instálalo usando el Administrador de Certificados de Windows
3. Configúralo en IIS

### 11.2 Configurar HTTPS en IIS

1. En IIS Manager, selecciona el sitio `CodificacionAutomatizada`
2. Haz clic en **Bindings...** (panel derecho)
3. Haz clic en **Add...**
4. Configura:
   - **Type**: `https`
   - **Port**: `443`
   - **SSL certificate**: Selecciona tu certificado
   - **Host name**: `tu-dominio.com`
5. Haz clic en **OK**

### 11.3 Redirigir HTTP a HTTPS

Agrega esta regla al `web.config` (antes de las otras reglas):

```xml
<rule name="Redirect to HTTPS" stopProcessing="true">
  <match url="(.*)" />
  <conditions>
    <add input="{HTTPS}" pattern="off" ignoreCase="true" />
  </conditions>
  <action type="Redirect" url="https://{HTTP_HOST}/{R:1}" redirectType="Permanent" />
</rule>
```

---

## 12. Verificación y Pruebas

### 12.1 Verificar que el Backend Está Corriendo

```powershell
# Verificar servicio
Get-Service CodificacionBackend

# Verificar que el puerto 8000 está escuchando
netstat -ano | findstr :8000

# Probar endpoint de health
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/health" -UseBasicParsing
```

### 12.2 Verificar que IIS Está Funcionando

1. Abre un navegador
2. Visita: `http://localhost` (o tu dominio)
3. Deberías ver la aplicación frontend

### 12.3 Verificar que el Proxy Funciona

1. Abre las herramientas de desarrollador del navegador (F12)
2. Ve a la pestaña **Network**
3. Intenta usar la aplicación
4. Verifica que las peticiones a `/api/*` se están redirigiendo correctamente

### 12.4 Probar la Codificación

1. Sube un archivo de respuestas
2. Inicia una codificación
3. Verifica que funciona correctamente
4. Revisa los logs si hay problemas

---

## 13. Comandos Útiles

### Gestión del Servicio Backend

```powershell
# Iniciar servicio
Start-Service CodificacionBackend

# Detener servicio
Stop-Service CodificacionBackend

# Reiniciar servicio
Restart-Service CodificacionBackend

# Ver estado
Get-Service CodificacionBackend

# Ver logs en tiempo real
Get-Content "C:\Apps\CodificacionAutomatizada\logs\backend.log" -Wait -Tail 20
```

### Gestión de IIS

```powershell
# Reiniciar IIS
iisreset

# Ver sitios
Get-WebSite

# Ver Application Pools
Get-WebAppPoolState -Name "CodificacionAutomatizadaAppPool"
```

### Verificación de Procesos

```powershell
# Ver procesos de Python
Get-Process python

# Ver puertos en uso
netstat -ano | findstr :8000
netstat -ano | findstr :80
netstat -ano | findstr :443
```

---

## 14. Troubleshooting

### 14.1 El Servicio No Inicia

1. Verifica los logs del servicio:
   ```powershell
   Get-Content "C:\Apps\CodificacionAutomatizada\logs\backend_service_errors.log" -Tail 50
   ```

2. Verifica que el entorno virtual existe:
   ```powershell
   Test-Path "C:\Apps\CodificacionAutomatizada\backend\venv\Scripts\python.exe"
   ```

3. Prueba ejecutar manualmente:
   ```powershell
   cd C:\Apps\CodificacionAutomatizada\backend
   .\venv\Scripts\Activate.ps1
   python -m uvicorn cod_backend.main:app --host 127.0.0.1 --port 8000
   ```

### 14.2 El Frontend No Carga

1. Verifica que el sitio está iniciado en IIS
2. Verifica que el Application Pool está corriendo
3. Revisa los logs de IIS en: `C:\inetpub\logs\LogFiles\W3SVC1\`
4. Verifica que `web.config` existe y está bien formado

### 14.3 El Proxy No Funciona

1. Verifica que ARR está habilitado (paso 6.6)
2. Verifica que URL Rewrite Module está instalado
3. Revisa el `web.config` para errores de sintaxis
4. Verifica que el backend está escuchando en `127.0.0.1:8000`

### 14.4 Errores de Permisos

1. Verifica que el usuario del servicio tiene permisos en el directorio
2. Verifica que IIS tiene permisos para leer el directorio del frontend
3. Revisa los logs de Windows Event Viewer para más detalles

---

## 15. Checklist de Despliegue

- [ ] Estructura de directorios creada
- [ ] Archivos del proyecto copiados
- [ ] Python 3.11+ instalado
- [ ] UV instalado
- [ ] Node.js 18+ LTS instalado
- [ ] IIS habilitado y reiniciado
- [ ] URL Rewrite Module instalado
- [ ] Application Request Routing instalado y habilitado
- [ ] NSSM instalado
- [ ] Entorno virtual del backend creado
- [ ] Dependencias del backend instaladas
- [ ] Archivo `.env.backend` configurado
- [ ] Archivo `logging_prod.json` creado
- [ ] Servicio de Windows creado y corriendo
- [ ] Dependencias del frontend instaladas
- [ ] Archivo `.env.production` configurado
- [ ] Frontend compilado (`npm run build`)
- [ ] Application Pool creado en IIS
- [ ] Sitio web creado en IIS
- [ ] Archivo `web.config` creado
- [ ] Firewall configurado
- [ ] Certificado SSL instalado (si aplica)
- [ ] HTTPS configurado (si aplica)
- [ ] Pruebas de funcionalidad completadas

---

## 16. Mantenimiento Regular

### Actualizar el Código

1. Detén el servicio:
   ```powershell
   Stop-Service CodificacionBackend
   ```

2. Copia los nuevos archivos

3. Si hay cambios en dependencias:
   ```powershell
   cd C:\Apps\CodificacionAutomatizada\backend
   .\venv\Scripts\Activate.ps1
   uv pip install -e .
   ```

4. Si hay cambios en el frontend:
   ```powershell
   cd C:\Apps\CodificacionAutomatizada\frontend
   npm ci --production
   npm run build
   ```

5. Reinicia el servicio:
   ```powershell
   Start-Service CodificacionBackend
   ```

### Limpiar Logs Antiguos

```powershell
# Eliminar logs más antiguos de 30 días
$logPath = "C:\Apps\CodificacionAutomatizada\logs"
Get-ChildItem -Path $logPath -File | Where-Object {
    $_.LastWriteTime -lt (Get-Date).AddDays(-30)
} | Remove-Item -Force
```

---

## Notas Finales

- **Seguridad**: Nunca expongas el backend directamente a Internet. Siempre usa IIS como reverse proxy.
- **Backups**: Realiza backups regulares de los directorios `result/` y `logs/`
- **Monitoreo**: Revisa los logs regularmente para detectar problemas temprano
- **Actualizaciones**: Mantén el sistema operativo y las dependencias actualizadas

Para más detalles sobre configuración avanzada, consulta `DEPLOYMENT_WINDOWS_SERVER.md`.

