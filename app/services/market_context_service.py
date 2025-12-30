"""
Servicio de contexto del mercado
Obtiene datos de APIs externas (Fear & Greed, Dominance, etc.)
"""
import httpx
from typing import Optional, Dict
from loguru import logger
from sqlalchemy.orm import Session
import time

from app.config import settings
from app.models.market_context import MarketContext, MarketRegimeEnum


class MarketContextService:
    """Servicio para obtener y guardar contexto del mercado"""
    
    async def fetch_fear_greed_index(self) -> Optional[Dict]:
        """
        Obtiene Fear & Greed Index de la API
        
        Returns:
            Diccionario con índice y clasificación o None
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    settings.FEAR_GREED_API_URL,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'data' in data and len(data['data']) > 0:
                        latest = data['data'][0]
                        
                        return {
                            'value': int(latest['value']),
                            'classification': latest['value_classification']
                        }
                
                logger.warning("No se pudo obtener Fear & Greed Index")
                return None
                
        except Exception as e:
            logger.error(f"Error obteniendo Fear & Greed Index: {e}")
            return None
    
    async def fetch_market_data(self) -> Optional[Dict]:
        """
        Obtiene datos generales del mercado (dominance, market cap, etc.)
        Nota: Se puede integrar con CoinGecko API o similar
        
        Returns:
            Diccionario con datos del mercado
        """
        try:
            # Placeholder - Integrar con CoinGecko o API similar
            # Por ahora retorna valores dummy
            
            return {
                'btc_dominance': 52.5,
                'eth_dominance': 17.3,
                'total_market_cap': 1750000000000,  # 1.75T
                'total_volume_24h': 85000000000  # 85B
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo datos del mercado: {e}")
            return None
    
    def determine_market_regime(self, btc_price_change_30d: float, volatility: float) -> MarketRegimeEnum:
        """
        Determina el régimen del mercado basado en cambios de precio y volatilidad
        
        Args:
            btc_price_change_30d: Cambio de precio de BTC en 30 días (%)
            volatility: Volatilidad (ATR o similar)
            
        Returns:
            Enum de régimen de mercado
        """
        try:
            if volatility > 5:  # Alta volatilidad
                return MarketRegimeEnum.VOLATILE
            elif btc_price_change_30d > 10:  # Subida fuerte
                return MarketRegimeEnum.BULL
            elif btc_price_change_30d < -10:  # Caída fuerte
                return MarketRegimeEnum.BEAR
            else:  # Movimiento lateral
                return MarketRegimeEnum.SIDEWAYS
                
        except Exception as e:
            logger.error(f"Error determinando régimen: {e}")
            return MarketRegimeEnum.UNKNOWN
    
    async def get_and_save_context(self, db: Session) -> Optional[MarketContext]:
        """
        Obtiene el contexto completo del mercado y lo guarda en la BD
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            MarketContext guardado o None
        """
        try:
            # Obtener Fear & Greed
            fear_greed = await self.fetch_fear_greed_index()
            
            # Obtener datos del mercado
            market_data = await self.fetch_market_data()
            
            if not market_data:
                logger.warning("No se pudieron obtener datos del mercado")
                return None
            
            # Determinar régimen (simplificado por ahora)
            regime = MarketRegimeEnum.UNKNOWN
            
            # Crear contexto
            context = MarketContext(
                timestamp=int(time.time() * 1000),
                btc_dominance=market_data.get('btc_dominance'),
                eth_dominance=market_data.get('eth_dominance'),
                total_market_cap=market_data.get('total_market_cap'),
                total_volume_24h=market_data.get('total_volume_24h'),
                fear_greed_index=fear_greed['value'] if fear_greed else None,
                fear_greed_classification=fear_greed['classification'] if fear_greed else None,
                market_regime=regime
            )
            
            db.add(context)
            db.commit()
            db.refresh(context)
            
            logger.info(f"Contexto de mercado guardado: F&G={context.fear_greed_index}, Regime={regime.value}")
            return context
            
        except Exception as e:
            logger.error(f"Error obteniendo/guardando contexto: {e}")
            db.rollback()
            return None
    
    def get_latest_context(self, db: Session) -> Optional[MarketContext]:
        """
        Obtiene el último contexto guardado en la base de datos
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Último MarketContext o None
        """
        try:
            context = db.query(MarketContext).order_by(
                MarketContext.timestamp.desc()
            ).first()
            
            return context
            
        except Exception as e:
            logger.error(f"Error obteniendo último contexto: {e}")
            return None


# Instancia global del servicio
market_context_service = MarketContextService()
