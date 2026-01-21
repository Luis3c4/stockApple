# 🔁 Flujo con Caché - Apple Stock Scraper

## Descripción

El scraper ahora implementa un **flujo inteligente con caché** que evita enviar alertas innecesarias cuando no hay cambios en la disponibilidad de stock.

## 🎯 Flujo Completo

### Cada Ejecución (ej. cada 2 horas)

```
1. 🌐 Abrir Apple Store con Playwright
2. 🤖 Interactuar como humano (clicks, formularios, etc.)
3. 📡 Apple hace el request a fulfillment-messages
4. 🎯 Interceptar fulfillment-messages
5. 📊 Extraer datos de stock
6. 🔍 Comparar con caché anterior
7. 🔔 SOLO si hay cambios → enviar alertas
8. 💾 Actualizar caché
9. ❌ Cerrar navegador
```

## 🚀 Uso

### Ejecución Normal con Caché

```bash
python main.py
```

El script automáticamente:
- ✅ Ejecuta el scraping completo
- ✅ Compara con caché anterior
- ✅ Solo envía alertas si detecta cambios
- ✅ Actualiza el caché
- ✅ Muestra resumen de cambios en consola

### Primera Ejecución

En la primera ejecución:
- Se crea el caché inicial
- Se considera como "cambio" (para registrar estado inicial)
- Se envía notificación con el estado actual
- Las siguientes ejecuciones compararán contra este estado

### Ejecuciones Siguientes

En ejecuciones posteriores:
- Se carga el caché anterior
- Se compara con datos nuevos
- **Solo se alerta si hay cambios**:
  - ✨ Nuevas tiendas con stock disponible
  - ⚠️ Tiendas que agotaron stock
- Se actualiza el caché con los datos más recientes

## 📦 Sistema de Caché

### Ubicación

Los archivos de caché se almacenan en:
```
cache/
└── availability_cache.json
```

### Estructura del Caché

```json
{
  "success": true,
  "timestamp": "2026-01-20T10:30:00",
  "product": "iPhone 17 Pro 256GB Silver Unlocked",
  "available_stores": [
    {
      "name": "Apple Aventura",
      "city": "Aventura",
      "state": "FL",
      "store_number": "R123",
      "status": "available",
      "pickup_quote": "Today at Apple Aventura",
      "available": true
    }
  ],
  "unavailable_stores": [...]
}
```

### Gestión del Caché

El sistema detecta automáticamente:
- **Nuevo stock**: Tiendas que antes no tenían y ahora sí
- **Stock agotado**: Tiendas que antes tenían y ahora no
- **Sin cambios**: Mismo estado que ejecución anterior

## 🔔 Sistema de Alertas

### Cuándo se Envía Alerta

Las alertas de Telegram **solo se envían cuando**:

1. **Primera ejecución** (estado inicial)
2. **Nuevo stock disponible** (tienda antes sin stock, ahora con stock)
3. **Stock agotado** (tienda antes con stock, ahora sin stock)

### Cuándo NO se Envía Alerta

No se envía alerta cuando:
- ❌ No hay cambios en disponibilidad
- ❌ Todas las tiendas mantienen su estado anterior
- ❌ Solo cambió el mensaje de pickup pero sigue disponible/no disponible

### Formato de Alertas

#### Alerta de Nuevo Stock
```
🎉 ¡NUEVO STOCK DISPONIBLE!
📱 iPhone 17 Pro 256GB Silver Unlocked

🕐 2026-01-20 10:30:00
📦 Última verificación: hace 2 horas

CAMBIOS DETECTADOS: 1 tienda(s) con nuevo stock

━━━━━━━━━━━━━━━━━
✨ NUEVO STOCK (1):

🎉 Apple Aventura
   📍 Aventura, FL
   ⏰ Today at Apple Aventura
```

#### Sin Cambios (NO se envía)
```
ℹ️ Sin cambios - 2 con stock, 15 sin stock
```

## 📊 Información en Consola

El sistema muestra información detallada en consola:

