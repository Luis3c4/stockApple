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

logger = logging.getLogger('AppleStockBot')

# Producto y URL objetivo (hardcodeados: el scraper está fijado a esta configuración específica)
PRODUCT_NAME = "iPhone 18 Pro Max"
PRODUCT_URL = "https://www.apple.com/shop/buy-iphone/iphone-18-pro/6.9-inch-display-256gb-burgundy-unlocked"

# El botón "Check availability" (PASO 2) suele tardar en aparecer o falla con un
# timeout de forma intermitente en el sitio real de Apple; reintentar el scraping
# completo (relanzando el navegador) resuelve la mayoría de los casos.
MAX_SCRAPE_ATTEMPTS = 9
RETRY_DELAY_MS = 60000


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
    
    def check_availability(self) -> Dict[str, Any]:
        """
        Verifica disponibilidad de productos en Apple Store, reintentando el
        scraping completo (relanzando el navegador) si falla por timeout.
        
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
        result: Dict[str, Any] = self._error_result("No se intentó el scraping")
        
        for attempt in range(1, MAX_SCRAPE_ATTEMPTS + 1):
            if attempt > 1:
                logger.warning(f"🔁 Reintentando scraping (intento {attempt}/{MAX_SCRAPE_ATTEMPTS})...")
            
            result = self._check_availability_attempt()
            
            if result['success']:
                return result
            
            logger.error(f"❌ Intento {attempt}/{MAX_SCRAPE_ATTEMPTS} falló: {result.get('error')}")
            if attempt < MAX_SCRAPE_ATTEMPTS:
                import time
                time.sleep(RETRY_DELAY_MS / 1000)
        
        logger.error(f"❌ Scraping falló tras {MAX_SCRAPE_ATTEMPTS} intentos")
        return result
    
    def _check_availability_attempt(self) -> Dict[str, Any]:
        """Realiza un único intento completo de scraping (lanza navegador, navega y extrae datos)"""
        logger.info(f"🔍 Iniciando scraping de: {PRODUCT_NAME}")
        logger.info(f"🌐 URL objetivo: {PRODUCT_URL}")
        
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
                
                # Navegar directamente al iPhone 18 Pro configurado (6.9", 256GB, Burgundy, Unlocked)
                logger.info("🌐 Navegando a configuración de iPhone 18 Pro...")
                response = page.goto(
                    PRODUCT_URL, 
                    wait_until='networkidle',
                    timeout=45000
                )
                
                if not response or not response.ok:
                    raise Exception(f"Error al cargar página: Status {response.status if response else 'N/A'}")
                
                logger.info(f"✓ Página cargada - Status: {response.status}")
                logger.info("✓ Configuración preseleccionada: 6.9\", 256GB, Burgundy, Unlocked")
                
                # Esperar a que cargue contenido dinámico (más margen para hardware lento)
                page.wait_for_timeout(5000)
                
                # Screenshot inicial para debug
                if not self.config.PLAYWRIGHT_HEADLESS:
                    logger.info("📸 Guardando screenshot de página inicial...")
                    page.screenshot(path=f"{self.screenshot_dir}/initial_page.png")
                
                # Extraer datos de disponibilidad (por cada color y capacidad configurados)
                colors_result = self._extract_availability_data(page)
                
                # Cerrar navegador
                context.close()
                browser.close()
                
                total_available = sum(
                    len(capacity_data['available_stores'])
                    for color_data in colors_result.values()
                    for capacity_data in color_data.values()
                )
                logger.info(f"✅ Scraping completado - Encontradas {total_available} tiendas con stock (todos los colores/capacidades)")
                
                # Usar el título del producto de la primera capacidad del primer color como referencia general
                first_color_data = next(iter(colors_result.values()), {})
                first_capacity_data = next(iter(first_color_data.values()), {})
                product_name = first_capacity_data.get('product_title') or PRODUCT_NAME
                
                return {
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'product': product_name,
                    'colors': colors_result
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
    
    def _select_capacity_and_capture(self, page: Page, color: str, capacity: str) -> Dict[str, Any]:
        """Selecciona una capacidad en el modal (radio) y captura/procesa su respuesta de fulfillment"""
        label = f"{color}_{capacity}"
        logger.info(f"🔁 Cambiando a capacidad {capacity} dentro del modal...")
        capacity_radio = f'input[name="pl_dimensionCapacity"][value="{capacity}"]'
        
        try:
            page.wait_for_selector(capacity_radio, timeout=20000)
            
            with page.expect_response(lambda r: 'fulfillment-messages' in r.url, timeout=25000) as resp_info:
                page.check(capacity_radio, force=True)
                logger.info(f"✓ Capacidad {capacity} seleccionada")
            
            fulfillment_data = self._safe_response_json(resp_info.value)
            return self._process_capacity_response(fulfillment_data, label)
        except PlaywrightTimeout as e:
            logger.error(f"⏱️ Timeout esperando datos de {label}: {e}")
            return {
                'available_stores': [],
                'unavailable_stores': [],
                'product_title': None
            }
    
    def _extract_availability_data(self, page: Page) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Extrae datos de disponibilidad de la página de Apple Store para todos
        los colores y capacidades configurados (matriz completa color x capacidad)
        
        Args:
            page: Página de Playwright
        
        Returns:
            dict: {
                'burgundy': {'256gb': {'available_stores': [...], 'unavailable_stores': [...], 'product_title': str}, '512gb': {...}},
                'glacier': {...}
            }
        """
        
        colors = self.config.TARGET_COLORS
        capacities = self.config.TARGET_CAPACITIES
        results_by_color: Dict[str, Dict[str, Dict[str, Any]]] = {}
        
        logger.info(f"🔎 Extrayendo datos de disponibilidad para colores: {colors} y capacidades: {capacities}")
        
        try:
            # 🔍 INSPECCIÓN: Página inicial del producto
            if self.config.PLAYWRIGHT_DEBUG:
                logger.info("🔍 PAUSA 1: Inspecciona la página del producto configurado")
                page.pause()
            
            # PASO 1: Seleccionar no Apple Care
            logger.info("🛡️ PASO 1: Seleccionando no Apple Care...")
            page.wait_for_selector('input[data-autom="noapplecare"]', timeout=20000)
            page.click('input[data-autom="noapplecare"]', force=True)
            logger.info("✓ No Apple Care seleccionado")
            page.wait_for_timeout(1500)
            
            # PASO 2: Click en botón "Check availability"
            # Selector dinámico: el número de parte varía según la config/región que Apple asigne
            # Timeout alto: en hardware lento el botón puede tardar en terminar de renderizarse
            logger.info("📍 PASO 2: Haciendo clic en 'Check availability'...")
            check_availability_btn = page.locator('button[data-autom^="productLocatorTriggerLink_"]').first
            check_availability_btn.wait_for(state='visible', timeout=30000)
            check_availability_btn.click()
            logger.info("✓ Modal de disponibilidad abierto")
            page.wait_for_timeout(2000)
            
            # 🔍 INSPECCIÓN: Modal de búsqueda
            if self.config.PLAYWRIGHT_DEBUG:
                logger.info("🔍 PAUSA 2: Inspecciona el modal de búsqueda")
                page.pause()
            
            # PASO 3: Ingresar "Miami" en el input
            logger.info("🔢 PASO 3: Ingresando 'Miami' en el buscador...")
            search_input = 'input[data-autom="zipCode"]'
            page.wait_for_selector(search_input, timeout=20000)
            page.fill(search_input, '33133')
            logger.info("✓ 'Miami' ingresado")
            
            # PASO 4: Esperar al fetch y hacer click en "Miami, FL", capturando el fulfillment
            # del primer color+capacidad (los que ya vienen preseleccionados en la URL del producto)
            logger.info("⏳ PASO 4: Esperando opciones del autocomplete...")
            miami_option = 'li[role="option"][data-option-index="0"]'
            page.wait_for_selector(miami_option, timeout=20000)
            page.wait_for_timeout(1500)  # Esperar a que se complete el fetch
            
            first_color = colors[0]
            first_capacity = capacities[0]
            logger.info(f"⏳ PASO 5: Esperando respuesta de la API de disponibilidad ({first_color}_{first_capacity})...")
            with page.expect_response(lambda r: 'fulfillment-messages' in r.url, timeout=25000) as resp_info:
                page.click(miami_option)
                logger.info("✓ 'Miami, FL' seleccionado")
            
            fulfillment_data = self._safe_response_json(resp_info.value)
            results_by_color[first_color] = {
                first_capacity: self._process_capacity_response(fulfillment_data, f"{first_color}_{first_capacity}")
            }
            
            # 🔍 INSPECCIÓN FINAL: Resultados en el modal
            if self.config.PLAYWRIGHT_DEBUG:
                logger.info("🔍 PAUSA 3: Inspecciona los resultados de disponibilidad")
                page.pause()
            
            # Screenshot final
            if not self.config.PLAYWRIGHT_HEADLESS:
                page.screenshot(path=f"{self.screenshot_dir}/availability_modal.png")
                logger.info("📸 Screenshot del modal de disponibilidad")
            
            # PASO 6: Repetir la consulta para el resto de capacidades configuradas
            # del primer color, cambiando el radio de capacidad dentro del mismo modal
            for capacity in capacities[1:]:
                results_by_color[first_color][capacity] = self._select_capacity_and_capture(page, first_color, capacity)
            
            # PASO 7: Iterar sobre el resto de colores configurados, cambiando el radio
            # de color y repitiendo la matriz de capacidades para cada uno
            for color in colors[1:]:
                logger.info(f"🎨 PASO 7: Cambiando a color {color} dentro del modal...")
                color_radio = f'input[name="pl_dimensionColor"][value="{color}"]'
                # El input de color está oculto tras el swatch/label; hay que clickear el
                # label (no forzar el input) para que el handler de Apple dispare el cambio
                color_label = f'li:has({color_radio}) label'
                
                try:
                    page.wait_for_selector(color_radio, timeout=20000)
                    
                    with page.expect_response(lambda r: 'fulfillment-messages' in r.url, timeout=25000) as resp_info:
                        page.click(color_label)
                        logger.info(f"✓ Color {color} seleccionado")
                    
                    fulfillment_data = self._safe_response_json(resp_info.value)
                    # La capacidad puede no resetearse a capacities[0] al cambiar de color,
                    # así que se lee del DOM cuál quedó realmente seleccionada
                    current_capacity = page.eval_on_selector(
                        'input[name="pl_dimensionCapacity"]:checked', 'el => el.value'
                    ) or capacities[0]
                    
                    results_by_color[color] = {
                        current_capacity: self._process_capacity_response(fulfillment_data, f"{color}_{current_capacity}")
                    }
                    
                    for capacity in capacities:
                        if capacity == current_capacity:
                            continue
                        results_by_color[color][capacity] = self._select_capacity_and_capture(page, color, capacity)
                
                except PlaywrightTimeout as e:
                    logger.error(f"⏱️ Timeout esperando datos de color {color}: {e}")
                    results_by_color[color] = {
                        capacity: {
                            'available_stores': [],
                            'unavailable_stores': [],
                            'product_title': None
                        }
                        for capacity in capacities
                    }
        
        except Exception as e:
            logger.error(f"❌ Error extrayendo datos: {e}", exc_info=True)
            raise
        
        return results_by_color
    
    def _safe_response_json(self, response) -> Optional[Dict[str, Any]]:
        """Parsea de forma segura el JSON de una respuesta de red"""
        try:
            data = response.json()
            logger.info(f"🎯 API interceptada: {response.url}")
            return data
        except Exception as e:
            logger.error(f"❌ Error parseando respuesta: {e}")
            return None
    
    def _process_capacity_response(self, fulfillment_data: Optional[Dict[str, Any]], label: str) -> Dict[str, Any]:
        """Procesa la respuesta de fulfillment-messages para una combinación color+capacidad específica"""
        if not fulfillment_data:
            logger.warning(f"⚠️ No se capturaron datos de la API para {label}")
            return {
                'available_stores': [],
                'unavailable_stores': [],
                'product_title': None
            }
        
        logger.info(f"📊 Procesando datos de disponibilidad ({label})...")
        available_stores, unavailable_stores, product_title = self._parse_fulfillment_data(
            fulfillment_data, label
        )
        logger.info(f"✅ [{label}] Encontradas {len(available_stores)} tiendas con stock")
        logger.info(f"📊 [{label}] Total de {len(unavailable_stores)} tiendas sin stock")
        
        return {
            'available_stores': available_stores,
            'unavailable_stores': unavailable_stores,
            'product_title': product_title
        }
    
    def _parse_fulfillment_data(self, data: Dict[str, Any], label: str = 'default') -> tuple[List[Dict[str, str]], List[Dict[str, str]], str]:
        """
        Parsea los datos de la API de fulfillment-messages para extraer disponibilidad
        
        Args:
            data: JSON response de la API de fulfillment
            label: identificador color+capacidad de esta respuesta (para logs y debug file)
        
        Returns:
            tuple: (available_stores, unavailable_stores, product_title)
        """
        available_stores = []
        unavailable_stores = []
        product_title = None
        
        try:
            logger.info(f"🔍 Analizando datos de la API ({label})...")
            
            # DEBUG: Guardar respuesta completa para inspección (un archivo por color+capacidad)
            import json
            debug_file = f"{self.screenshot_dir}/api_response_debug_{label}.json"
            with open(debug_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Respuesta API guardada en: {debug_file}")
            
            # Estructura real de Apple Store API
            if 'body' in data and 'content' in data['body']:
                # Intentar extraer título del producto desde deliveryMessage (nivel superior)
                delivery_message = data['body']['content'].get('deliveryMessage', {})
                for part_number, part_data in delivery_message.items():
                    if not isinstance(part_data, dict):
                        continue

                    regular_data = part_data.get('regular', {})
                    sub_header = regular_data.get('subHeader', '')
                    if isinstance(sub_header, str) and sub_header.startswith('For '):
                        product_title = sub_header.removeprefix('For ').strip()
                        logger.info(f"📱 Producto detectado desde deliveryMessage ({part_number}): {product_title}")
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
        
        # Si no se pudo extraer el título del producto, usar el fallback hardcodeado
        if not product_title:
            product_title = PRODUCT_NAME
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
        
        base_name = f"{self.screenshot_dir}/error_{error_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            page.screenshot(path=f"{base_name}.png", full_page=True)
            logger.info(f"📸 Screenshot de error guardado: {base_name}.png")
        except Exception as e:
            logger.error(f"❌ No se pudo guardar screenshot: {e}")
        
        # HTML completo para diagnosticar qué renderizó Apple (útil en runners remotos)
        try:
            with open(f"{base_name}.html", 'w', encoding='utf-8') as f:
                f.write(page.content())
            logger.info(f"💾 HTML de error guardado: {base_name}.html")
        except Exception as e:
            logger.error(f"❌ No se pudo guardar HTML: {e}")
    
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
            'product': PRODUCT_NAME,
            'error': error_message,
            'colors': {}
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
                response = page.goto("https://www.apple.com/shop/buy-iphone", timeout=15000)
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
        🔁 FLUJO SIN CACHÉ - Siempre scrapea y envía los datos actuales
        
        Returns:
            dict: resultado del scraping (ver check_availability)
        """
        logger.info("=" * 70)
        logger.info("🔁 INICIANDO SCRAPING")
        logger.info("=" * 70)
        
        scraping_result = self.check_availability()
        
        if not scraping_result.get('success'):
            logger.error("❌ Scraping falló - No se puede continuar")
            return scraping_result
        
        colors_summary = {
            color: {cap: len(data['available_stores']) for cap, data in color_data.items()}
            for color, color_data in scraping_result['colors'].items()
        }
        logger.info(f"✅ Scraping completado - tiendas con stock por color/capacidad: {colors_summary}")
        logger.info("=" * 70)
        
        return scraping_result
