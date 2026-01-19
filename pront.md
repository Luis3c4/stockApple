Necesito crear DESDE CERO un proyecto Python para un bot de Telegram que verifique automáticamente la disponibilidad de productos Apple usando web scraping con Playwright.

=== OBJETIVO DEL PROYECTO ===
Bot automatizado que:
1. Hace scraping de Apple Store USA cada día
2. Busca iPhone 17 (última generación 2026) en tiendas de Florida
3. Envía notificación diaria a Telegram con disponibilidad
4. Se ejecuta automáticamente 1 vez al día

=== PUNTO DE PARTIDA ===
- Tengo: Python 3.14+ instalado
- NO tengo: Ningún archivo, ninguna librería instalada
- Sistema operativo: Windows (tengo wsl en caso alguna libreria lo necesite)

=== ESTRUCTURA COMPLETA DEL PROYECTO ===

Crear esta estructura de carpetas y archivos:

apple-stock-bot/
├── .env                          # Variables de entorno (NO committer)
├── .env.example                  # Ejemplo de variables
├── .gitignore                    # Archivos a ignorar en Git
├── requirements.txt              # Dependencias Python
├── README.md                     # Documentación del proyecto
├── main.py                       # Punto de entrada principal
├── config.py                     # Configuración y variables de entorno
├── services/
│   ├── __init__.py
│   ├── apple_scraper.py         # Scraping con Playwright
│   └── telegram_notifier.py     # Envío de mensajes Telegram
├── utils/
│   ├── __init__.py
│   ├── scheduler.py             # Programación de tareas
│   └── logger.py                # Sistema de logs
├── screenshots/                  # Carpeta para capturas de error
└── logs/                        # Carpeta para archivos de log

=== ARCHIVO 1: requirements.txt ===

playwright==1.41.0
python-telegram-bot==20.7
apscheduler==3.10.4
python-dotenv==1.0.0
pytz==2024.1

Comentar cada librería:
# playwright - Navegador headless para scraping
# python-telegram-bot - API de Telegram
# apscheduler - Programación de tareas automáticas
# python-dotenv - Manejo de variables de entorno
# pytz - Zonas horarias


=== ARCHIVO 2: .env.example ===

Crear plantilla con:

# Telegram Configuration
TELEGRAM_BOT_TOKEN=tu_bot_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui

# Scraping Configuration
APPLE_STORE_URL=https://www.apple.com/shop/buy-iphone
PLAYWRIGHT_HEADLESS=true
SCREENSHOT_ON_ERROR=true

# Scheduling
CHECK_HOUR=10
CHECK_MINUTE=0
TIMEZONE=America/New_York

# Target Configuration
TARGET_PRODUCT=iPhone 17
TARGET_STATE=Florida


=== ARCHIVO 3: .gitignore ===

Crear con:

# Environment
.env
venv/
env/
*.pyc
__pycache__/

# Playwright
.playwright/

