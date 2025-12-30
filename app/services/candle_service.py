"""
Servicio para manejar velas (candles) y coordinar el flujo completo
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from decimal import Decimal
from loguru import logger
import time

from app.models.candle import Candle
from app.models.indicator import Indicator
from app.schemas.candle import CandleCreate, CandleResponse, CandleWithIndicators
from app.services.indicator_calculator import indicator_calculator
from app.config import settings


class CandleService:
    """Servicio para operaciones con velas"""
    
    @staticmethod
    def create_candle(db: Session, candle_data: CandleCreate) -> Candle:
        """
        Crea una nueva vela en la base de datos
        
        Args:
            db: Sesión de base de datos
            candle_data: Datos de la vela
            
        Returns:
            Vela creada
            
        Raises:
            Exception si la vela ya existe (duplicate key)
        """
        db_candle = Candle(
            symbol=candle_data.symbol,
            timeframe=candle_data.timeframe,
            open_time=candle_data.open_time,
            open=candle_data.open,
            high=candle_data.high,
            low=candle_data.low,
            close=candle_data.close,
            volume=candle_data.volume,
            close_time=candle_data.close_time,
            quote_volume=candle_data.quote_volume,
            trades_count=candle_data.trades_count,
            taker_buy_volume=candle_data.taker_buy_volume,
            taker_buy_quote_volume=candle_data.taker_buy_quote_volume
        )
        
        db.add(db_candle)
        db.commit()
        db.refresh(db_candle)
        
        logger.info(f"Vela creada: {candle_data.symbol} {candle_data.timeframe} @ {candle_data.open_time}")
        return db_candle
    
    @staticmethod
    def get_historical_candles(
        db: Session,
        symbol: str,
        timeframe: str,
        limit: int = 200
    ) -> List[Candle]:
        """
        Obtiene velas históricas para un símbolo y timeframe
        
        Args:
            db: Sesión de base de datos
            symbol: Símbolo (BTCUSDT)
            timeframe: Timeframe (1h, 4h)
            limit: Cantidad máxima de velas
            
        Returns:
            Lista de velas ordenadas por tiempo
        """
        candles = db.query(Candle).filter(
            Candle.symbol == symbol,
            Candle.timeframe == timeframe
        ).order_by(Candle.open_time.desc()).limit(limit).all()
        
        # Revertir para tener orden ascendente (más antiguo primero)
        candles.reverse()
        
        logger.debug(f"Obtenidas {len(candles)} velas históricas para {symbol} {timeframe}")
        return candles
    
    @staticmethod
    def calculate_and_save_indicators(db: Session, candle: Candle) -> Optional[Indicator]:
        """
        Calcula y guarda indicadores para una vela
        
        Args:
            db: Sesión de base de datos
            candle: Vela recién creada
            
        Returns:
            Indicador guardado o None si no hay suficientes datos
        """
        try:
            # Obtener velas históricas (necesitamos al menos 200 para buenos cálculos)
            historical = CandleService.get_historical_candles(
                db,
                candle.symbol,
                candle.timeframe,
                limit=settings.MAX_CANDLES_HISTORY
            )
            
            if len(historical) < settings.MIN_CANDLES_FOR_INDICATORS:
                logger.warning(
                    f"No hay suficientes velas para calcular indicadores: "
                    f"{len(historical)} < {settings.MIN_CANDLES_FOR_INDICATORS}"
                )
                return None
            
            # Convertir a diccionarios para el calculador
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
            
            # Calcular indicadores
            indicators_data = indicator_calculator.calculate_all_indicators(candles_data)
            
            if not indicators_data:
                logger.error("Error calculando indicadores")
                return None
            
            # Guardar en la base de datos
            db_indicator = Indicator(
                candle_id=candle.id,
                symbol=candle.symbol,
                timeframe=candle.timeframe,
                **indicators_data
            )
            
            db.add(db_indicator)
            db.commit()
            db.refresh(db_indicator)
            
            logger.info(f"Indicadores guardados para vela {candle.id}")
            return db_indicator
            
        except Exception as e:
            logger.error(f"Error calculando/guardando indicadores: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def get_latest_candle_with_indicators(
        db: Session,
        symbol: str,
        timeframe: str
    ) -> Optional[Dict]:
        """
        Obtiene la última vela con sus indicadores
        
        Args:
            db: Sesión de base de datos
            symbol: Símbolo
            timeframe: Timeframe
            
        Returns:
            Diccionario con vela e indicadores o None
        """
        candle = db.query(Candle).filter(
            Candle.symbol == symbol,
            Candle.timeframe == timeframe
        ).order_by(Candle.open_time.desc()).first()
        
        if not candle:
            return None
        
        indicator = db.query(Indicator).filter(
            Indicator.candle_id == candle.id
        ).first()
        
        result = {
            'candle': candle,
            'indicator': indicator
        }
        
        return result


# Instancia global del servicio
candle_service = CandleService()
