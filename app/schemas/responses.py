"""
Schemas para respuestas comunes de la API
"""
from pydantic import BaseModel
from typing import Optional, Any


class SuccessResponse(BaseModel):
    """Respuesta exitosa genérica"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Respuesta de error"""
    success: bool = False
    error: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    """Respuesta de health check"""
    status: str
    database: str
    ml_model: Optional[str] = None
    version: str
