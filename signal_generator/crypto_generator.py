"""
加密货币AI信号生成模块
使用LLM分析K线和链上数据生成交易信号
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
    BIG_DROP = "大跌预警"  # 跌≥5%
    BIG_RISE = "大涨信号"  # 涨≥5%
    EXTREME_DROP = "暴跌警示"  # 跌≥10%
    EXTREME_RISE = "暴涨预警"  # 涨≥10%
    VOLUME_SPIKE = "成交量异动"
    NEUTRAL = "中性"


class Position(Enum):
    """仓位建议"""
    LONG = "多"
    SHORT = "空"
    HOLD = "观望"


@dataclass
class CryptoSignal:
    """加密货币交易信号"""
    symbol: str              # BTC/USDT
    base_symbol: str         # BTC
    signal_type: SignalType
    position: Position
    entry_price: float       # 当前价格作为参考
    current_price: float
    change_percent: float
    volatility: float        # 24h波动率
    timestamp: int
    
    # AI分析
    analysis: str            # 详细分析
    key_levels: Dict         # 关键价位
    risk_level: str         # 低/中/高/极高
    recommendation: str     # 操作建议
    
    # 可选字段
    stop_loss: float = None   # 止损位
    take_profit: float = None # 止盈位
    leverage: int = 1       # 建议杠杆倍数
    confidence: float = 0.5       # 置信度 0-1
    
    # 风险提示
    disclaimer: str = "⚠️ 加密货币是高风险投资，本信号仅供参考，不构成投资建议 DYOR"
    
    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'base_symbol': self.base_symbol,
            'signal_type': self.signal_type.value,
            'position': self.position.value,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'change_percent': self.change_percent,
            'volatility': self.volatility,
            'analysis': self.analysis,
            'key_levels': self.key_levels,
            'risk_level': self.risk_level,
            'recommendation': self.recommendation,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'leverage': self.leverage,
            'confidence': self.confidence,
            'timestamp': datetime.fromtimestamp(self.timestamp).isoformat(),
            'disclaimer': self.disclaimer
        }
    
    def to_telegram_message(self) -> str:
        """生成Telegram消息格式"""
        emoji = {
            SignalType.BIG_DROP: "📉",
            SignalType.BIG_RISE: "🚀",
            SignalType.EXTREME_DROP: "🔻",
            SignalType.EXTREME_RISE: "🔺",
            SignalType.VOLUME_SPIKE: "⚡",
            SignalType.NEUTRAL: "📊"
        }[self.signal_type]
        
        position_emoji = {
            Position.LONG: "🟢",
            Position.SHORT: "🔴",
            Position.HOLD: "🟡"
        }[self.position]
        
        risk_emoji = {
            "低": "🟢",
            "中": "🟡",
            "高": "🟠",
            "极高": "🔴"
        }[self.risk_level]
        
        message = f"""
{emoji} **{self.signal_type.value}** | {position_emoji} **{self.position.value}**

*{self.base_symbol}* ({self.symbol})
💰 当前价格: ${self.current_price:,.2f}
📊 24h涨跌: {self.change_percent:+.2f}%
📈 24h波动: {self.volatility:.2f}%

**AI技术分析:**
{self.analysis}

**关键价位:**
• 入场参考: ${self.entry_price:,.2f}
• 止损: ${self.stop_loss:,.2f}" if self.stop_loss else ""
• 止盈: ${self.take_profit:,.2f}" if self.take_profit else ""

**风险/建议:**
{risk_emoji} 风险等级: {self.risk_level}
💡 建议杠杆: {self.leverage}x
💡 操作: {self.recommendation}
📈 置信度: {self.confidence:.0%}

