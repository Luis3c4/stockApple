"""
Servicio de notificaciones por Telegram
Envía mensajes con resultados de disponibilidad
"""

import re
import requests
import logging
from typing import Dict, List, Any
from config import Config

logger = logging.getLogger('AppleStockBot')


def _display_product_name(product: str) -> str:
    """Recorta capacidad/color del título (ej. 'iPhone 18 Pro Max 256GB Burgundy' -> 'iPhone 18 Pro Max')"""
    return re.split(r'\s+\d+\s*[GT]B\b', product)[0].strip()


class TelegramBot:
    """Cliente para enviar notificaciones vía Telegram"""
    
    def __init__(self):
        """Inicializa el bot de Telegram"""
        self.token = Config.TELEGRAM_BOT_TOKEN
        self.chat_ids = Config.TELEGRAM_CHAT_IDS  # Lista de chat IDs
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
    def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """
        Envía un mensaje de texto a todos los chats configurados
        
        Args:
            message: Texto del mensaje (puede incluir HTML)
            parse_mode: Formato del mensaje ('HTML' o 'Markdown')
        
        Returns:
            bool: True si se envió correctamente a al menos un chat
        """
        if not self.token or not self.chat_ids:
            logger.error("❌ Token o Chat ID de Telegram no configurados")
            return False
        
        success_count = 0
        for chat_id in self.chat_ids:
            try:
                url = f"{self.base_url}/sendMessage"
                payload = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': parse_mode,
                    'disable_web_page_preview': True
                }
                
                response = requests.post(url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    logger.info(f"✅ Mensaje enviado a chat {chat_id}")
                    success_count += 1
                else:
                    logger.error(f"❌ Error enviando a chat {chat_id}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Excepción al enviar a chat {chat_id}: {e}", exc_info=True)
        
        return success_count > 0
    
    def send_availability_report(self, result: Dict[str, Any]) -> bool:
        """
        Envía un reporte formateado de disponibilidad (siempre con los datos actuales del scrap)
        
        Args:
            result: Diccionario con resultados del scraping
        
        Returns:
            bool: True si se envió correctamente
        """
        if not result.get('success', False):
            message = self._format_error_message(result)
        else:
            message = self._format_availability_message(result)
        
        return self.send_message(message)
    
    def _format_availability_message(self, result: Dict[str, Any]) -> str:
        """
        Formatea el mensaje con los resultados de disponibilidad actuales.
        Color = título de variante, capacidad = subtítulo, tiendas = texto normal.
        
        Args:
            result: Resultados del scraping
        
        Returns:
            str: Mensaje formateado en HTML
        """
        colors = result.get('colors', {})
        product = _display_product_name(result.get('product', 'iPhone 17 Pro Max'))
        timestamp = result.get('timestamp', '')
        
        message_parts = [
            f"📱 <b>{product}</b>",
            f"🕐 {timestamp[:19]}",
            ""
        ]
        
        for color, color_data in colors.items():
            message_parts.append(f"<b>{color.upper()}</b>")
            
            for capacity, capacity_data in color_data.items():
                available = capacity_data.get('available_stores', [])
                
                message_parts.append(f"<i>{capacity.upper()}</i>")
                
                if not available:
                    message_parts.append("Sin stock disponible en ninguna tienda")
                else:
                    for store in available[:5]:
                        name = store.get('name', 'Unknown')
                        city = store.get('city', '')
                        state = store.get('state', '')
                        message_parts.append(f"{name} - {city}, {state}")
                    if len(available) > 5:
                        message_parts.append("ℹ️ Hay más tiendas disponibles en la página de Apple")
                
                message_parts.append("")
        
        return "\n".join(message_parts).rstrip()
    
    def _format_error_message(self, result: Dict[str, Any]) -> str:
        """
        Formatea un mensaje de error
        
        Args:
            result: Resultados con error
        
        Returns:
            str: Mensaje de error formateado
        """
        error = result.get('error', 'Error desconocido')
        timestamp = result.get('timestamp', '')
        
        return f"❌ <b>ERROR EN SCRAPING</b>\n🕐 {timestamp[:19]}\n\n<code>{error}</code>"
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión con Telegram enviando un mensaje de prueba
        
        Returns:
            bool: True si la conexión funciona
        """
        logger.info("🧪 Probando conexión con Telegram...")
        
        test_message = "🧪 <b>Test de Conexión</b>\n✅ El bot de Telegram está funcionando correctamente."
        
        return self.send_message(test_message)

