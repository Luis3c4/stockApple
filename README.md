# 🍎 Apple Store Scraper

Scraper automatizado para verificar la disponibilidad de productos Apple en tiendas específicas usando Playwright.

![Python](https://img.shields.io/badge/python-3.14+-blue.svg)
![Playwright](https://img.shields.io/badge/playwright-1.57+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 📋 Características

- 🤖 **Scraping con Playwright** - Navegación completa con JavaScript
- 📸 **Screenshots automáticos** - Capturas en caso de error y durante el proceso
- 📊 **Logging detallado** - Sistema completo de logs con rotación diaria
- 🔧 **Configuración flexible** - Variables de entorno para fácil personalización
- 🎯 **Búsqueda específica** - Filtra por producto y estado/región
- 💾 **Export a JSON** - Guarda resultados en formato JSON

## 🚀 Instalación

### Prerrequisitos

- Python 3.14 o superior
- Conexión a internet

### Paso 1: Preparar el entorno

```bash
# Crear entorno virtual (recomendado)
python -m venv .venv

# Activar entorno virtual
# En Windows:
.venv\Scripts\activate

# En Linux/macOS:
source .venv/bin/activate
```

### Paso 2: Instalar dependencias

```bash
# Instalar paquetes Python
pip install -r requirements.txt

# Instalar navegador Chromium para Playwright
playwright install chromium
```

### Paso 3: Configurar variables

```bash
# Crear archivo de configuración
copy .env.example .env

# Editar .env con tus valores (opcional, tiene defaults)
```

## 📖 Uso

### Ejecutar scraper (modo invisible)

```bash
python main.py
```

### Ver el navegador durante scraping (recomendado para desarrollo)

```bash
python main.py --headless=false
```

### Guardar resultados en JSON

```bash
python main.py --save-json
```

### Probar conexión con Apple Store

```bash
python main.py --test
```

### Ver configuración actual

```bash
python main.py --show-config
```

## ⚙️ Configuración

Edita el archivo `.env` para personalizar el scraper:

```env
# URL de Apple Store
APPLE_STORE_URL=https://www.apple.com/shop/buy-iphone

# Modo headless (true = invisible, false = ver navegador)
PLAYWRIGHT_HEADLESS=false

# Screenshots automáticos en errores
SCREENSHOT_ON_ERROR=true

# Screenshots durante el proceso
SAVE_SCREENSHOTS=true

# Producto a buscar
TARGET_PRODUCT=iPhone 17

# Estado/región donde buscar
TARGET_STATE=Florida
```

### Configuraciones importantes

| Variable | Descripción | Default |
|----------|-------------|---------|
| `PLAYWRIGHT_HEADLESS` | Navegador invisible | `false` |
| `SCREENSHOT_ON_ERROR` | Capturas en errores | `true` |
| `SAVE_SCREENSHOTS` | Capturas del proceso | `true` |
| `TARGET_PRODUCT` | Producto a buscar | `iPhone 17` |
| `TARGET_STATE` | Estado/región | `Florida` |

## 📁 Estructura del Proyecto

```
apple-store-scraper/
├── main.py                      # 🎯 Punto de entrada
├── config.py                    # ⚙️ Configuración
├── requirements.txt             # 📦 Dependencias
├── .env                         # 🔐 Variables de entorno
├── .env.example                 # 📋 Plantilla de configuración
├── README.md                    # 📖 Esta documentación
│
├── services/                    # 🔧 Servicios
│   ├── __init__.py
│   └── apple_scraper.py        # 🕷️ Scraper de Apple Store
│
├── utils/                       # 🛠️ Utilidades
│   ├── __init__.py
│   └── logger.py               # 📊 Sistema de logging
│
├── logs/                        # 📝 Archivos de log
│   └── apple_bot_YYYYMMDD.log
│
└── screenshots/                 # 📸 Capturas de pantalla
    ├── initial_page.png
    └── error_*.png
```

## 🔧 Personalización del Scraper

### Actualizar selectores CSS

⚠️ **Los selectores CSS de Apple Store cambian frecuentemente**

Edita [services/apple_scraper.py](services/apple_scraper.py) en el método `_extract_availability_data()`:

```python
def _extract_availability_data(self, page: Page):
    # Actualiza estos selectores según la estructura real
    store_items = page.query_selector_all(
        '.tu-selector-css-actualizado'  # <- Modifica esto
    )
    # ... resto del código
```

### Proceso recomendado para actualizar selectores:

1. **Ejecuta con navegador visible:**
   ```bash
   python main.py --headless=false
   ```

2. **Inspecciona la página:**
   - Usa F12 para abrir DevTools
   - Inspecciona los elementos de las tiendas
   - Identifica los selectores CSS correctos

3. **Actualiza el código:**
   - Modifica `_extract_availability_data()` en `apple_scraper.py`
   - Usa los nuevos selectores

4. **Prueba:**
   ```bash
   python main.py --headless=false
   ```

## 📊 Resultados

### En consola

Los resultados se muestran automáticamente en la consola con formato:

```
📊 RESULTADOS DEL SCRAPING
======================================
📅 Timestamp: 2026-01-16 10:30:00
📱 Producto: iPhone 17

✅ DISPONIBLE en 2 tienda(s):
   1. Apple Aventura
      ℹ️  Available for pickup today
   2. Apple Brickell City Centre

❌ No disponible en 3 tienda(s):
   • Apple International Plaza
   • Apple The Falls
   • Apple Dadeland

📊 Total: 2 disponible(s) de 5 tienda(s)
```

### En archivo JSON

Con `--save-json`, genera archivo como:

```json
{
  "success": true,
  "timestamp": "2026-01-16T10:30:00",
  "product": "iPhone 17",
  "available_stores": [
    {
      "name": "Apple Aventura",
      "status": "available",
      "details": "Available for pickup today"
    }
  ],
  "unavailable_stores": [...]
}
```

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

### Buscar otros productos

```env
# En .env
TARGET_PRODUCT=MacBook Pro
TARGET_STATE=California
```

## 🚀 Próximos pasos

Una vez que el scraping funcione correctamente:

- [ ] Añadir bot de Telegram para notificaciones
- [ ] Implementar scheduler para ejecuciones automáticas
- [ ] Dashboard web para monitoreo
- [ ] Soporte para múltiples productos simultáneos
- [ ] Integración con Discord
- [ ] Soporte para otras tiendas (Best Buy, Amazon)

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

## ⚠️ Disclaimer

Este proyecto es para fines educativos y personales. No está afiliado con Apple Inc. El web scraping puede violar términos de servicio de algunos sitios. Usa bajo tu propia responsabilidad y asegúrate de cumplir con las leyes aplicables.

## 📞 Soporte

Si tienes problemas:

1. Revisa esta documentación
2. Ejecuta con `--headless=false` para ver el navegador
3. Revisa los logs en `logs/`
4. Revisa los screenshots en `screenshots/`
5. Verifica que los selectores CSS estén actualizados

---

**Creado para monitorear disponibilidad de productos Apple 🍎**

*Última actualización: Enero 2026*


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

### Iniciar bot (modo automático)

Ejecuta verificaciones automáticas según el horario configurado:

```bash
python main.py
```

El bot se mantendrá corriendo y ejecutará verificaciones en el horario programado.

### Verificación manual (una vez)

Ejecuta una verificación inmediata sin esperar al horario programado:

```bash
python main.py --check-now
```

### Probar conexión con Telegram

Envía un mensaje de prueba para verificar que la configuración es correcta:

```bash
python main.py --test-telegram
```

### Probar scraper de Apple

Verifica que Playwright puede acceder a Apple Store:

```bash
python main.py --test-scraper
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

## 🚀 Despliegue en Producción

### Opción 1: Servidor Linux (VPS)

```bash
# Instalar dependencias del sistema
sudo apt update
sudo apt install python3 python3-pip

# Clonar proyecto
git clone <tu-repo>
cd apple-stock-bot

# Instalar dependencias
pip3 install -r requirements.txt
playwright install chromium
playwright install-deps

# Configurar .env
nano .env

# Ejecutar con nohup
nohup python3 main.py > output.log 2>&1 &
```

### Opción 2: systemd service (Linux)

Crear `/etc/systemd/system/apple-bot.service`:

```ini
[Unit]
Description=Apple Stock Bot
After=network.target

[Service]
Type=simple
User=tu-usuario
WorkingDirectory=/ruta/a/apple-stock-bot
ExecStart=/ruta/a/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Activar:
```bash
sudo systemctl enable apple-bot
sudo systemctl start apple-bot
sudo systemctl status apple-bot
```

### Opción 3: Docker (próximamente)

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## ⚠️ Disclaimer

Este bot es para uso educacional y personal. No está afiliado con Apple Inc. Usa este software bajo tu propia responsabilidad. El scraping puede violar los términos de servicio de algunos sitios web. Asegúrate de cumplir con todas las leyes y términos aplicables.

## 📞 Soporte

Si tienes problemas:

1. Revisa esta documentación
2. Revisa los logs en `logs/`
3. Ejecuta los tests: `--test-telegram` y `--test-scraper`
4. Abre un issue en GitHub con detalles completos

## 🎯 Roadmap

- [ ] Soporte para múltiples productos simultáneos
- [ ] Dashboard web para monitoreo
- [ ] Integración con Discord además de Telegram
- [ ] Notificaciones basadas en umbrales de disponibilidad
- [ ] Soporte para más tiendas (Best Buy, Amazon, etc.)
- [ ] Docker container para despliegue fácil

---

**Creado con ❤️ para monitorear stock de Apple**

*Última actualización: Enero 2026*
