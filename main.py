#!/usr/bin/env python3
"""
Apple Store Scraper - Extractor de disponibilidad de productos Apple

Realiza scraping de Apple Store para verificar disponibilidad de productos
en tiendas específicas.

Uso:
    python main.py                    # Ejecutar scraper
    python main.py --headless=false   # Ejecutar con navegador visible
    python main.py --show-config      # Mostrar configuración actual

Autor: Apple Store Scraper
Versión: 1.0.0
Fecha: Enero 2026
"""

import sys
import argparse
import json
from typing import Optional
from datetime import datetime

from config import Config
from utils.logger import setup_logger
from services.apple_scraper import AppleScraper

# Inicializar logger global
logger = setup_logger()


def run_scraper(show_browser: bool = False) -> dict:
    """
    Ejecuta el scraper de Apple Store con flujo de caché
    
    Args:
        show_browser: Si True, muestra el navegador durante el scraping
    
    Returns:
        dict: Resultados del scraping con información de cambios
    """
    logger.info("🔄 Iniciando scraper de Apple Store con caché...")
    
    # Sobrescribir configuración si se especifica
    if show_browser:
        Config.PLAYWRIGHT_HEADLESS = False
        logger.info("👀 Modo visible activado - Se mostrará el navegador")
    
    try:
        # Crear instancia del scraper
        scraper = AppleScraper()
        
        # 🔁 EJECUTAR FLUJO COMPLETO CON CACHÉ
        logger.info("🕷️ Iniciando flujo con caché...")
        result = scraper.check_availability_with_cache()
        
        # Mostrar resultados
        display_results(result)
        
        # 🔔 SOLO ENVIAR NOTIFICACIÓN SI HAY CAMBIOS
        if Config.TELEGRAM_ENABLED:
            if result.get('should_alert', False):
                logger.info("📱 HAY CAMBIOS - Enviando notificación a Telegram...")
                try:
                    from services.telegram_bot import TelegramBot
                    telegram = TelegramBot()
                    telegram.send_availability_report(result)
                    logger.info("✅ Notificación enviada exitosamente")
                except Exception as e:
                    logger.error(f"❌ Error enviando notificación a Telegram: {e}", exc_info=True)
            else:
                logger.info("ℹ️ Sin cambios - No se enviará notificación a Telegram")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error ejecutando scraper: {e}", exc_info=True)
        sys.exit(1)


def display_results(result: dict) -> None:
    """
    Muestra los resultados del scraping de forma formateada
    Incluye información de cambios cuando se usa caché
    
    Args:
        result: Diccionario con resultados del scraping
    """
    logger.info("=" * 70)
    logger.info("📊 RESULTADOS DEL SCRAPING")
    logger.info("=" * 70)
    
    if not result.get('success'):
        logger.error(f"❌ Error: {result.get('error', 'Desconocido')}")
        return
    
    logger.info(f"📅 Timestamp: {result.get('timestamp', 'N/A')}")
    logger.info(f"📱 Producto: {result.get('product', 'N/A')}")
    
    # 📦 Información de caché
    if 'cache_age' in result and result.get('cache_age'):
        logger.info(f"📦 Caché anterior: {result['cache_age']} de antigüedad")
    
    # 🔔 Información de cambios
    if 'has_changes' in result:
        if result.get('is_first_run'):
            logger.info(f"🆕 Estado: Primera ejecución - Datos iniciales")
        elif result['has_changes']:
            logger.info(f"🔔 Estado: CAMBIOS DETECTADOS")
            logger.info(f"   {result.get('summary', '')}")
            
            # Mostrar detalles de cambios
            changes = result.get('changes', {})
            if changes.get('new_available'):
                logger.info(f"   ✨ {len(changes['new_available'])} tienda(s) con NUEVO stock")
            if changes.get('new_unavailable'):
                logger.info(f"   ⚠️ {len(changes['new_unavailable'])} tienda(s) AGOTARON stock")
        else:
            logger.info(f"ℹ️ Estado: Sin cambios desde última verificación")
            logger.info(f"   {result.get('summary', '')}")
    
    logger.info("")
    
    available = result.get('available_stores', [])
    unavailable = result.get('unavailable_stores', [])
    
    # Si hay cambios, mostrar primero los cambios destacados
    if result.get('has_changes') and not result.get('is_first_run'):
        changes = result.get('changes', {})
        
        if changes.get('new_available'):
            logger.info(f"✨ NUEVO STOCK ({len(changes['new_available'])} tienda(s)):")
            for i, store in enumerate(changes['new_available'], 1):
                logger.info(f"   {i}. 🎉 {store.get('name', 'Unknown')} - {store.get('city', '')}, {store.get('state', '')}")
                logger.info(f"      {store.get('pickup_quote', '')}")
            logger.info("")
        
        if changes.get('new_unavailable'):
            logger.info(f"⚠️ STOCK AGOTADO ({len(changes['new_unavailable'])} tienda(s)):")
            for i, store in enumerate(changes['new_unavailable'], 1):
                logger.info(f"   {i}. 📉 {store.get('name', 'Unknown')} - {store.get('city', '')}, {store.get('state', '')}")
            logger.info("")
    
    # Resumen de todas las tiendas
    if available:
        logger.info(f"✅ DISPONIBLE en {len(available)} tienda(s) (total):")
        for i, store in enumerate(available, 1):
            name = store.get('name', 'Unknown')
            city = store.get('city', '')
            state = store.get('state', '')
            logger.info(f"   {i}. {name} - {city}, {state}")
        logger.info("")
    
    if unavailable:
        logger.info(f"❌ No disponible en {len(unavailable)} tienda(s):")
        for store in unavailable[:5]:  # Mostrar máximo 5
            name = store.get('name', 'Unknown')
            city = store.get('city', '')
            state = store.get('state', '')
            logger.info(f"   • {name} - {city}, {state}")
        if len(unavailable) > 5:
            logger.info(f"   ... y {len(unavailable) - 5} más")
        logger.info("")
    
    if not available and not unavailable:
        logger.warning("⚠️ No se encontraron datos de disponibilidad")
        logger.info("💡 Ejecuta con --headless=false para ver qué está pasando")
        logger.info("💡 Revisa screenshots/ para capturas de pantalla")
    
    total = len(available) + len(unavailable)
    logger.info(f"📊 Total: {len(available)} disponible(s) de {total} tienda(s) verificadas")
    logger.info("=" * 70)


