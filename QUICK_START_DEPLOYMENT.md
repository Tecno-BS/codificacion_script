# Guía Rápida de Despliegue - Windows Server

Esta es una versión resumida de la guía completa. Para detalles completos, consulta:
- **Despliegue Manual**: `DEPLOYMENT_MANUAL_WINDOWS_SERVER.md` (sin scripts)
- **Despliegue con Scripts**: `DEPLOYMENT_WINDOWS_SERVER.md` (con scripts automatizados)

## 🚀 Pasos Rápidos

### 1. Preparar el Servidor

```powershell
# Ejecutar como Administrador
cd C:\Apps\CodificacionAutomatizada\scripts\deployment
.\install-dependencies.ps1
```

**Reiniciar el servidor después de este paso.**

### 2. Copiar Archivos

```powershell
# Copiar backend a C:\Apps\CodificacionAutomatizada\backend
# Copiar frontend a C:\Apps\CodificacionAutomatizada\frontend
```

### 3. Configurar Backend

```powershell
cd C:\Apps\CodificacionAutomatizada\backend

# Crear entorno virtual e instalar dependencias
uv venv
.\venv\Scripts\Activate.ps1
uv pip install -e .

# Crear archivo .env.backend (copiar desde .env.backend.example)
# Editar y configurar OPENAI_API_KEY y otros valores

# Configurar servicio de Windows
cd ..\scripts\deployment
.\setup-backend-service.ps1
Start-Service CodificacionBackend
```

### 4. Configurar Frontend

```powershell
cd C:\Apps\CodificacionAutomatizada\frontend

# Instalar dependencias
npm ci --production

# Crear .env.production
@"
NEXT_PUBLIC_BACKEND_URL=https://tu-dominio.com/api
NODE_ENV=production
"@ | Out-File -FilePath .env.production -Encoding utf8

# Compilar
npm run build
```

### 5. Configurar IIS

```powershell
cd C:\Apps\CodificacionAutomatizada\scripts\deployment
.\setup-iis-site.ps1 -Domain "tu-dominio.com"
```

### 6. Verificar

```powershell
# Verificar servicio backend
Get-Service CodificacionBackend

# Verificar sitio IIS
Get-WebSite -Name CodificacionAutomatizada

# Probar backend
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/health"

# Probar frontend
Invoke-WebRequest -Uri "http://localhost"
```

## ✅ Checklist Mínimo

- [ ] Dependencias instaladas
- [ ] Servidor reiniciado
- [ ] Backend configurado y servicio corriendo
- [ ] Frontend compilado
- [ ] IIS configurado
- [ ] Variables de entorno configuradas
- [ ] Pruebas de funcionalidad completadas

## 🔧 Comandos Útiles

```powershell
# Iniciar/Detener/Reiniciar servicio
Start-Service CodificacionBackend
Stop-Service CodificacionBackend
Restart-Service CodificacionBackend

# Ver logs
Get-Content C:\Apps\CodificacionAutomatizada\logs\backend.log -Tail 50 -Wait

# Reiniciar IIS
iisreset
```

## 📚 Documentación Completa

Para información detallada sobre:
- Configuración de HTTPS
- Monitoreo y alertas
- Backup automático
- Troubleshooting avanzado

Consulta `DEPLOYMENT_WINDOWS_SERVER.md`

