"""
加密货币数据采集模块
从Binance、OKX、CoinGecko等交易所获取数据
"""
import ccxt
import asyncio
import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class CryptoQuote:
    """加密货币行情数据"""
    symbol: str          # 如 BTC/USDT
    base_symbol: str    # BTC
    quote_symbol: str  # USDT
    price: float
    change_percent: float
    high_24h: float
    low_24h: float
    volume_24h: float
    volume_quote_24h: float
    timestamp: int
    
    # 额外指标
    bid: float = 0.0    # 买一价
    ask: float = 0.0    # 卖一价
    spread: float = 0.0
    
    # 异动标志
    @property
    def is_big_drop(self) -> bool:
        """是否大跌 (≥5%)"""
        return self.change_percent <= -5.0
    
    @property
    def is_big_rise(self) -> bool:
        """是否大涨 (≥5%)"""
        return self.change_percent >= 5.0
    
    @property
    def is_extreme_drop(self) -> bool:
        """是否暴跌 (≥10%)"""
        return self.change_percent <= -10.0
    
    @property
    def is_extreme_rise(self) -> bool:
        """是否暴涨 (≥10%)"""
        return self.change_percent >= 10.0
    
    @property
    def volatility(self) -> float:
        """波动率"""
        if self.low_24h == 0:
            return 0.0
        return ((self.high_24h - self.low_24h) / self.low_24h) * 100


@dataclass
class OHLCVData:
    """K线数据"""
    symbol: str
    timeframe: str
    timestamps: List[int]
    opens: List[float]
    highs: List[float]
    lows: List[float]
    closes: List[float]
    volumes: List[float]