def save_results_json(result: dict, filename: Optional[str] = None) -> None:
    """
    Guarda los resultados en un archivo JSON
    
    Args:
        result: Diccionario con resultados
        filename: Nombre del archivo (opcional)
    """
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"results_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Resultados guardados en: {filename}")
    except Exception as e:
        logger.error(f"❌ Error guardando resultados: {e}")


def test_connection() -> None:
    """Prueba la conexión con Apple Store y Telegram"""
    logger.info("🧪 Probando conexión con Apple Store...")
    
    try:
        scraper = AppleScraper()
        apple_ok = scraper.test_connection()
        
        if not apple_ok:
            logger.error("❌ No se pudo conectar con Apple Store")
        
        # Test Telegram si está habilitado
        if Config.TELEGRAM_ENABLED:
            logger.info("")
            logger.info("🧪 Probando conexión con Telegram...")
            from services.telegram_bot import TelegramBot
            telegram = TelegramBot()
            telegram_ok = telegram.test_connection()
            
            if not telegram_ok:
                logger.error("❌ No se pudo conectar con Telegram")
        else:
            logger.info("📱 Telegram deshabilitado (TELEGRAM_ENABLED=false)")
            telegram_ok = False
        
        # Resumen
        logger.info("")
        logger.info("=" * 70)
        logger.info("📊 RESUMEN DE PRUEBAS")
        logger.info("=" * 70)
        logger.info(f"🌐 Apple Store: {'✅ OK' if apple_ok else '❌ FALLO'}")
        if Config.TELEGRAM_ENABLED:
            logger.info(f"📱 Telegram:    {'✅ OK' if telegram_ok else '❌ FALLO'}")
        logger.info("=" * 70)
        
        if not apple_ok:
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"❌ Error en test de conexión: {e}", exc_info=True)
        sys.exit(1)


def show_config() -> None:
    """Muestra la configuración actual del scraper"""
    print(Config.display_config())


def main() -> None:
    """
    Función principal - Punto de entrada del programa
    Parsea argumentos y ejecuta el scraper
    """
    
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(
        description='🍎 Apple Store Scraper - Verificador de disponibilidad de productos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py                      # Ejecutar scraper (modo headless)
  python main.py --headless=false     # Ver navegador durante scraping
  python main.py --test               # Probar conexión
  python main.py --show-config        # Ver configuración
  python main.py --save-json          # Guardar resultados en JSON

Para más información: README.md
        """
    )
    
    # Definir argumentos
    parser.add_argument(
        '--headless',
        type=str,
        default='true',
        choices=['true', 'false'],
        help='Ejecutar navegador en modo headless (invisible)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Probar conexión con Apple Store y Telegram'
    )
    
    parser.add_argument(
        '--test-telegram',
        action='store_true',
        help='Probar solo conexión con Telegram'
    )
    
    parser.add_argument(
        '--show-config',
        action='store_true',
        help='Mostrar configuración actual'
    )
    
    parser.add_argument(
        '--save-json',
        action='store_true',
        help='Guardar resultados en archivo JSON'
    )
    
    # Parsear argumentos
    args = parser.parse_args()
    
    # Ejecutar acción correspondiente
    try:
        if args.show_config:
            show_config()
            return
        
        if args.test:
            test_connection()
            return
        
        if args.test_telegram:
            logger.info("🧪 Probando solo Telegram...")
            if not Config.TELEGRAM_ENABLED:
                logger.warning("⚠️ Telegram está deshabilitado")
                logger.info("💡 Configura TELEGRAM_ENABLED=true en .env")
                return
            
            from services.telegram_bot import TelegramBot
            telegram = TelegramBot()
            if telegram.test_connection():
                logger.info("✅ Telegram funcionando correctamente")
            else:
                logger.error("❌ Error conectando con Telegram")
                logger.info("💡 Verifica TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en .env")
            return
        
        # Validar configuración
        try:
            Config.validate()
            logger.info("✅ Configuración validada correctamente")
        except ValueError as e:
            logger.error(f"❌ Error en configuración: {e}")
            logger.error("💡 Crea un archivo .env basado en .env.example")
            sys.exit(1)
        
        # Ejecutar scraper
        show_browser = args.headless.lower() == 'false'
        result = run_scraper(show_browser=show_browser)
        
        # Guardar resultados si se especifica
        if args.save_json:
            save_results_json(result)
    
    except KeyboardInterrupt:
        logger.info("\n👋 Programa interrumpido por usuario")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"❌ Error crítico: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
