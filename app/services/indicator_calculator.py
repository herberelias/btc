"""
Calculador de Indicadores Técnicos
Calcula RSI, MACD, EMAs, Bollinger Bands, ATR, Stochastic, etc.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from decimal import Decimal
from loguru import logger


class IndicatorCalculator:
    """Calcula indicadores técnicos a partir de datos de velas"""
    
    @staticmethod
    def prepare_dataframe(candles: List[Dict]) -> pd.DataFrame:
        """
        Convierte lista de velas en DataFrame de pandas
        
        Args:
            candles: Lista de diccionarios con datos OHLCV
            
        Returns:
            DataFrame con columnas: open, high, low, close, volume
        """
        df = pd.DataFrame(candles)
        
        # Convertir a float para cálculos
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = df[col].astype(float)
        
        # Ordenar por tiempo
        if 'open_time' in df.columns:
            df = df.sort_values('open_time')
        
        return df
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> Optional[float]:
        """Calcula RSI (Relative Strength Index)"""
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None
        except Exception as e:
            logger.error(f"Error calculando RSI: {e}")
            return None
    
    @staticmethod
    def calculate_macd(df: pd.DataFrame) -> Dict[str, Optional[float]]:
        """Calcula MACD (Moving Average Convergence Divergence)"""
        try:
            ema_fast = df['close'].ewm(span=12, adjust=False).mean()
            ema_slow = df['close'].ewm(span=26, adjust=False).mean()
            macd = ema_fast - ema_slow
            signal = macd.ewm(span=9, adjust=False).mean()
            histogram = macd - signal
            
            return {
                'macd': float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else None,
                'macd_signal': float(signal.iloc[-1]) if not pd.isna(signal.iloc[-1]) else None,
                'macd_histogram': float(histogram.iloc[-1]) if not pd.isna(histogram.iloc[-1]) else None
            }
        except Exception as e:
            logger.error(f"Error calculando MACD: {e}")
            return {'macd': None, 'macd_signal': None, 'macd_histogram': None}
    
    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int) -> Optional[float]:
        """Calcula EMA (Exponential Moving Average)"""
        try:
            ema = df['close'].ewm(span=period, adjust=False).mean()
            return float(ema.iloc[-1]) if not pd.isna(ema.iloc[-1]) else None
        except Exception as e:
            logger.error(f"Error calculando EMA {period}: {e}")
            return None
    
    @staticmethod
    def calculate_sma(df: pd.DataFrame, period: int) -> Optional[float]:
        """Calcula SMA (Simple Moving Average)"""
        try:
            sma = df['close'].rolling(window=period).mean()
            return float(sma.iloc[-1]) if not pd.isna(sma.iloc[-1]) else None
        except Exception as e:
            logger.error(f"Error calculando SMA {period}: {e}")
            return None
    
    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std: float = 2) -> Dict[str, Optional[float]]:
        """Calcula Bollinger Bands"""
        try:
            middle = df['close'].rolling(window=period).mean()
            std_dev = df['close'].rolling(window=period).std()
            upper = middle + (std_dev * std)
            lower = middle - (std_dev * std)
            
            upper_val = float(upper.iloc[-1]) if not pd.isna(upper.iloc[-1]) else None
            middle_val = float(middle.iloc[-1]) if not pd.isna(middle.iloc[-1]) else None
            lower_val = float(lower.iloc[-1]) if not pd.isna(lower.iloc[-1]) else None
            
            # Calcular ancho de bandas
            width = None
            if upper_val and lower_val and middle_val:
                width = ((upper_val - lower_val) / middle_val) * 100
            
            return {
                'bb_upper': upper_val,
                'bb_middle': middle_val,
                'bb_lower': lower_val,
                'bb_width': width
            }
        except Exception as e:
            logger.error(f"Error calculando Bollinger Bands: {e}")
            return {'bb_upper': None, 'bb_middle': None, 'bb_lower': None, 'bb_width': None}
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> Optional[float]:
        """Calcula ATR (Average True Range)"""
        try:
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean()
            return float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else None
        except Exception as e:
            logger.error(f"Error calculando ATR: {e}")
            return None
    
    @staticmethod
    def calculate_stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict[str, Optional[float]]:
        """Calcula Stochastic Oscillator"""
        try:
            low_min = df['low'].rolling(window=k_period).min()
            high_max = df['high'].rolling(window=k_period).max()
            stoch_k = 100 * (df['close'] - low_min) / (high_max - low_min)
            stoch_d = stoch_k.rolling(window=d_period).mean()
            
            return {
                'stoch_k': float(stoch_k.iloc[-1]) if not pd.isna(stoch_k.iloc[-1]) else None,
                'stoch_d': float(stoch_d.iloc[-1]) if not pd.isna(stoch_d.iloc[-1]) else None
            }
        except Exception as e:
            logger.error(f"Error calculando Stochastic: {e}")
            return {'stoch_k': None, 'stoch_d': None}
    
    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> Optional[float]:
        """Calcula ADX (Average Directional Index) - Simplificado"""
        # ADX es complejo, retornamos None por ahora
        return None
    
    @staticmethod
    def calculate_cci(df: pd.DataFrame, period: int = 20) -> Optional[float]:
        """Calcula CCI (Commodity Channel Index)"""
        try:
            tp = (df['high'] + df['low'] + df['close']) / 3
            sma = tp.rolling(window=period).mean()
            mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
            cci = (tp - sma) / (0.015 * mad)
            return float(cci.iloc[-1]) if not pd.isna(cci.iloc[-1]) else None
        except Exception as e:
            logger.error(f"Error calculando CCI: {e}")
            return None
    
    @staticmethod
    def calculate_willr(df: pd.DataFrame, period: int = 14) -> Optional[float]:
        """Calcula Williams %R"""
        try:
            high_max = df['high'].rolling(window=period).max()
            low_min = df['low'].rolling(window=period).min()
            willr = -100 * (high_max - df['close']) / (high_max - low_min)
            return float(willr.iloc[-1]) if not pd.isna(willr.iloc[-1]) else None
        except Exception as e:
            logger.error(f"Error calculando Williams %R: {e}")
            return None
    
    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> Optional[float]:
        """Calcula OBV (On-Balance Volume)"""
        try:
            obv = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
            return float(obv.iloc[-1]) if not pd.isna(obv.iloc[-1]) else None
        except Exception as e:
            logger.error(f"Error calculando OBV: {e}")
            return None
    
    @staticmethod
    def calculate_volume_indicators(df: pd.DataFrame, period: int = 20) -> Dict[str, Optional[float]]:
        """Calcula indicadores basados en volumen"""
        try:
            volume_avg = df['volume'].rolling(window=period).mean().iloc[-1]
            current_volume = df['volume'].iloc[-1]
            
            volume_ratio = None
            if volume_avg > 0:
                volume_ratio = (current_volume / volume_avg) * 100
            
            return {
                'volume_avg_20': float(volume_avg) if not pd.isna(volume_avg) else None,
                'volume_ratio': float(volume_ratio) if volume_ratio and not pd.isna(volume_ratio) else None
            }
        except Exception as e:
            logger.error(f"Error calculando indicadores de volumen: {e}")
            return {'volume_avg_20': None, 'volume_ratio': None}
    
    def calculate_all_indicators(self, candles: List[Dict]) -> Dict:
        """
        Calcula todos los indicadores técnicos
        
        Args:
            candles: Lista de velas (últimas 200 mínimo para cálculos precisos)
            
        Returns:
            Diccionario con todos los indicadores calculados
        """
        try:
            df = self.prepare_dataframe(candles)
            
            if len(df) < 50:
                logger.warning(f"Pocas velas para cálculos precisos: {len(df)} (recomendado: 200+)")
            
            indicators = {}
            
            # RSI
            indicators['rsi_14'] = self.calculate_rsi(df, 14)
            indicators['rsi_7'] = self.calculate_rsi(df, 7)
            
            # MACD
            macd_data = self.calculate_macd(df)
            indicators.update(macd_data)
            
            # EMAs
            indicators['ema_9'] = self.calculate_ema(df, 9)
            indicators['ema_20'] = self.calculate_ema(df, 20)
            indicators['ema_50'] = self.calculate_ema(df, 50)
            indicators['ema_100'] = self.calculate_ema(df, 100)
            indicators['ema_200'] = self.calculate_ema(df, 200)
            
            # SMAs
            indicators['sma_20'] = self.calculate_sma(df, 20)
            indicators['sma_50'] = self.calculate_sma(df, 50)
            indicators['sma_200'] = self.calculate_sma(df, 200)
            
            # Bollinger Bands
            bb_data = self.calculate_bollinger_bands(df)
            indicators.update(bb_data)
            
            # ATR
            indicators['atr'] = self.calculate_atr(df)
            
            # Volumen
            volume_data = self.calculate_volume_indicators(df)
            indicators.update(volume_data)
            
            # Stochastic
            stoch_data = self.calculate_stochastic(df)
            indicators.update(stoch_data)
            
            # ADX
            indicators['adx'] = self.calculate_adx(df)
            
            # CCI
            indicators['cci'] = self.calculate_cci(df)
            
            # Williams %R
            indicators['willr'] = self.calculate_willr(df)
            
            # OBV
            indicators['obv'] = self.calculate_obv(df)
            
            logger.info(f"Indicadores calculados exitosamente para {len(df)} velas")
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculando indicadores: {e}")
            return {}


# Instancia global del calculador
indicator_calculator = IndicatorCalculator()