class CryptoDataCollector:
    """加密货币数据采集器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.exchange_name = config.get('exchange', 'binance')
        self.timeframes = config.get('timeframes', ['1h', '4h', '1d'])
        
        # 初始化交易所
        self.exchange = self._init_exchange()
        
        # 缓存
        self._price_cache = {}
        self._cache_time = 0
        self._cache_ttl = config.get('cache_ttl', 10)  # 缓存10秒
    
    def _init_exchange(self) -> ccxt.Exchange:
        """初始化交易所"""
        exchange_config = {
            'enableRateLimit': True,
            'timeout': 30000,
            # 代理配置 - 解决国内访问问题
            'proxies': {
                'http': 'http://127.0.0.1:7890',
                'https': 'http://127.0.0.1:7890',
            }
        }
        
        # API密钥配置（可选）
        if self.config.get('api_key'):
            exchange_config['apiKey'] = self.config['api_key']
        if self.config.get('secret'):
            exchange_config['secret'] = self.config['secret']
        
        exchange_class = getattr(ccxt, self.exchange_name, None)
        if not exchange_class:
            logger.warning(f"交易所 {self.exchange_name} 不支持，使用binance")
            exchange_class = ccxt.binance
        
        return exchange_class(exchange_config)
    
    async def get_realtime_price(self, symbol: str) -> Optional[CryptoQuote]:
        """
        获取单币种实时行情
        
        Args:
            symbol: 交易对 (如 'BTC/USDT')
        
        Returns:
            CryptoQuote对象或None
        """
        try:
            # 使用ticker API获取24小时统计
            ticker = self.exchange.fetch_ticker(symbol)
            
            return self._parse_ticker(symbol, ticker)
            
        except Exception as e:
            logger.error(f"获取{symbol}数据失败: {e}")
            return None
    
    async def get_batch_prices(self, symbols: List[str]) -> List[CryptoQuote]:
        """
        批量获取币种行情
        
        Args:
            symbols: 交易对列表
        
        Returns:
            CryptoQuote列表
        """
        quotes = []
        
        # 使用fetch_tickers批量获取
        try:
            tickers = self.exchange.fetch_tickers(symbols)
            
            for symbol, ticker in tickers.items():
                if ticker:
                    quote = self._parse_ticker(symbol, ticker)
                    if quote:
                        quotes.append(quote)
        
        except Exception as e:
            logger.error(f"批量获取数据失败: {e}")
            # 降级为单次获取
            for symbol in symbols:
                quote = await self.get_realtime_price(symbol)
                if quote:
                    quotes.append(quote)
        
        return quotes
    
    def _parse_ticker(self, symbol: str, ticker: Dict) -> CryptoQuote:
        """解析交易所ticker数据"""
        # 分离基础币种和计价币种
        parts = symbol.split('/')
        base_symbol = parts[0] if len(parts) > 1 else symbol
        quote_symbol = parts[1] if len(parts) > 1 else 'USDT'
        
        # 计算24小时涨跌幅
        open_price = ticker.get('open', 0)
        close_price = ticker.get('last', ticker.get('close', 0))
        
        change_percent = 0.0
        if open_price and open_price != 0:
            change_percent = ((close_price - open_price) / open_price) * 100
        
        # 计算买卖价差
        bid = ticker.get('bid', 0)
        ask = ticker.get('ask', 0)
        spread = 0.0
        if bid and ask and ask != 0:
            spread = ((ask - bid) / ask) * 100
        
        return CryptoQuote(
            symbol=symbol,
            base_symbol=base_symbol,
            quote_symbol=quote_symbol,
            price=close_price,
            change_percent=change_percent,
            high_24h=ticker.get('high', 0),
            low_24h=ticker.get('low', 0),
            volume_24h=ticker.get('baseVolume', 0),
            volume_quote_24h=ticker.get('quoteVolume', 0),
            timestamp=int(time.time()),
            bid=bid,
            ask=ask,
            spread=spread
        )
    
    async def get_ohlcv(self, symbol: str, timeframe: str = '1h', 
                        limit: int = 100) -> Optional[OHLCVData]:
        """
        获取K线数据
        
        Args:
            symbol: 交易对
            timeframe: 时间周期 (1m, 5m, 15m, 1h, 4h, 1d, 1w)
            limit: 数量限制
        
        Returns:
            OHLCVData对象或None
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(
                symbol, 
                timeframe=timeframe, 
                limit=limit
            )
            
            if not ohlcv:
                return None
            
            # 分离数据
            timestamps = [k[0] for k in ohlcv]
            opens = [k[1] for k in ohlcv]
            highs = [k[2] for k in ohlcv]
            lows = [k[3] for k in ohlcv]
            closes = [k[4] for k in ohlcv]
            volumes = [k[5] for k in ohlcv]
            
            return OHLCVData(
                symbol=symbol,
                timeframe=timeframe,
                timestamps=timestamps,
                opens=opens,
                highs=highs,
                lows=lows,
                closes=closes,
                volumes=volumes
            )
            
        except Exception as e:
            logger.error(f"获取{symbol} K线失败 ({timeframe}): {e}")
            return None
    
    async def get_market_summary(self) -> Dict:
        """
        获取市场整体情况
        
        Returns:
            市场摘要信息
        """
        try:
            # 获取BTC价格作为市场情绪指标
            btc_quote = await self.get_realtime_price('BTC/USDT')
            
            # 获取主要币种
            major_symbols = [
                'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 
                'XRP/USDT', 'ADA/USDT', 'SOL/USDT'
            ]
            major_quotes = await self.get_batch_prices(major_symbols)
            
            if not major_quotes:
                return {'status': 'error', 'message': '无法获取市场数据'}
            
            # 计算平均涨跌幅
            avg_change = sum(q.change_percent for q in major_quotes) / len(major_quotes)
            
            # 统计涨跌情况
            gainers = sum(1 for q in major_quotes if q.change_percent > 0)
            losers = len(major_quotes) - gainers
            
            # 检查是否有极端行情
            extremes = [q for q in major_quotes if q.is_extreme_rise or q.is_extreme_drop]
            
            return {
                'status': 'ok',
                'timestamp': int(time.time()),
                'btc_price': btc_quote.price if btc_quote else 0,
                'btc_change': btc_quote.change_percent if btc_quote else 0,
                'market_sentiment': self._calculate_sentiment(avg_change),
                'major_coins': [
                    {
                        'symbol': q.symbol,
                        'price': q.price,
                        'change': q.change_percent,
                        'volatility': q.volatility
                    }
                    for q in major_quotes
                ],
                'summary': {
                    'avg_change': avg_change,
                    'gainers': gainers,
                    'losers': losers,
                    'extremes': len(extremes)
                }
            }
            
        except Exception as e:
            logger.error(f"获取市场摘要失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _calculate_sentiment(self, avg_change: float) -> str:
        """根据平均涨跌幅计算市场情绪"""
        if avg_change >= 5:
            return "极度乐观 🚀"
        elif avg_change >= 2:
            return "乐观 😊"
        elif avg_change >= -2:
            return "中性 😐"
        elif avg_change >= -5:
            return "悲观 😟"
        else:
            return "极度悲观 📉"
    
    async def get_trending(self, limit: int = 10) -> List[Dict]:
        """
        获取24小时热门币种（按交易量）
        
        Returns:
            热门币种列表
        """
        try:
            # 获取所有ticker
            tickers = self.exchange.fetch_tickers()
            
            # 按交易量排序
            sorted_tickers = sorted(
                tickers.items(),
                key=lambda x: x[1].get('quoteVolume', 0),
                reverse=True
            )
            
            # 取前N个
            top_tickers = sorted_tickers[:limit]
            
            return [
                {
                    'symbol': symbol,
                    'price': ticker.get('last', 0),
                    'change': self._calc_change(ticker),
                    'volume': ticker.get('quoteVolume', 0)
                }
                for symbol, ticker in top_tickers
            ]
            
        except Exception as e:
            logger.error(f"获取热门币种失败: {e}")
            return []
    
    def _calc_change(self, ticker: Dict) -> float:
        """计算涨跌幅"""
        open_price = ticker.get('open', 0)
        close_price = ticker.get('last', ticker.get('close', 0))
        
        if open_price and open_price != 0:
            return ((close_price - open_price) / open_price) * 100
        return 0.0
    
    async def get_order_book(self, symbol: str, limit: int = 10) -> Optional[Dict]:
        """
        获取订单簿
        
        Args:
            symbol: 交易对
            limit: 深度
        
        Returns:
            订单簿数据
        """
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit=limit)
            
            return {
                'symbol': symbol,
                'bids': orderbook.get('bids', [])[:limit],
                'asks': orderbook.get('asks', [])[:limit],
                'timestamp': orderbook.get('timestamp', 0)
            }
            
        except Exception as e:
            logger.error(f"获取订单簿失败: {e}")
            return None


class CoinGeckoCollector:
    """CoinGecko基本面数据采集器（免费API）"""
    
    def __init__(self, config: Dict = {}):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = None
    
    def _get_session(self):
        if not self.session:
            import requests
            self.session = requests.Session()
        return self.session
    
    def get_market_data(self, vs_currency: str = 'usd', limit: int = 100) -> List[Dict]:
        """
        获取市场数据
        
        Args:
            vs_currency: 计价货币
            limit: 返回数量
        
        Returns:
            市场数据列表
        """
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': vs_currency,
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': False,
                'price_change_percentage': '24h'
            }
            
            session = self._get_session()
            response = session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"获取CoinGecko数据失败: {e}")
            return []
    
    def get_coin_info(self, coin_id: str) -> Optional[Dict]:
        """
        获取单个币种信息
        
        Args:
            coin_id: CoinGecko币种ID (如 'bitcoin')
        
        Returns:
            币种信息
        """
        try:
            url = f"{self.base_url}/coins/{coin_id}"
            params = {
                'localization': False,
                'tickers': False,
                'market_data': True,
                'community_data': False,
                'developer_data': False
            }
            
            session = self._get_session()
            response = session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"获取{coin_id}信息失败: {e}")
            return None
