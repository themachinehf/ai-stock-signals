"""
AI信号生成模块
使用LLM分析市场数据生成交易信号
"""
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class SignalType(Enum):
    """信号类型"""
    BIG_DROP = "大跌预警"
    BIG_RISE = "大涨信号"
    NEUTRAL = "中性"

@dataclass
class TradingSignal:
    """交易信号"""
    symbol: str
    name: str
    signal_type: SignalType
    current_price: float
    change_percent: float
    analysis: str
    risk_level: str  # 低/中/高
    recommendation: str  # 建议操作
    confidence: float  # 置信度 0-1
    timestamp: int
    disclaimer: str = "⚠️ 本信号仅供参考，不构成投资建议"
    
    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'name': self.name,
            'signal_type': self.signal_type.value,
            'current_price': self.current_price,
            'change_percent': self.change_percent,
            'analysis': self.analysis,
            'risk_level': self.risk_level,
            'recommendation': self.recommendation,
            'confidence': self.confidence,
            'timestamp': datetime.fromtimestamp(self.timestamp).isoformat(),
            'disclaimer': self.disclaimer
        }
    
    def to_telegram_message(self) -> str:
        """生成Telegram消息格式"""
        emoji = {
            SignalType.BIG_DROP: "📉",
            SignalType.BIG_RISE: "🚀",
            SignalType.NEUTRAL: "📊"
        }[self.signal_type]
        
        risk_emoji = {
            "低": "🟢",
            "中": "🟡",
            "高": "🔴"
        }[self.risk_level]
        
        message = f"""
{emoji} **{self.signal_type.value}**

*{self.name}* ({self.symbol})
💰 当前价格: {self.current_price:.2f}
📊 涨跌幅: {self.change_percent:+.2f}%

**AI分析:**
{self.analysis}

{risk_emoji} 风险等级: {self.risk_level}
💡 建议: {self.recommendation}
📈 置信度: {self.confidence:.0%}

---
{self.disclaimer}
"""
        return message


class SignalGenerator:
    """AI信号生成器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.api_key = config.get('api_key')
        self.model = config.get('model', 'gpt-4o-mini')
        self.base_url = config.get('base_url', 'https://api.openai.com/v1')
    
    async def generate_signal(self, stock_quote, market_context: Dict = None) -> TradingSignal:
        """
        为单只股票生成交易信号
        
        Args:
            stock_quote: 股票行情数据
            market_context: 市场上下文信息
        
        Returns:
            TradingSignal对象
        """
        # 基础分析
        if stock_quote.is_big_drop:
            signal_type = SignalType.BIG_DROP
        elif stock_quote.is_big_rise:
            signal_type = SignalType.BIG_RISE
        else:
            signal_type = SignalType.NEUTRAL
        
        # 使用LLM进行深度分析
        analysis = await self._analyze_with_llm(stock_quote, signal_type, market_context)
        
        # 计算风险等级和置信度
        risk_level, recommendation = self._assess_risk(stock_quote, signal_type, analysis)
        confidence = self._calculate_confidence(stock_quote, signal_type)
        
        return TradingSignal(
            symbol=stock_quote.symbol,
            name=stock_quote.name,
            signal_type=signal_type,
            current_price=stock_quote.price,
            change_percent=stock_quote.change_percent,
            analysis=analysis,
            risk_level=risk_level,
            recommendation=recommendation,
            confidence=confidence,
            timestamp=stock_quote.timestamp
        )
    
    async def generate_signals_batch(self, quotes: List, market_context: Dict = None) -> List[TradingSignal]:
        """批量生成信号"""
        signals = []
        for quote in quotes:
            signal = await self.generate_signal(quote, market_context)
            signals.append(signal)
        return signals
    
    async def _analyze_with_llm(self, quote, signal_type: SignalType, context: Dict = None) -> str:
        """
        使用LLM分析市场数据
        
        Args:
            quote: 股票行情
            signal_type: 信号类型
            context: 市场上下文
        
        Returns:
            分析文本
        """
        # 如果没有API key，使用规则分析
        if not self.api_key:
            return self._rule_based_analysis(quote, signal_type)
        
        try:
            # 构建prompt
            prompt = self._build_prompt(quote, signal_type, context)
            
            # 调用LLM (示例使用OpenAI格式)
            # 实际实现时需要根据provider调整
            response = await self._call_llm(prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"LLM分析失败: {e}")
            return self._rule_based_analysis(quote, signal_type)
    
    def _build_prompt(self, quote, signal_type: SignalType, context: Dict = None) -> str:
        """构建LLM prompt"""
        context_str = ""
        if context:
            context_str = f"""
市场整体情况:
- 市场情绪: {context.get('market_sentiment', '未知')}
- 平均涨跌幅: {context.get('avg_change', 0):.2f}%
"""
        
        prompt = f"""
作为专业的A股分析师，请分析以下股票:

股票: {quote.name} ({quote.symbol})
当前价格: {quote.price:.2f}
涨跌幅: {quote.change_percent:+.2f}%
信号类型: {signal_type.value}
{context_str}

请提供:
1. 简要分析 (2-3句话)
2. 可能的驱动因素

请保持专业、客观。
"""
        return prompt
    
    async def _call_llm(self, prompt: str) -> str:
        """调用LLM API"""
        import openai
        
        client = openai.AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def _rule_based_analysis(self, quote, signal_type: SignalType) -> str:
        """基于规则的分析（无LLM时使用）"""
        if signal_type == SignalType.BIG_DROP:
            if quote.change_percent <= -7:
                return "股价大幅下跌超过7%，可能存在恐慌性抛售。建议关注是否有重大利空消息。"
            elif quote.change_percent <= -5:
                return "股价跌幅较大，需关注市场整体走势和资金流向。"
            else:
                return "股价出现明显下跌，建议保持谨慎。"
        elif signal_type == SignalType.BIG_RISE:
            if quote.change_percent >= 7:
                return "股价大幅上涨超过7%，可能有重大利好支撑，谨慎追高。"
            elif quote.change_percent >= 5:
                return "股价涨幅较大，需关注成交量是否配合。"
            else:
                return "股价表现活跃，可关注后续走势。"
        else:
            return "股价运行平稳，未出现明显异动。"
    
    def _assess_risk(self, quote, signal_type: SignalType, analysis: str) -> tuple:
        """评估风险等级和建议"""
        if signal_type == SignalType.BIG_DROP:
            if quote.change_percent <= -7:
                return "高", "建议观望，谨慎抄底"
            elif quote.change_percent <= -5:
                return "中高", "建议谨慎，暂不入场"
            else:
                return "中", "建议观察，等待企稳"
        elif signal_type == SignalType.BIG_RISE:
            if quote.change_percent >= 7:
                return "高", "建议观望，谨慎追高"
            elif quote.change_percent >= 5:
                return "中高", "建议谨慎，避免追涨"
            else:
                return "中", "建议观察，趋势确认后操作"
        else:
            return "低", "建议观望，等待机会"
    
    def _calculate_confidence(self, quote, signal_type: SignalType) -> float:
        """计算信号置信度"""
        # 基于涨跌幅绝对值计算置信度
        abs_change = abs(quote.change_percent)
        
        if abs_change >= 7:
            return 0.85
        elif abs_change >= 5:
            return 0.75
        elif abs_change >= 3:
            return 0.60
        else:
            return 0.40
