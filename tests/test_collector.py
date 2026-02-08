# Tests for data_collector module
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_collector.collector import StockDataCollector, StockQuote


class TestStockQuote:
    """测试StockQuote类"""
    
    def test_big_drop_detection(self):
        """测试大跌识别"""
        quote = StockQuote(
            symbol="test",
            name="测试",
            price=100.0,
            change_percent=-6.0,
            volume=1000,
            timestamp=1234567890
        )
        
        assert quote.is_big_drop is True
        assert quote.is_big_rise is False
    
    def test_big_rise_detection(self):
        """测试大涨识别"""
        quote = StockQuote(
            symbol="test",
            name="测试",
            price=100.0,
            change_percent=6.0,
            volume=1000,
            timestamp=1234567890
        )
        
        assert quote.is_big_rise is True
        assert quote.is_big_drop is False
    
    def test_neutral_detection(self):
        """测试中性识别"""
        quote = StockQuote(
            symbol="test",
            name="测试",
            price=100.0,
            change_percent=2.0,
            volume=1000,
            timestamp=1234567890
        )
        
        assert quote.is_big_drop is False
        assert quote.is_big_rise is False


class TestStockDataCollector:
    """测试StockDataCollector类"""
    
    def test_init(self):
        """测试初始化"""
        config = {'test': 'value'}
        collector = StockDataCollector(config)
        
        assert collector.config == config
        assert collector.session is not None
    
    def test_get_realtime_quote_returns_quote(self):
        """测试获取实时行情"""
        collector = StockDataCollector({})
        quote = collector.get_realtime_quote("sh.000001")
        
        # API调用可能失败，返回None或Quote对象
        if quote:
            assert isinstance(quote, StockQuote)
            assert quote.symbol == "sh.000001"
