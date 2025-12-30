"""
Configuración de logger con loguru
"""
import sys
from loguru import logger
from app.config import settings


def setup_logger():
    """Configura el logger global"""
    
    # Remover handlers por defecto
    logger.remove()
    
    # Agregar handler para consola
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True
    )
    
    # Agregar handler para archivo
    logger.add(
        settings.LOG_FILE,
        rotation="500 MB",
        retention="10 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=settings.LOG_LEVEL
    )
    
    logger.info("Logger configurado correctamente")


# Configurar logger al importar
setup_logger()
