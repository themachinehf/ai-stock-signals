"""
A股AI交易信号系统主程序
"""
import asyncio
import yaml
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent))

from data_collector import StockDataCollector
from signal_generator import SignalGenerator
from telegram_bot import SignalBot

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AStockSignalSystem:
    """A股信号系统主类"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        
        # 初始化模块
        self.collector = StockDataCollector(self.config.get('stock', {}))
        self.generator = SignalGenerator(self.config.get('llm', {}))
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
        logger.info("🚀 启动A股AI交易信号系统...")
        
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
        watchlist = self.config.get('stock', {}).get('watchlist', [])
        
        logger.info(f"📡 开始监控 {len(watchlist)} 只股票")
        logger.info(f"🔄 检查间隔: {check_interval}秒")
        
        while self._running:
            try:
                await self.check_stocks(watchlist)
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
            
            # 等待下一次检查
            for _ in range(check_interval):
                if not self._running:
                    break
                await asyncio.sleep(1)
    
    async def check_stocks(self, symbols: List[str]):
        """检查股票状态"""
        logger.info(f"📊 开始检查 {len(symbols)} 只股票...")
        
        # 获取市场摘要
        market_summary = self.collector.get_market_summary()
        
        # 获取所有股票行情
        quotes = self.collector.get_batch_quotes(symbols)
        
        if not quotes:
            logger.warning("未获取到任何股票数据")
            return
        
        # 过滤出异动股票
        active_quotes = [q for q in quotes if q.is_big_drop or q.is_big_rise]
        
        if active_quotes:
            logger.info(f"⚡ 发现 {len(active_quotes)} 只异动股票")
            
            # 生成信号并发送
            for quote in active_quotes:
                signal = await self.generator.generate_signal(quote, market_summary)
                
                # 发送到频道
                await self.bot.send_signal(signal)
                
                # 广播给订阅用户
                sent_count = await self.bot.broadcast_signal(signal)
                logger.info(f"广播给 {sent_count} 位订阅用户")
                
                self._last_signals.append({
                    'signal': signal,
                    'timestamp': datetime.now()
                })
        
        # 每天发送一次市场摘要
        now = datetime.now()
        if now.hour == 9 and now.minute < 5:  # 开盘时间
            await self.bot.send_market_summary(market_summary)
        
        logger.info("✅ 检查完成")
    
    def get_last_signals(self, limit: int = 10) -> list:
        """获取最近的信号"""
        return self._last_signals[-limit:]
    
    async def run_once(self):
        """单次运行（用于测试）"""
        watchlist = self.config.get('stock', {}).get('watchlist', [])
        
        # 启动Bot（不启动监控循环）
        await self.bot.start()
        
        # 执行一次检查
        await self.check_stocks(watchlist)
        
        # 停止Bot
        await self.bot.stop()


async def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='A股AI交易信号系统')
    parser.add_argument('--config', '-c', default='config.yaml', help='配置文件路径')
    parser.add_argument('--once', '-o', action='store_true', help='单次运行（测试用）')
    args = parser.parse_args()
    
    # 复制示例配置
    if not Path(args.config).exists():
        if Path('config.example.yaml').exists():
            import shutil
            shutil.copy('config.example.yaml', args.config)
            logger.info(f"已创建配置文件 {args.config}，请编辑配置后重新运行")
            return
    
    system = AStockSignalSystem(args.config)
    
    if args.once:
        await system.run_once()
    else:
        await system.start()


if __name__ == "__main__":
    asyncio.run(main())
