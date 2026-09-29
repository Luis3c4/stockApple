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
        Envía un reporte formateado de disponibilidad
        Prioriza mostrar cambios si están disponibles
        
        Args:
            result: Diccionario con resultados del scraping
        
        Returns:
            bool: True si se envió correctamente
        """
        if not result.get('success', False):
            # Enviar mensaje de error
            message = self._format_error_message(result)
            return self.send_message(message)
        
        # Sin cambios y sin stock en ninguna capacidad → mensaje simple
        if (
            result.get('has_changes') is False
            and not result.get('is_first_run', False)
            and not any(c.get('available_stores') for c in result.get('capacities', {}).values())
        ):
            message = self._format_no_stock_message(result)
        # Si hay información de cambios, usar formato de cambios
        elif result.get('has_changes') is not None and not result.get('is_first_run', False):
            message = self._format_changes_message(result)
        else:
            # Formato normal (primera ejecución o sin sistema de caché)
            message = self._format_availability_message(result)
        
        return self.send_message(message)
    
    def _format_no_stock_message(self, result: Dict[str, Any]) -> str:
        """
        Mensaje simple para cuando no hay cambios ni stock disponible en ninguna capacidad
        
        Args:
            result: Resultados del scraping
        
        Returns:
            str: Mensaje corto en HTML
        """
        product = _display_product_name(result.get('product', 'iPhone 17 Pro Max'))
        capacities = ", ".join(c.upper() for c in result.get('capacities', {}).keys())
        
        return f"😔 Aún sin stock de <b>{product}</b> {capacities}"
    
    def _format_availability_message(self, result: Dict[str, Any]) -> str:
        """
        Formatea el mensaje con los resultados de disponibilidad
        
        Args:
            result: Resultados del scraping
        
        Returns:
            str: Mensaje formateado en HTML
        """
        capacities = result.get('capacities', {})
        product = _display_product_name(result.get('product', 'iPhone 17 Pro Max'))
        timestamp = result.get('timestamp', '')
        
        any_available = any(c.get('available_stores') for c in capacities.values())
        
        # Encabezado
        if any_available:
            header = "🎉 <b>¡STOCK DISPONIBLE!</b>"
        else:
            header = "⚠️ <b>Sin Stock Disponible</b>"
        
        message_parts = [
            header,
            f"📱 <b>{product}</b>",
            "",
            f"🕐 <i>{timestamp[:19]}</i>",
            ""
        ]
        
        for capacity, capacity_data in capacities.items():
            available = capacity_data.get('available_stores', [])
            unavailable = capacity_data.get('unavailable_stores', [])
            emoji = "✅" if available else "❌"
            
            message_parts.append("━━━━━━━━━━━━━━━━━")
            message_parts.append(f"<b>📦 {capacity.upper()}</b>")
            message_parts.append("")
            
            # Tiendas con stock
            if available:
                message_parts.append(f"<b>{emoji} TIENDAS CON STOCK ({len(available)}):</b>")
                message_parts.append("")
                for store in available:
                    name = store.get('name', 'Unknown')
                    city = store.get('city', '')
                    state = store.get('state', '')
                    quote = store.get('pickup_quote', 'Available')
                    message_parts.append(f"✅ <b>{name}</b>")
                    message_parts.append(f"   📍 {city}, {state}")
                    message_parts.append(f"   ⏰ {quote}")
                    message_parts.append("")
            
            # Tiendas sin stock (limitar a 5 para no saturar)
            if unavailable:
                count = min(5, len(unavailable))
                message_parts.append(f"<b>❌ SIN STOCK ({len(unavailable)}):</b>")
                if len(unavailable) > 5:
                    message_parts.append(f"<i>(Mostrando {count} de {len(unavailable)})</i>")
                message_parts.append("")
                for store in unavailable[:count]:
                    name = store.get('name', 'Unknown')
                    city = store.get('city', '')
                    quote = store.get('pickup_quote', 'Not Available')
                    message_parts.append(f"❌ {name} ({city}) - {quote}")
                message_parts.append("")
        
        message_parts.append("━━━━━━━━━━━━━━━━━")
        message_parts.append("🤖 <i>Apple Stock Bot</i>")
        
        return "\n".join(message_parts)
    
    def _format_changes_message(self, result: Dict[str, Any]) -> str:
        """
        Formatea el mensaje destacando los cambios desde la última verificación
        
        Args:
            result: Resultados del scraping con información de cambios
        
        Returns:
            str: Mensaje formateado en HTML destacando cambios
        """
        changes_by_capacity = result.get('changes_by_capacity', {})
        product = _display_product_name(result.get('product', 'iPhone 17 Pro Max'))
        timestamp = result.get('timestamp', '')
        summary = result.get('summary', '')
        cache_age = result.get('cache_age', 'N/A')
        
        any_new_available = any(c.get('new_available') for c in changes_by_capacity.values())
        any_new_unavailable = any(c.get('new_unavailable') for c in changes_by_capacity.values())
        
        # Encabezado según tipo de cambio
        if any_new_available:
            header = "🎉 <b>¡NUEVO STOCK DISPONIBLE!</b>"
        elif any_new_unavailable:
            header = "⚠️ <b>ALERTA: Stock Agotado</b>"
        else:
            header = "📊 <b>Actualización de Stock</b>"
        
        message_parts = [
            header,
            f"📱 <b>{product}</b>",
            "",
            f"🕐 {timestamp[:19]}",
            f"📦 Última verificación: hace {cache_age}",
            "",
            f"<i>{summary}</i>",
            ""
        ]
        
        for capacity, changes in changes_by_capacity.items():
            new_available = changes.get('new_available', [])
            new_unavailable = changes.get('new_unavailable', [])
            still_available = changes.get('still_available', [])
            
            if not (new_available or new_unavailable or still_available):
                continue
            
            message_parts.append("━━━━━━━━━━━━━━━━━")
            message_parts.append(f"<b>📦 {capacity.upper()}</b>")
            message_parts.append("")
            
            # 🎉 NUEVO STOCK (lo más importante)
            if new_available:
                message_parts.append(f"<b>✨ NUEVO STOCK ({len(new_available)}):</b>")
                message_parts.append("")
                for store in new_available:
                    name = store.get('name', 'Unknown')
                    city = store.get('city', '')
                    state = store.get('state', '')
                    quote = store.get('pickup_quote', 'Available')
                    message_parts.append(f"🎉 <b>{name}</b>")
                    message_parts.append(f"   📍 {city}, {state}")
                    message_parts.append(f"   ⏰ {quote}")
                    message_parts.append("")
            
            # ⚠️ STOCK AGOTADO
            if new_unavailable:
                message_parts.append(f"<b>📉 STOCK AGOTADO ({len(new_unavailable)}):</b>")
                message_parts.append("")
                for store in new_unavailable:
                    name = store.get('name', 'Unknown')
                    city = store.get('city', '')
                    state = store.get('state', '')
                    message_parts.append(f"❌ {name} ({city}, {state})")
                message_parts.append("")
            
            # ✅ RESUMEN - Tiendas que aún tienen stock
            if still_available:
                message_parts.append(f"<b>✅ AÚN CON STOCK ({len(still_available)}):</b>")
                message_parts.append("")
                for store in still_available[:5]:  # Máximo 5
                    name = store.get('name', 'Unknown')
                    city = store.get('city', '')
                    state = store.get('state', '')
                    message_parts.append(f"✅ {name} ({city}, {state})")
                if len(still_available) > 5:
                    message_parts.append(f"... y {len(still_available) - 5} más")
                message_parts.append("")
        
        message_parts.append("━━━━━━━━━━━━━━━━━")
        message_parts.append("🤖 <i>Apple Stock Bot</i>")
        
        return "\n".join(message_parts)
    
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
        
        return f"""❌ <b>ERROR EN SCRAPING</b>

🕐 {timestamp[:19]}

<b>Error:</b>
<code>{error}</code>

━━━━━━━━━━━━━━━━━
🤖 <i>Apple Stock Bot</i>
"""
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión con Telegram enviando un mensaje de prueba
        
        Returns:
            bool: True si la conexión funciona
        """
        logger.info("🧪 Probando conexión con Telegram...")
        
        test_message = """🧪 <b>Test de Conexión</b>

✅ El bot de Telegram está funcionando correctamente.

━━━━━━━━━━━━━━━━━
🤖 <i>Apple Stock Bot</i>
"""
        
        return self.send_message(test_message)
