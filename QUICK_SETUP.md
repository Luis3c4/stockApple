# 🚀 Inicio Rápido - Configuración Automática

## ✅ Prerrequisitos

Antes de configurar la ejecución automática, asegúrate de tener:

1. **Python y dependencias instaladas**
   ```powershell
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Archivo `.env` configurado** con valores correctos:
   ```env
   PLAYWRIGHT_HEADLESS=true
   PLAYWRIGHT_DEBUG=false
   TELEGRAM_ENABLED=true
   TELEGRAM_BOT_TOKEN=tu_token_aqui
   TELEGRAM_CHAT_ID=tu_chat_id_aqui
   ```

3. **Verificar que funciona manualmente**:
   ```powershell
   python main.py
   ```

---

## 🎯 Configuración en 3 Pasos

### 1️⃣ Ejecutar el configurador automático

```powershell
.\setup_task_scheduler.ps1
```

Esto creará una tarea programada con **5 ejecuciones diarias**:
- 🌅 06:00 - Antes de apertura
- ☀️ 10:00 - Media mañana
- 🕐 14:00 - Mediodía
- 🌆 18:00 - Tarde
- 🌙 20:00 - Noche

### 2️⃣ Probar la configuración

```powershell
# Ejecutar manualmente
Start-ScheduledTask -TaskName "AppleStoreScraper"

# Ver logs
Get-Content logs\task_scheduler.log -Tail 20
```

### 3️⃣ Verificar estado

```powershell
.\check_task_status.ps1
```

---

## 📊 Monitoreo

### Ver estado actual
```powershell
.\check_task_status.ps1
```

### Ver logs en tiempo real
```powershell
Get-Content logs\task_scheduler.log -Wait
```

### Ver todas las ejecuciones del día
```powershell
Get-Content logs\task_scheduler.log | Select-String "Ejecución #"
```

---

## 🛠️ Gestión

### Deshabilitar temporalmente
```powershell
Disable-ScheduledTask -TaskName "AppleStoreScraper"
```

### Habilitar nuevamente
```powershell
Enable-ScheduledTask -TaskName "AppleStoreScraper"
```

### Eliminar la tarea
```powershell
.\setup_task_scheduler.ps1 -Remove
```

### Modificar horarios
```powershell
# 1. Eliminar tarea actual
.\setup_task_scheduler.ps1 -Remove

# 2. Editar setup_task_scheduler.ps1 y cambiar las horas

# 3. Crear nuevamente
.\setup_task_scheduler.ps1
```

---

## 🔔 Notificaciones de Telegram

Si todo está configurado correctamente, recibirás mensajes automáticos:

✅ **Cuando hay cambios en disponibilidad**
✅ **Cuando se encuentra stock**
✅ **Si hay errores en el scraping**

Para enviar a múltiples chats:
```env
TELEGRAM_CHAT_ID=6238521803,1234567890,9876543210
```

---

## ❓ Solución de Problemas

### La tarea no se ejecuta

1. Verificar que existe:
   ```powershell
   Get-ScheduledTask -TaskName "AppleStoreScraper"
   ```

2. Revisar estado:
   ```powershell
   .\check_task_status.ps1
   ```

3. Ejecutar manualmente para ver errores:
   ```powershell
   .\run_task.ps1
   ```

### No llegan notificaciones de Telegram

```powershell
# Probar bot manualmente
python -c "from services.telegram_bot import TelegramBot; bot = TelegramBot(); bot.send_message('Prueba desde Task Scheduler')"
```

### Error de política de ejecución

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📖 Documentación Completa

Para más detalles, consulta:
- [AUTO_EXECUTION_GUIDE.md](AUTO_EXECUTION_GUIDE.md) - Guía completa
- [README.md](README.md) - Documentación general

---

## 🎉 ¡Listo!

Una vez configurado:
- ✅ El bot se ejecutará automáticamente 5 veces al día
- ✅ Recibirás notificaciones de Telegram
- ✅ Los logs se guardarán automáticamente
- ✅ Todo funcionará en segundo plano

**No necesitas hacer nada más. El bot trabaja por ti! 🤖**
