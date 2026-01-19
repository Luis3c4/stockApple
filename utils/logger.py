"""
Sistema de logging configurado para Apple Stock Bot
Maneja logs en consola y archivos con rotación diaria
"""

import logging
import os
from datetime import datetime
from typing import Optional


def setup_logger(name: str = 'AppleStockBot', level: int = logging.INFO) -> logging.Logger:
    """
    Configura el sistema de logging para el bot
    
    Args:
        name: Nombre del logger
        level: Nivel de logging (default: INFO)
    
    Returns:
        Logger configurado
    """
    
    # Crear carpeta de logs si no existe
    os.makedirs('logs', exist_ok=True)
    
    # Formato detallado del log
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Crear formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Configurar logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicar handlers si ya existen
    if logger.handlers:
        return logger
    
    # Console handler - output a la consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler - output a archivo con fecha
    log_filename = f'logs/apple_bot_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logger.info(f"Logger inicializado - Archivo: {log_filename}")
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Obtiene un logger existente o crea uno nuevo
    
    Args:
        name: Nombre del logger (default: AppleStockBot)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name or 'AppleStockBot')
