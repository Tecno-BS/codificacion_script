# Guía de Despliegue en Producción - Windows Server

Esta guía te llevará paso a paso para desplegar el proyecto de codificación automatizada en un servidor Windows Server usando las mejores prácticas de la industria.

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Preparación del Servidor](#preparación-del-servidor)
3. [Instalación de Dependencias](#instalación-de-dependencias)
4. [Configuración del Backend](#configuración-del-backend)
5. [Configuración del Frontend](#configuración-del-frontend)
6. [Configuración de IIS como Reverse Proxy](#configuración-de-iis-como-reverse-proxy)
7. [Configuración de Servicios de Windows](#configuración-de-servicios-de-windows)
8. [Configuración de Variables de Entorno](#configuración-de-variables-de-entorno)
9. [Configuración de Logs](#configuración-de-logs)
10. [Configuración de Seguridad](#configuración-de-seguridad)
11. [Configuración de HTTPS](#configuración-de-https)
12. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)
13. [Backup y Recuperación](#backup-y-recuperación)
14. [Troubleshooting](#troubleshooting)

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

Ejecuta en PowerShell como Administrador:

```powershell
# Crear directorio principal de la aplicación
New-Item -ItemType Directory -Path "C:\Apps\CodificacionAutomatizada" -Force
New-Item -ItemType Directory -Path "C:\Apps\CodificacionAutomatizada\backend" -Force
New-Item -ItemType Directory -Path "C:\Apps\CodificacionAutomatizada\frontend" -Force
New-Item -ItemType Directory -Path "C:\Apps\CodificacionAutomatizada\logs" -Force
New-Item -ItemType Directory -Path "C:\Apps\CodificacionAutomatizada\backups" -Force

# Crear directorios para datos de la aplicación
New-Item -ItemType Directory -Path "C:\Apps\CodificacionAutomatizada\backend\result" -Force
New-Item -ItemType Directory -Path "C:\Apps\CodificacionAutomatizada\backend\result\codificaciones" -Force
New-Item -ItemType Directory -Path "C:\Apps\CodificacionAutomatizada\backend\result\codigos_nuevos" -Force
New-Item -ItemType Directory -Path "C:\Apps\CodificacionAutomatizada\backend\temp" -Force
```

### 2.2 Configurar Permisos

```powershell
# Crear usuario de servicio (recomendado para seguridad)
$serviceUser = "NT AUTHORITY\NETWORK SERVICE"  # O crear un usuario específico

# Otorgar permisos al directorio de la aplicación
$acl = Get-Acl "C:\Apps\CodificacionAutomatizada"
$permission = $serviceUser, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission
$acl.SetAccessRule($accessRule)
Set-Acl "C:\Apps\CodificacionAutomatizada" $acl
```

---

## 3. Instalación de Dependencias

### 3.1 Instalar Python 3.11+

1. Descarga Python 3.11+ desde [python.org](https://www.python.org/downloads/)
2. Durante la instalación, marca:
   - ✅ "Add Python to PATH"
   - ✅ "Install for all users"
3. Verifica la instalación:

```powershell
python --version
# Debe mostrar: Python 3.11.x o superior
```

### 3.2 Instalar UV (Gestor de Paquetes Python)

```powershell
# Instalar uv usando PowerShell
irm https://astral.sh/uv/install.ps1 | iex

# Verificar instalación
uv --version
```

### 3.3 Instalar Node.js 18+ LTS

1. Descarga Node.js LTS desde [nodejs.org](https://nodejs.org/)
2. Instala con configuración por defecto
3. Verifica:

```powershell
node --version
npm --version
```

### 3.4 Instalar IIS y Características Necesarias

```powershell
# Habilitar IIS y características necesarias
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

# Instalar URL Rewrite Module (necesario para reverse proxy)
# Descargar desde: https://www.iis.net/downloads/microsoft/url-rewrite
# O usar Chocolatey:
choco install urlrewrite -y
```

### 3.5 Instalar Application Request Routing (ARR)

```powershell
# Descargar e instalar ARR desde:
# https://www.iis.net/downloads/microsoft/application-request-routing
# O usar Chocolatey:
choco install iis-arr -y
```

---

## 4. Configuración del Backend

### 4.1 Copiar Archivos del Backend

Copia todos los archivos del directorio `backend/` a `C:\Apps\CodificacionAutomatizada\backend\`

### 4.2 Crear Entorno Virtual y Instalar Dependencias

```powershell
cd C:\Apps\CodificacionAutomatizada\backend

# Crear entorno virtual usando uv
uv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar dependencias
uv pip install -e .
```

### 4.3 Crear Archivo de Configuración de Producción

Crea el archivo `C:\Apps\CodificacionAutomatizada\backend\.env.backend`:

```env
# OpenAI Configuration
OPENAI_API_KEY=tu_clave_api_aqui
OPENAI_MODEL=gpt-4o-mini

# Server Configuration
HOST=127.0.0.1
PORT=8000
WORKERS=4

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# Paths (ajustar según tu estructura)
PROJECT_ROOT=C:\Apps\CodificacionAutomatizada
```

### 4.4 Crear Script de Inicio del Backend

Crea `C:\Apps\CodificacionAutomatizada\backend\start_backend.bat`:

```batch
@echo off
cd /d "C:\Apps\CodificacionAutomatizada\backend"
call venv\Scripts\activate.bat
uvicorn cod_backend.main:app --host 127.0.0.1 --port 8000 --workers 4 --log-level info --log-config logging_prod.json
```

### 4.5 Crear Configuración de Logging

Crea `C:\Apps\CodificacionAutomatizada\backend\logging_prod.json`:

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

---

## 5. Configuración del Frontend

### 5.1 Copiar Archivos del Frontend

Copia todos los archivos del directorio `frontend/` a `C:\Apps\CodificacionAutomatizada\frontend\`

### 5.2 Instalar Dependencias y Compilar

```powershell
cd C:\Apps\CodificacionAutomatizada\frontend

# Instalar dependencias
npm ci --production

# Crear archivo .env.production
@"
NEXT_PUBLIC_BACKEND_URL=https://tu-dominio.com/api
NODE_ENV=production
"@ | Out-File -FilePath .env.production -Encoding utf8

# Compilar para producción
npm run build
```

### 5.3 Verificar que la Compilación fue Exitosa

```powershell
# Verificar que existe .next
Test-Path ".next"
# Debe retornar: True
```

---

## 6. Configuración de IIS como Reverse Proxy

### 6.1 Crear Sitio Web en IIS

```powershell
# Crear sitio web para el frontend
Import-Module WebAdministration
New-WebSite -Name "CodificacionAutomatizada" `
    -Port 80 `
    -HostHeader "tu-dominio.com" `
    -PhysicalPath "C:\Apps\CodificacionAutomatizada\frontend\.next\standalone" `
    -Force

# Si Next.js no genera standalone, usar:
# -PhysicalPath "C:\Apps\CodificacionAutomatizada\frontend"
```

### 6.2 Configurar Application Pool

```powershell
# Crear Application Pool
New-WebAppPool -Name "CodificacionAutomatizadaAppPool"

# Configurar Application Pool
Set-ItemProperty IIS:\AppPools\CodificacionAutomatizadaAppPool `
    -Name managedRuntimeVersion -Value ""

# Asignar al sitio
Set-ItemProperty IIS:\Sites\CodificacionAutomatizada `
    -Name applicationPool -Value "CodificacionAutomatizadaAppPool"
```

### 6.3 Configurar URL Rewrite para Reverse Proxy

Crea `C:\Apps\CodificacionAutomatizada\frontend\web.config`:

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

### 6.4 Habilitar ARR en IIS

```powershell
# Habilitar Application Request Routing
Import-Module WebAdministration
Set-WebConfigurationProperty -Filter "system.webServer/proxy" -Name enabled -Value $true -PSPath "IIS:\"
```

---

## 7. Configuración de Servicios de Windows

### 7.1 Instalar NSSM (Non-Sucking Service Manager)

```powershell
# Usar Chocolatey
choco install nssm -y

# O descargar manualmente desde: https://nssm.cc/download
```

### 7.2 Crear Servicio para el Backend

```powershell
# Crear servicio para el backend
nssm install CodificacionBackend `
    "C:\Apps\CodificacionAutomatizada\backend\venv\Scripts\python.exe" `
    "-m uvicorn cod_backend.main:app --host 127.0.0.1 --port 8000 --workers 4 --log-level info --log-config C:\Apps\CodificacionAutomatizada\backend\logging_prod.json"

# Configurar directorio de trabajo
nssm set CodificacionBackend AppDirectory "C:\Apps\CodificacionAutomatizada\backend"

# Configurar usuario (recomendado: NETWORK SERVICE o usuario específico)
nssm set CodificacionBackend ObjectName "NT AUTHORITY\NETWORK SERVICE"

# Configurar reinicio automático
nssm set CodificacionBackend AppExit Default Restart
nssm set CodificacionBackend AppRestartDelay 5000

# Configurar logs
nssm set CodificacionBackend AppStdout "C:\Apps\CodificacionAutomatizada\logs\backend_service.log"
nssm set CodificacionBackend AppStderr "C:\Apps\CodificacionAutomatizada\logs\backend_service_errors.log"

# Iniciar servicio
nssm start CodificacionBackend
```

### 7.3 Verificar que el Servicio Está Corriendo

```powershell
Get-Service CodificacionBackend
# Debe mostrar: Running
```

---

## 8. Configuración de Variables de Entorno

### 8.1 Variables de Entorno del Sistema (Opcional)

Si prefieres usar variables de entorno del sistema en lugar de archivos .env:

```powershell
# Configurar variables de entorno del sistema
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "tu_clave_api", "Machine")
[System.Environment]::SetEnvironmentVariable("OPENAI_MODEL", "gpt-4o-mini", "Machine")
[System.Environment]::SetEnvironmentVariable("ENVIRONMENT", "production", "Machine")

# Reiniciar el servicio para que tome las nuevas variables
Restart-Service CodificacionBackend
```

---

## 9. Configuración de Logs

### 9.1 Configurar Rotación de Logs

Crea un script de PowerShell para rotar logs: `C:\Apps\CodificacionAutomatizada\scripts\rotate_logs.ps1`

```powershell
# Script de rotación de logs
$logPath = "C:\Apps\CodificacionAutomatizada\logs"
$maxAge = 30  # días

Get-ChildItem -Path $logPath -File | Where-Object {
    $_.LastWriteTime -lt (Get-Date).AddDays(-$maxAge)
} | Remove-Item -Force

Write-Host "Logs antiguos eliminados"
```

### 9.2 Crear Tarea Programada para Rotación

```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File C:\Apps\CodificacionAutomatizada\scripts\rotate_logs.ps1"

$trigger = New-ScheduledTaskTrigger -Daily -At 2AM

Register-ScheduledTask -TaskName "RotarLogsCodificacion" `
    -Action $action `
    -Trigger $trigger `
    -Description "Rotar logs antiguos de la aplicación de codificación" `
    -RunLevel Highest
```

---

## 10. Configuración de Seguridad

### 10.1 Configurar Firewall de Windows

```powershell
# Permitir tráfico HTTP/HTTPS
New-NetFirewallRule -DisplayName "Codificacion HTTP" `
    -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow

New-NetFirewallRule -DisplayName "Codificacion HTTPS" `
    -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# Bloquear acceso directo al backend (solo localhost)
New-NetFirewallRule -DisplayName "Bloquear Backend Externo" `
    -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Block
```

### 10.2 Configurar Request Filtering en IIS

```powershell
# Limitar tamaño de archivos subidos (50 MB)
Set-WebConfigurationProperty -Filter "system.webServer/security/requestFiltering/requestLimits" `
    -Name maxAllowedContentLength -Value 52428800 -PSPath "IIS:\Sites\CodificacionAutomatizada"

# Bloquear extensiones peligrosas
Add-WebConfigurationProperty -Filter "system.webServer/security/requestFiltering/fileExtensions" `
    -Name "." -Value @{fileExtension=".exe"; allowed="false"} -PSPath "IIS:\Sites\CodificacionAutomatizada"
```

---

## 11. Configuración de HTTPS

### 11.1 Obtener Certificado SSL

**Opción A: Certificado Let's Encrypt (Gratis)**

```powershell
# Instalar win-acme
choco install win-acme -y

# Obtener certificado
wacs.exe --target iis --siteid 1 --validation filesystem --store iis
```

**Opción B: Certificado Comercial**

1. Obtén un certificado SSL de un proveedor comercial
2. Instálalo en el servidor usando el Administrador de Certificados
3. Configúralo en IIS

### 11.2 Configurar HTTPS en IIS

```powershell
# Crear binding HTTPS
New-WebBinding -Name "CodificacionAutomatizada" `
    -Protocol https `
    -Port 443 `
    -HostHeader "tu-dominio.com"

# Asignar certificado (ajustar thumbprint)
$cert = Get-ChildItem Cert:\LocalMachine\My | Where-Object {$_.Subject -like "*tu-dominio.com*"}
$binding = Get-WebBinding -Name "CodificacionAutomatizada" -Protocol https
$binding.AddSslCertificate($cert.Thumbprint, "My")
```

### 11.3 Redirigir HTTP a HTTPS

Agrega esta regla al `web.config`:

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

## 12. Monitoreo y Mantenimiento

### 12.1 Crear Script de Health Check

Crea `C:\Apps\CodificacionAutomatizada\scripts\health_check.ps1`:

```powershell
$backendUrl = "http://127.0.0.1:8000/api/v1/health"
$frontendUrl = "http://localhost"

try {
    $backendResponse = Invoke-WebRequest -Uri $backendUrl -UseBasicParsing -TimeoutSec 5
    if ($backendResponse.StatusCode -eq 200) {
        Write-Host "Backend: OK" -ForegroundColor Green
    } else {
        Write-Host "Backend: ERROR - Status $($backendResponse.StatusCode)" -ForegroundColor Red
        # Reiniciar servicio
        Restart-Service CodificacionBackend
    }
} catch {
    Write-Host "Backend: ERROR - $($_.Exception.Message)" -ForegroundColor Red
    Restart-Service CodificacionBackend
}

try {
    $frontendResponse = Invoke-WebRequest -Uri $frontendUrl -UseBasicParsing -TimeoutSec 5
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "Frontend: OK" -ForegroundColor Green
    } else {
        Write-Host "Frontend: ERROR - Status $($frontendResponse.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "Frontend: ERROR - $($_.Exception.Message)" -ForegroundColor Red
}
```

### 12.2 Configurar Tarea Programada para Health Check

```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File C:\Apps\CodificacionAutomatizada\scripts\health_check.ps1"

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365)

Register-ScheduledTask -TaskName "HealthCheckCodificacion" `
    -Action $action `
    -Trigger $trigger `
    -Description "Verificar salud de la aplicación cada 5 minutos" `
    -RunLevel Highest
```

---

## 13. Backup y Recuperación

### 13.1 Script de Backup

Crea `C:\Apps\CodificacionAutomatizada\scripts\backup.ps1`:

```powershell
$backupPath = "C:\Apps\CodificacionAutomatizada\backups"
$date = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = Join-Path $backupPath $date

New-Item -ItemType Directory -Path $backupDir -Force

# Backup de resultados
Copy-Item -Path "C:\Apps\CodificacionAutomatizada\backend\result" `
    -Destination (Join-Path $backupDir "result") `
    -Recurse -Force

# Backup de configuración
Copy-Item -Path "C:\Apps\CodificacionAutomatizada\backend\.env.backend" `
    -Destination (Join-Path $backupDir "env.backend") `
    -Force

# Backup de logs (últimos 7 días)
$logPath = "C:\Apps\CodificacionAutomatizada\logs"
Get-ChildItem -Path $logPath -File | Where-Object {
    $_.LastWriteTime -gt (Get-Date).AddDays(-7)
} | Copy-Item -Destination (Join-Path $backupDir "logs") -Force

# Eliminar backups antiguos (más de 30 días)
Get-ChildItem -Path $backupPath -Directory | Where-Object {
    $_.CreationTime -lt (Get-Date).AddDays(-30)
} | Remove-Item -Recurse -Force

Write-Host "Backup completado: $backupDir"
```

### 13.2 Configurar Backup Automático

```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File C:\Apps\CodificacionAutomatizada\scripts\backup.ps1"

$trigger = New-ScheduledTaskTrigger -Daily -At 3AM

Register-ScheduledTask -TaskName "BackupCodificacion" `
    -Action $action `
    -Trigger $trigger `
    -Description "Backup diario de la aplicación" `
    -RunLevel Highest
```

---

## 14. Troubleshooting

### 14.1 Verificar Logs

```powershell
# Ver logs del backend
Get-Content "C:\Apps\CodificacionAutomatizada\logs\backend.log" -Tail 50

# Ver logs de errores
Get-Content "C:\Apps\CodificacionAutomatizada\logs\backend_errors.log" -Tail 50

# Ver logs del servicio
Get-Content "C:\Apps\CodificacionAutomatizada\logs\backend_service.log" -Tail 50
```

### 14.2 Verificar Estado de Servicios

```powershell
# Estado del servicio backend
Get-Service CodificacionBackend

# Verificar que el puerto 8000 está escuchando
netstat -ano | findstr :8000

# Verificar procesos de Python
Get-Process python
```

### 14.3 Reiniciar Servicios

```powershell
# Reiniciar backend
Restart-Service CodificacionBackend

# Reiniciar IIS
iisreset
```

### 14.4 Verificar Configuración de IIS

```powershell
# Ver configuración del sitio
Get-WebSite -Name "CodificacionAutomatizada"

# Ver Application Pool
Get-WebAppPoolState -Name "CodificacionAutomatizadaAppPool"

# Ver logs de IIS
Get-Content "C:\inetpub\logs\LogFiles\W3SVC1\*.log" -Tail 50
```

---

## 15. Checklist de Despliegue

- [ ] Servidor Windows Server configurado
- [ ] Python 3.11+ instalado
- [ ] Node.js 18+ LTS instalado
- [ ] IIS instalado y configurado
- [ ] URL Rewrite Module instalado
- [ ] Application Request Routing instalado y habilitado
- [ ] Archivos del backend copiados
- [ ] Entorno virtual creado y dependencias instaladas
- [ ] Archivo .env.backend configurado
- [ ] Servicio de Windows creado para el backend
- [ ] Archivos del frontend copiados
- [ ] Frontend compilado (npm run build)
- [ ] Sitio web creado en IIS
- [ ] web.config configurado correctamente
- [ ] Certificado SSL instalado (si aplica)
- [ ] Firewall configurado
- [ ] Logs configurados
- [ ] Backup automático configurado
- [ ] Health check configurado
- [ ] Pruebas de funcionalidad completadas

---

## 16. Comandos Útiles

```powershell
# Iniciar servicio
Start-Service CodificacionBackend

# Detener servicio
Stop-Service CodificacionBackend

# Reiniciar servicio
Restart-Service CodificacionBackend

# Ver estado del servicio
Get-Service CodificacionBackend

# Ver logs en tiempo real
Get-Content "C:\Apps\CodificacionAutomatizada\logs\backend.log" -Wait -Tail 20

# Reiniciar IIS
iisreset

# Ver procesos de Python
Get-Process python

# Ver puertos en uso
netstat -ano | findstr :8000
netstat -ano | findstr :80
netstat -ano | findstr :443
```

---

## Notas Finales

- **Seguridad**: Nunca expongas el backend directamente a Internet. Siempre usa IIS como reverse proxy.
- **Monitoreo**: Configura alertas para monitorear el estado de la aplicación.
- **Backups**: Realiza backups regulares y prueba la restauración periódicamente.
- **Actualizaciones**: Mantén el sistema operativo y las dependencias actualizadas.
- **Logs**: Revisa los logs regularmente para detectar problemas temprano.

Para soporte adicional, consulta los logs en `C:\Apps\CodificacionAutomatizada\logs\`.

