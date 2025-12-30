"""
Schemas Pydantic para velas (candles)
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from decimal import Decimal


class CandleCreate(BaseModel):
    """Schema para crear una vela nueva"""
    symbol: str = Field(..., min_length=1, max_length=20, description="Símbolo del par (ej: BTCUSDT)")
    timeframe: str = Field(..., min_length=1, max_length=10, description="Timeframe (5m, 15m, 1h, etc.)")
    open_time: int = Field(..., gt=0, description="Timestamp de apertura en milisegundos")
    open: Decimal = Field(..., gt=0, decimal_places=8)
    high: Decimal = Field(..., gt=0, decimal_places=8)
    low: Decimal = Field(..., gt=0, decimal_places=8)
    close: Decimal = Field(..., gt=0, decimal_places=8)
    volume: Decimal = Field(..., ge=0, decimal_places=8)
    close_time: int = Field(..., gt=0, description="Timestamp de cierre en milisegundos")
    quote_volume: Optional[Decimal] = Field(None, ge=0, decimal_places=8)
    trades_count: Optional[int] = Field(None, ge=0)
    taker_buy_volume: Optional[Decimal] = Field(None, ge=0, decimal_places=8)
    taker_buy_quote_volume: Optional[Decimal] = Field(None, ge=0, decimal_places=8)
    
    @field_validator('high')
    @classmethod
    def high_must_be_highest(cls, v, info):
        """Validar que high sea el precio más alto"""
        values = info.data
        if 'low' in values and v < values['low']:
            raise ValueError('high debe ser mayor o igual que low')
        if 'open' in values and v < values['open']:
            if 'low' not in values or values['open'] < values['low']:
                pass  # Open puede estar fuera del rango en casos especiales
        return v
    
    @field_validator('close_time')
    @classmethod
    def close_time_after_open(cls, v, info):
        """Validar que close_time sea después de open_time"""
        if 'open_time' in info.data and v <= info.data['open_time']:
            raise ValueError('close_time debe ser mayor que open_time')
        return v
    
    class Config:
        from_attributes = True


class CandleResponse(BaseModel):
    """Schema para respuesta de vela"""
    id: int
    symbol: str
    timeframe: str
    open_time: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    close_time: int
    quote_volume: Optional[Decimal] = None
    trades_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class CandleWithIndicators(CandleResponse):
    """Schema para vela con indicadores calculados"""
    indicators: Optional[dict] = None
    prediction: Optional[dict] = None
    
    class Config:
        from_attributes = True