```
======================================================================
🔁 INICIANDO FLUJO CON CACHÉ
======================================================================
📦 Caché anterior: 2 horas de antigüedad
🕷️ PASO 1-5: Ejecutando scraping...
✅ Scraping completado - 2 tiendas con stock
🔍 PASO 6: Comparando con caché...
🔔 CAMBIOS DETECTADOS - Se debe enviar alerta
   CAMBIOS DETECTADOS: 1 tienda(s) con nuevo stock
💾 PASO 8: Actualizando caché...
✅ PASO 9: Navegador cerrado
======================================================================
🏁 FLUJO COMPLETADO - Alerta: SÍ
======================================================================

📊 RESULTADOS DEL SCRAPING
======================================================================
📅 Timestamp: 2026-01-20T10:30:00
📱 Producto: iPhone 17 Pro 256GB Silver Unlocked
📦 Caché anterior: 2 horas de antigüedad
🔔 Estado: CAMBIOS DETECTADOS
   CAMBIOS DETECTADOS: 1 tienda(s) con nuevo stock
   ✨ 1 tienda(s) con NUEVO stock

✨ NUEVO STOCK (1 tienda(s)):
   1. 🎉 Apple Aventura - Aventura, FL
      Today at Apple Aventura

✅ DISPONIBLE en 2 tienda(s) (total):
   1. Apple Aventura - Aventura, FL
   2. Apple Dadeland - Miami, FL
```

## ⚙️ Configuración

### Variables de Entorno

Agregar en `.env`:

```bash
# Cache Configuration
CACHE_DIR=cache
CACHE_ENABLED=true
```

### Desactivar Sistema de Caché

Si deseas volver al comportamiento anterior (siempre alertar):

```python
# En main.py, reemplazar:
result = scraper.check_availability_with_cache()

# Por:
result = scraper.check_availability()
```

## 🔄 Programación Automática

### Windows (PowerShell)

Ejecutar cada 2 horas:

```powershell
# Crear tarea programada
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\path\to\main.py"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 2)
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "AppleStockChecker"
```

### Linux/Mac (cron)

```bash
# Editar crontab
crontab -e

# Agregar línea para ejecutar cada 2 horas
0 */2 * * * cd /path/to/APPLE && python main.py
```

## 🧪 Testing

### Probar el Flujo

```bash
# Primera ejecución (crea caché)
python main.py

# Segunda ejecución (sin cambios, no alerta)
python main.py

# Simular cambio (borrar caché y ejecutar)
rm cache/availability_cache.json
python main.py
```

### Verificar Caché

```bash
# Ver contenido del caché
cat cache/availability_cache.json

# Ver edad del caché
python -c "from utils.cache_manager import CacheManager; cm = CacheManager(); print(cm.get_cache_age())"
```

## 📝 Logs

Los logs muestran claramente:
- ✅ Cuándo se carga el caché
- 🔍 Qué cambios se detectaron
- 💾 Cuándo se actualiza el caché
- 🔔 Si se enviará o no alerta

Ejemplo:
```
2026-01-20 10:30:00 - INFO - 📦 Cache Manager inicializado - Directorio: cache
2026-01-20 10:30:05 - INFO - ✅ Caché cargado - Última actualización: 2026-01-20T08:30:00
2026-01-20 10:30:45 - INFO - ✨ NUEVO STOCK: Apple Aventura (Aventura, FL)
2026-01-20 10:30:45 - INFO - 🔔 CAMBIOS DETECTADOS: 1 tienda(s) con nuevo stock
2026-01-20 10:30:45 - INFO - 💾 Caché actualizado - Timestamp: 2026-01-20T10:30:00
2026-01-20 10:30:46 - INFO - 📱 HAY CAMBIOS - Enviando notificación a Telegram...
```

## 🎯 Ventajas

✅ **Reduce ruido**: Solo alertas cuando hay cambios reales  
✅ **Ahorra recursos**: No envía mensajes innecesarios  
✅ **Historial**: Mantiene registro del último estado  
✅ **Transparente**: Logs claros de qué está pasando  
✅ **Configurable**: Fácil activar/desactivar  

## 🔧 Mantenimiento

### Limpiar Caché

```bash
# Borrar manualmente
rm cache/availability_cache.json

# O usar Python
python -c "from utils.cache_manager import CacheManager; CacheManager().clear_cache()"
```

### Forzar Alerta

Para forzar envío de alerta (testing):
```bash
# Borrar caché y ejecutar
rm cache/availability_cache.json && python main.py
```
