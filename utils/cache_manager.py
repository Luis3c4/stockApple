"""
Cache Manager para Apple Stock Scraper
Gestiona el caché de disponibilidad de productos
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger('AppleStockBot')


class CacheManager:
    """
    Gestiona el caché de disponibilidad de productos
    Permite comparar resultados nuevos con anteriores
    """
    
    def __init__(self, cache_dir: str = 'cache'):
        """
        Inicializa el cache manager
        
        Args:
            cache_dir: Directorio donde se guardarán los archivos de caché
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_file = os.path.join(cache_dir, 'availability_cache.json')
        logger.info(f"📦 Cache Manager inicializado - Directorio: {cache_dir}")
    
    def load_cache(self) -> Optional[Dict[str, Any]]:
        """
        Carga el caché desde el archivo
        
        Returns:
            dict: Datos del caché o None si no existe
        """
        if not os.path.exists(self.cache_file):
            logger.info("📂 No existe caché previo")
            return None
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            logger.info(f"✅ Caché cargado - Última actualización: {cache_data.get('timestamp', 'N/A')}")
            return cache_data
            
        except Exception as e:
            logger.error(f"❌ Error cargando caché: {e}")
            return None
    
    def save_cache(self, data: Dict[str, Any]) -> bool:
        """
        Guarda datos en el caché
        
        Args:
            data: Datos a guardar (resultado del scraper)
        
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Caché actualizado - Timestamp: {data.get('timestamp', 'N/A')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando caché: {e}")
            return False
    
    def compare_with_cache(self, new_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compara los datos nuevos con el caché para detectar cambios
        
        Args:
            new_data: Nuevos datos del scraper
        
        Returns:
            dict: {
                'has_changes': bool,
                'changes': {
                    'new_available': list[dict],      # Tiendas que ahora tienen stock
                    'new_unavailable': list[dict],    # Tiendas que ahora NO tienen stock
                    'still_available': list[dict],    # Tiendas que siguen con stock
                    'still_unavailable': list[dict]   # Tiendas que siguen sin stock
                },
                'summary': str
            }
        """
        cached_data = self.load_cache()
        
        # Si no hay caché, todo es nuevo
        if cached_data is None:
            logger.info("🆕 Primera ejecución - No hay caché previo para comparar")
            return {
                'has_changes': True,  # Primera vez se considera cambio
                'is_first_run': True,
                'changes': {
                    'new_available': new_data.get('available_stores', []),
                    'new_unavailable': [],
                    'still_available': [],
                    'still_unavailable': new_data.get('unavailable_stores', [])
                },
                'summary': 'Primera ejecución - Datos iniciales capturados'
            }
        
        # Comparar disponibilidad
        old_available = {s['store_number']: s for s in cached_data.get('available_stores', [])}
        old_unavailable = {s['store_number']: s for s in cached_data.get('unavailable_stores', [])}
        
        new_available = {s['store_number']: s for s in new_data.get('available_stores', [])}
        new_unavailable = {s['store_number']: s for s in new_data.get('unavailable_stores', [])}
        
        # Detectar cambios
        changes = {
            'new_available': [],      # Ahora disponible (antes no lo estaba)
            'new_unavailable': [],    # Ahora NO disponible (antes sí lo estaba)
            'still_available': [],    # Sigue disponible
            'still_unavailable': []   # Sigue NO disponible
        }
        
        # Tiendas que ahora tienen stock (antes no tenían)
        for store_num, store_data in new_available.items():
            if store_num in old_unavailable:
                changes['new_available'].append(store_data)
                logger.info(f"✨ NUEVO STOCK: {store_data['name']} ({store_data['city']}, {store_data['state']})")
            elif store_num in old_available:
                changes['still_available'].append(store_data)
        
        # Tiendas que ahora NO tienen stock (antes sí tenían)
        for store_num, store_data in new_unavailable.items():
            if store_num in old_available:
                changes['new_unavailable'].append(store_data)
                logger.info(f"⚠️ STOCK AGOTADO: {store_data['name']} ({store_data['city']}, {store_data['state']})")
            elif store_num in old_unavailable:
                changes['still_unavailable'].append(store_data)
        
        # Determinar si hubo cambios significativos
        has_changes = len(changes['new_available']) > 0 or len(changes['new_unavailable']) > 0
        
        # Generar resumen
        summary_parts = []
        if changes['new_available']:
            summary_parts.append(f"{len(changes['new_available'])} tienda(s) con nuevo stock")
        if changes['new_unavailable']:
            summary_parts.append(f"{len(changes['new_unavailable'])} tienda(s) agotaron stock")
        
        if has_changes:
            summary = "CAMBIOS DETECTADOS: " + ", ".join(summary_parts)
            logger.info(f"🔔 {summary}")
        else:
            summary = f"Sin cambios - {len(changes['still_available'])} con stock, {len(changes['still_unavailable'])} sin stock"
            logger.info(f"ℹ️ {summary}")
        
        return {
            'has_changes': has_changes,
            'is_first_run': False,
            'changes': changes,
            'summary': summary
        }
    
    def get_cache_age(self) -> Optional[str]:
        """
        Obtiene la antigüedad del caché
        
        Returns:
            str: Descripción de la antigüedad o None si no existe
        """
        if not os.path.exists(self.cache_file):
            return None
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            timestamp_str = cache_data.get('timestamp')
            if not timestamp_str:
                return "Desconocida"
            
            cache_time = datetime.fromisoformat(timestamp_str)
            now = datetime.now()
            delta = now - cache_time
            
            hours = delta.total_seconds() / 3600
            if hours < 1:
                minutes = int(delta.total_seconds() / 60)
                return f"{minutes} minutos"
            elif hours < 24:
                return f"{int(hours)} horas"
            else:
                days = int(hours / 24)
                return f"{days} días"
                
        except Exception as e:
            logger.error(f"Error calculando antigüedad del caché: {e}")
            return "Error"
    
    def clear_cache(self) -> bool:
        """
        Limpia el caché eliminando el archivo
        
        Returns:
            bool: True si se eliminó exitosamente
        """
        if not os.path.exists(self.cache_file):
            logger.info("ℹ️ No hay caché que limpiar")
            return True
        
        try:
            os.remove(self.cache_file)
            logger.info("🗑️ Caché eliminado")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando caché: {e}")
            return False
