# 🚀 加密货币AI交易信号系统

**注意：** 本项目已从A股转型到加密货币领域。原A股版本请查看 [ai-stock-signals标签](https://github.com/themachinehf/crypto-ai-signals/tree/stock-version)。

AI驱动的加密货币交易信号生成和推送系统，支持Binance、OKX等主流交易所。

## 📋 功能特性

- 📊 **实时监控** - 监控主流币种异动（涨跌≥5%）
- 🤖 **AI分析** - 使用LLM智能分析K线形态和市场情绪
- 📱 **Telegram推送** - 实时推送给订阅用户
- 🌐 **Web展示** - 实时信号展示页面

## 🛠️ 安装

```bash
# 克隆项目
cd /home/themachine/.openclaw/workspace/ai-stock-signals

# 安装依赖
pip install -r requirements.txt

# 配置系统
cp crypto_config.example.yaml crypto_config.yaml
# 编辑 crypto_config.yaml 填入你的配置
```

## ⚙️ 配置

编辑 `crypto_config.yaml`:

```yaml
# Telegram Bot
telegram:
  bot_token: "YOUR_BOT_TOKEN"
  channel_id: "YOUR_CHANNEL_ID"

# LLM (可选，无API key时使用规则分析)
llm:
  api_key: "YOUR_OPENAI_API_KEY"
  model: "gpt-4o-mini"

# 交易所配置
crypto:
  exchange: "binance"  # binance, okx, coinbase, kucoin
  watchlist:
    - "BTC/USDT"
    - "ETH/USDT"
    - "BNB/USDT"
    - "SOL/USDT"
  drop_threshold: -5.0
  rise_threshold: 5.0
```

## 🚀 运行

```bash
# 加密货币模式
python crypto_main.py --once

# 常规运行（启动监控循环）
python crypto_main.py

# Web展示页
python web_ui/main.py
```

## 📁 项目结构

```
ai-stock-signals/
├── main.py                  # A股主程序（保留）
├── crypto_main.py           # 加密货币主程序
├── crypto_config.example.yaml  # 加密货币配置示例
├── config.example.yaml      # A股配置示例（保留）
├── requirements.txt         # 依赖列表
├── data_collector/
│   ├── collector.py         # A股行情采集
│   └── crypto_collector.py  # 加密货币行情采集 ⭐
├── signal_generator/
│   ├── analyzer.py          # A股信号分析
│   └── crypto_generator.py  # 加密货币信号分析 ⭐
├── telegram_bot/
│   └── bot.py               # Bot实现
└── web_ui/
    └── main.py              # FastAPI应用
```

## 📊 支持的交易对

| 交易所 | API类型 | 实时数据 | K线数据 |
|--------|---------|----------|---------|
| Binance | 公开/私有 | ✅ | ✅ |
| OKX | 公开/私有 | ✅ | ✅ |
| Coinbase | 公开 | ✅ | ✅ |
| KuCoin | 公开 | ✅ | ✅ |

## 📱 Telegram Bot命令

- `/start` - 启动机器人
- `/subscribe` - 订阅信号推送
- `/unsubscribe` - 取消订阅
- `/status` - 查看系统状态
- `/help` - 帮助信息

## ⚠️ 风险提示

**重要提示：**
- ⚠️ 加密货币是高风险投资，市场24/7运行
- ⚠️ 本系统提供的所有信号仅供参考，不构成投资建议
- ⚠️ **DYOR (Do Your Own Research)** - 请自行研究
- ⚠️ 杠杆交易风险极大，可能导致本金全部亏损
- ⚠️ 历史表现不代表未来收益
- ⚠️ 请根据自身风险承受能力理性投资

## 📄 许可证

MIT License
