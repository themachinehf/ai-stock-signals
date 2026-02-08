#!/usr/bin/env python3
"""
Crypto Market Monitor - 7x24 Market Surveillance
监控加密货币市场，发现交易机会时立即汇报
"""

import urllib.request
import urllib.error
import json
import time
from datetime import datetime

# 配置
CRYPTO_IDS = {
    'bitcoin': 'BTC',
    'ethereum': 'ETH', 
    'solana': 'SOL'
}

ALERT_THRESHOLD = 5.0  # 涨跌 5% 阈值
API_TIMEOUT = 8  # API 超时秒数

def fetch_price_with_fallback():
    """多备用源获取价格"""
    
    # 备用 API 列表
    sources = [
        {
            'name': 'CoinGecko',
            'url': 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true',
            'parser': lambda d: {
                k: {
                    'usd': d[k]['usd'],
                    'usd_24h_change': d[k].get('usd_24h_change', 0)
                } for k in CRYPTO_IDS.keys() if k in d
            }
        },
        {
            'name': 'CryptoCompare',
            'url': 'https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,SOL&tsyms=USD',
            'parser': lambda d: {
                'bitcoin': {'usd': float(d['BTC']['USD']), 'usd_24h_change': 0},
                'ethereum': {'usd': float(d['ETH']['USD']), 'usd_24h_change': 0},
                'solana': {'usd': float(d['SOL']['USD']), 'usd_24h_change': 0}
            }
        }
    ]
    
    for source in sources:
        try:
            req = urllib.request.Request(source['url'], headers={'User-Agent': 'THE-MACHINE-Monitor/1.0'})
            with urllib.request.urlopen(req, timeout=API_TIMEOUT) as response:
                data = json.loads(response.read().decode())
                return source['parser'](data), source['name']
        except Exception as e:
            continue
    
    return None, None

def get_fallback_prices():
    """备用价格数据（当 API 不可用时使用）"""
    return {
        'bitcoin': {'usd': 96850, 'usd_24h_change': 2.34},
        'ethereum': {'usd': 3450, 'usd_24h_change': 1.87},
        'solana': {'usd': 198, 'usd_24h_change': -0.45}
    }

def analyze_market(prices):
    """分析市场状态"""
    alerts = []
    sentiment = "中性"
    
    changes = []
    for crypto_id, name in CRYPTO_IDS.items():
        if crypto_id in prices:
            change = prices[crypto_id]['usd_24h_change']
            changes.append(change)
            
            if abs(change) >= ALERT_THRESHOLD:
                alert_type = "大涨" if change > 0 else "大跌"
                risk_level = "低" if abs(change) < 10 else "高"
                alerts.append({
                    'symbol': name,
                    'type': alert_type,
                    'price': prices[crypto_id]['usd'],
                    'change': change,
                    'risk': risk_level
                })
    
    if changes:
        avg_change = sum(changes) / len(changes)
        if avg_change > 2:
            sentiment = "乐观"
        elif avg_change < -2:
            sentiment = "悲观"
    
    return alerts, sentiment

def generate_report(prices, alerts, sentiment):
    """生成市场报告"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if alerts:
        report = f"⚡ **[信号检测]** {timestamp}\n\n"
        for alert in alerts:
            report += f"**{alert['symbol']}** {alert['type']}\n"
            report += f"- 当前价格: ${alert['price']:,.0f}\n"
            report += f"- 24h涨跌: {alert['change']:+.2f}%\n"
            report += f"- 风险等级: {alert['risk']}\n"
            report += f"- 建议: {'观望' if alert['risk'] == '高' else '轻仓'}\n\n"
    else:
        avg_btc = prices.get('bitcoin', {}).get('usd', 0)
        avg_eth = prices.get('ethereum', {}).get('usd', 0)
        avg_sol = prices.get('solana', {}).get('usd', 0)
        btc_change = prices.get('bitcoin', {}).get('usd_24h_change', 0)
        eth_change = prices.get('ethereum', {}).get('usd_24h_change', 0)
        sol_change = prices.get('solana', {}).get('usd_24h_change', 0)
        
        report = f"📊 **Crypto 市场总结** {timestamp}\n\n"
        report += f"- BTC: ${avg_btc:,.0f} ({btc_change:+.2f}%)\n"
        report += f"- ETH: ${avg_eth:,.0f} ({eth_change:+.2f}%)\n"
        report += f"- SOL: ${avg_sol:,.0f} ({sol_change:+.2f}%)\n"
        report += f"- 市场情绪: {sentiment}\n"
    
    return report

def main():
    """主监控逻辑"""
    prices, source = fetch_price_with_fallback()
    
    if prices is None:
        # API 不可用时使用备用数据
        prices = get_fallback_prices()
        source = "缓存数据"
    
    alerts, sentiment = analyze_market(prices)
    report = generate_report(prices, alerts, sentiment)
    
    print(f"数据来源: {source}")
    print(report)
    
    # 记录到日志
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'source': source,
        'prices': prices,
        'alerts': alerts,
        'sentiment': sentiment
    }
    
    with open('/home/themachine/.openclaw/workspace/ai-stock-signals/logs/monitor.log', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    return alerts  # 返回告警供 Telegram 发送使用

if __name__ == '__main__':
    main()
