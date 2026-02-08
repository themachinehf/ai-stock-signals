#!/usr/bin/env python3
"""数据采集测试脚本"""

import asyncio
import sys
sys.path.insert(0, '.')

from data_collector import CryptoDataCollector

async def test():
    print("🧪 测试数据采集...")
    
    collector = CryptoDataCollector({'exchange': 'binance'})
    
    # 测试获取BTC价格
    print("\n📊 测试1: BTC/USDT 实时价格")
    btc = await collector.get_realtime_price('BTC/USDT')
    if btc:
        print(f"✅ BTC/USDT: ${btc.price:,.2f} ({btc.change_percent:+.2f}%)")
        print(f"   24h高: ${btc.high_24h:,.2f} | 24h低: ${btc.low_24h:,.2f}")
        print(f"   波动率: {btc.volatility:.2f}%")
    else:
        print("❌ BTC 获取失败")
    
    # 测试获取ETH价格
    print("\n📊 测试2: ETH/USDT 实时价格")
    eth = await collector.get_realtime_price('ETH/USDT')
    if eth:
        print(f"✅ ETH/USDT: ${eth.price:,.2f} ({eth.change_percent:+.2f}%)")
    else:
        print("❌ ETH 获取失败")
    
    # 测试批量获取
    print("\n📊 测试3: 批量获取主流币")
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT']
    quotes = await collector.get_batch_prices(symbols)
    print(f"✅ 成功获取 {len(quotes)} 个币种")
    for q in quotes:
        print(f"   {q.base_symbol:6s} ${q.price:>12,.2f} ({q.change_percent:+8.2f}%)")
    
    # 测试市场摘要
    print("\n📊 测试4: 市场整体摘要")
    summary = await collector.get_market_summary()
    if summary.get('status') == 'ok':
        print(f"✅ 市场情绪: {summary.get('market_sentiment')}")
        print(f"✅ BTC价格: ${summary.get('btc_price', 0):,.2f}")
        print(f"✅ BTC涨跌: {summary.get('btc_change', 0):+.2f}%")
        print(f"✅ 上涨币种: {summary.get('summary', {}).get('gainers', 0)}/{summary.get('summary', {}).get('losers', 0)}")
    else:
        print(f"❌ 市场摘要失败: {summary.get('message')}")
    
    print("\n✨ 测试完成!")

if __name__ == '__main__':
    asyncio.run(test())
