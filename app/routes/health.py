"""
Ruta de health check y estado del sistema
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from loguru import logger

from app.database import get_db
from app.config import settings
from app.ml.predictor import ml_predictor

router = APIRouter(tags=["health"])


@router.get("/health", response_model=dict)
def health_check(db: Session = Depends(get_db)):
    """
    Health check del sistema
    
    Returns:
        Estado del servidor, base de datos y modelo ML
    """
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database unhealthy: {e}")
        db_status = "unhealthy"
    
    # Check ML model
    ml_status = "loaded" if ml_predictor.model is not None else "not loaded"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "ml_model": ml_status,
        "version": "1.0.0",
        "model_version": settings.MODEL_VERSION
    }


@router.get("/stats", response_model=dict)
def get_stats(db: Session = Depends(get_db)):
    """
    Estadísticas generales del sistema
    
    Returns:
        Contadores básicos
    """
    try:
        from app.models.candle import Candle
        from app.models.prediction import Prediction
        from app.models.result import Result
        
        total_candles = db.query(Candle).count()
        total_predictions = db.query(Prediction).count()
        total_results = db.query(Result).count()
        
        return {
            "total_candles": total_candles,
            "total_predictions": total_predictions,
            "total_results": total_results
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo stats: {e}")
        return {
            "total_candles": 0,
            "total_predictions": 0,
            "total_results": 0
        }
