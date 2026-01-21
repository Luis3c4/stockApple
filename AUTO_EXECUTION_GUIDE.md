# 🤖 Guía de Ejecución Automática

## ⚙️ Configuración Previa (IMPORTANTE)

Antes de ejecutar automáticamente, **debes configurar tu `.env`** con estos valores:

```env
# MODO HEADLESS - Navegador invisible (OBLIGATORIO para automático)
PLAYWRIGHT_HEADLESS=true

# DEBUG - Sin pausas (OBLIGATORIO para automático)
PLAYWRIGHT_DEBUG=false

# TELEGRAM - Activado para recibir notificaciones
TELEGRAM_ENABLED=true

# SCREENSHOTS - Opcional (false ahorra espacio)
SAVE_SCREENSHOTS=false
```

### ✅ Verificar configuración actual
```powershell
python main.py --show-config
```

---

## 🎯 Opción 1: Script PowerShell de Loop Continuo

### Ejecutar cada X minutos indefinidamente

```powershell
# Ejecutar cada 15 minutos (por defecto)
.\run_scheduler.ps1

# Ejecutar cada 10 minutos
.\run_scheduler.ps1 -IntervalMinutes 10

# Ejecutar cada 5 minutos
.\run_scheduler.ps1 -IntervalMinutes 5
```

### Ejecutar un número limitado de veces

```powershell
# Cada 5 minutos, máximo 12 veces (1 hora total)
.\run_scheduler.ps1 -IntervalMinutes 5 -MaxRuns 12

# Cada 15 minutos, máximo 4 veces (1 hora total)
.\run_scheduler.ps1 -IntervalMinutes 15 -MaxRuns 4
```

### Detener el scheduler
- Presiona **Ctrl+C** en la ventana de PowerShell

### Ver logs del scheduler
```powershell
Get-Content logs\scheduler.log -Tail 50
```

---

## 📅 Opción 2: Programador de Tareas de Windows (Task Scheduler) ⭐ RECOMENDADO

Ideal para ejecuciones en segundo plano sin mantener una ventana abierta.

### ⚡ Configuración Automática (MÁS FÁCIL)

Ejecuta este comando para configurar automáticamente los horarios:

```powershell
.\setup_task_scheduler.ps1
```

**Esto creará una tarea con 5 ejecuciones diarias:**

| Hora  | Descripción |
|-------|-------------|
| 🌅 **06:00** | Primer chequeo (antes de apertura de tienda) |
| ☀️ **10:00** | Segundo chequeo |
| 🕐 **14:00** | Tercer chequeo |
| 🌆 **18:00** | Cuarto chequeo |
| 🌙 **20:00** | Último chequeo del día |

### 📋 Comandos útiles

```powershell
# Probar la tarea manualmente
Start-ScheduledTask -TaskName "AppleStoreScraper"

# Ver logs de las ejecuciones
Get-Content logs\task_scheduler.log -Tail 50

# Deshabilitar temporalmente
Disable-ScheduledTask -TaskName "AppleStoreScraper"

# Habilitar nuevamente
Enable-ScheduledTask -TaskName "AppleStoreScraper"

# Eliminar la tarea
.\setup_task_scheduler.ps1 -Remove

# Ver estado de la tarea
Get-ScheduledTask -TaskName "AppleStoreScraper"
```

### 🛠️ Configuración Manual (Opcional)

<details>
<summary>Click aquí para ver los pasos manuales</summary>

#### Paso 1: Abrir Programador de Tareas
1. Presiona `Win + R`
2. Escribe `taskschd.msc`
3. Presiona Enter

#### Paso 2: Crear Nueva Tarea
1. Click derecho en "Biblioteca del Programador de tareas"
2. Seleccionar "Crear tarea..."

#### Paso 3: Configurar General
- **Nombre**: AppleStoreScraper
- **Descripción**: Monitoreo automático de disponibilidad iPhone - 5 ejecuciones diarias
- Configurar para: Windows 10/11

#### Paso 4: Configurar Desencadenadores (5 triggers)
Crear 5 desencadenadores (uno para cada horario):

**Trigger 1 - 06:00:**
- **Iniciar la tarea**: Diariamente
- **Hora de inicio**: 06:00:00
- ✅ Habilitado

**Trigger 2 - 10:00:**
- **Iniciar la tarea**: Diariamente
- **Hora de inicio**: 10:00:00
- ✅ Habilitado

**Trigger 3 - 14:00:**
- **Iniciar la tarea**: Diariamente
- **Hora de inicio**: 14:00:00
- ✅ Habilitado

**Trigger 4 - 18:00:**
- **Iniciar la tarea**: Diariamente
- **Hora de inicio**: 18:00:00
- ✅ Habilitado

**Trigger 5 - 20:00:**
- **Iniciar la tarea**: Diariamente
- **Hora de inicio**: 20:00:00
- ✅ Habilitado

#### Paso 5: Configurar Acciones
- **Programa**: `powershell.exe`
- **Argumentos**: `-ExecutionPolicy Bypass -WindowStyle Hidden -File "C:\Users\eltio\Documents\APPLE\run_task.ps1"`
- **Iniciar en**: `C:\Users\eltio\Documents\APPLE`

#### Paso 6: Configurar Condiciones
- ❌ Desmarcar "Iniciar solo si el equipo está conectado a CA"
- ✅ Iniciar solo si hay conexión de red disponible

#### Paso 7: Configurar Configuración
- ✅ Permitir que la tarea se ejecute a petición
- ✅ Ejecutar la tarea lo antes posible después de perder una ejecución programada
- Si la tarea no finaliza: **Detener la tarea existente**
- Tiempo límite: 1 hora