---
🔴 **{self.disclaimer}**
"""
        return message


class CryptoSignalGenerator:
    """加密货币AI信号生成器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.api_key = config.get('api_key')
        self.model = config.get('model', 'gpt-4o-mini')
        self.base_url = config.get('base_url', 'https://api.openai.com/v1')
    
    async def generate_signal(self, quote, ohlcv: Dict = None, 
                              market_context: Dict = None) -> CryptoSignal:
        """
        为单个币种生成交易信号
        
        Args:
            quote: CryptoQuote对象
            ohlcv: K线数据（可选）
            market_context: 市场上下文
        
        Returns:
            CryptoSignal对象
        """
        # 确定信号类型
        signal_type = self._determine_signal_type(quote)
        
        # 确定仓位方向
        position = self._determine_position(quote, signal_type)
        
        # 生成分析
        analysis = await self._analyze(quote, ohlcv, market_context, signal_type)
        
        # 计算关键价位
        key_levels = self._calculate_levels(quote)
        
        # 评估风险
        risk_level, recommendation = self._assess_risk(quote, signal_type, position, analysis)
        
        # 计算置信度
        confidence = self._calculate_confidence(quote, signal_type)
        
        # 计算止盈止损
        stop_loss, take_profit = self._calc_sl_tp(quote, position, risk_level)
        
        # 建议杠杆
        leverage = self._suggest_leverage(risk_level)
        
        return CryptoSignal(
            symbol=quote.symbol,
            base_symbol=quote.base_symbol,
            signal_type=signal_type,
            position=position,
            entry_price=quote.price,
            current_price=quote.price,
            change_percent=quote.change_percent,
            volatility=quote.volatility,
            analysis=analysis,
            key_levels=key_levels,
            risk_level=risk_level,
            recommendation=recommendation,
            stop_loss=stop_loss,
            take_profit=take_profit,
            leverage=leverage,
            confidence=confidence,
            timestamp=quote.timestamp
        )
    
    def _determine_signal_type(self, quote) -> SignalType:
        """确定信号类型"""
        if quote.is_extreme_rise:
            return SignalType.EXTREME_RISE
        elif quote.is_extreme_drop:
            return SignalType.EXTREME_DROP
        elif quote.is_big_rise:
            return SignalType.BIG_RISE
        elif quote.is_big_drop:
            return SignalType.BIG_DROP
        elif quote.volume_24h > quote.price * 1e8:  # 大成交量
            return SignalType.VOLUME_SPIKE
        else:
            return SignalType.NEUTRAL
    
    def _determine_position(self, quote, signal_type: SignalType) -> Position:
        """确定仓位方向"""
        if signal_type in [SignalType.EXTREME_RISE, SignalType.BIG_RISE]:
            return Position.HOLD  # 追高风险大，建议观望
        elif signal_type in [SignalType.EXTREME_DROP, SignalType.BIG_DROP]:
            return Position.HOLD  # 抄底需谨慎
        elif signal_type == SignalType.VOLUME_SPIKE:
            return Position.LONG if quote.change_percent > 0 else Position.SHORT
        else:
            return Position.HOLD
    
    async def _analyze(self, quote, ohlcv: Dict, context: Dict, 
                       signal_type: SignalType) -> str:
        """生成AI分析"""
        if not self.api_key:
            return self._rule_based_analysis(quote, signal_type)
        
        try:
            prompt = self._build_prompt(quote, ohlcv, context, signal_type)
            response = await self._call_llm(prompt)
            return response
        except Exception as e:
            logger.error(f"LLM分析失败: {e}")
            return self._rule_based_analysis(quote, signal_type)
    
    def _build_prompt(self, quote, ohlcv: Dict, context: Dict, 
                      signal_type: SignalType) -> str:
        """构建LLM prompt"""
        context_str = ""
        if context:
            context_str = f"""
市场整体情况:
- BTC价格: ${context.get('btc_price', 0):,.2f}
- 市场情绪: {context.get('market_sentiment', '未知')}
- 主流币涨跌比: {context.get('summary', {}).get('gainers', 0)}/{context.get('summary', {}).get('losers', 0)}
"""
        
        ohlcv_str = ""
        if ohlcv and len(ohlcv.closes) >= 20:
            recent = ohlcv.closes[-20:]
            trend = "上涨" if recent[-1] > recent[0] else "下跌"
            ohlcv_str = f"""
K线分析 (最近20周期):
- 趋势: {trend}
- 最高价: ${max(recent):,.2f}
- 最低价: ${min(recent):,.2f}
- 当前价: ${quote.price:,.2f}
"""
        
        prompt = f"""
作为专业的加密货币技术分析师，请分析以下交易对:

{ohlcv_str}
币种: {quote.symbol}
当前价格: ${quote.price:,.2f}
24h涨跌: {quote.change_percent:+.2f}%
24h波动率: {quote.volatility:.2f}%
24h成交量: {quote.volume_24h:,.2f}
买卖价差: {quote.spread:.3f}%
信号类型: {signal_type.value}
{context_str}

请提供:
1. 简要技术分析 (2-3句话)
2. 可能的驱动因素
3. 风险提示

请保持专业、客观，提示高风险。
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
            max_tokens=400,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def _rule_based_analysis(self, quote, signal_type: SignalType) -> str:
        """基于规则的分析（无LLM时使用）"""
        analysis_map = {
            SignalType.EXTREME_DROP: f"币种{quote.base_symbol}出现{abs(quote.change_percent):.1f}%的大幅下跌，波动率高达{quote.volatility:.1f}%。短期可能出现超卖，但需警惕进一步下跌风险。",
            SignalType.BIG_DROP: f"{quote.base_symbol}跌幅达到{abs(quote.change_percent):.1f}%，需关注是否有重大利空消息或链上异动。",
            SignalType.EXTREME_RISE: f"注意：{quote.base_symbol}涨幅超过{quote.change_percent:.1f}%，属于异常波动。追高风险极高，建议观望。",
            SignalType.BIG_RISE: f"{quote.base_symbol}表现强势，涨幅{quote.change_percent:.1f}%。如成交量配合，可能延续涨势。",
            SignalType.VOLUME_SPIKE: f"{quote.base_symbol}成交量出现明显放大，波动加剧。需关注是资金流入还是流出。",
            SignalType.NEUTRAL: f"{quote.base_symbol}价格运行平稳，未出现明显异动。建议等待方向选择。"
        }
        
        return analysis_map.get(signal_type, "市场情况不明朗，建议观望。")
    
    def _calculate_levels(self, quote) -> Dict:
        """计算关键价位"""
        volatility = quote.volatility / 100
        
        return {
            'pivot': quote.price,
            'resistance_1': quote.price * (1 + volatility * 0.5),
            'support_1': quote.price * (1 - volatility * 0.5),
            'resistance_2': quote.price * (1 + volatility),
            'support_2': quote.price * (1 - volatility)
        }
    
    def _assess_risk(self, quote, signal_type: SignalType, 
                     position: Position, analysis: str) -> tuple:
        """评估风险等级"""
        # 基础风险
        base_risk = "中"
        
        if signal_type in [SignalType.EXTREME_DROP, SignalType.EXTREME_RISE]:
            base_risk = "极高"
        elif signal_type in [SignalType.BIG_DROP, SignalType.BIG_RISE]:
            base_risk = "高"
        
        # 根据波动率调整
        if quote.volatility > 10:
            risk = "极高" if base_risk == "高" else base_risk
        elif quote.visatility > 5:
            risk = "高" if base_risk == "中" else base_risk
        else:
            risk = base_risk
        
        # 建议
        recommendation_map = {
            ("极高", Position.HOLD): "强烈建议观望，切勿抄底/追高",
            ("极高", Position.LONG): "风险极高，建议极小仓位",
            ("极高", Position.SHORT): "风险极高，建议极小仓位",
            ("高", Position.HOLD): "建议观望，等待更好的入场时机",
            ("高", Position.LONG): "建议轻仓，设置好止损",
            ("高", Position.SHORT): "建议轻仓，设置好止损",
            ("中", Position.HOLD): "可小仓位试单",
            ("中", Position.LONG): "可考虑入场，设好止损",
            ("中", Position.SHORT): "可考虑入场，设好止损"
        }
        
        recommendation = recommendation_map.get((risk, position), "建议观望")
        
        return risk, recommendation
    
    def _calculate_confidence(self, quote, signal_type: SignalType) -> float:
        """计算置信度"""
        # 基于信号类型和波动率
        base = 0.5
        
        if signal_type in [SignalType.EXTREME_DROP, SignalType.EXTREME_RISE]:
            base = 0.7
        elif signal_type in [SignalType.BIG_DROP, SignalType.BIG_RISE]:
            base = 0.6
        
        # 根据成交量调整
        if quote.spread < 0.1:  # 买卖价差小，说明流动性好
            base += 0.1
        elif quote.spread > 0.5:  # 价差大，流动性差
            base -= 0.1
        
        return min(max(base, 0.3), 0.95)
    
    def _calc_sl_tp(self, quote, position: Position, risk_level: str) -> tuple:
        """计算止损止盈位"""
        volatility = quote.volatility / 100
        
        # 根据风险等级确定止损幅度
        sl_multiplier = {
            "低": 0.02,
            "中": 0.03,
            "高": 0.05,
            "极高": 0.08
        }.get(risk_level, 0.05)
        
        # 根据仓位方向计算
        if position == Position.LONG:
            stop_loss = quote.price * (1 - sl_multiplier)
            take_profit = quote.price * (1 + sl_multiplier * 2)
        elif position == Position.SHORT:
            stop_loss = quote.price * (1 + sl_multiplier)
            take_profit = quote.price * (1 - sl_multiplier * 2)
        else:
            return None, None
        
        return stop_loss, take_profit
    
    def _suggest_leverage(self, risk_level: str) -> int:
        """建议杠杆倍数"""
        leverage_map = {
            "低": 3,
            "中": 2,
            "高": 1,
            "极高": 1
        }
        return leverage_map.get(risk_level, 1)
    
    async def generate_batch_signals(self, quotes: List, 
                                      market_context: Dict = None) -> List[CryptoSignal]:
        """批量生成信号"""
        signals = []
        for quote in quotes:
            # 获取K线数据
            ohlcv = None
            try:
                from data_collector import CryptoDataCollector
                collector = CryptoDataCollector({})
                ohlcv = await collector.get_ohlcv(quote.symbol)
            except:
                pass
            
            signal = await self.generate_signal(quote, ohlcv, market_context)
            signals.append(signal)
        return signals
