# 🍎 Apple Store Scraper

Bot automatizado para monitorear disponibilidad de productos Apple (color x capacidad) en tiendas específicas, con notificaciones Telegram.

![Python](https://img.shields.io/badge/python-3.14+-blue.svg)
![Playwright](https://img.shields.io/badge/playwright-1.57+-green.svg)

## 📋 Características

- 🤖 **Scraping inteligente** - Navegación con Playwright interceptando la API real de Apple (`fulfillment-messages`)
- 🎨 **Matriz color x capacidad** - Verifica todas las combinaciones configuradas
- 🔁 **Sistema de caché** - Compara con la última verificación y detecta cambios
- 📱 **Telegram** - Notificación en cada ejecución (con o sin cambios)
- 📊 **Logs detallados** - Tracking completo con rotación diaria
- 🧪 **Comandos de testing** incluidos (`--test`, `--test-telegram`, `--show-config`)

---

## 🚀 Instalación

### Prerrequisitos

- Python 3.14 o superior
- Cuenta de Telegram y bot creado

### 1️⃣ Crear entorno virtual e instalar dependencias

```bash
python -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate

pip install -r requirements.txt
playwright install chromium
```

### 2️⃣ Configurar variables de entorno

Copia `.env.example` a `.env` y completa los valores:

```env
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_DEBUG=false
SAVE_SCREENSHOTS=false
SCREENSHOT_ON_ERROR=true

TARGET_CAPACITIES=256gb,512gb
TARGET_COLORS=burgundy,glacier,silver,black

TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui
```

> ⚠️ La primera capacidad y el primer color deben coincidir con los que trae la URL hardcodeada en `services/apple_scraper.py` (`PRODUCT_URL`).

#### Obtener credenciales de Telegram

1. Busca **@BotFather** en Telegram, envía `/newbot` y sigue las instrucciones. Copia el token en `TELEGRAM_BOT_TOKEN`.
2. Busca **@userinfobot**, inicia con `/start` y copia tu Chat ID en `TELEGRAM_CHAT_ID` (acepta varios IDs separados por coma).

### 3️⃣ Probar manualmente

```bash
python main.py
```

Cada ejecución realiza una única verificación y termina (pensado para ser lanzado por un scheduler externo, ver systemd timer más abajo).

---

## 📖 Uso

```bash
python main.py                      # Ejecutar verificación completa
python main.py --headless=false     # Ver el navegador durante el scraping
python main.py --test               # Probar conexión con Apple Store y Telegram
python main.py --test-telegram      # Probar solo la conexión con Telegram
python main.py --show-config        # Mostrar configuración actual (sin datos sensibles)
python main.py --save-json          # Guardar resultados en archivo JSON
```

---

## 🔄 Sistema de Caché

**Flujo:**
1. 🌐 Scraping con Playwright
2. 📡 Intercepta la API de Apple (`fulfillment-messages`) para cada color y capacidad
3. 🔍 Compara con el caché anterior (`cache/availability_cache.json`)
4. 🔔 **Siempre notifica** (mensaje detallado si hay cambios, mensaje corto "aún sin stock" si no los hay)
5. 💾 Actualiza el caché

**Detecta:**
- ✨ Nuevas tiendas con stock
- 📉 Tiendas que agotaron stock
- ✅ Sin cambios (notifica con mensaje corto)

---

## ⚙️ Configuración (.env)

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram | *(requerido)* |
| `TELEGRAM_CHAT_ID` | ID del/los chat(s) donde enviar mensajes (separados por coma) | *(requerido)* |
| `TARGET_CAPACITIES` | Capacidades a verificar (separadas por coma) | `256gb,512gb` |
| `TARGET_COLORS` | Colores a verificar (separados por coma) | `burgundy,glacier,silver,black` |
| `PLAYWRIGHT_HEADLESS` | Ejecutar navegador invisible | `true` |
| `PLAYWRIGHT_DEBUG` | Pausar con el inspector de Playwright | `false` |
| `SCREENSHOT_ON_ERROR` | Guardar capturas en errores | `true` |
| `SAVE_SCREENSHOTS` | Guardar capturas en cada ejecución | `false` |

---

## 📁 Estructura del Proyecto

```
stockApple/
├── main.py                      # Punto de entrada principal
├── config.py                    # Configuración y variables de entorno
├── requirements.txt             # Dependencias Python
├── .env                         # Variables de entorno (crear desde .env.example)
├── .env.example                 # Plantilla de configuración
│
├── services/
│   ├── apple_scraper.py         # Scraping con Playwright
│   └── telegram_bot.py          # Notificaciones a Telegram
│
├── utils/
│   ├── logger.py                 # Sistema de logging
│   └── cache_manager.py          # Gestor de caché
│
├── cache/
│   └── availability_cache.json
│
├── logs/
│   └── apple_bot_YYYYMMDD.log
│
└── screenshots/                  # Capturas y dumps de debug por color/capacidad
```

---

## 🐛 Troubleshooting

### Error: Playwright no instalado

```bash
playwright install chromium
```

### No recibo notificaciones Telegram

- Verifica que `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` sean correctos (sin espacios al inicio/final)
- Inicia una conversación con tu bot (envíale `/start`)
- Ejecuta `python main.py --test-telegram` para probar

### El scraper no encuentra productos / selectores desactualizados

⚠️ **Los selectores CSS de Apple Store cambian con frecuencia.**

1. Ejecuta en modo visible: `python main.py --headless=false`
2. Observa qué elementos busca el navegador (herramientas de desarrollador, F12)
3. Revisa los screenshots/dumps en `screenshots/` para ver la respuesta real de la API
4. Actualiza los selectores en [services/apple_scraper.py](services/apple_scraper.py), método `_extract_availability_data()`

### Playwright falla en Windows

Si hay problemas, usa WSL (Windows Subsystem for Linux):

```bash
# En WSL Ubuntu
sudo apt update
sudo apt install python3-pip
pip3 install -r requirements.txt
playwright install-deps
playwright install chromium
```

### Configuración de Playwright en Ubuntu 26.04

```bash
# Actualizar playwright a la última versión (necesario para que reconozca Ubuntu 26.04)
pip install --upgrade playwright

# Instalar Chromium y dependencias del sistema
playwright install chromium
playwright install-deps
```

### Logs y debugging

- **Logs:** `logs/apple_bot_YYYYMMDD.log`
- **Screenshots/dumps:** `screenshots/`
- **Modo debug:** `PLAYWRIGHT_HEADLESS=false`

---

## ⏰ Automatización con systemd timer

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

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now stockapple.timer
```

---

## 📝 Notas Importantes

### 🤖 Anti-detección

El scraper incluye:
- User-agent realista
- Viewport y locale configurados
- Delays entre acciones
- Flags anti-detección de Playwright

### 📊 Rate limiting

Sé respetuoso con Apple Store:
- No ejecutes verificaciones demasiado frecuentes
- Apple puede bloquear IPs con tráfico excesivo
- Usa los horarios del systemd timer como referencia

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## ⚠️ Disclaimer

Este bot es para uso educacional y personal. No está afiliado con Apple Inc. Usa este software bajo tu propia responsabilidad. El scraping puede violar los términos de servicio de algunos sitios web. Asegúrate de cumplir con todas las leyes y términos aplicables.
