"""
Rutas para operaciones con velas (candles)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from loguru import logger

from app.database import get_db
from app.schemas.candle import CandleCreate, CandleResponse, CandleWithIndicators
from app.schemas.responses import SuccessResponse, ErrorResponse
from app.services.candle_service import candle_service
from app.services.market_context_service import market_context_service
from app.services.prediction_service import prediction_service
from app.models.market_context import MarketContext

router = APIRouter(prefix="/candles", tags=["candles"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_candle(
    candle_data: CandleCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva vela y automáticamente:
    1. Calcula indicadores técnicos
    2. Obtiene contexto del mercado
    3. Genera predicción con ML
    4. Retorna señal si confidence >= threshold
    
    Args:
        candle_data: Datos de la vela (OHLCV)
        db: Sesión de base de datos
        
    Returns:
        Diccionario con vela, indicadores y predicción (si aplica)
    """
    try:
        # 1. Crear vela
        try:
            candle = candle_service.create_candle(db, candle_data)
        except Exception as e:
            if "Duplicate entry" in str(e) or "unique constraint" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Vela ya existe: {candle_data.symbol} {candle_data.timeframe} @ {candle_data.open_time}"
                )
            raise
        
        # 2. Calcular indicadores
        indicator = candle_service.calculate_and_save_indicators(db, candle)
        
        response = {
            "success": True,
            "candle_id": candle.id,
            "indicators_calculated": indicator is not None
        }
        
        if not indicator:
            response["message"] = "Vela guardada pero no hay suficientes datos para calcular indicadores"
            response["prediction"] = None
            return response
        
        # 3. Obtener/crear contexto de mercado
        market_context = await market_context_service.get_and_save_context(db)
        market_context_id = market_context.id if market_context else None
        
        # 4. Convertir indicadores a diccionario
        indicators_dict = {
            'rsi_14': float(indicator.rsi_14) if indicator.rsi_14 else None,
            'rsi_7': float(indicator.rsi_7) if indicator.rsi_7 else None,
            'macd': float(indicator.macd) if indicator.macd else None,
            'macd_signal': float(indicator.macd_signal) if indicator.macd_signal else None,
            'macd_histogram': float(indicator.macd_histogram) if indicator.macd_histogram else None,
            'ema_9': float(indicator.ema_9) if indicator.ema_9 else None,
            'ema_20': float(indicator.ema_20) if indicator.ema_20 else None,
            'ema_50': float(indicator.ema_50) if indicator.ema_50 else None,
            'ema_200': float(indicator.ema_200) if indicator.ema_200 else None,
            'sma_20': float(indicator.sma_20) if indicator.sma_20 else None,
            'bb_upper': float(indicator.bb_upper) if indicator.bb_upper else None,
            'bb_middle': float(indicator.bb_middle) if indicator.bb_middle else None,
            'bb_lower': float(indicator.bb_lower) if indicator.bb_lower else None,
            'bb_width': float(indicator.bb_width) if indicator.bb_width else None,
            'atr': float(indicator.atr) if indicator.atr else None,
            'volume_avg_20': float(indicator.volume_avg_20) if indicator.volume_avg_20 else None,
            'volume_ratio': float(indicator.volume_ratio) if indicator.volume_ratio else None,
            'stoch_k': float(indicator.stoch_k) if indicator.stoch_k else None,
            'stoch_d': float(indicator.stoch_d) if indicator.stoch_d else None,
            'adx': float(indicator.adx) if indicator.adx else None,
            'cci': float(indicator.cci) if indicator.cci else None,
            'willr': float(indicator.willr) if indicator.willr else None,
            'obv': float(indicator.obv) if indicator.obv else None,
        }
        
        # 5. Generar predicción
        prediction = prediction_service.generate_prediction(
            db,
            candle,
            indicators_dict,
            market_context_id
        )
        
        if prediction:
            # Preparar datos de contexto de mercado
            market_context_data = None
            if market_context:
                market_context_data = {
                    "regime": market_context.market_regime.value if market_context.market_regime else "unknown",
                    "fear_greed_index": market_context.fear_greed_index,
                    "fear_greed_classification": market_context.fear_greed_classification,
                    "btc_dominance": float(market_context.btc_dominance) if market_context.btc_dominance else None,
                    "volatility_index": float(market_context.volatility_index) if market_context.volatility_index else None
                }
            
            response["prediction"] = {
                "id": prediction.id,
                "symbol": prediction.symbol,
                "timeframe": prediction.timeframe,
                "type": prediction.prediction_type.value,
                "confidence": float(prediction.confidence_score),
                "entry_price": float(prediction.entry_price),
                "stop_loss": float(prediction.suggested_stop_loss) if prediction.suggested_stop_loss else None,
                "take_profit": float(prediction.suggested_take_profit) if prediction.suggested_take_profit else None,
                "risk_reward": float(prediction.risk_reward_ratio) if prediction.risk_reward_ratio else None,
                "position_size": float(prediction.position_size_recommended) if prediction.position_size_recommended else None,
                "model_version": prediction.model_version,
                "expires_at": prediction.expiration_time,
                "market_context": market_context_data
            }
        else:
            response["prediction"] = None
            response["message"] = "No high-confidence signal generated"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en create_candle: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando vela: {str(e)}"
        )


@router.get("/{symbol}/{timeframe}", response_model=list)
def get_candles(
    symbol: str,
    timeframe: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene velas históricas para un símbolo y timeframe
    
    Args:
        symbol: Símbolo (BTCUSDT)
        timeframe: Timeframe (1h, 4h)
        limit: Cantidad de velas
        db: Sesión de base de datos
        
    Returns:
        Lista de velas
    """
    try:
        candles = candle_service.get_historical_candles(db, symbol, timeframe, limit)
        
        return [
            {
                "id": c.id,
                "symbol": c.symbol,
                "timeframe": c.timeframe,
                "open_time": c.open_time,
                "open": float(c.open),
                "high": float(c.high),
                "low": float(c.low),
                "close": float(c.close),
                "volume": float(c.volume),
                "close_time": c.close_time
            }
            for c in candles
        ]
        
    except Exception as e:
        logger.error(f"Error obteniendo velas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
