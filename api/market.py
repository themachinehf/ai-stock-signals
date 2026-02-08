from fastapi import APIRouter
from typing import Dict
import sys
sys.path.insert(0, '.')

router = APIRouter()

@router.get("/market")
async def get_market():
    """获取市场摘要"""
    from data_collector import CryptoDataCollector
    
    collector = CryptoDataCollector({'exchange': 'binance'})
    summary = await collector.get_market_summary()
    
    return summary

@router.get("/price/{symbol}")
async def get_price(symbol: str):
    """获取单个币种价格"""
    from data_collector import CryptoDataCollector
    
    collector = CryptoDataCollector({'exchange': 'binance'})
    quote = await collector.get_realtime_price(symbol.upper())
    
    if quote:
        return {
            'symbol': quote.symbol,
            'price': quote.price,
            'change_24h': quote.change_percent,
            'high_24h': quote.high_24h,
            'low_24h': quote.low_24h,
            'volume': quote.volume_24h,
            'volatility': quote.volatility
        }
    return {'error': 'Symbol not found'}
