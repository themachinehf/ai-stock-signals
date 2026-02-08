"""
加密货币AI交易信号系统主程序
从A股信号系统改造，支持Binance等交易所
"""
import asyncio
import yaml
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import List

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent))

from data_collector import CryptoDataCollector, CoinGeckoCollector
from signal_generator import CryptoSignalGenerator
from telegram_bot import SignalBot

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CryptoSignalSystem:
    """加密货币信号系统主类"""
    
    def __init__(self, config_path: str = "crypto_config.yaml"):
        self.config = self._load_config(config_path)
        
        # 初始化模块
        self.collector = CryptoDataCollector(self.config.get('crypto', {}))
        self.generator = CryptoSignalGenerator(self.config.get('llm', {}))
        self.bot = SignalBot(self.config.get('telegram', {}))
        
        # 运行状态
        self._running = False
        self._last_signals = []
    
    def _load_config(self, path: str) -> dict:
        """加载配置文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件 {path} 不存在，使用默认配置")
            return {}
    
    async def start(self):
        """启动系统"""
        logger.info("🚀 启动加密货币AI交易信号系统...")
        
        # 启动Telegram Bot
        bot_started = await self.bot.start()
        if not bot_started:
            logger.warning("Bot启动失败，将以仅监控模式运行")
        
        self._running = True
        
        # 注册信号处理器
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
        
        # 启动监控循环
        await self.monitor_loop()
    
    async def stop(self):
        """停止系统"""
        logger.info("🛑 正在停止系统...")
        self._running = False
        await self.bot.stop()
    
    async def monitor_loop(self):
        """主监控循环"""
        check_interval = self.config.get('system', {}).get('check_interval', 300)
        watchlist = self.config.get('crypto', {}).get('watchlist', [])
        
        logger.info(f"📡 开始监控 {len(watchlist)} 个交易对")
        logger.info(f"🔄 检查间隔: {check_interval}秒")
        
        while self._running:
            try:
                await self.check_cryptos(watchlist)
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
            
            # 等待下一次检查
            for _ in range(check_interval):
                if not self._running:
                    break
                await asyncio.sleep(1)
    
    async def check_cryptos(self, symbols: List[str]):
        """检查加密货币状态"""
        logger.info(f"📊 开始检查 {len(symbols)} 个交易对...")
        
        # 获取市场摘要
        market_summary = await self.collector.get_market_summary()
        
        if market_summary.get('status') == 'ok':
            logger.info(f"🌍 市场情绪: {market_summary.get('market_sentiment')}")
            logger.info(f"📈 BTC: ${market_summary.get('btc_price', 0):,.2f} ({market_summary.get('btc_change', 0):+.2f}%)")
        
        # 获取所有币种行情
        quotes = await self.collector.get_batch_prices(symbols)
        
        if not quotes:
            logger.warning("未获取到任何加密货币数据")
            return
        
        # 过滤出异动币种
        active_quotes = [
            q for q in quotes 
            if q.is_big_drop or q.is_big_rise or q.is_extreme_drop or q.is_extreme_rise
        ]
        
        if active_quotes:
            logger.info(f"⚡ 发现 {len(active_quotes)} 个异动币种")
            
            # 生成信号并发送
            for quote in active_quotes:
                signal = await self.generator.generate_signal(quote, market_context=market_summary)
                
                # 发送到频道
                await self.bot.send_signal(signal)
                
                # 广播给订阅用户
                sent_count = await self.bot.broadcast_signal(signal)
                logger.info(f"广播给 {sent_count} 位订阅用户")
                
                self._last_signals.append({
                    'signal': signal,
                    'timestamp': datetime.now()
                })
        
        # 每4小时发送一次市场摘要
        now = datetime.now()
        if now.hour % 4 == 0 and now.minute < 5:
            await self.bot.send_market_summary(market_summary)
        
        logger.info("✅ 检查完成")
    
    def get_last_signals(self, limit: int = 10) -> list:
        """获取最近的信号"""
        return self._last_signals[-limit:]
    
    async def run_once(self):
        """单次运行（用于测试）"""
        watchlist = self.config.get('crypto', {}).get('watchlist', [])
        
        # 启动Bot（不启动监控循环）
        await self.bot.start()
        
        # 执行一次检查
        await self.check_cryptos(watchlist)
        
        # 停止Bot
        await self.bot.stop()


async def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='加密货币AI交易信号系统')
    parser.add_argument('--config', '-c', default='crypto_config.yaml', help='配置文件路径')
    parser.add_argument('--once', '-o', action='store_true', help='单次运行（测试用）')
    args = parser.parse_args()
    
    # 复制示例配置
    if not Path(args.config).exists():
        if Path('crypto_config.example.yaml').exists():
            import shutil
            shutil.copy('crypto_config.example.yaml', args.config)
            logger.info(f"已创建配置文件 {args.config}，请编辑配置后重新运行")
            return
    
    system = CryptoSignalSystem(args.config)
    
    if args.once:
        await system.run_once()
    else:
        await system.start()


if __name__ == "__main__":
    asyncio.run(main())
