"""
Web展示页 - FastAPI后端
"""
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

app = FastAPI(title="A股AI交易信号", description="A股AI交易信号展示")

# 简易内存存储（生产环境请使用数据库）
signals_store = []
system_status = {
    "running": False,
    "last_check": None,
    "subscribers": 0
}

class SignalResponse(BaseModel):
    """信号响应模型"""
    symbol: str
    name: str
    signal_type: str
    current_price: float
    change_percent: float
    analysis: str
    risk_level: str
    recommendation: str
    confidence: float
    timestamp: str
    disclaimer: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """首页"""
    return """
    <html>
        <head>
            <title>A股AI交易信号</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                .header { text-align: center; margin-bottom: 40px; }
                .signal { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px; }
                .rise { background: #e8f5e9; border-left: 4px solid #4caf50; }
                .drop { background: #ffebee; border-left: 4px solid #f44336; }
                .neutral { background: #f5f5f5; border-left: 4px solid #9e9e9e; }
                .disclaimer { margin-top: 40px; padding: 15px; background: #fff3e0; border-radius: 8px; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 A股AI交易信号</h1>
                <p>AI智能分析A股市场异动</p>
            </div>
            
            <h2>📊 实时信号</h2>
            <div id="signals">
                <p>正在加载信号...</p>
            </div>
            
            <div class="disclaimer">
                ⚠️ <strong>免责声明</strong><br>
                本系统提供的所有信号仅供参考，不构成任何投资建议。<br>
                投资有风险，入市需谨慎。历史表现不代表未来收益。
            </div>
            
            <script>
                async function loadSignals() {
                    try {
                        const response = await fetch('/api/signals');
                        const data = await response.json();
                        
                        const container = document.getElementById('signals');
                        
                        if (data.signals && data.signals.length > 0) {
                            let html = '';
                            data.signals.forEach(signal => {
                                const cssClass = signal.signal_type.includes('涨') ? 'rise' : 
                                                signal.signal_type.includes('跌') ? 'drop' : 'neutral';
                                const emoji = signal.signal_type.includes('涨') ? '🚀' : 
                                             signal.signal_type.includes('跌') ? '📉' : '📊';
                                
                                html += `
                                    <div class="signal ${cssClass}">
                                        <strong>${emoji} ${signal.signal_type}</strong><br>
                                        ${signal.name} (${signal.symbol})<br>
                                        当前价格: ${signal.current_price.toFixed(2)} | 
                                        涨跌幅: <span style="color: ${signal.change_percent > 0 ? 'green' : 'red'}">
                                        ${signal.change_percent > 0 ? '+' : ''}${signal.change_percent.toFixed(2)}%</span><br>
                                        ${signal.analysis}<br>
                                        <small>风险: ${signal.risk_level} | 置信度: ${(signal.confidence * 100).toFixed(0)}%</small>
                                    </div>
                                `;
                            });
                            container.innerHTML = html;
                        } else {
                            container.innerHTML = '<p>暂无信号</p>';
                        }
                    } catch (e) {
                        container.innerHTML = '<p>加载失败</p>';
                    }
                }
                
                loadSignals();
                setInterval(loadSignals, 30000);  // 每30秒刷新
            </script>
        </body>
    </html>
    """

@app.get("/api/signals")
async def get_signals() -> dict:
    """获取信号列表"""
    return {
        "status": "ok",
        "signals": [s.to_dict() for s in signals_store[-20:]],
        "count": len(signals_store)
    }

@app.get("/api/status")
async def get_status() -> dict:
    """获取系统状态"""
    return {
        "running": system_status["running"],
        "last_check": system_status["last_check"],
        "subscribers": system_status["subscribers"],
        "total_signals": len(signals_store)
    }

@app.post("/api/webhook/signal")
async def webhook_signal(signal: dict):
    """接收信号的Webhook"""
    signals_store.append(signal)
    return {"status": "received", "count": len(signals_store)}

# === 测试用示例 ===
@app.on_event("startup")
async def startup_event():
    """启动时添加示例信号"""
    from signal_generator.analyzer import TradingSignal, SignalType
    import time
    
    # 添加一个示例信号
    example_signal = TradingSignal(
        symbol="sh.600519",
        name="贵州茅台",
        signal_type=SignalType.BIG_RISE,
        current_price=1850.00,
        change_percent=5.5,
        analysis="股价大幅上涨5.5%，创近期新高。可能有业绩利好支撑。",
        risk_level="中",
        recommendation="建议观望，避免追高",
        confidence=0.75,
        timestamp=int(time.time())
    )
    signals_store.append(example_signal)
    
    system_status["running"] = True


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
