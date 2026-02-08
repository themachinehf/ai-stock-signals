"""
系统测试脚本
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from data_collector.collector import StockDataCollector, StockQuote
from signal_generator.analyzer import SignalGenerator, SignalType


async def test_data_collector():
    """测试数据采集"""
    print("=" * 50)
    print("🧪 测试数据采集模块")
    print("=" * 50)
    
    collector = StockDataCollector({})
    
    # 测试获取上证指数
    print("\n📊 获取上证指数...")
    quote = collector.get_realtime_quote("sh.000001")
    
    if quote:
        print(f"✅ 成功获取:")
        print(f"   名称: {quote.name}")
        print(f"   价格: {quote.price}")
        print(f"   涨跌幅: {quote.change_percent:.2f}%")
        print(f"   大跌信号: {quote.is_big_drop}")
        print(f"   大涨信号: {quote.is_big_rise}")
    else:
        print("❌ 获取失败")
    
    return quote is not None


async def test_signal_generator():
    """测试信号生成"""
    print("\n" + "=" * 50)
    print("🧪 测试信号生成模块")
    print("=" * 50)
    
    # 创建测试数据
    test_quote = StockQuote(
        symbol="sh.600519",
        name="贵州茅台",
        price=1800.0,
        change_percent=5.5,
        volume=5000000,
        timestamp=1699900000
    )
    
    generator = SignalGenerator({})
    
    # 测试规则分析
    print("\n🤖 测试AI信号生成...")
    signal = await generator.generate_signal(test_quote, None)
    
    print(f"✅ 信号生成成功:")
    print(f"   类型: {signal.signal_type.value}")
    print(f"   价格: {signal.current_price}")
    print(f"   涨跌幅: {signal.change_percent:.2f}%")
    print(f"   分析: {signal.analysis}")
    print(f"   风险: {signal.risk_level}")
    print(f"   建议: {signal.recommendation}")
    print(f"   置信度: {signal.confidence:.0%}")
    
    # 测试Telegram消息格式
    print("\n📱 Telegram消息预览:")
    print("-" * 50)
    print(signal.to_telegram_message())
    print("-" * 50)
    
    return True


async def test_batch_signals():
    """测试批量信号生成"""
    print("\n" + "=" * 50)
    print("🧪 测试批量信号生成")
    print("=" * 50)
    
    test_quotes = [
        StockQuote("sh.600519", "贵州茅台", 1800.0, 5.5, 5000000, 1699900000),
        StockQuote("sz.000651", "格力电器", 35.0, -6.2, 3000000, 1699900000),
        StockQuote("sh.000001", "上证指数", 3200.0, 0.5, 10000000, 1699900000),
    ]
    
    generator = SignalGenerator({})
    signals = await generator.generate_signals_batch(test_quotes)
    
    print(f"\n✅ 生成 {len(signals)} 个信号")
    
    for s in signals:
        print(f"   • {s.symbol} {s.signal_type.value} ({s.change_percent:+.1f}%)")
    
    return len(signals) == 3


async def main():
    """主测试函数"""
    print("\n" + "=" * 50)
    print("🚀 A股AI交易信号系统 - 测试套件")
    print("=" * 50)
    
    results = []
    
    # 测试1: 数据采集
    try:
        result1 = await test_data_collector()
        results.append(("数据采集", result1))
    except Exception as e:
        print(f"❌ 数据采集测试失败: {e}")
        results.append(("数据采集", False))
    
    # 测试2: 信号生成
    try:
        result2 = await test_signal_generator()
        results.append(("信号生成", result2))
    except Exception as e:
        print(f"❌ 信号生成测试失败: {e}")
        results.append(("信号生成", False))
    
    # 测试3: 批量处理
    try:
        result3 = await test_batch_signals()
        results.append(("批量处理", result3))
    except Exception as e:
        print(f"❌ 批量处理测试失败: {e}")
        results.append(("批量处理", False))
    
    # 输出结果汇总
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"   {name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 所有测试通过!")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查系统配置")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
