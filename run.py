"""
Punto de entrada de la aplicación
"""
import uvicorn
from app.config import settings
from app.utils.logger import setup_logger

if __name__ == "__main__":
    # Configurar logger
    setup_logger()
    
    # Iniciar servidor
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        workers=settings.WORKERS if settings.ENVIRONMENT == "production" else 1,
        reload=settings.ENVIRONMENT != "production",
        log_level=settings.LOG_LEVEL.lower()
    )
