"""
Rutas para predicciones
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from loguru import logger

from app.database import get_db
from app.services.prediction_service import prediction_service
from app.models.market_context import MarketContext

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/active", response_model=dict)
def get_active_predictions(
    symbol: Optional[str] = Query(None, description="Filtrar por símbolo"),
    timeframe: Optional[str] = Query(None, description="Filtrar por timeframe"),
    min_confidence: Optional[float] = Query(None, ge=0, le=100, description="Confianza mínima"),
    db: Session = Depends(get_db)
):
    """
    Obtiene señales activas con alta confianza
    
    Args:
        symbol: Filtro opcional por símbolo
        timeframe: Filtro opcional por timeframe
        min_confidence: Confianza mínima (default: 70%)
        db: Sesión de base de datos
        
    Returns:
        Diccionario con señales activas
    """
    try:
        predictions = prediction_service.get_active_predictions(
            db,
            symbol=symbol,
            timeframe=timeframe,
            min_confidence=min_confidence
        )
        
        signals = []
        for pred in predictions:
            # Obtener contexto de mercado si existe
            market_context_data = None
            if pred.market_context_id:
                context = db.query(MarketContext).filter(
                    MarketContext.id == pred.market_context_id
                ).first()
                
                if context:
                    market_context_data = {
                        "regime": context.market_regime.value if context.market_regime else "unknown",
                        "fear_greed_index": context.fear_greed_index,
                        "fear_greed_classification": context.fear_greed_classification,
                        "btc_dominance": float(context.btc_dominance) if context.btc_dominance else None,
                        "volatility_index": float(context.volatility_index) if context.volatility_index else None
                    }
            
            signals.append({
                "id": pred.id,
                "symbol": pred.symbol,
                "timeframe": pred.timeframe,
                "type": pred.prediction_type.value,
                "confidence": float(pred.confidence_score),
                "entry_price": float(pred.entry_price),
                "current_price": float(pred.current_price) if pred.current_price else float(pred.entry_price),
                "stop_loss": float(pred.suggested_stop_loss) if pred.suggested_stop_loss else None,
                "take_profit": float(pred.suggested_take_profit) if pred.suggested_take_profit else None,
                "risk_reward": float(pred.risk_reward_ratio) if pred.risk_reward_ratio else None,
                "position_size": float(pred.position_size_recommended) if pred.position_size_recommended else None,
                "model_version": pred.model_version,
                "prediction_time": pred.prediction_time,
                "expires_at": pred.expiration_time,
                "status": pred.status.value,
                "priority": pred.priority.value,
                "market_context": market_context_data,
                "created_at": pred.created_at.isoformat()
            })
        
        return {
            "signals": signals,
            "total": len(signals),
            "filters": {
                "symbol": symbol,
                "timeframe": timeframe,
                "min_confidence": min_confidence
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo predicciones activas: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{prediction_id}", response_model=dict)
def get_prediction_detail(
    prediction_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene detalle de una predicción específica
    
    Args:
        prediction_id: ID de la predicción
        db: Sesión de base de datos
        
    Returns:
        Detalle de la predicción
    """
    try:
        from app.models.prediction import Prediction
        
        prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Predicción no encontrada")
        
        # Obtener contexto de mercado si existe
        market_context_data = None
        if prediction.market_context_id:
            context = db.query(MarketContext).filter(
                MarketContext.id == prediction.market_context_id
            ).first()
            
            if context:
                market_context_data = {
                    "regime": context.market_regime.value,
                    "fear_greed_index": context.fear_greed_index,
                    "fear_greed_classification": context.fear_greed_classification,
                    "btc_dominance": float(context.btc_dominance) if context.btc_dominance else None
                }
        
        return {
            "id": prediction.id,
            "symbol": prediction.symbol,
            "timeframe": prediction.timeframe,
            "type": prediction.prediction_type.value,
            "confidence": float(prediction.confidence_score),
            "entry_price": float(prediction.entry_price),
            "current_price": float(prediction.current_price) if prediction.current_price else None,
            "stop_loss": float(prediction.suggested_stop_loss) if prediction.suggested_stop_loss else None,
            "take_profit": float(prediction.suggested_take_profit) if prediction.suggested_take_profit else None,
            "risk_reward": float(prediction.risk_reward_ratio) if prediction.risk_reward_ratio else None,
            "position_size": float(prediction.position_size_recommended) if prediction.position_size_recommended else None,
            "model_version": prediction.model_version,
            "model_type": prediction.model_type,
            "features_used": prediction.features_used,
            "prediction_time": prediction.prediction_time,
            "expiration_time": prediction.expiration_time,
            "status": prediction.status.value,
            "priority": prediction.priority.value,
            "market_context": market_context_data,
            "created_at": prediction.created_at.isoformat(),
            "updated_at": prediction.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo detalle de predicción: {e}")
        raise HTTPException(status_code=500, detail=str(e))
