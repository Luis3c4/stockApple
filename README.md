# 🍎 Apple Store Scraper

Bot automatizado para monitorear disponibilidad de productos Apple en tiendas específicas con notificaciones Telegram.

![Python](https://img.shields.io/badge/python-3.14+-blue.svg)
![Playwright](https://img.shields.io/badge/playwright-1.57+-green.svg)

## 📋 Características

- 🤖 **Scraping inteligente** - Navegación con Playwright interceptando API real
- 🔁 **Sistema de caché** - Solo alerta cuando hay cambios reales
- 📱 **Telegram** - Notificaciones automáticas de cambios de stock
- 📊 **Logs detallados** - Tracking completo con rotación diaria
- 🔧 **Timeout inteligente** - 5 minutos máximo por ejecución

---

## 🚀 Instalación Rápida

### 1️⃣ Instalar dependencias
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

### 2️⃣ Configurar Telegram
Edita `.env`:
```env
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_DEBUG=false
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui
TARGET_PRODUCT=iPhone 17 Pro Max
TARGET_STATE=Florida
```

### 3️⃣ Probar manualmente
```powershell
python main.py
```

---

## 🔄 Sistema de Caché

**Flujo inteligente:**
1. 🌐 Scraping con Playwright
2. 📡 Intercepta API de Apple (fulfillment-messages)
3. 🔍 Compara con caché anterior
4. 🔔 **Solo alerta si hay cambios**
5. 💾 Actualiza caché

**Detecta:**
- ✨ Nuevas tiendas con stock
- 📉 Tiendas que agotaron stock
- ✅ Sin cambios (no envía alerta)

**Ubicación:** `cache/availability_cache.json`

---

## ⚙️ Configuración (.env)

```env
# Producto a monitorear
TARGET_PRODUCT=iPhone 17 Pro Max
TARGET_CAPACITY=256GB
TARGET_COLOR=Silver

# Región
TARGET_STATE=Florida

# Playwright
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_DEBUG=false
SAVE_SCREENSHOTS=false

# Telegram
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=tu_token
TELEGRAM_CHAT_ID=tu_chat_id
```

---

## 🛠️ Comandos Útiles

### Desarrollo
```powershell
# Ver navegador (debugging)
python main.py --headless=false

# Probar conexión Apple Store
python main.py --test

# Ver configuración actual
python main.py --show-config
```

---

## 📁 Estructura del Proyecto

```
apple-store-scraper/
├── main.py                      # Punto de entrada
├── config.py                    # Configuración
├── requirements.txt             # Dependencias
├── .env                         # Variables de entorno
│
├── services/                    
│   ├── apple_scraper.py        # Scraper principal
│   └── telegram_bot.py         # Notificaciones
│
├── utils/                       
│   ├── logger.py               # Sistema de logs
│   └── cache_manager.py        # Gestor de caché
│
├── cache/                       
│   └── availability_cache.json
│
├── logs/                        
│   └── apple_bot_YYYYMMDD.log
│
└── screenshots/                 
```

---

## 🔧 Troubleshooting

### No recibo notificaciones Telegram
- Verifica `TELEGRAM_ENABLED=true`
- Confirma token y chat_id correctos
- Prueba manualmente: `python main.py`

### Selectores CSS desactualizados
- Apple cambia su sitio frecuentemente
- Ejecuta con `--headless=false` para ver qué busca
- Actualiza selectores en `services/apple_scraper.py`

---

## 📚 Recursos

- **Telegram Bot**: [@BotFather](https://t.me/botfather)
- **Playwright Docs**: [playwright.dev](https://playwright.dev)

---

## 🐛 Troubleshooting

### Error: Playwright no instalado

```bash
playwright install chromium
```

### El scraper no encuentra productos

1. **Verifica la URL:**
   - Asegúrate que `APPLE_STORE_URL` sea correcta

2. **Ejecuta en modo visible:**
   ```bash
   python main.py --headless=false
   ```

3. **Revisa los screenshots:**
   - Chequea `screenshots/` para ver qué está capturando

4. **Actualiza los selectores:**
   - Los selectores CSS en `apple_scraper.py` necesitan actualizarse
   - Apple cambia su estructura frecuentemente

### Playwright falla en Windows

Si hay problemas, usa WSL:

```bash
# En WSL Ubuntu
sudo apt update
sudo apt install python3-pip
pip3 install -r requirements.txt
playwright install-deps
playwright install chromium
```

### Logs y debugging

- **Logs:** `logs/apple_bot_YYYYMMDD.log`
- **Screenshots:** `screenshots/`
- **Modo debug:** `PLAYWRIGHT_HEADLESS=false`

## 💡 Tips

### Para desarrollo

```bash
# Ver navegador + guardar screenshots
python main.py --headless=false --save-json
```

### Para producción

```env
# En .env
PLAYWRIGHT_HEADLESS=true
SCREENSHOT_ON_ERROR=true
SAVE_SCREENSHOTS=false
```

## 📝 Notas Importantes

### ⚠️ Selectores CSS

**Los selectores cambian frecuentemente.** Este scraper incluye selectores genéricos que debes actualizar según la estructura actual de Apple Store.

### 🤖 Anti-detección

El scraper incluye:
- User-agent realista
- Viewport y locale configurados
- Delays entre acciones
- Flags anti-detección de Playwright

### 📊 Rate limiting

Sé respetuoso con Apple Store:
- No ejecutes demasiadas veces en corto tiempo
- Apple puede bloquear IPs con tráfico excesivo
- Usa delays apropiados

## 📄 Licencia

MIT License - Ver archivo `LICENSE`

## 📋 Características

- 🤖 **Scraping automático** con Playwright (navegación completa con JavaScript)
- 📱 **Notificaciones a Telegram** con mensajes formateados
- ⏰ **Verificación diaria programada** usando APScheduler
- 📸 **Screenshots automáticos** en caso de error para debugging
- 📊 **Sistema de logging** completo con rotación diaria
- 🔧 **Configuración flexible** mediante variables de entorno
- 🧪 **Comandos de testing** incluidos

## 🚀 Instalación

### Prerrequisitos

- Python 3.14 o superior
- Cuenta de Telegram y bot creado
- Conexión a internet

### Paso 1: Clonar o descargar el proyecto

```bash
cd apple-stock-bot
```

### Paso 2: Crear entorno virtual (recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate

# En Linux/macOS:
source venv/bin/activate
```

### Paso 3: Instalar dependencias

```bash
# Instalar paquetes Python
pip install -r requirements.txt

# Instalar navegador Chromium para Playwright
playwright install chromium
```

### Paso 4: Configurar variables de entorno

1. Copiar el archivo de ejemplo:
```bash
copy .env.example .env
```

2. Editar `.env` con tus valores:
```env
TELEGRAM_BOT_TOKEN=tu_token_real_aqui
TELEGRAM_CHAT_ID=tu_chat_id_real_aqui
```

### Paso 5: Obtener credenciales de Telegram

#### Crear Bot de Telegram:

1. Abre Telegram y busca **@BotFather**
2. Envía el comando `/newbot`
3. Sigue las instrucciones para crear tu bot
4. **Copia el token** que te da BotFather
5. Pégalo en `.env` como `TELEGRAM_BOT_TOKEN`

#### Obtener tu Chat ID:

1. Busca **@userinfobot** en Telegram
2. Inicia una conversación con `/start`
3. El bot te mostrará tu **Chat ID**
4. Cópialo y pégalo en `.env` como `TELEGRAM_CHAT_ID`

## 📖 Uso

### Ejecutar verificación

Ejecuta una única verificación de disponibilidad:

```bash
python main.py
```

Cada ejecución realiza una única verificación y termina (pensado para ser lanzado por un scheduler externo, ver systemd timer).

### Probar conexión con Telegram

Envía un mensaje de prueba para verificar que la configuración es correcta:

```bash
python main.py --test-telegram
```

### Probar conexión con Apple Store y Telegram

```bash
python main.py --test
```

### Mostrar configuración

Muestra la configuración actual sin datos sensibles:

```bash
python main.py --show-config
```

## ⚙️ Configuración

Todas las configuraciones se manejan en el archivo `.env`:

### Variables Principales

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram | *(requerido)* |
| `TELEGRAM_CHAT_ID` | ID del chat donde enviar mensajes | *(requerido)* |
| `CHECK_HOUR` | Hora de verificación diaria (0-23) | `10` |
| `CHECK_MINUTE` | Minuto de verificación (0-59) | `0` |
| `TIMEZONE` | Zona horaria para el scheduler | `America/New_York` |
| `TARGET_PRODUCT` | Producto a buscar | `iPhone 17` |
| `TARGET_STATE` | Estado donde buscar tiendas | `Florida` |
| `PLAYWRIGHT_HEADLESS` | Ejecutar navegador invisible | `true` |
| `SCREENSHOT_ON_ERROR` | Guardar capturas en errores | `true` |

### Ejemplo de configuración personalizada

```env
# Verificar a las 3:30 PM hora de California
CHECK_HOUR=15
CHECK_MINUTE=30
TIMEZONE=America/Los_Angeles

# Buscar iPhone 17 Pro Max
TARGET_PRODUCT=iPhone 17 Pro Max
TARGET_STATE=California

# Ver el navegador durante scraping (útil para debug)
PLAYWRIGHT_HEADLESS=false
```

## 📁 Estructura del Proyecto

```
apple-stock-bot/
├── main.py                      # 🎯 Punto de entrada principal
├── config.py                    # ⚙️ Configuración y variables de entorno
├── requirements.txt             # 📦 Dependencias Python
├── .env                         # 🔐 Variables de entorno (crear desde .env.example)
├── .env.example                 # 📋 Plantilla de configuración
├── .gitignore                   # 🚫 Archivos a ignorar en Git
├── README.md                    # 📖 Esta documentación
│
├── services/                    # 🔧 Servicios principales
│   ├── __init__.py
│   ├── apple_scraper.py        # 🕷️ Scraping con Playwright
│   └── telegram_notifier.py    # 📱 Notificaciones Telegram
│
├── utils/                       # 🛠️ Utilidades
│   ├── __init__.py
│   ├── logger.py               # 📊 Sistema de logging
│   └── scheduler.py            # ⏰ Programación de tareas
│
├── logs/                        # 📝 Archivos de log (generados)
│   └── apple_bot_YYYYMMDD.log
│
└── screenshots/                 # 📸 Capturas de pantalla (generadas)
    └── error_*.png
```

## 🐛 Troubleshooting

### Error: Playwright no instalado

```bash
playwright install chromium
```

### Error: Token de Telegram inválido

- Verifica que el token en `.env` sea correcto
- Asegúrate de que no haya espacios al inicio/final
- Verifica que usaste el token completo de @BotFather

### Error: No se reciben mensajes en Telegram

- Verifica que `TELEGRAM_CHAT_ID` sea correcto
- Inicia una conversación con tu bot (envíale `/start`)
- Ejecuta `python main.py --test-telegram` para probar

### El scraping no encuentra productos

⚠️ **Los selectores CSS de Apple Store cambian frecuentemente**

1. Ejecuta con `PLAYWRIGHT_HEADLESS=false` en `.env`:
   ```env
   PLAYWRIGHT_HEADLESS=false
   ```

2. Observa qué elementos busca el navegador

3. Revisa los screenshots en `screenshots/` para ver la página real

4. Actualiza los selectores CSS en [services/apple_scraper.py](services/apple_scraper.py) en el método `_extract_availability_data()`

5. Busca comentarios con `TODO` en el código que indican áreas que necesitan actualización

### Playwright falla en Windows

Si tienes problemas, considera usar WSL (Windows Subsystem for Linux):

```bash
# En WSL Ubuntu
sudo apt update
sudo apt install python3-pip
pip3 install -r requirements.txt
playwright install-deps
playwright install chromium
```

### Logs y debugging

- Los logs se guardan en `logs/apple_bot_YYYYMMDD.log`
- Los screenshots de error se guardan en `screenshots/`
- Usa `PLAYWRIGHT_HEADLESS=false` para ver el navegador en acción

## 🔧 Personalización Avanzada

### Cambiar selectores CSS

Los selectores CSS de Apple Store deben actualizarse según la estructura actual de la página. Edita [services/apple_scraper.py](services/apple_scraper.py):

```python
def _extract_availability_data(self, page: Page):
    # Actualiza estos selectores según la estructura real
    store_items = page.query_selector_all(
        '.tu-selector-aqui'  # <- Actualiza esto
    )
    # ... resto del código
```

### Añadir múltiples horarios de verificación

Edita [utils/scheduler.py](utils/scheduler.py) para añadir más jobs:

```python
# Verificación matutina
self.scheduler.add_job(
    self.run_check,
    trigger=CronTrigger(hour=9, minute=0),
    id='morning_check'
)

# Verificación vespertina
self.scheduler.add_job(
    self.run_check,
    trigger=CronTrigger(hour=18, minute=0),
    id='evening_check'
)
```

### Añadir más productos o estados

Modifica `.env` o adapta el código para buscar múltiples productos.

## 📝 Notas Importantes

### ⚠️ Actualización de Selectores

**Los selectores CSS de Apple Store cambian con frecuencia.** Este bot incluye selectores genéricos que probablemente necesitarás actualizar.

**Proceso recomendado:**

1. Ejecuta el bot con `PLAYWRIGHT_HEADLESS=false`
2. Observa la página que se abre
3. Usa las herramientas de desarrollador del navegador (F12)
4. Inspecciona los elementos de las tiendas
5. Actualiza los selectores en `apple_scraper.py`

### 🤖 Comportamiento similar a humano

El scraper incluye:
- User-agent realista
- Delays entre acciones
- Configuración de viewport y locale
- Flags anti-detección

### 📊 Rate limiting

Sé considerado con Apple Store:
- No ejecutes verificaciones muy frecuentes
- El bot está diseñado para 1 verificación diaria
- Apple puede bloquear IPs con tráfico excesivo

## Configuración de Playwright en Ubuntu 26.04

```bash
# Actualizar playwright a última versión (necesario para que reconozca Ubuntu 26.04)
pip install --upgrade playwright

# Instalar Chromium y dependencias del sistema
playwright install chromium
playwright install-deps
```

## Automatización con systemd timer

```bash
# Crear el servicio
sudo nano /etc/systemd/system/stockapple.service
```

```ini
[Unit]
Description=StockApple - chequeo de stock iPhone
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=jaxi
WorkingDirectory=/home/jaxi/Documentos/stockApple
ExecStart=/home/jaxi/Documentos/stockApple/.venv/bin/python main.py
StandardOutput=journal
StandardError=journal
```

```bash
# Crear el timer con los horarios de chequeo
sudo nano /etc/systemd/system/stockapple.timer
```

```ini
[Unit]
Description=Timer para StockApple

[Timer]
OnCalendar=*-*-* 06,10,14,18,20:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## ⚠️ Disclaimer

Este bot es para uso educacional y personal. No está afiliado con Apple Inc. Usa este software bajo tu propia responsabilidad. El scraping puede violar los términos de servicio de algunos sitios web. Asegúrate de cumplir con todas las leyes y términos aplicables.
---
