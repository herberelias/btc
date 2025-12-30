"""
Modelo de patrones ganadores
"""
from sqlalchemy import Column, BigInteger, String, DECIMAL, Integer, Boolean, Enum, JSON, Text, TIMESTAMP, Index
from sqlalchemy.sql import func
import enum
from app.database import Base


class PatternStrengthEnum(str, enum.Enum):
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"


class MarketRegimeBestEnum(str, enum.Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    ANY = "any"


class WinningPattern(Base):
    __tablename__ = "winning_patterns"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    pattern_name = Column(String(100), nullable=False)
    pattern_description = Column(Text)
    symbol = Column(String(20))
    timeframe = Column(String(10))
    conditions = Column(JSON, nullable=False)
    win_rate = Column(DECIMAL(5, 2), nullable=False)
    avg_profit = Column(DECIMAL(10, 4), nullable=False)
    avg_loss = Column(DECIMAL(10, 4), nullable=False)
    max_profit = Column(DECIMAL(10, 4))
    max_loss = Column(DECIMAL(10, 4))
    risk_reward = Column(DECIMAL(10, 4), nullable=False)
    profit_factor = Column(DECIMAL(10, 4))
    occurrences = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    last_occurrence = Column(BigInteger)
    first_occurrence = Column(BigInteger)
    market_regime_best = Column(Enum(MarketRegimeBestEnum), default=MarketRegimeBestEnum.ANY)
    confidence_threshold = Column(DECIMAL(5, 2))
    min_volume_required = Column(DECIMAL(20, 8))
    optimal_entry_conditions = Column(JSON)
    optimal_exit_conditions = Column(JSON)
    pattern_strength = Column(Enum(PatternStrengthEnum), default=PatternStrengthEnum.MODERATE)
    is_active = Column(Boolean, default=True)
    reliability_score = Column(DECIMAL(5, 2))
    consistency_score = Column(DECIMAL(5, 2))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    __table_args__ = (
        Index('unique_pattern', 'pattern_name', 'symbol', 'timeframe', unique=True),
        Index('idx_win_rate', 'win_rate'),
        Index('idx_symbol_timeframe', 'symbol', 'timeframe'),
        Index('idx_market_regime', 'market_regime_best'),
        Index('idx_active', 'is_active'),
        Index('idx_strength', 'pattern_strength', 'win_rate'),
    )
