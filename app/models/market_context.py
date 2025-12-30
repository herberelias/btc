"""
Modelo de contexto del mercado
"""
from sqlalchemy import Column, BigInteger, String, DECIMAL, Integer, Enum, TIMESTAMP, Index
from sqlalchemy.sql import func
import enum
from app.database import Base


class MarketRegimeEnum(str, enum.Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"


class MarketContext(Base):
    __tablename__ = "market_context"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp = Column(BigInteger, nullable=False)
    btc_dominance = Column(DECIMAL(10, 4))
    eth_dominance = Column(DECIMAL(10, 4))
    total_market_cap = Column(DECIMAL(20, 2))
    total_volume_24h = Column(DECIMAL(20, 2))
    fear_greed_index = Column(Integer)
    fear_greed_classification = Column(String(50))
    market_regime = Column(Enum(MarketRegimeEnum), default=MarketRegimeEnum.UNKNOWN)
    volatility_index = Column(DECIMAL(10, 4))
    btc_price = Column(DECIMAL(20, 8))
    eth_price = Column(DECIMAL(20, 8))
    altcoin_season_index = Column(DECIMAL(10, 4))
    defi_dominance = Column(DECIMAL(10, 4))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    __table_args__ = (
        Index('idx_timestamp', 'timestamp'),
        Index('idx_market_regime', 'market_regime'),
        Index('idx_created', 'created_at'),
    )
