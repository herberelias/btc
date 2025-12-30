"""
Modelo de predicciones de ML
"""
from sqlalchemy import Column, BigInteger, String, DECIMAL, Integer, ForeignKey, Enum, JSON, Text, TIMESTAMP, Index
from sqlalchemy.sql import func
import enum
from app.database import Base


class PredictionTypeEnum(str, enum.Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"
    STRONG_LONG = "STRONG_LONG"
    STRONG_SHORT = "STRONG_SHORT"


class PredictionStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    MONITORING = "MONITORING"


class PredictionPriorityEnum(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    prediction_type = Column(Enum(PredictionTypeEnum), nullable=False)
    confidence_score = Column(DECIMAL(5, 2), nullable=False)
    entry_price = Column(DECIMAL(20, 8), nullable=False)
    current_price = Column(DECIMAL(20, 8))
    suggested_stop_loss = Column(DECIMAL(20, 8))
    suggested_take_profit = Column(DECIMAL(20, 8))
    stop_loss_percentage = Column(DECIMAL(10, 4))
    take_profit_percentage = Column(DECIMAL(10, 4))
    risk_reward_ratio = Column(DECIMAL(10, 4))
    position_size_recommended = Column(DECIMAL(10, 4))
    max_position_size = Column(DECIMAL(10, 4))
    model_version = Column(String(20), nullable=False)
    model_type = Column(String(50))
    features_used = Column(JSON)
    market_context_id = Column(BigInteger, ForeignKey('market_context.id', ondelete='SET NULL'))
    prediction_time = Column(BigInteger, nullable=False)
    expiration_time = Column(BigInteger)
    time_horizon_hours = Column(Integer)
    status = Column(Enum(PredictionStatusEnum), default=PredictionStatusEnum.PENDING)
    priority = Column(Enum(PredictionPriorityEnum), default=PredictionPriorityEnum.MEDIUM)
    tags = Column(JSON)
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    __table_args__ = (
        Index('idx_symbol_timeframe', 'symbol', 'timeframe'),
        Index('idx_status_confidence', 'status', 'confidence_score'),
        Index('idx_prediction_time', 'prediction_time'),
        Index('idx_expiration', 'expiration_time'),
        Index('idx_model_version', 'model_version'),
        Index('idx_active_signals', 'status', 'confidence_score', 'expiration_time'),
        Index('idx_created', 'created_at'),
    )
