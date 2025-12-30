"""
Predictor usando modelos ML entrenados
"""
import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
from loguru import logger

from app.config import settings
from app.ml.feature_engineer import feature_engineer


class MLPredictor:
    """Hace predicciones usando modelos ML"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.model_version = settings.MODEL_VERSION
    
    def load_model(self, model_version: Optional[str] = None) -> bool:
        """
        Carga modelo entrenado
        
        Args:
            model_version: Versión del modelo (default: settings.MODEL_VERSION)
            
        Returns:
            True si carga exitosa, False si no
        """
        try:
            version = model_version or self.model_version
            model_path = Path(settings.MODEL_PATH) / f"model_v{version}.pkl"
            scaler_path = Path(settings.MODEL_PATH) / f"scaler_v{version}.pkl"
            
            if not model_path.exists():
                logger.warning(f"Modelo no encontrado: {model_path}")
                return False
            
            self.model = joblib.load(model_path)
            
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
            
            logger.info(f"Modelo v{version} cargado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            return False
    
    def predict(
        self,
        candles: list,
        indicators: Dict,
        market_context: Optional[Dict] = None,
        current_price: float = None
    ) -> Optional[Dict]:
        """
        Genera predicción usando el modelo ML
        
        Args:
            candles: Lista de velas históricas
            indicators: Indicadores técnicos
            market_context: Contexto del mercado
            current_price: Precio actual
            
        Returns:
            Diccionario con predicción o None si no se puede predecir
        """
        try:
            # Si no hay modelo cargado, intentar cargar
            if self.model is None:
                loaded = self.load_model()
                if not loaded:
                    logger.warning("No hay modelo ML disponible, usando reglas básicas")
                    return self._predict_with_rules(indicators, current_price)
            
            # Crear features
            features = feature_engineer.create_all_features(candles, indicators, market_context)
            
            if not features:
                logger.error("No se pudieron crear features")
                return None
            
            # Convertir a array
            feature_values = list(features.values())
            X = np.array([feature_values])
            
            # Normalizar si hay scaler
            if self.scaler:
                X = self.scaler.transform(X)
            
            # Predecir
            prediction = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            
            # Convertir predicción a tipo
            pred_type = self._convert_prediction_to_type(prediction)
            
            # Calcular confidence
            confidence = float(max(probabilities) * 100)
            
            # Calcular stop loss y take profit
            atr = indicators.get('atr', 0)
            if current_price and atr:
                stop_loss, take_profit = self._calculate_levels(current_price, pred_type, atr)
            else:
                stop_loss, take_profit = None, None
            
            result = {
                'type': pred_type,
                'confidence': confidence,
                'features_used': features,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'model_version': self.model_version
            }
            
            logger.info(f"Predicción: {pred_type} (conf: {confidence:.2f}%)")
            return result
            
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            # Fallback a reglas básicas
            return self._predict_with_rules(indicators, current_price)
    
    def _predict_with_rules(self, indicators: Dict, current_price: Optional[float]) -> Optional[Dict]:
        """
        Predicción basada en reglas simples (fallback si no hay modelo ML)
        
        Args:
            indicators: Indicadores técnicos
            current_price: Precio actual
            
        Returns:
            Predicción basada en reglas o None
        """
        try:
            rsi = indicators.get('rsi_14', 50)
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            ema_20 = indicators.get('ema_20', 0)
            ema_50 = indicators.get('ema_50', 0)
            
            score = 0
            reasons = []
            
            # RSI
            if rsi < 30:
                score += 2
                reasons.append("RSI oversold")
            elif rsi > 70:
                score -= 2
                reasons.append("RSI overbought")
            
            # MACD
            if macd > macd_signal:
                score += 1
                reasons.append("MACD bullish")
            elif macd < macd_signal:
                score -= 1
                reasons.append("MACD bearish")
            
            # EMAs
            if ema_20 > ema_50:
                score += 1
                reasons.append("EMA 20>50")
            elif ema_20 < ema_50:
                score -= 1
                reasons.append("EMA 20<50")
            
            # Determinar tipo
            if score >= 2:
                pred_type = "LONG"
                confidence = min(60 + (score * 5), 75)
            elif score <= -2:
                pred_type = "SHORT"
                confidence = min(60 + (abs(score) * 5), 75)
            else:
                pred_type = "NEUTRAL"
                confidence = 50
            
            # Calcular niveles
            atr = indicators.get('atr', 0)
            if current_price and atr:
                stop_loss, take_profit = self._calculate_levels(current_price, pred_type, atr)
            else:
                stop_loss, take_profit = None, None
            
            return {
                'type': pred_type,
                'confidence': float(confidence),
                'features_used': {'rules': reasons},
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'model_version': 'rules-based'
            }
            
        except Exception as e:
            logger.error(f"Error en predicción con reglas: {e}")
            return None
    
    @staticmethod
    def _convert_prediction_to_type(prediction: int) -> str:
        """Convierte predicción numérica a tipo"""
        if prediction == 1:
            return "LONG"
        elif prediction == -1:
            return "SHORT"
        else:
            return "NEUTRAL"
    
    @staticmethod
    def _calculate_levels(current_price: float, pred_type: str, atr: float) -> Tuple[float, float]:
        """
        Calcula stop loss y take profit basado en ATR
        
        Args:
            current_price: Precio actual
            pred_type: Tipo de predicción (LONG/SHORT)
            atr: Average True Range
            
        Returns:
            (stop_loss, take_profit)
        """
        multiplier = 1.5  # Multiplicador de ATR para stop loss
        risk_reward = 1.5  # Risk/Reward ratio
        
        if pred_type == "LONG":
            stop_loss = current_price - (atr * multiplier)
            distance = current_price - stop_loss
            take_profit = current_price + (distance * risk_reward)
        elif pred_type == "SHORT":
            stop_loss = current_price + (atr * multiplier)
            distance = stop_loss - current_price
            take_profit = current_price - (distance * risk_reward)
        else:
            stop_loss = current_price - (atr * multiplier)
            take_profit = current_price + (atr * multiplier)
        
        return round(stop_loss, 2), round(take_profit, 2)


# Instancia global del predictor
ml_predictor = MLPredictor()
