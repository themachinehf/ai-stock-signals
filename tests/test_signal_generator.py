# Tests for signal_generator module
import pytest
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from signal_generator.analyzer import SignalGenerator, SignalType, TradingSignal


class TestTradingSignal:
    """测试TradingSignal类"""
    
    def test_to_dict(self):
        """测试转换为字典"""
        signal = TradingSignal(
            symbol="test",
            name="测试",
            signal_type=SignalType.BIG_RISE,
            current_price=100.0,
            change_percent=5.0,
            analysis="测试分析",
            risk_level="中",
            recommendation="建议买入",
            confidence=0.8,
            timestamp=1234567890
        )
        
        data = signal.to_dict()
        
        assert data['symbol'] == 'test'
        assert data['signal_type'] == '大涨信号'
        assert data['current_price'] == 100.0
        assert data['change_percent'] == 5.0
        assert data['risk_level'] == '中'
        assert data['confidence'] == 0.8
    
    def test_to_telegram_message(self):
        """测试Telegram消息格式"""
        signal = TradingSignal(
            symbol="test",
            name="测试股票",
            signal_type=SignalType.BIG_RISE,
            current_price=100.0,
            change_percent=5.0,
            analysis="这是一条测试分析",
            risk_level="中",
            recommendation="建议观望",
            confidence=0.75,
            timestamp=1234567890
        )
        
        message = signal.to_telegram_message()
        
        assert '🚀' in message
        assert '大涨信号' in message
        assert '测试股票' in message
        assert '100.00' in message
        assert '+5.00%' in message
        assert '建议观望' in message
        assert '⚠️' in message


class TestSignalGenerator:
    """测试SignalGenerator类"""
    
    def test_init(self):
        """测试初始化"""
        config = {'api_key': 'test', 'model': 'test'}
        generator = SignalGenerator(config)
        
        assert generator.api_key == 'test'
        assert generator.model == 'test'
    
    @pytest.mark.asyncio
    async def test_generate_signal_no_llm(self):
        """测试无LLM时的信号生成"""
        # 不配置api_key，测试规则分析
        generator = SignalGenerator({})
        
        # 创建测试quote
        from data_collector.collector import StockQuote
        
        quote = StockQuote(
            symbol="test",
            name="测试",
            price=100.0,
            change_percent=-6.0,
            volume=1000,
            timestamp=1234567890
        )
        
        signal = await generator.generate_signal(quote, None)
        
        assert signal.symbol == 'test'
        assert signal.signal_type == SignalType.BIG_DROP
        assert signal.analysis != ''
    
    def test_calculate_confidence(self):
        """测试置信度计算"""
        generator = SignalGenerator({})
        
        # 测试不同涨跌幅的置信度
        # 这里需要访问私有方法或通过生成信号来测试
        
