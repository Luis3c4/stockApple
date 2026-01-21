"""
Scraper para Apple Store usando Playwright
Automatiza navegación y extracción de datos de disponibilidad
"""

from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeout
import logging
from datetime import datetime
import os
from typing import Dict, List, Any, Optional

from config import Config
from utils.cache_manager import CacheManager

logger = logging.getLogger('AppleStockBot')


class AppleScraper:
    """
    Scraper para verificar disponibilidad de productos en Apple Store
    Usa Playwright para navegación realista con JavaScript completo
    """
    
    def __init__(self):
        """Inicializa el scraper con configuración"""
        self.config = Config
        self.screenshot_dir = 'screenshots'
        os.makedirs(self.screenshot_dir, exist_ok=True)
        self.cache_manager = CacheManager()  # Inicializar cache manager
    
    def check_availability(self) -> Dict[str, Any]:
        """
        Verifica disponibilidad de productos en Apple Store
        
        Returns:
            dict: {
                'success': bool,
                'timestamp': str (ISO format),
                'product': str,
                'available_stores': list[dict],
                'unavailable_stores': list[dict],
                'error': str (opcional)
            }
        """
        logger.info(f"🔍 Iniciando scraping de: {self.config.TARGET_PRODUCT}")
        logger.info(f"🌐 URL objetivo: {self.config.APPLE_STORE_URL}")
        
        with sync_playwright() as p:
            browser: Optional[Browser] = None
            page: Optional[Page] = None
            
            try:
                # Lanzar navegador Chromium
                logger.info(f"🚀 Lanzando navegador (headless={self.config.PLAYWRIGHT_HEADLESS})")
                browser = p.chromium.launch(
                    headless=self.config.PLAYWRIGHT_HEADLESS,
                    args=['--disable-blink-features=AutomationControlled']  # Evitar detección de bot
                )
                
                # Crear contexto con configuración realista
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-US',
                    timezone_id='America/New_York'
                )
                
                page = context.new_page()
                
                # Navegar directamente al iPhone 17 Pro configurado (6.9", 256GB, Silver, Unlocked)
                logger.info("🌐 Navegando a configuración de iPhone 17 Pro...")
                product_url = "https://www.apple.com/shop/buy-iphone/iphone-17-pro/6.9-inch-display-256gb-silver-unlocked"
                response = page.goto(
                    product_url, 
                    wait_until='networkidle',
                    timeout=30000
                )
                
                if not response or not response.ok:
                    raise Exception(f"Error al cargar página: Status {response.status if response else 'N/A'}")
                
                logger.info(f"✓ Página cargada - Status: {response.status}")
                logger.info("✓ Configuración preseleccionada: 6.9\", 256GB, Silver, Unlocked")
                
                # Esperar a que cargue contenido dinámico
                page.wait_for_timeout(3000)
                
                # Screenshot inicial para debug
                if not self.config.PLAYWRIGHT_HEADLESS:
                    logger.info("📸 Guardando screenshot de página inicial...")
                    page.screenshot(path=f"{self.screenshot_dir}/initial_page.png")
                
                # Extraer datos de disponibilidad
                result = self._extract_availability_data(page)
                
                # Cerrar navegador
                context.close()
                browser.close()
                
                logger.info(f"✅ Scraping completado - Encontradas {len(result['available_stores'])} tiendas con stock")
                
                # Usar el título del producto de la API si está disponible, sino usar el de config
                product_name = result.get('product_title') or self.config.TARGET_PRODUCT
                
                return {
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'product': product_name,
                    **result
                }
                
            except PlaywrightTimeout as e:
                logger.error(f"⏱️ Timeout durante scraping: {e}")
                if page:
                    self._save_error_screenshot(page, 'timeout')
                return self._error_result(f"Timeout navegando Apple Store: {str(e)}")
                
            except Exception as e:
                logger.error(f"❌ Error durante scraping: {e}", exc_info=True)
                if page:
                    self._save_error_screenshot(page, 'error')
                return self._error_result(str(e))
                
            finally:
                # Asegurar limpieza de recursos
                if browser:
                    try:
                        browser.close()
                    except:
                        pass
    
    def _extract_availability_data(self, page: Page) -> Dict[str, Any]:
        """
        Extrae datos de disponibilidad de la página de Apple Store
        
        Args:
            page: Página de Playwright
        
        Returns:
            dict con listas de tiendas disponibles/no disponibles y título del producto
        """
        
        available_stores = []
        unavailable_stores = []
        product_title = None
        
        logger.info("🔎 Extrayendo datos de disponibilidad...")
        
        # Variable para capturar la respuesta de la API
        fulfillment_data = None
        
        # Interceptor de respuestas de red
        def handle_response(response):
            nonlocal fulfillment_data
            if 'fulfillment-messages' in response.url:
                logger.info(f"🎯 API interceptada: {response.url}")
                try:
                    fulfillment_data = response.json()
                    logger.info(f"✓ Datos de disponibilidad capturados")
                except Exception as e:
                    logger.error(f"❌ Error parseando respuesta: {e}")
        
        # Configurar interceptor
        page.on("response", handle_response)
        
        try:
            # 🔍 INSPECCIÓN: Página inicial del producto
            if self.config.PLAYWRIGHT_DEBUG:
                logger.info("🔍 PAUSA 1: Inspecciona la página del producto configurado")
                page.pause()
            
            # PASO 1: Seleccionar no Apple Care
            logger.info("🛡️ PASO 1: Seleccionando no Apple Care...")
            page.wait_for_selector('input[data-autom="noapplecare"]', timeout=10000)
            page.click('input[data-autom="noapplecare"]', force=True)
            logger.info("✓ No Apple Care seleccionado")
            page.wait_for_timeout(1000)
            
            # PASO 2: Click en botón "Check availability"
            logger.info("📍 PASO 2: Haciendo clic en 'Check availability'...")
            check_availability_btn = 'button[data-autom^="productLocatorTriggerLink"]'
            page.wait_for_selector(check_availability_btn, timeout=10000)
            page.click(check_availability_btn)
            logger.info("✓ Modal de disponibilidad abierto")
            page.wait_for_timeout(2000)
            
            # 🔍 INSPECCIÓN: Modal de búsqueda
            if self.config.PLAYWRIGHT_DEBUG:
                logger.info("🔍 PAUSA 2: Inspecciona el modal de búsqueda")
                page.pause()
            
            # PASO 3: Ingresar "Miami" en el input
            logger.info("🔢 PASO 3: Ingresando 'Miami' en el buscador...")
            search_input = 'input[data-autom="zipCode"]'
            page.wait_for_selector(search_input, timeout=10000)
            page.fill(search_input, 'Miami')
            logger.info("✓ 'Miami' ingresado")
            
            # PASO 4: Esperar al fetch y hacer click en "Miami, FL"
            logger.info("⏳ PASO 4: Esperando opciones del autocomplete...")
            miami_option = 'li[role="option"][data-option-index="0"]'
            page.wait_for_selector(miami_option, timeout=10000)
            page.wait_for_timeout(1000)  # Esperar a que se complete el fetch
            page.click(miami_option)
            logger.info("✓ 'Miami, FL' seleccionado")
            
            # PASO 5: Esperar a que se haga la petición a la API
            logger.info("⏳ PASO 5: Esperando respuesta de la API de disponibilidad...")
            page.wait_for_timeout(3000)  # Dar tiempo a la API para responder
            
            # 🔍 INSPECCIÓN FINAL: Resultados en el modal
            if self.config.PLAYWRIGHT_DEBUG:
                logger.info("🔍 PAUSA 3: Inspecciona los resultados de disponibilidad")
                page.pause()
            
            # Screenshot final
            if not self.config.PLAYWRIGHT_HEADLESS:
                page.screenshot(path=f"{self.screenshot_dir}/availability_modal.png")
                logger.info("📸 Screenshot del modal de disponibilidad")
            
            # PASO 6: Procesar los datos capturados de la API
            if fulfillment_data:
                logger.info("📊 Procesando datos de disponibilidad...")
                available_stores, unavailable_stores, product_title = self._parse_fulfillment_data(fulfillment_data)
                logger.info(f"✅ Encontradas {len(available_stores)} tiendas con stock")
                logger.info(f"📊 Total de {len(unavailable_stores)} tiendas sin stock")
            else:
                logger.warning("⚠️ No se capturaron datos de la API de disponibilidad")
                logger.info("💡 Recomendación: Verifica que el interceptor esté funcionando correctamente")
        
        except Exception as e:
            logger.error(f"❌ Error extrayendo datos: {e}", exc_info=True)
        
        return {
            'available_stores': available_stores,
            'unavailable_stores': unavailable_stores,
            'product_title': product_title  # Título completo del producto desde la API
        }
    
    def _parse_fulfillment_data(self, data: Dict[str, Any]) -> tuple[List[Dict[str, str]], List[Dict[str, str]], str]:
        """
        Parsea los datos de la API de fulfillment-messages para extraer disponibilidad
        
        Args:
            data: JSON response de la API de fulfillment
        
        Returns:
            tuple: (available_stores, unavailable_stores, product_title)
        """
        available_stores = []
        unavailable_stores = []
        product_title = None
        
        try:
            logger.info("🔍 Analizando datos de la API...")
            
            # DEBUG: Guardar respuesta completa para inspección
            import json
            debug_file = f"{self.screenshot_dir}/api_response_debug.json"
            with open(debug_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Respuesta API guardada en: {debug_file}")
            
            # Estructura real de Apple Store API
            if 'body' in data and 'content' in data['body']:
                # Intentar extraer título del producto desde deliveryMessage (nivel superior)
                delivery_message = data['body']['content'].get('deliveryMessage', {})
                for part_number, part_data in delivery_message.items():
                    if part_number.startswith('MF') and isinstance(part_data, dict):
                        regular_data = part_data.get('regular', {})
                        sub_header = regular_data.get('subHeader', '')
                        if sub_header and sub_header.startswith('For '):
                            product_title = sub_header.replace('For ', '')
                            logger.info(f"📱 Producto detectado desde deliveryMessage: {product_title}")
                            break
                
                stores_data = data['body']['content'].get('pickupMessage', {}).get('stores', [])
                
                logger.info(f"📍 Analizando {len(stores_data)} tiendas...")
                
                for store in stores_data:
                    store_name = store.get('storeName', 'Unknown Store')
                    city = store.get('city', '')
                    state = store.get('state', '')
                    store_number = store.get('storeNumber', '')
                    
                    # Obtener información de disponibilidad por número de parte
                    parts_availability = store.get('partsAvailability', {})
                    
                    # Puede haber múltiples partes, tomar la primera disponible
                    part_info = None
                    pickup_display = 'unavailable'
                    pickup_quote = 'Not Available'
                    
                    for part_number, part_data in parts_availability.items():
                        pickup_display = part_data.get('pickupDisplay', 'unavailable')
                        pickup_quote = part_data.get('pickupSearchQuote', 'Not Available')
                        store_pick_eligible = part_data.get('storePickEligible', False)
                        
                        # Obtener mensaje formateado y título del producto
                        message_types = part_data.get('messageTypes', {})
                        
                        # DEBUG: Ver estructura completa de message_types
                        if not product_title:
                            logger.info(f"🔍 DEBUG - message_types keys: {list(message_types.keys())}")
                            if 'regular' in message_types:
                                regular_keys = list(message_types['regular'].keys())
                                logger.info(f"🔍 DEBUG - regular keys: {regular_keys}")
                        
                        # Extraer el título del producto desde messageTypes.regular (solo una vez)
                        if not product_title and 'regular' in message_types:
                            product_title = message_types['regular'].get('storePickupProductTitle', '')
                            if product_title:
                                logger.info(f"📱 Producto detectado desde messageTypes: {product_title}")
                        
                        # Intentar también desde regular.subHeader si tiene formato "For [ProductName]"
                        if not product_title and 'regular' in message_types:
                            sub_header = message_types['regular'].get('subHeader', '')
                            if sub_header and sub_header.startswith('For '):
                                product_title = sub_header.replace('For ', '')
                                logger.info(f"📱 Producto detectado desde subHeader: {product_title}")
                        
                        regular_message = message_types.get('regular', {})
                        formatted_quote = regular_message.get('storePickupQuote', pickup_quote)
                        
                        part_info = {
                            'part_number': part_number,
                            'pickup_display': pickup_display,
                            'pickup_quote': pickup_quote,
                            'formatted_quote': formatted_quote,
                            'store_pick_eligible': store_pick_eligible
                        }
                        break  # Usar la primera parte
                    
                    # Crear info de la tienda
                    store_info = {
                        'name': store_name,
                        'city': city,
                        'state': state,
                        'store_number': store_number,
                        'status': pickup_display,
                        'pickup_quote': pickup_quote,
                        'available': pickup_display == 'available',
                        'part_info': part_info
                    }
                    
                    # Determinar si está disponible
                    is_available = pickup_display == 'available'
                    
                    if is_available:
                        available_stores.append(store_info)
                        logger.info(f"  ✅ {store_name} ({city}, {state}): {pickup_quote}")
                    else:
                        unavailable_stores.append(store_info)
                        logger.info(f"  ❌ {store_name} ({city}, {state}): {pickup_quote}")
            
            else:
                logger.warning("⚠️ Estructura de datos no reconocida. Guardando raw data...")
                # Guardar JSON para inspección
                import json
                with open(f"{self.screenshot_dir}/api_response.json", 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"💾 Respuesta guardada en: {self.screenshot_dir}/api_response.json")
        
        except Exception as e:
            logger.error(f"❌ Error parseando datos de fulfillment: {e}", exc_info=True)
        
        # Si no se pudo extraer el título del producto, usar el de config como fallback
        if not product_title:
            product_title = self.config.TARGET_PRODUCT
            logger.warning(f"⚠️ No se pudo extraer título del producto, usando: {product_title}")
        
        return available_stores, unavailable_stores, product_title
    
       
    def _save_error_screenshot(self, page: Page, error_type: str) -> None:
        """
        Guarda screenshot cuando ocurre un error
        
        Args:
            page: Página de Playwright
            error_type: Tipo de error (para nombre de archivo)
        """
        if not self.config.SCREENSHOT_ON_ERROR:
            return
        
        filename = f"{self.screenshot_dir}/error_{error_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        try:
            page.screenshot(path=filename, full_page=True)
            logger.info(f"📸 Screenshot de error guardado: {filename}")
        except Exception as e:
            logger.error(f"❌ No se pudo guardar screenshot: {e}")
    
    def _error_result(self, error_message: str) -> Dict[str, Any]:
        """
        Retorna resultado de error estandarizado
        
        Args:
            error_message: Mensaje de error
        
        Returns:
            dict con estructura de error
        """
        return {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'product': self.config.TARGET_PRODUCT,
            'error': error_message,
            'available_stores': [],
            'unavailable_stores': []
        }
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión a Apple Store sin hacer scraping completo
        
        Returns:
            bool: True si la conexión funciona
        """
        logger.info("🧪 Probando conexión a Apple Store...")
        
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                response = page.goto(self.config.APPLE_STORE_URL, timeout=15000)
                browser.close()
                
                if response and response.ok:
                    logger.info(f"✅ Conexión exitosa - Status: {response.status}")
                    return True
                else:
                    logger.error(f"❌ Conexión fallida - Status: {response.status if response else 'N/A'}")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Error probando conexión: {e}")
                return False
    
    def check_availability_with_cache(self) -> Dict[str, Any]:
        """
        🔁 FLUJO COMPLETO CON CACHÉ
        
        Ejecuta el flujo correcto:
        1. Abre Apple con Playwright
        2. Interactúa como humano
        3. Apple hace el request
        4. Intercepta fulfillment-messages
        5. Extrae stock
        6. Compara con caché
        7. Solo si hay cambios → retorna con flag de alerta
        8. Actualiza caché
        9. Cierra
        
        Returns:
            dict: {
                'success': bool,
                'timestamp': str,
                'product': str,
                'has_changes': bool,           # 🔔 Indica si hay cambios
                'should_alert': bool,          # 🔔 Indica si enviar alerta
                'changes': dict,               # Detalles de los cambios
                'available_stores': list,
                'unavailable_stores': list,
                'cache_age': str,              # Antigüedad del caché anterior
                'error': str (opcional)
            }
        """
        logger.info("=" * 70)
        logger.info("🔁 INICIANDO FLUJO CON CACHÉ")
        logger.info("=" * 70)
        
        # Mostrar info del caché anterior
        cache_age = self.cache_manager.get_cache_age()
        if cache_age:
            logger.info(f"📦 Caché anterior: {cache_age} de antigüedad")
        else:
            logger.info("📦 Sin caché previo - Primera ejecución")
        
        # PASO 1-5: Ejecutar scraping normal (abre, interactúa, intercepta, extrae)
        logger.info("🕷️ PASO 1-5: Ejecutando scraping...")
        scraping_result = self.check_availability()
        
        # Si el scraping falló, retornar error
        if not scraping_result.get('success'):
            logger.error("❌ Scraping falló - No se puede continuar")
            return {
                **scraping_result,
                'has_changes': False,
                'should_alert': False,
                'changes': {},
                'cache_age': cache_age
            }
        
        logger.info(f"✅ Scraping completado - {len(scraping_result['available_stores'])} tiendas con stock")
        
        # PASO 6: Comparar con caché
        logger.info("🔍 PASO 6: Comparando con caché...")
        comparison = self.cache_manager.compare_with_cache(scraping_result)
        
        # PASO 7: Determinar si debe alertar
        has_changes = comparison['has_changes']
        is_first_run = comparison.get('is_first_run', False)
        should_alert = has_changes  # Alertar solo si hay cambios
        
        if has_changes:
            if is_first_run:
                logger.info("🆕 Primera ejecución - Se guardará estado inicial")
            else:
                logger.info(f"🔔 CAMBIOS DETECTADOS - Se debe enviar alerta")
                logger.info(f"   {comparison['summary']}")
        else:
            logger.info(f"ℹ️ Sin cambios - No se enviará alerta")
            logger.info(f"   {comparison['summary']}")
        
        # PASO 8: Actualizar caché (siempre actualizar con datos más recientes)
        logger.info("💾 PASO 8: Actualizando caché...")
        self.cache_manager.save_cache(scraping_result)
        
        # PASO 9: (El cierre ya se hizo en check_availability)
        logger.info("✅ PASO 9: Navegador cerrado")
        
        logger.info("=" * 70)
        logger.info(f"🏁 FLUJO COMPLETADO - Alerta: {'SÍ' if should_alert else 'NO'}")
        logger.info("=" * 70)
        
        # Retornar resultado enriquecido
        return {
            **scraping_result,
            'has_changes': has_changes,
            'should_alert': should_alert,
            'changes': comparison['changes'],
            'summary': comparison['summary'],
            'cache_age': cache_age,
            'is_first_run': is_first_run
        }
