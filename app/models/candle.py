"""
Modelo de velas (OHLCV)
"""
from sqlalchemy import Column, BigInteger, String, DECIMAL, Integer, TIMESTAMP, Index
from sqlalchemy.sql import func
from app.database import Base


class Candle(Base):
    __tablename__ = "candles"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    open_time = Column(BigInteger, nullable=False)
    open = Column(DECIMAL(20, 8), nullable=False)
    high = Column(DECIMAL(20, 8), nullable=False)
    low = Column(DECIMAL(20, 8), nullable=False)
    close = Column(DECIMAL(20, 8), nullable=False)
    volume = Column(DECIMAL(20, 8), nullable=False)
    close_time = Column(BigInteger, nullable=False)
    quote_volume = Column(DECIMAL(20, 8))
    trades_count = Column(Integer)
    taker_buy_volume = Column(DECIMAL(20, 8))
    taker_buy_quote_volume = Column(DECIMAL(20, 8))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    __table_args__ = (
        Index('unique_candle', 'symbol', 'timeframe', 'open_time', unique=True),
        Index('idx_symbol_timeframe', 'symbol', 'timeframe'),
        Index('idx_open_time', 'open_time'),
        Index('idx_lookup', 'symbol', 'timeframe', 'open_time'),
    )
