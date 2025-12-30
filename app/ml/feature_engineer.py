"""
Feature Engineering para Machine Learning
Crea features avanzados a partir de velas e indicadores
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from loguru import logger


class FeatureEngineer:
    """Crea features para el modelo ML"""
    
    @staticmethod
    def create_price_features(df: pd.DataFrame) -> Dict:
        """Crea features basados en precio"""
        try:
            features = {}
            
            # Cambios porcentuales
            features['price_change_1'] = ((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100) if len(df) >= 2 else 0
            features['price_change_5'] = ((df['close'].iloc[-1] - df['close'].iloc[-6]) / df['close'].iloc[-6] * 100) if len(df) >= 6 else 0
            
            # Ratios
            last_candle = df.iloc[-1]
            features['high_low_ratio'] = float(last_candle['high'] / last_candle['low']) if last_candle['low'] > 0 else 1
            features['close_open_ratio'] = float(last_candle['close'] / last_candle['open']) if last_candle['open'] > 0 else 1
            
            return features
        except Exception as e:
            logger.error(f"Error creando price features: {e}")
            return {}
    
    @staticmethod
    def create_trend_features(indicators: Dict) -> Dict:
        """Crea features basados en tendencia"""
        try:
            features = {}
            
            # EMA crosses
            if indicators.get('ema_20') and indicators.get('ema_50'):
                features['ema_20_50_cross'] = 1 if indicators['ema_20'] > indicators['ema_50'] else -1
            else:
                features['ema_20_50_cross'] = 0
            
            if indicators.get('ema_50') and indicators.get('ema_200'):
                features['ema_50_200_cross'] = 1 if indicators['ema_50'] > indicators['ema_200'] else -1
            else:
                features['ema_50_200_cross'] = 0
            
            # MACD cross
            if indicators.get('macd') and indicators.get('macd_signal'):
                features['macd_signal_cross'] = 1 if indicators['macd'] > indicators['macd_signal'] else -1
            else:
                features['macd_signal_cross'] = 0
            
            # Price position
            if indicators.get('ema_20'):
                features['price_above_ema20'] = 1  # Esto se calculará en runtime
            else:
                features['price_above_ema20'] = 0
            
            return features
        except Exception as e:
            logger.error(f"Error creando trend features: {e}")
            return {}
    
    @staticmethod
    def create_volume_features(df: pd.DataFrame, indicators: Dict) -> Dict:
        """Crea features basados en volumen"""
        try:
            features = {}
            
            # Volume ratio ya está en indicators
            features['volume_ratio'] = indicators.get('volume_ratio', 0)
            
            # Cambio de volumen
            if len(df) >= 2:
                vol_change = ((df['volume'].iloc[-1] - df['volume'].iloc[-2]) / df['volume'].iloc[-2] * 100) if df['volume'].iloc[-2] > 0 else 0
                features['volume_change_1'] = float(vol_change)
            else:
                features['volume_change_1'] = 0
            
            # Tendencia de volumen (últimas 5 velas)
            if len(df) >= 5:
                volumes = df['volume'].iloc[-5:].values
                trend = np.polyfit(range(5), volumes, 1)[0]  # Pendiente
                features['volume_trend_5'] = float(trend)
            else:
                features['volume_trend_5'] = 0
            
            return features
        except Exception as e:
            logger.error(f"Error creando volume features: {e}")
            return {}
    
    @staticmethod
    def create_volatility_features(indicators: Dict) -> Dict:
        """Crea features basados en volatilidad"""
        try:
            features = {}
            
            features['bb_width'] = indicators.get('bb_width', 0)
            features['atr'] = indicators.get('atr', 0)
            
            return features
        except Exception as e:
            logger.error(f"Error creando volatility features: {e}")
            return {}
    
    @staticmethod
    def create_momentum_features(indicators: Dict) -> Dict:
        """Crea features basados en momentum"""
        try:
            features = {}
            
            features['rsi_14'] = indicators.get('rsi_14', 50)
            features['rsi_7'] = indicators.get('rsi_7', 50)
            features['macd_histogram'] = indicators.get('macd_histogram', 0)
            features['stoch_k'] = indicators.get('stoch_k', 50)
            features['stoch_d'] = indicators.get('stoch_d', 50)
            features['adx'] = indicators.get('adx', 0)
            features['cci'] = indicators.get('cci', 0)
            
            return features
        except Exception as e:
            logger.error(f"Error creando momentum features: {e}")
            return {}
    
    @staticmethod
    def create_all_features(candles: List[Dict], indicators: Dict, market_context: Optional[Dict] = None) -> Dict[str, float]:
        """
        Crea todos los features para el modelo ML
        
        Args:
            candles: Lista de velas históricas
            indicators: Indicadores técnicos calculados
            market_context: Contexto del mercado (opcional)
            
        Returns:
            Diccionario con todos los features
        """
        try:
            df = pd.DataFrame(candles)
            
            # Convertir a float
            for col in ['open', 'high', 'low', 'close', 'volume']:
                if col in df.columns:
                    df[col] = df[col].astype(float)
            
            all_features = {}
            
            # Price features
            price_features = FeatureEngineer.create_price_features(df)
            all_features.update(price_features)
            
            # Trend features
            trend_features = FeatureEngineer.create_trend_features(indicators)
            all_features.update(trend_features)
            
            # Volume features
            volume_features = FeatureEngineer.create_volume_features(df, indicators)
            all_features.update(volume_features)
            
            # Volatility features
            volatility_features = FeatureEngineer.create_volatility_features(indicators)
            all_features.update(volatility_features)
            
            # Momentum features
            momentum_features = FeatureEngineer.create_momentum_features(indicators)
            all_features.update(momentum_features)
            
            # Market context features
            if market_context:
                all_features['btc_dominance'] = market_context.get('btc_dominance', 50)
                all_features['fear_greed_index'] = market_context.get('fear_greed_index', 50)
                
                # Market regime (encoded)
                regime = market_context.get('market_regime', 'unknown')
                all_features['market_regime_encoded'] = 1 if regime == 'bull' else (-1 if regime == 'bear' else 0)
            else:
                all_features['btc_dominance'] = 50
                all_features['fear_greed_index'] = 50
                all_features['market_regime_encoded'] = 0
            
            # Asegurar que todos los features son float
            for key, value in all_features.items():
                if value is None:
                    all_features[key] = 0.0
                elif isinstance(value, (int, float)):
                    all_features[key] = float(value)
                else:
                    all_features[key] = 0.0
            
            logger.info(f"Features creados: {len(all_features)} features")
            return all_features
            
        except Exception as e:
            logger.error(f"Error creando features: {e}")
            return {}


# Instancia global
feature_engineer = FeatureEngineer()
