"""
Servicio de predicciones
Coordina el flujo completo: velas -> indicadores -> ML -> predicción
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict
from decimal import Decimal
from loguru import logger
import time

from app.models.prediction import Prediction, PredictionTypeEnum, PredictionStatusEnum, PredictionPriorityEnum
from app.models.candle import Candle
from app.services.candle_service import candle_service
from app.services.market_context_service import market_context_service
from app.ml.predictor import ml_predictor
from app.config import settings


class PredictionService:
    """Servicio para generar y gestionar predicciones"""
    
    def generate_prediction(
        self,
        db: Session,
        candle: Candle,
        indicators: Dict,
        market_context_id: Optional[int] = None
    ) -> Optional[Prediction]:
        """
        Genera una predicción para una vela con sus indicadores
        
        Args:
            db: Sesión de base de datos
            candle: Vela reciente
            indicators: Indicadores calculados
            market_context_id: ID del contexto de mercado
            
        Returns:
            Predicción guardada o None si no cumple threshold
        """
        try:
            # Obtener velas históricas
            historical = candle_service.get_historical_candles(
                db,
                candle.symbol,
                candle.timeframe,
                limit=settings.MAX_CANDLES_HISTORY
            )
            
            if len(historical) < settings.MIN_CANDLES_FOR_INDICATORS:
                logger.warning("No hay suficientes velas para predicción")
                return None
            
            # Convertir velas a diccionarios
            candles_data = [
                {
                    'open_time': c.open_time,
                    'open': float(c.open),
                    'high': float(c.high),
                    'low': float(c.low),
                    'close': float(c.close),
                    'volume': float(c.volume)
                }
                for c in historical
            ]
            
            # Obtener contexto de mercado
            market_context_data = None
            if market_context_id:
                context = db.query(MarketContext).filter(
                    MarketContext.id == market_context_id
                ).first()
                
                if context:
                    market_context_data = {
                        'btc_dominance': float(context.btc_dominance) if context.btc_dominance else 50,
                        'fear_greed_index': context.fear_greed_index if context.fear_greed_index else 50,
                        'market_regime': context.market_regime.value if context.market_regime else 'unknown'
                    }
            
            # Generar predicción con ML
            current_price = float(candle.close)
            prediction_data = ml_predictor.predict(
                candles_data,
                indicators,
                market_context_data,
                current_price
            )
            
            if not prediction_data:
                logger.warning("No se pudo generar predicción")
                return None
            
            # Verificar threshold de confianza
            if prediction_data['confidence'] < settings.MIN_CONFIDENCE_THRESHOLD:
                logger.info(
                    f"Predicción descartada: confianza {prediction_data['confidence']:.2f}% "
                    f"< threshold {settings.MIN_CONFIDENCE_THRESHOLD}%"
                )
                return None
            
            # Calcular expiración (24 horas por defecto)
            expiration_hours = 24
            expiration_time = candle.open_time + (expiration_hours * 3600 * 1000)
            
            # Calcular stop loss y take profit percentages
            entry_price = current_price
            stop_loss = prediction_data.get('stop_loss')
            take_profit = prediction_data.get('take_profit')
            
            stop_loss_pct = None
            take_profit_pct = None
            risk_reward = None
            
            if stop_loss and take_profit:
                if prediction_data['type'] == "LONG":
                    stop_loss_pct = ((entry_price - stop_loss) / entry_price) * 100
                    take_profit_pct = ((take_profit - entry_price) / entry_price) * 100
                elif prediction_data['type'] == "SHORT":
                    stop_loss_pct = ((stop_loss - entry_price) / entry_price) * 100
                    take_profit_pct = ((entry_price - take_profit) / entry_price) * 100
                
                if stop_loss_pct and take_profit_pct and stop_loss_pct > 0:
                    risk_reward = take_profit_pct / stop_loss_pct
            
            # Determinar prioridad basada en confianza
            if prediction_data['confidence'] >= 85:
                priority = PredictionPriorityEnum.CRITICAL
            elif prediction_data['confidence'] >= 75:
                priority = PredictionPriorityEnum.HIGH
            elif prediction_data['confidence'] >= 70:
                priority = PredictionPriorityEnum.MEDIUM
            else:
                priority = PredictionPriorityEnum.LOW
            
            # Crear predicción
            db_prediction = Prediction(
                symbol=candle.symbol,
                timeframe=candle.timeframe,
                prediction_type=getattr(PredictionTypeEnum, prediction_data['type']),
                confidence_score=Decimal(str(prediction_data['confidence'])),
                entry_price=Decimal(str(entry_price)),
                current_price=Decimal(str(current_price)),
                suggested_stop_loss=Decimal(str(stop_loss)) if stop_loss else None,
                suggested_take_profit=Decimal(str(take_profit)) if take_profit else None,
                stop_loss_percentage=Decimal(str(stop_loss_pct)) if stop_loss_pct else None,
                take_profit_percentage=Decimal(str(take_profit_pct)) if take_profit_pct else None,
                risk_reward_ratio=Decimal(str(risk_reward)) if risk_reward else None,
                position_size_recommended=Decimal('5.0'),  # 5% por defecto
                model_version=prediction_data.get('model_version', settings.MODEL_VERSION),
                model_type='RandomForest',
                features_used=prediction_data.get('features_used'),
                market_context_id=market_context_id,
                prediction_time=candle.open_time,
                expiration_time=expiration_time,
                time_horizon_hours=expiration_hours,
                status=PredictionStatusEnum.PENDING,
                priority=priority
            )
            
            db.add(db_prediction)
            db.commit()
            db.refresh(db_prediction)
            
            logger.info(
                f"Predicción generada: {candle.symbol} {candle.timeframe} -> "
                f"{prediction_data['type']} ({prediction_data['confidence']:.2f}%)"
            )
            
            return db_prediction
            
        except Exception as e:
            logger.error(f"Error generando predicción: {e}")
            db.rollback()
            return None
    
    def get_active_predictions(
        self,
        db: Session,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
        min_confidence: Optional[float] = None
    ) -> list:
        """
        Obtiene predicciones activas
        
        Args:
            db: Sesión de base de datos
            symbol: Filtrar por símbolo
            timeframe: Filtrar por timeframe
            min_confidence: Confianza mínima
            
        Returns:
            Lista de predicciones activas
        """
        try:
            current_time = int(time.time() * 1000)
            
            query = db.query(Prediction).filter(
                Prediction.status == PredictionStatusEnum.PENDING,
                Prediction.confidence_score >= (min_confidence or settings.MIN_CONFIDENCE_THRESHOLD)
            )
            
            # Filtrar por expiración
            query = query.filter(
                (Prediction.expiration_time == None) | 
                (Prediction.expiration_time > current_time)
            )
            
            if symbol:
                query = query.filter(Prediction.symbol == symbol)
            
            if timeframe:
                query = query.filter(Prediction.timeframe == timeframe)
            
            predictions = query.order_by(
                Prediction.confidence_score.desc(),
                Prediction.created_at.desc()
            ).all()
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error obteniendo predicciones activas: {e}")
            return []


# Instancia global del servicio
prediction_service = PredictionService()
