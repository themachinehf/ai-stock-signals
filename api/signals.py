from fastapi import APIRouter
from typing import List
import sys
sys.path.insert(0, '.')

router = APIRouter()

@router.get("/signals")
async def get_signals():
    """获取所有信号"""
    # 这里可以添加信号获取逻辑
    return {
        'status': 'ok',
        'message': 'Signal generation API ready',
        'watchlist': [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT',
            'XRP/USDT', 'ADA/USDT', 'DOGE/USDT', 'MATIC/USDT',
            'LTC/USDT', 'LINK/USDT'
        ]
    }

@router.get("/signals/{symbol}")
async def get_symbol_signal(symbol: str):
    """获取单个币种信号"""
    from data_collector import CryptoDataCollector
    from signal_generator import CryptoSignalGenerator
    
    collector = CryptoDataCollector({'exchange': 'binance'})
    generator = CryptoSignalGenerator({})
    
    quote = await collector.get_realtime_price(symbol.upper())
    
    if quote:
        signal = await generator.generate_signal(quote)
        return signal.to_dict()
    
    return {'error': 'Symbol not found'}
