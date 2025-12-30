"""
Schemas Pydantic para predicciones
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime
from enum import Enum


class PredictionType(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"
    STRONG_LONG = "STRONG_LONG"
    STRONG_SHORT = "STRONG_SHORT"


class PredictionStatus(str, Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    MONITORING = "MONITORING"


class PredictionPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PredictionResponse(BaseModel):
    """Schema para respuesta de predicción"""
    id: int
    symbol: str
    timeframe: str
    type: str = Field(alias="prediction_type")
    confidence: Decimal = Field(alias="confidence_score")
    entry_price: Decimal
    current_price: Optional[Decimal] = None
    stop_loss: Decimal = Field(alias="suggested_stop_loss")
    take_profit: Decimal = Field(alias="suggested_take_profit")
    risk_reward: Decimal = Field(alias="risk_reward_ratio")
    position_size: Optional[Decimal] = Field(None, alias="position_size_recommended")
    model_version: str
    prediction_time: int
    expires_at: Optional[int] = Field(None, alias="expiration_time")
    status: str
    priority: str
    market_context: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True


class ActiveSignalsResponse(BaseModel):
    """Schema para respuesta de señales activas"""
    signals: List[PredictionResponse]
    total: int
    filters: Optional[Dict[str, Any]] = None


class PredictionStats(BaseModel):
    """Schema para estadísticas de predicciones"""
    total_predictions: int
    evaluated_predictions: int
    winning_trades: int
    losing_trades: int
    win_rate: Decimal
    avg_return: Decimal
    avg_confidence: Decimal
