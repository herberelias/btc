"""
Modelo de resultados de predicciones
"""
from sqlalchemy import Column, BigInteger, DECIMAL, Integer, Boolean, ForeignKey, Enum, TIMESTAMP, Index
from sqlalchemy.sql import func
import enum
from app.database import Base


class ActualOutcomeEnum(str, enum.Enum):
    WIN = "WIN"
    LOSS = "LOSS"
    NEUTRAL = "NEUTRAL"
    PARTIAL_WIN = "PARTIAL_WIN"
    PARTIAL_LOSS = "PARTIAL_LOSS"


class ExitReasonEnum(str, enum.Enum):
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"
    MANUAL = "MANUAL"
    TIMEOUT = "TIMEOUT"
    REVERSAL_SIGNAL = "REVERSAL_SIGNAL"
    OTHER = "OTHER"


class Result(Base):
    __tablename__ = "results"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    prediction_id = Column(BigInteger, ForeignKey('predictions.id', ondelete='CASCADE'), nullable=False)
    actual_outcome = Column(Enum(ActualOutcomeEnum), nullable=False)
    entry_price = Column(DECIMAL(20, 8), nullable=False)
    exit_price = Column(DECIMAL(20, 8), nullable=False)
    highest_price = Column(DECIMAL(20, 8))
    lowest_price = Column(DECIMAL(20, 8))
    profit_loss_percentage = Column(DECIMAL(10, 4), nullable=False)
    profit_loss_usd = Column(DECIMAL(20, 8))
    max_favorable_excursion = Column(DECIMAL(10, 4))
    max_adverse_excursion = Column(DECIMAL(10, 4))
    hit_stop_loss = Column(Boolean, default=False)
    hit_take_profit = Column(Boolean, default=False)
    exit_reason = Column(Enum(ExitReasonEnum))
    duration_minutes = Column(Integer)
    duration_hours = Column(DECIMAL(10, 4))
    slippage = Column(DECIMAL(10, 4))
    fees_paid = Column(DECIMAL(20, 8))
    net_profit_loss = Column(DECIMAL(20, 8))
    trade_quality_score = Column(DECIMAL(5, 2))
    market_condition_during_trade = Column(String(50))
    volatility_during_trade = Column(DECIMAL(10, 4))
    result_time = Column(BigInteger, nullable=False)
    evaluation_time = Column(TIMESTAMP, server_default=func.current_timestamp())
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    __table_args__ = (
        Index('idx_prediction', 'prediction_id'),
        Index('idx_outcome', 'actual_outcome'),
        Index('idx_profit_loss', 'profit_loss_percentage'),
        Index('idx_quality', 'trade_quality_score'),
        Index('idx_result_time', 'result_time'),
        Index('idx_analysis', 'actual_outcome', 'profit_loss_percentage', 'duration_hours'),
    )
