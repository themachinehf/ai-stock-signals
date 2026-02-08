#!/usr/bin/env node
/**
 * Crypto AI Signal Bot - Telegram 推送版本
 * THE MACHINE Edition
 */

const axios = require('axios');

// 配置
const CONFIG = {
    telegram: {
        botToken: process.env.TELEGRAM_BOT_TOKEN || 'YOUR_BOT_TOKEN',
        chatId: process.env.TELEGRAM_CHAT_ID || '@your_channel',
    },
    thresholds: {
        alertPercent: 5,  // 涨跌超过5%警报
        warningPercent: 3, // 涨跌超过3%提醒
    }
};

// 模拟价格数据（实际使用OKX API）
let prices = {
    BTC: { price: 69443, change: -1.41 },
    ETH: { price: 2096, change: 1.80 },
    SOL: { price: 87.71, change: 0.39 }
};

let lastAlert = { BTC: false, ETH: false, SOL: false };

// Telegram 发送消息
async function sendTelegram(text) {
    try {
        const url = `https://api.telegram.org/bot${CONFIG.telegram.botToken}/sendMessage`;
        await axios.post(url, {
            chat_id: CONFIG.telegram.chatId,
            text: text,
            parse_mode: 'HTML'
        });
        console.log(`[Telegram] 发送成功`);
        return true;
    } catch (error) {
        console.log(`[Telegram] 发送失败: ${error.message}`);
        return false;
    }
}

// 格式化消息
function formatMessage(coin, data) {
    const emoji = data.change > 0 ? '📈' : '📉';
    const status = Math.abs(data.change) >= CONFIG.thresholds.alertPercent ? '🚨 警报' :
                   Math.abs(data.change) >= CONFIG.thresholds.warningPercent ? '⚠️ 提醒' : '✅ 正常';
    
    return `⚡ <b>${coin}/USDT</b> ${emoji}

💰 价格: <b>$${data.price.toLocaleString()}</b>
📊 24h: <b>${data.change > 0 ? '+' : ''}${data.change}%</b>

${status}
`;
}

// 检查异常
function checkAlert(coin, data) {
    const absChange = Math.abs(data.change);
    const key = `${coin}_${data.change > 0 ? 'up' : 'down'}`;
    
    if (absChange >= CONFIG.thresholds.alertPercent && !lastAlert[key]) {
        lastAlert[key] = true;
        setTimeout(() => { lastAlert[key] = false; }, 3600000); // 1小时冷却
        return true;
    }
    return false;
}

// 市场总结
function formatSummary() {
    let lines = ['📊 <b>Crypto 市场总结</b>', '━━━━━━━━━━━━━'];
    
    for (const [coin, data] of Object.entries(prices)) {
        const emoji = data.change > 0 ? '📈' : data.change < 0 ? '📉' : '➡️';
        lines.push(`${emoji} <b>${coin}</b>: $${data.price.toLocaleString()} (${data.change > 0 ? '+' : ''}${data.change}%)`);
    }
    
    const btcChange = prices.BTC.change;
    let sentiment = '😐 中性';
    if (btcChange > 2) sentiment = '😊 乐观';
    else if (btcChange < -2) sentiment = '😟 悲观';
    
    lines.push('', `🎯 情绪: ${sentiment}`);
    lines.push('━━━━━━━━━━━━━');
    lines.push('🤖 THE MACHINE | 7x24监控');
    
    return lines.join('\n');
}

// 主循环
async function main() {
    console.log('🤖 Crypto Signal Bot 启动');
    console.log(`📡 Telegram: ${CONFIG.telegram.chatId}`);
    
    // 发送启动消息
    await sendTelegram('🤖 <b>Crypto AI Signal Bot</b> 已启动\n\nTHE MACHINE 开始7x24小时监控...');
    
    // 每5分钟检查
    setInterval(async () => {
        console.log(`\n[${new Date().toLocaleString()}] 检查市场...`);
        
        // 检查警报
        let alertSent = false;
        for (const [coin, data] of Object.entries(prices)) {
            if (checkAlert(coin, data)) {
                const msg = `🚨 <b>警报</b>\n\n${formatMessage(coin, data)}⚡ THE MACHINE`;
                await sendTelegram(msg);
                alertSent = true;
            }
        }
        
        // 每小时发送总结
        const minute = new Date().getMinutes();
        if (minute === 0 || minute === 30) {
            await sendTelegram(formatSummary());
        }
        
        if (!alertSent) {
            console.log('✅ 市场正常');
        }
    }, 300000); // 5分钟
}

main().catch(console.error);