# Logs and Screenshots
logs/*.log
screenshots/*.png

# IDE
.vscode/
.idea/
*.swp


=== ARCHIVO 4: config.py ===

Crear clase de configuración usando python-dotenv:

from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # Scraping
    APPLE_STORE_URL = os.getenv('APPLE_STORE_URL', 'https://www.apple.com/shop/buy-iphone')
    PLAYWRIGHT_HEADLESS = os.getenv('PLAYWRIGHT_HEADLESS', 'true').lower() == 'true'
    SCREENSHOT_ON_ERROR = os.getenv('SCREENSHOT_ON_ERROR', 'true').lower() == 'true'
    
    # Scheduling
    CHECK_HOUR = int(os.getenv('CHECK_HOUR', 10))
    CHECK_MINUTE = int(os.getenv('CHECK_MINUTE', 0))
    TIMEZONE = os.getenv('TIMEZONE', 'America/New_York')
    
    # Target
    TARGET_PRODUCT = os.getenv('TARGET_PRODUCT', 'iPhone 17')
    TARGET_STATE = os.getenv('TARGET_STATE', 'Florida')
    
    @staticmethod
    def validate():
        """Valida que las configuraciones críticas estén presentes"""
        if not Config.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN no configurado")
        if not Config.TELEGRAM_CHAT_ID:
            raise ValueError("TELEGRAM_CHAT_ID no configurado")


=== ARCHIVO 5: utils/logger.py ===

Crear sistema de logging:

import logging
import os
from datetime import datetime

def setup_logger():
    """Configura el sistema de logging"""
    
    # Crear carpeta de logs si no existe
    os.makedirs('logs', exist_ok=True)
    
    # Formato del log
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler
            logging.FileHandler(
                f'logs/apple_bot_{datetime.now().strftime("%Y%m%d")}.log'
            )
        ]
    )
    
    return logging.getLogger('AppleStockBot')


=== ARCHIVO 6: services/apple_scraper.py ===

Crear clase completa con Playwright:

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import logging
from datetime import datetime
import os
from config import Config

logger = logging.getLogger('AppleStockBot')

class AppleScraper:
    """Scraper para Apple Store usando Playwright"""
    
    def __init__(self):
        self.config = Config
        self.screenshot_dir = 'screenshots'
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def check_availability(self):
        """
        Verifica disponibilidad de productos en Apple Store
        
        Returns:
            dict: {
                'success': bool,
                'timestamp': str,
                'product': str,
                'available_stores': list,
                'unavailable_stores': list,
                'error': str (opcional)
            }
        """
        logger.info(f"Iniciando scraping de {self.config.TARGET_PRODUCT}")
        
        with sync_playwright() as p:
            try:
                # Lanzar navegador
                browser = p.chromium.launch(
                    headless=self.config.PLAYWRIGHT_HEADLESS
                )
                
                # Crear contexto con user agent realista
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )
                
                page = context.new_page()
                
                # Navegar a Apple Store
                logger.info(f"Navegando a {self.config.APPLE_STORE_URL}")
                page.goto(self.config.APPLE_STORE_URL, wait_until='networkidle')
                
                # Esperar que cargue la página
                page.wait_for_timeout(3000)
                
                # Aquí implementar la lógica específica de scraping
                # Los selectores deben ser ajustados según la estructura actual de Apple
                
                # Ejemplo de flujo:
                # 1. Buscar el producto (iPhone 17)
                # 2. Hacer clic en "Check availability"
                # 3. Ingresar ZIP code de Florida o seleccionar tiendas
                # 4. Extraer información de disponibilidad
                
                result = self._extract_availability_data(page)
                
                browser.close()
                
                return {
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'product': self.config.TARGET_PRODUCT,
                    **result
                }
                
            except PlaywrightTimeout as e:
                logger.error(f"Timeout durante scraping: {e}")
                self._save_error_screenshot(page, 'timeout')
                return self._error_result(f"Timeout: {str(e)}")
                
            except Exception as e:
                logger.error(f"Error durante scraping: {e}")
                if 'page' in locals():
                    self._save_error_screenshot(page, 'error')
                return self._error_result(str(e))
    
    def _extract_availability_data(self, page):
        """
        Extrae datos de disponibilidad de la página
        
        NOTA IMPORTANTE: Los selectores CSS deben ser actualizados
        según la estructura real de Apple Store en el momento de uso.
        """
        
        available_stores = []
        unavailable_stores = []
        
        # TODO: Implementar selectores CSS reales
        # Ejemplo genérico:
        
        try:
            # Esperar elementos de tiendas
            page.wait_for_selector('.store-list', timeout=10000)
            
            # Extraer tiendas (ajustar selectores)
            stores = page.query_selector_all('.store-item')
            
            for store in stores:
                store_name = store.query_selector('.store-name').inner_text()
                availability = store.query_selector('.availability-status')
                
                if availability and 'available' in availability.inner_text().lower():
                    available_stores.append({
                        'name': store_name,
                        'status': 'available'
                    })
                else:
                    unavailable_stores.append({
                        'name': store_name,
                        'status': 'unavailable'
                    })
        
        except Exception as e:
            logger.warning(f"Error extrayendo datos: {e}")
        
        return {
            'available_stores': available_stores,
            'unavailable_stores': unavailable_stores
        }
    
    def _save_error_screenshot(self, page, error_type):
        """Guarda screenshot cuando hay error"""
        if self.config.SCREENSHOT_ON_ERROR:
            filename = f"{self.screenshot_dir}/error_{error_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            try:
                page.screenshot(path=filename)
                logger.info(f"Screenshot guardado: {filename}")
            except Exception as e:
                logger.error(f"No se pudo guardar screenshot: {e}")
    
    def _error_result(self, error_message):
        """Retorna resultado de error estandarizado"""
        return {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'product': self.config.TARGET_PRODUCT,
            'error': error_message,
            'available_stores': [],
            'unavailable_stores': []
        }


=== ARCHIVO 7: services/telegram_notifier.py ===

Crear servicio de Telegram:

from telegram import Bot
from telegram.error import TelegramError
import logging
from config import Config

logger = logging.getLogger('AppleStockBot')

class TelegramNotifier:
    """Servicio para enviar notificaciones a Telegram"""
    
    def __init__(self):
        self.bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        self.chat_id = Config.TELEGRAM_CHAT_ID
    
    def send_availability_report(self, data):
        """
        Envía reporte de disponibilidad formateado
        
        Args:
            data: dict con información de disponibilidad
        """
        message = self._format_message(data)
        
        try:
            self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            logger.info("Notificación enviada exitosamente a Telegram")
            return True
            
        except TelegramError as e:
            logger.error(f"Error enviando mensaje a Telegram: {e}")
            return False
    
    def _format_message(self, data):
        """Formatea el mensaje para Telegram"""
        
        if not data.get('success'):
            return f"""
🚨 *Error en Verificación*

⏰ {data.get('timestamp', 'N/A')}
❌ Error: {data.get('error', 'Desconocido')}

El bot intentará nuevamente en la próxima ejecución programada.
"""
        
        message_parts = [
            "🍎 *Reporte de Stock - Apple Store*",
            f"📅 {data.get('timestamp', 'N/A')}",
            f"📱 Producto: *{data.get('product', 'N/A')}*",
            ""
        ]
        
        available = data.get('available_stores', [])
        unavailable = data.get('unavailable_stores', [])
        
        if available:
            message_parts.append("✅ *DISPONIBLE en:*")
            for store in available:
                message_parts.append(f"   📍 {store.get('name', 'Unknown')}")
            message_parts.append("")
        
        if unavailable:
            message_parts.append("❌ *No disponible en:*")
            for store in unavailable:
                message_parts.append(f"   📍 {store.get('name', 'Unknown')}")
        
        if not available and not unavailable:
            message_parts.append("⚠️ No se encontraron tiendas")
        
        return "\n".join(message_parts)


=== ARCHIVO 8: utils/scheduler.py ===

Crear scheduler con APScheduler:

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import logging
from config import Config
from services.apple_scraper import AppleScraper
from services.telegram_notifier import TelegramNotifier

logger = logging.getLogger('AppleStockBot')

class AppleStockScheduler:
    """Programador de verificaciones automáticas"""
    
    def __init__(self):
        self.scheduler = BlockingScheduler(timezone=pytz.timezone(Config.TIMEZONE))
        self.scraper = AppleScraper()
        self.notifier = TelegramNotifier()
    
    def run_check(self):
        """Ejecuta una verificación completa"""
        logger.info("="*60)
        logger.info("Iniciando verificación programada")
        logger.info("="*60)
        
        try:
            # Hacer scraping
            result = self.scraper.check_availability()
            
            # Enviar notificación
            self.notifier.send_availability_report(result)
            
            logger.info("Verificación completada exitosamente")
            
        except Exception as e:
            logger.error(f"Error en verificación: {e}")
            # Intentar notificar el error
            try:
                self.notifier.send_availability_report({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
            except:
                pass
    
    def start(self):
        """Inicia el scheduler"""
        logger.info(f"Iniciando scheduler - Verificación diaria a las {Config.CHECK_HOUR}:{Config.CHECK_MINUTE:02d}")
        
        # Programar tarea diaria
        self.scheduler.add_job(
            self.run_check,
            trigger=CronTrigger(
                hour=Config.CHECK_HOUR,
                minute=Config.CHECK_MINUTE,
                timezone=pytz.timezone(Config.TIMEZONE)
            ),
            id='daily_check',
            name='Verificación diaria de stock Apple'
        )
        
        logger.info("Scheduler configurado. Esperando próxima ejecución...")
        logger.info(f"Próxima ejecución: {self.scheduler.get_jobs()[0].next_run_time}")
        
        # Iniciar scheduler (bloquea el programa)
        self.scheduler.start()


=== ARCHIVO 9: main.py ===

Crear punto de entrada principal:

#!/usr/bin/env python3
"""
Apple Stock Bot - Bot de Telegram para verificar disponibilidad de productos Apple

Uso:
    python main.py                    # Iniciar bot con scheduler
    python main.py --check-now        # Ejecutar verificación inmediata
    python main.py --test-telegram    # Probar notificación Telegram
"""

import sys
import argparse
from datetime import datetime

from config import Config
from utils.logger import setup_logger
from utils.scheduler import AppleStockScheduler
from services.apple_scraper import AppleScraper
from services.telegram_notifier import TelegramNotifier

logger = setup_logger()

def check_now():
    """Ejecuta una verificación inmediata (sin scheduler)"""
    logger.info("Ejecutando verificación manual...")
    
    scraper = AppleScraper()
    notifier = TelegramNotifier()
    
    result = scraper.check_availability()
    notifier.send_availability_report(result)
    
    logger.info("Verificación manual completada")

def test_telegram():
    """Prueba la conexión con Telegram"""
    logger.info("Probando conexión con Telegram...")
    
    notifier = TelegramNotifier()
    
    test_data = {
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'product': 'iPhone 17 Pro (Test)',
        'available_stores': [
            {'name': 'Apple Aventura (Test)'}
        ],
        'unavailable_stores': []
    }
    
    success = notifier.send_availability_report(test_data)
    
    if success:
        logger.info("✅ Test de Telegram exitoso")
    else:
        logger.error("❌ Test de Telegram falló")

def start_bot():
    """Inicia el bot con scheduler automático"""
    logger.info("="*60)
    logger.info("🍎 Apple Stock Bot - Iniciando")
    logger.info("="*60)
    
    # Validar configuración
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Error en configuración: {e}")
        logger.error("Verifica tu archivo .env")
        sys.exit(1)
    
    # Iniciar scheduler
    scheduler = AppleStockScheduler()
    scheduler.start()

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Apple Stock Bot')
    parser.add_argument('--check-now', action='store_true', help='Ejecutar verificación inmediata')
    parser.add_argument('--test-telegram', action='store_true', help='Probar notificación de Telegram')
    
    args = parser.parse_args()
    
    if args.check_now:
        check_now()
    elif args.test_telegram:
        test_telegram()
    else:
        start_bot()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n👋 Bot detenido por usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error crítico: {e}", exc_info=True)
        sys.exit(1)


=== ARCHIVO 10: README.md ===

Crear documentación completa:

# 🍎 Apple Stock Bot

Bot de Telegram que verifica automáticamente la disponibilidad de productos Apple en tiendas de Florida.

## 📋 Características

- 🤖 Scraping automático con Playwright
- 📱 Notificaciones a Telegram
- ⏰ Verificación diaria programada
- 📸 Screenshots en caso de error
- 📊 Logging detallado

## 🚀 Instalación

### 1. Clonar el proyecto
```bash
git clone <tu-repo>
cd apple-stock-bot
```

### 2. Crear entorno virtual
```bash
python -m venv venv

# Activar entorno
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus valores
```

### 5. Obtener credenciales de Telegram

1. Hablar con @BotFather en Telegram
2. Crear bot con `/newbot`
3. Copiar el token
4. Obtener tu chat_id con @userinfobot
5. Configurar en `.env`

## 📖 Uso

### Iniciar bot (modo automático)
```bash
python main.py
```

### Verificación manual (una vez)
```bash
python main.py --check-now
```

### Probar Telegram
```bash
python main.py --test-telegram
```

## ⚙️ Configuración

Edita `.env` para personalizar:

- `CHECK_HOUR`: Hora de verificación (0-23)
- `TARGET_PRODUCT`: Producto a buscar
- `PLAYWRIGHT_HEADLESS`: true/false (false para ver el navegador)

## 📁 Estructura

apple-stock-bot/
├── config.py              # Configuración
├── main.py               # Punto de entrada
├── services/             # Lógica principal
│   ├── apple_scraper.py
│   └── telegram_notifier.py
└── utils/                # Utilidades
├── scheduler.py
└── logger.py

## 🐛 Troubleshooting

**Error: Playwright no instalado**
```bash
playwright install chromium
```

**Error: Token de Telegram inválido**
- Verifica que el token en `.env` sea correcto
- Sin espacios al principio/final

**Error 541 o scraping falla**
- Ejecuta con `PLAYWRIGHT_HEADLESS=false` para ver qué pasa
- Revisa `screenshots/` para ver capturas de error
- Actualiza selectores CSS en `apple_scraper.py`

## 📝 Notas Importantes

⚠️ **Los selectores CSS de Apple cambian frecuentemente**

Después de configurar, debes:
1. Ejecutar con headless=false
2. Ver qué elementos busca
3. Ajustar selectores en `apple_scraper.py`

## 📄 Licencia

MIT


=== INSTRUCCIONES FINALES ===

1. Genera TODOS los archivos completos
2. Incluye comentarios explicativos en el código
3. Usa type hints en Python
4. Implementa logging robusto
5. Manejo de errores en todos los puntos críticos

IMPORTANTE: Los selectores CSS de Apple Store deben ser genéricos/comentados
ya que cambiarán y el usuario deberá ajustarlos según la estructura actual
de la web. Incluir comentarios claros sobre esto.

Genera el proyecto completo con todos los archivos listos para usar.