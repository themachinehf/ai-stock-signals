"""
Telegram Bot模块
推送交易信号给订阅用户
"""
import asyncio
import logging
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

logger = logging.getLogger(__name__)

class SignalBot:
    """交易信号Telegram Bot"""
    
    def __init__(self, config: Dict):
        self.token = config.get('bot_token')
        self.channel_id = config.get('channel_id')
        self.admin_id = config.get('admin_user_id')
        
        self.application = None
        self.subscribers = set()  # 订阅用户ID集合
        
        # 启动状态
        self._running = False
    
    async def start(self):
        """启动Bot"""
        if not self.token:
            logger.error("未配置Telegram Bot Token")
            return False
        
        self.application = (
            ApplicationBuilder()
            .token(self.token)
            .proxy_url('http://127.0.0.1:7890')
            .get_updates_proxy_url('http://127.0.0.1:7890')
            .build()
        )
        
        # 初始化
        await self.application.initialize()
        
        # 注册命令处理器
        self.application.add_handler(CommandHandler("start", self._cmd_start))
        self.application.add_handler(CommandHandler("help", self._cmd_help))
        self.application.add_handler(CommandHandler("subscribe", self._cmd_subscribe))
        self.application.add_handler(CommandHandler("unsubscribe", self._cmd_unsubscribe))
        self.application.add_handler(CommandHandler("status", self._cmd_status))
        self.application.add_handler(CallbackQueryHandler(self._handle_callback))
        
        # 启动轮询
        await self.application.start()
        await self.application.updater.start_polling()
        
        self._running = True
        logger.info("Telegram Bot已启动")
        
        return True
    
    async def stop(self):
        """停止Bot"""
        if self.application:
            await self.application.stop()
            self._running = False
            logger.info("Telegram Bot已停止")
    
    async def send_signal(self, signal) -> bool:
        """
        发送交易信号到频道
        
        Args:
            signal: TradingSignal对象
        
        Returns:
            是否发送成功
        """
        if not self.channel_id:
            logger.error("未配置频道ID")
            return False
        
        try:
            message = signal.to_telegram_message()
            
            # 添加操作按钮
            keyboard = [
                [
                    InlineKeyboardButton("📊 查看详情", callback_data=f"detail_{signal.symbol}"),
                    InlineKeyboardButton("🔔 订阅通知", callback_data="subscribe")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.application.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            logger.info(f"信号已发送: {signal.symbol} {signal.signal_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"发送信号失败: {e}")
            return False
    
    async def broadcast_signal(self, signal) -> int:
        """
        广播信号给所有订阅用户
        
        Returns:
            成功发送的用户数
        """
        success_count = 0
        message = signal.to_telegram_message()
        
        for user_id in self.subscribers:
            try:
                await self.application.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='Markdown'
                )
                success_count += 1
                await asyncio.sleep(0.1)  # 避免触发限流
            except Exception as e:
                logger.warning(f"发送用户{user_id}失败: {e}")
        
        return success_count
    
    async def send_market_summary(self, summary: Dict):
        """发送市场摘要"""
        if not self.channel_id:
            return
        
        sentiment_emoji = {
            "极度乐观 🚀": "🟢",
            "乐观 😊": "🟢",
            "中性 😐": "🟡",
            "悲观 😟": "🟠",
            "极度悲观 📉": "🔴"
        }
        
        emoji = sentiment_emoji.get(summary.get('market_sentiment', '中性 😐'), "🟡")
        
        message = f"""
{emoji} **{summary.get('market_sentiment', '中性')}**

📅 {summary.get('timestamp', '')}

**主要指数:**
"""
        
        for idx in summary.get('indices', []):
            change_emoji = "📈" if idx['change'] > 0 else "📉" if idx['change'] < 0 else "➡️"
            message += f"{change_emoji} {idx['name']}: {idx['change']:+.2f}%\n"
        
        message += f"\n平均涨跌幅: **{summary.get('avg_change', 0):+.2f}%**"
        message += "\n\n---\n⚠️ 仅供参考，不构成投资建议"
        
        try:
            await self.application.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"发送市场摘要失败: {e}")
    
    # === Command Handlers ===
    
    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令"""
        user = update.message.from_user
        welcome_message = f"""
🎯 **{user.first_name}，欢迎使用A股AI交易信号！**

这是一个AI驱动的A股交易信号推送系统，帮助您:
- 📊 监控A股异动
- 🚀 捕捉大涨信号
- 📉 预警大跌风险
- 🤖 AI智能分析

发送 /subscribe 订阅信号推送
发送 /help 查看帮助
"""
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /help 命令"""
        help_text = """
📚 **使用帮助**

**可用命令:**
- /start - 启动机器人
- /subscribe - 订阅信号推送
- /unsubscribe - 取消订阅
- /status - 查看市场状态
- /help - 显示帮助信息

**订阅说明:**
- 免费用户每天接收3次信号推送
- 付费用户实时接收所有信号
- 如需升级，请联系管理员

**风险提示:**
⚠️ 所有信号仅供参考，不构成投资建议
⚠️ 投资有风险，入市需谨慎
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def _cmd_subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /subscribe 命令"""
        user_id = update.message.from_user.id
        
        if user_id in self.subscribers:
            await update.message.reply_text("✅ 您已订阅信号推送，无需重复订阅")
        else:
            self.subscribers.add(user_id)
            await update.message.reply_text(
                "✅ *订阅成功！* 🎉\n\n您将收到:\n• 大涨信号推送\n• 大跌预警\n• 每日市场摘要\n\n发送 /unsubscribe 取消订阅",
                parse_mode='Markdown'
            )
            logger.info(f"用户 {user_id} 订阅了信号")
    
    async def _cmd_unsubscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /unsubscribe 命令"""
        user_id = update.message.from_user.id
        
        if user_id in self.subscribers:
            self.subscribers.remove(user_id)
            await update.message.reply_text("✅ 已取消订阅\n\n如需重新订阅，发送 /subscribe", parse_mode='Markdown')
            logger.info(f"用户 {user_id} 取消了订阅")
        else:
            await update.message.reply_text("ℹ️ 您尚未订阅信号推送")
    
    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /status 命令"""
        status_text = f"""
📊 **系统状态**

🤖 Bot状态: {'运行中' if self._running else '已停止'}
👥 订阅用户: {len(self.subscribers)}人
📡 频道: {'已配置' if self.channel_id else '未配置'}

⚠️ 免责声明:
本系统提供的信号仅供参考，不构成投资建议。
历史表现不代表未来收益。
"""
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def _handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理按钮回调"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "subscribe":
            user_id = query.from_user.id
            if user_id not in self.subscribers:
                self.subscribers.add(user_id)
                await query.edit_message_text("✅ 订阅成功！您将收到信号推送")
            else:
                await query.edit_message_text("ℹ️ 您已订阅")
        elif query.data.startswith("detail_"):
            symbol = query.data.replace("detail_", "")
            await query.edit_message_text(f"📊 **{symbol}** 详情\n\n功能开发中...", parse_mode='Markdown')