#### Paso 8: Guardar y Probar
- Click en "Aceptar"
- Click derecho en la tarea → "Ejecutar"
- Verificar logs en `logs\task_scheduler.log`

</details>

---

## 📊 Monitoreo y Logs

### Ver logs en tiempo real (Scheduler)
```powershell
Get-Content logs\scheduler.log -Wait
```

### Ver logs de Task Scheduler
```powershell
Get-Content logs\task_scheduler.log -Wait
```

### Ver logs del scraper principal
```powershell
Get-Content logs\apple_scraper.log -Tail 100
```

### Ver todos los logs recientes
```powershell
Get-ChildItem logs\*.log | ForEach-Object { 
    Write-Host "`n=== $($_.Name) ===" -ForegroundColor Cyan
    Get-Content $_.FullName -Tail 20 
}
```

---

## 🔔 Notificaciones de Telegram

Si configuraste correctamente `TELEGRAM_ENABLED=true` y tus credenciales de Telegram:

✅ **Recibirás notificaciones automáticas cuando**:
- Hay cambios en disponibilidad
- Se encuentra stock disponible
- Hay errores durante el scraping

📱 **Múltiples chats**: Puedes enviar a varios chats separando IDs con comas:
```env
TELEGRAM_CHAT_ID=6238521803,1234567890,9876543210
```

---

## ⚡ Recomendaciones

### ✅ Horarios Configurados (5 ejecuciones diarias)

Los horarios están optimizados para capturar actualizaciones de inventario:

| Hora | Razón | Probabilidad de cambios |
|------|-------|------------------------|
| **06:00** | Actualización nocturna del inventario | 🟢 Alta |
| **10:00** | Después de apertura de tiendas | 🟡 Media |
| **14:00** | Media jornada, posibles reposiciones | 🟡 Media |
| **18:00** | Antes de cierre, ajustes finales | 🟡 Media |
| **20:00** | Post-cierre, inventario actualizado | 🟢 Alta |

**Ventajas de estos horarios:**
- ✅ No satura el servidor de Apple (5 consultas/día)
- ✅ Captura actualizaciones de madrugada
- ✅ Monitorea horarios comerciales
- ✅ Permite dormir sin preocupaciones
- ✅ Evita bloqueos por exceso de requests

### Para evitar ser bloqueado
- ✅ Horarios espaciados (mínimo 4 horas entre ejecuciones)
- ✅ Habilitar cache (`CACHE_ENABLED=true`)
- ✅ Usar headless mode (`PLAYWRIGHT_HEADLESS=true`)
- ✅ Respetar horarios comerciales

### Optimización de recursos
```env
# Deshabilitar screenshots para ahorrar espacio
SAVE_SCREENSHOTS=false

# Mantener solo screenshots de errores
SCREENSHOT_ON_ERROR=true

# Cache activado (reduce carga al servidor)
CACHE_ENABLED=true
```

---

## 🛑 Detener Ejecución Automática

### Opción 1 (Scheduler PowerShell)
- Presiona **Ctrl+C** en la terminal

### Opción 2 (Task Scheduler)
1. Abrir Programador de Tareas (`taskschd.msc`)
2. Buscar "Apple Store Scraper"
3. Click derecho → **Deshabilitar** (o Eliminar)

---

## ❓ Solución de Problemas

### El script no se ejecuta automáticamente
```powershell
# Verificar política de ejecución
Get-ExecutionPolicy

# Si está restringida, cambiar a RemoteSigned
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### No llegan notificaciones de Telegram
```powershell
# Probar envío manual
python -c "from services.telegram_bot import TelegramBot; bot = TelegramBot(); bot.send_message('Test')"
```

### Ver si el proceso está corriendo
```powershell
Get-Process python
```

### Error "No module named 'playwright'"
```powershell
# Reinstalar dependencias
pip install -r requirements.txt
playwright install chromium
```

---

## 📝 Ejemplo de Uso Completo

```powershell
# 1. Verificar configuración actual
python main.py --show-config

# 2. Asegurarse que .env está configurado correctamente
# PLAYWRIGHT_HEADLESS=true
# PLAYWRIGHT_DEBUG=false
# TELEGRAM_ENABLED=true

# 3. Probar una ejecución manual
python main.py

# 4. Si todo funciona, configurar Task Scheduler
.\setup_task_scheduler.ps1

# 5. Probar la tarea manualmente
Start-ScheduledTask -TaskName "AppleStoreScraper"

# 6. Monitorear logs
Get-Content logs\task_scheduler.log -Tail 50 -Wait
```

### 📊 Vista de un día típico

```
🌅 06:00 → Ejecución automática → Telegram: "Sin stock disponible"
☀️ 10:00 → Ejecución automática → Telegram: "Sin stock disponible"  
🕐 14:00 → Ejecución automática → Telegram: "Sin stock disponible"
🌆 18:00 → Ejecución automática → Telegram: "🎉 ¡STOCK DISPONIBLE! Miami Beach"
🌙 20:00 → Ejecución automática → Telegram: "Stock disponible en 2 tiendas"
```

---

## 🎯 Siguiente Paso

Una vez configurado, el bot:
1. ✅ Se ejecutará automáticamente cada X minutos
2. ✅ Te enviará notificaciones de Telegram cuando haya cambios
3. ✅ Guardará logs de cada ejecución
4. ✅ Funcionará en segundo plano sin ventanas visibles

**¿Todo listo?** Ejecuta el scheduler y deja que el bot trabaje por ti! 🚀
