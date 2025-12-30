"""
Configuración global de la aplicación
"""
import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Servidor
    PORT: int = 3001
    ENVIRONMENT: str = "production"
    WORKERS: int = 4
    
    # Base de datos
    DB_HOST: str = "localhost"
    DB_USER: str = "crypto_user"
    DB_PASSWORD: str = "CryptoSenales2025!"
    DB_NAME: str = "btc"
    DB_PORT: int = 3306
    
    # Machine Learning
    MODEL_VERSION: str = "1.0"
    MODEL_PATH: str = "./app/ml/models/"
    AUTO_RETRAIN: bool = True
    RETRAIN_HOUR: int = 3
    MIN_CONFIDENCE_THRESHOLD: float = 70.0
    
    # APIs externas
    COINGECKO_API_KEY: str = ""
    FEAR_GREED_API_URL: str = "https://api.alternative.me/fng/"
    CRYPTO_COMPARE_API_KEY: str = ""
    
    # Configuración de la app
    MIN_CANDLES_FOR_INDICATORS: int = 50
    MAX_CANDLES_HISTORY: int = 500
    DEFAULT_SYMBOLS: str = "BTCUSDT,ETHUSDT,BNBUSDT"
    DEFAULT_TIMEFRAMES: str = "5m,15m,1h,4h,1d"
    
    # Logs
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    @property
    def DATABASE_URL(self) -> str:
        """Construye la URL de conexión a la base de datos"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
    
    @property
    def SYMBOLS_LIST(self) -> List[str]:
        """Lista de símbolos por defecto"""
        return [s.strip() for s in self.DEFAULT_SYMBOLS.split(",")]
    
    @property
    def TIMEFRAMES_LIST(self) -> List[str]:
        """Lista de timeframes por defecto"""
        return [t.strip() for t in self.DEFAULT_TIMEFRAMES.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()
