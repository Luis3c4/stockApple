"""
Configuración del Apple Stock Scraper
Carga y valida variables de entorno
"""

from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()


class Config:
    """Clase de configuración centralizada con validación"""
    
    # === Scraping Configuration ===
    APPLE_STORE_URL: str = os.getenv(
        'APPLE_STORE_URL', 
        'https://www.apple.com/shop/buy-iphone'
    )
    PLAYWRIGHT_HEADLESS: bool = os.getenv('PLAYWRIGHT_HEADLESS', 'false').lower() == 'true'
    PLAYWRIGHT_DEBUG: bool = os.getenv('PLAYWRIGHT_DEBUG', 'false').lower() == 'true'  # Pausar con inspector
    SCREENSHOT_ON_ERROR: bool = os.getenv('SCREENSHOT_ON_ERROR', 'true').lower() == 'true'
    SAVE_SCREENSHOTS: bool = os.getenv('SAVE_SCREENSHOTS', 'true').lower() == 'true'
    
    # === Cache Configuration ===
    CACHE_DIR: str = os.getenv('CACHE_DIR', 'cache')  # Directorio para caché
    CACHE_ENABLED: bool = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'  # Habilitar sistema de caché
    
    # === Target Configuration ===
    TARGET_PRODUCT: str = os.getenv('TARGET_PRODUCT', 'iPhone 17')
    TARGET_STATE: str = os.getenv('TARGET_STATE', 'Florida')
    
    # === Telegram Configuration ===
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID', '')
    TELEGRAM_CHAT_IDS: list = [id.strip() for id in os.getenv('TELEGRAM_CHAT_ID', '').split(',') if id.strip()]
    TELEGRAM_ENABLED: bool = os.getenv('TELEGRAM_ENABLED', 'true').lower() == 'true'
    
    @staticmethod
    def validate() -> None:
        """
        Valida que las configuraciones críticas estén presentes
        
        Raises:
            ValueError: Si falta alguna configuración crítica
        """
        if not Config.APPLE_STORE_URL:
            raise ValueError("❌ APPLE_STORE_URL no configurado")
        
        if not Config.TARGET_PRODUCT:
            raise ValueError("❌ TARGET_PRODUCT no configurado")
    
    @staticmethod
    def display_config() -> str:
        """Retorna una representación string de la configuración"""
        return f"""
╔══════════════════════════════════════════════╗
║   Apple Store Scraper - Configuración      ║
╚══════════════════════════════════════════════╝

🍎 Scraping:
   URL: {Config.APPLE_STORE_URL}
   Headless: {Config.PLAYWRIGHT_HEADLESS}
   Screenshots en error: {Config.SCREENSHOT_ON_ERROR}
   Guardar screenshots: {Config.SAVE_SCREENSHOTS}

📦 Cache:
   Directorio: {Config.CACHE_DIR}
   Habilitado: {Config.CACHE_ENABLED}

🎯 Target:
   Producto: {Config.TARGET_PRODUCT}
   Estado: {Config.TARGET_STATE}

📱 Telegram:
   Habilitado: {Config.TELEGRAM_ENABLED}
   Bot Token: {'Configurado' if Config.TELEGRAM_BOT_TOKEN else 'No configurado'}
   Chat ID: {'Configurado' if Config.TELEGRAM_CHAT_ID else 'No configurado'}
"""
