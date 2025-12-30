"""
Modelo de indicadores técnicos
"""
from sqlalchemy import Column, BigInteger, String, DECIMAL, ForeignKey, TIMESTAMP, Index
from sqlalchemy.sql import func
from app.database import Base


class Indicator(Base):
    __tablename__ = "indicators"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    candle_id = Column(BigInteger, ForeignKey('candles.id', ondelete='CASCADE'), nullable=False)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    
    # RSI
    rsi_14 = Column(DECIMAL(10, 4))
    rsi_7 = Column(DECIMAL(10, 4))
    
    # MACD
    macd = Column(DECIMAL(20, 8))
    macd_signal = Column(DECIMAL(20, 8))
    macd_histogram = Column(DECIMAL(20, 8))
    
    # EMAs
    ema_9 = Column(DECIMAL(20, 8))
    ema_20 = Column(DECIMAL(20, 8))
    ema_50 = Column(DECIMAL(20, 8))
    ema_100 = Column(DECIMAL(20, 8))
    ema_200 = Column(DECIMAL(20, 8))
    
    # SMAs
    sma_20 = Column(DECIMAL(20, 8))
    sma_50 = Column(DECIMAL(20, 8))
    sma_200 = Column(DECIMAL(20, 8))
    
    # Bollinger Bands
    bb_upper = Column(DECIMAL(20, 8))
    bb_middle = Column(DECIMAL(20, 8))
    bb_lower = Column(DECIMAL(20, 8))
    bb_width = Column(DECIMAL(10, 4))
    
    # Otros indicadores
    atr = Column(DECIMAL(20, 8))
    volume_avg_20 = Column(DECIMAL(20, 8))
    volume_ratio = Column(DECIMAL(10, 4))
    stoch_k = Column(DECIMAL(10, 4))
    stoch_d = Column(DECIMAL(10, 4))
    adx = Column(DECIMAL(10, 4))
    cci = Column(DECIMAL(10, 4))
    willr = Column(DECIMAL(10, 4))
    obv = Column(DECIMAL(20, 2))
    
    calculated_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    __table_args__ = (
        Index('idx_candle', 'candle_id'),
        Index('idx_symbol_timeframe', 'symbol', 'timeframe'),
        Index('idx_rsi', 'rsi_14'),
        Index('idx_calculated', 'calculated_at'),
    )
