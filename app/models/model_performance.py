"""
Modelo de performance de modelos ML
"""
from sqlalchemy import Column, BigInteger, String, DECIMAL, Integer, Boolean, Enum, JSON, Text, TIMESTAMP, Index
from sqlalchemy.sql import func
import enum
from app.database import Base


class PerformanceTrendEnum(str, enum.Enum):
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DEGRADING = "DEGRADING"
    UNKNOWN = "UNKNOWN"


class ModelPerformance(Base):
    __tablename__ = "model_performance"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    model_version = Column(String(20), nullable=False, unique=True)
    model_type = Column(String(50), nullable=False)
    model_architecture = Column(Text)
    training_date = Column(TIMESTAMP, nullable=False)
    dataset_size = Column(Integer, nullable=False)
    training_duration_minutes = Column(Integer)
    accuracy = Column(DECIMAL(5, 2))
    precision_score = Column(DECIMAL(5, 2))
    recall_score = Column(DECIMAL(5, 2))
    f1_score = Column(DECIMAL(5, 2))
    auc_roc = Column(DECIMAL(5, 4))
    sharpe_ratio = Column(DECIMAL(10, 4))
    sortino_ratio = Column(DECIMAL(10, 4))
    max_drawdown = Column(DECIMAL(10, 4))
    avg_profit_per_trade = Column(DECIMAL(10, 4))
    avg_loss_per_trade = Column(DECIMAL(10, 4))
    total_trades_analyzed = Column(Integer)
    winning_trades = Column(Integer)
    losing_trades = Column(Integer)
    win_rate = Column(DECIMAL(5, 2))
    profit_factor = Column(DECIMAL(10, 4))
    expectancy = Column(DECIMAL(10, 4))
    best_timeframe = Column(String(10))
    worst_timeframe = Column(String(10))
    best_symbol = Column(String(20))
    worst_symbol = Column(String(20))
    best_market_condition = Column(String(50))
    features_importance = Column(JSON)
    hyperparameters = Column(JSON)
    training_config = Column(JSON)
    validation_metrics = Column(JSON)
    test_metrics = Column(JSON)
    is_active = Column(Boolean, default=False)
    deployment_date = Column(TIMESTAMP)
    retirement_date = Column(TIMESTAMP)
    performance_trend = Column(Enum(PerformanceTrendEnum), default=PerformanceTrendEnum.UNKNOWN)
    confidence_interval_lower = Column(DECIMAL(5, 2))
    confidence_interval_upper = Column(DECIMAL(5, 2))
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    __table_args__ = (
        Index('idx_version', 'model_version'),
        Index('idx_active', 'is_active'),
        Index('idx_performance', 'win_rate', 'sharpe_ratio'),
        Index('idx_training_date', 'training_date'),
    )
