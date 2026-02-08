"""
A股数据采集模块
从新浪/东方财富等免费API获取A股数据
"""
import requests
import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StockQuote:
    """股票行情数据"""
    symbol: str
    name: str
    price: float
    change_percent: float
    volume: float
    timestamp: int
    
    @property
    def is_big_drop(self) -> bool:
        """是否大跌"""
        return self.change_percent <= -5.0
    
    @property
    def is_big_rise(self) -> bool:
        """是否大涨"""
        return self.change_percent >= 5.0


class StockDataCollector:
    """A股数据采集器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = "https://hq.sinajs.cn"
        self.session = requests.Session()
        self.session.headers.update({
            'Referer': 'https://finance.sina.com.cn/'
        })
    
    def get_realtime_quote(self, symbol: str) -> Optional[StockQuote]:
        """
        获取单只股票实时行情
        
        Args:
            symbol: 股票代码 (如 'sh.600519')
        
        Returns:
            StockQuote对象或None
        """
        try:
            # 新浪行情API
            params = {'list': symbol}
            response = self.session.get(
                f"{self.base_url}/cn={symbol}",
                params=params,
                timeout=10
            )
            response.encoding = 'gbk'
            
            if response.status_code == 200:
                data = response.text
                return self._parse_sina_response(symbol, data)
            
        except Exception as e:
            logger.error(f"获取{symbol}数据失败: {e}")
        
        return None
    
    def get_batch_quotes(self, symbols: List[str]) -> List[StockQuote]:
        """
        批量获取股票行情
        
        Args:
            symbols: 股票代码列表
        
        Returns:
            StockQuote列表
        """
        quotes = []
        for symbol in symbols:
            quote = self.get_realtime_quote(symbol)
            if quote:
                quotes.append(quote)
            time.sleep(0.1)  # 避免请求过快
        
        return quotes
    
    def _parse_sina_response(self, symbol: str, data: str) -> Optional[StockQuote]:
        """解析新浪行情API响应"""
        try:
            # 格式: var hq_str_sh600519="贵州茅台,1800.00,..."
            parts = data.split('"')
            if len(parts) < 2:
                return None
            
            values = parts[1].split(',')
            if len(values) < 32:
                return None
            
            name = values[0]
            open_price = float(values[1])
            yesterday_close = float(values[2])
            current_price = float(values[3])
            high_price = float(values[4])
            low_price = float(values[5])
            volume = float(values[8])
            
            change_percent = ((current_price - yesterday_close) / yesterday_close) * 100
            
            return StockQuote(
                symbol=symbol,
                name=name,
                price=current_price,
                change_percent=change_percent,
                volume=volume,
                timestamp=int(time.time())
            )
            
        except Exception as e:
            logger.error(f"解析数据失败: {e}")
            return None
    
    def get_market_summary(self) -> Dict:
        """
        获取市场整体情况
        
        Returns:
            市场摘要信息
        """
        # 获取主要指数
        index_symbols = ['sh.000001', 'sz.399001', 'sh.000300']
        quotes = self.get_batch_quotes(index_symbols)
        
        if not quotes:
            return {'status': 'error', 'message': '无法获取市场数据'}
        
        total_change = sum(q.change_percent for q in quotes) / len(quotes)
        
        return {
            'status': 'ok',
            'timestamp': int(time.time()),
            'market_sentiment': self._calculate_sentiment(total_change),
            'indices': [
                {'symbol': q.symbol, 'name': q.name, 'change': q.change_percent}
                for q in quotes
            ],
            'avg_change': total_change
        }
    
    def _calculate_sentiment(self, avg_change: float) -> str:
        """根据平均涨跌幅计算市场情绪"""
        if avg_change >= 3:
            return "极度乐观 🚀"
        elif avg_change >= 1:
            return "乐观 😊"
        elif avg_change >= -1:
            return "中性 😐"
        elif avg_change >= -3:
            return "悲观 😟"
        else:
            return "极度悲观 📉"
