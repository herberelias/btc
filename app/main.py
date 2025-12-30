"""
Aplicación principal FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.utils.logger import setup_logger
from app.routes import candles, predictions, health

# Crear instancia de FastAPI
app = FastAPI(
    title="Crypto Trading Backend with ML",
    description="Backend para trading de criptomonedas con Machine Learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(health.router, prefix="/api/v1")
app.include_router(candles.router, prefix="/api/v1")
app.include_router(predictions.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    logger.info("=" * 60)
    logger.info("Iniciando Crypto Trading Backend")
    logger.info(f"Entorno: {settings.ENVIRONMENT}")
    logger.info(f"Puerto: {settings.PORT}")
    logger.info(f"Base de datos: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    logger.info(f"Modelo ML: v{settings.MODEL_VERSION}")
    logger.info("=" * 60)
    
    # Intentar cargar modelo ML
    from app.ml.predictor import ml_predictor
    loaded = ml_predictor.load_model()
    if loaded:
        logger.info("✓ Modelo ML cargado exitosamente")
    else:
        logger.warning("⚠ Modelo ML no encontrado - usando predicciones basadas en reglas")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación"""
    logger.info("Deteniendo Crypto Trading Backend...")


@app.get("/")
def root():
    """Endpoint raíz"""
    return {
        "message": "Crypto Trading Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


# Para desarrollo
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True
    )
