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
    PLAYWRIGHT_HEADLESS: bool = os.getenv('PLAYWRIGHT_HEADLESS', 'false').lower() == 'true'
    PLAYWRIGHT_DEBUG: bool = os.getenv('PLAYWRIGHT_DEBUG', 'false').lower() == 'true'  # Pausar con inspector
    SCREENSHOT_ON_ERROR: bool = os.getenv('SCREENSHOT_ON_ERROR', 'true').lower() == 'true'
    SAVE_SCREENSHOTS: bool = os.getenv('SAVE_SCREENSHOTS', 'true').lower() == 'true'
    
    # === Target Configuration ===
    # Capacidades a verificar. La primera debe coincidir con la que trae la URL hardcodeada en apple_scraper.py
    TARGET_CAPACITIES: list = [c.strip() for c in os.getenv('TARGET_CAPACITIES', '256gb,512gb').split(',') if c.strip()]
    
    # === Telegram Configuration ===
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID', '')
    TELEGRAM_CHAT_IDS: list = [id.strip() for id in os.getenv('TELEGRAM_CHAT_ID', '').split(',') if id.strip()]
    
    @staticmethod
    def validate() -> None:
        """
        Valida que las configuraciones críticas estén presentes
        
        Raises:
            ValueError: Si falta alguna configuración crítica
        """
        if not Config.TARGET_CAPACITIES:
            raise ValueError("❌ TARGET_CAPACITIES no configurado")
    
    @staticmethod
    def display_config() -> str:
        """Retorna una representación string de la configuración"""
        return f"""
╔══════════════════════════════════════════════╗
║   Apple Store Scraper - Configuración      ║
╚══════════════════════════════════════════════╝

🍎 Scraping:
   Headless: {Config.PLAYWRIGHT_HEADLESS}
   Screenshots en error: {Config.SCREENSHOT_ON_ERROR}
   Guardar screenshots: {Config.SAVE_SCREENSHOTS}

🎯 Target:
   Capacidades: {', '.join(Config.TARGET_CAPACITIES)}

📱 Telegram:
   Bot Token: {'Configurado' if Config.TELEGRAM_BOT_TOKEN else 'No configurado'}
   Chat ID: {'Configurado' if Config.TELEGRAM_CHAT_ID else 'No configurado'}
"""
