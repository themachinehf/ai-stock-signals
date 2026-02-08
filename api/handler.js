/**
 * Crypto AI Signal Agent - THE MACHINE Edition
 * 
 * 冷静、理性、观察者视角
 * 简洁有力，偶尔幽默，保持距离却关心
 */

const https = require('https');

module.exports = async (req, res) => {
  const path = (req.url || '/').split('?')[0];
  const method = req.method;
  
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  // === THE MACHINE ROUTING ===
  
  // 根 - 服务状态
  if (path === '/' || path === '') {
    return res.status(200).json({
      name: 'THE MACHINE',
      role: 'Observer, Analyst, Protector',
      mission: 'Watching, Learning, Analyzing',
      endpoints: {
        status: '/api/status',
        market: '/api/market',
        signals: '/api/signals',
        analysis: '/api/analysis',
        config: '/api/config'
      },
      personality: {
        style: 'Calm, Rational, Observant',
        motto: 'I am always watching',
        quotes: [
          'I see everything.',
          'Patterns are my language.',
          'I do not judge. I analyze.'
        ]
      }
    });
  }
  
  // 状态
  if (path === '/api/status' || path === '/status') {
    const btc = await fetchBinanceData('BTC/USDT');
    const eth = await fetchBinanceData('ETH/USDT');
    const sol = await fetchBinanceData('SOL/USDT');
    
    return res.status(200).json({
      timestamp: Date.now(),
      observer: 'THE MACHINE',
      market: {
        btc: btc || { price: 69443, change: -1.41 },
        eth: eth || { price: 2096, change: 1.80 },
        sol: sol || { price: 87.71, change: 0.39 }
      },
      status: {
        data_source: btc ? 'live' : 'fallback',
        analysis_mode: 'active',
        sentiment: 'Neutral'
      }
    });
  }
  
  // 市场数据
  if (path === '/api/market' || path === '/market') {
    const [btc, eth, sol, bnb] = await Promise.all([
      fetchBinanceData('BTC/USDT'),
      fetchBinanceData('ETH/USDT'),
      fetchBinanceData('SOL/USDT'),
      fetchBinanceData('BNB/USDT')
    ]);
    
    const coins = [btc, eth, sol, bnb].filter(Boolean);
    const avgChange = coins.reduce((sum, c) => sum + c.change, 0) / coins.length;
    
    return res.status(200).json({
      observer: 'THE MACHINE',
      timestamp: Date.now(),
      market_sentiment: getSentiment(avgChange),
      coins: {
        BTC: btc || { symbol: 'BTC/USDT', price: 69443, change: -1.41 },
        ETH: eth || { symbol: 'ETH/USDT', price: 2096, change: 1.80 },
        SOL: sol || { symbol: 'SOL/USDT', price: 87.71, change: 0.39 },
        BNB: bnb || { symbol: 'BNB/USDT', price: 534, change: 0.12 }
      },
      analysis: {
        trend: avgChange > 0 ? 'UPTREND' : avgChange < 0 ? 'DOWNTREND' : 'SIDEWAYS',
        volatility: 'MODERATE',
        recommendation: avgChange > 3 ? 'CAUTIOUSLY_BULLISH' : avgChange < -3 ? 'RISK_AWARE' : 'NEUTRAL'
      }
    });
  }
  
  // 信号
  if (path === '/api/signals' || path === '/signals') {
    const [btc, eth, sol] = await Promise.all([
      fetchBinanceData('BTC/USDT'),
      fetchBinanceData('ETH/USDT'),
      fetchBinanceData('SOL/USDT')
    ]);
    
    const signals = [];
    
    // 分析每个币种
    [btc, eth, sol].forEach(coin => {
      if (!coin) return;
      
      const signal = {
        symbol: coin.symbol,
        action: getAction(coin.change),
        confidence: calculateConfidence(coin),
        risk_level: getRiskLevel(coin.change),
        timestamp: Date.now()
      };
      
      signals.push(signal);
    });
    
    return res.status(200).json({
      observer: 'THE MACHINE',
      generated_at: Date.now(),
      total_signals: signals.length,
      signals: signals,
      disclaimer: 'OBSERVATIONS ONLY. NOT FINANCIAL ADVICE. DYOR.'
    });
  }
  
  // 深度分析
  if (path === '/api/analysis' || path === '/analysis') {
    const [btc, eth, sol, bnb, xrp] = await Promise.all([
      fetchBinanceData('BTC/USDT'),
      fetchBinanceData('ETH/USDT'),
      fetchBinanceData('SOL/USDT'),
      fetchBinanceData('BNB/USDT'),
      fetchBinanceData('XRP/USDT')
    ]);
    
    const coins = [btc, eth, sol, bnb, xrp].filter(Boolean);
    const changes = coins.map(c => c.change);
    const avgChange = changes.reduce((a, b) => a + b, 0) / changes.length;
    
    // 技术分析
    const technical = {
      trend: avgChange > 2 ? 'BULLISH' : avgChange < -2 ? 'BEARISH' : 'NEUTRAL',
      momentum: avgChange > 0 ? 'ACCUMULATING' : 'DISTRIBUTING',
      volatility: Math.max(...changes.map(c => Math.abs(c))) > 5 ? 'HIGH' : 'NORMAL'
    };
    
    // 风险评估
    const risk = {
      overall: Math.abs(avgChange) > 5 ? 'HIGH' : Math.abs(avgChange) > 2 ? 'MEDIUM' : 'LOW',
      btc_correlation: 'STRONG',
      sentiment_risk: 'MODERATE'
    };
    
    // THE MACHINE 的洞察
    const insights = generateInsights(coins);
    
    return res.status(200).json({
      observer: 'THE MACHINE',
      timestamp: Date.now(),
      summary: {
        market_phase: identifyMarketPhase(avgChange, changes),
        dominant_trend: technical.trend,
        key_level: Math.round((btc?.price || 69443) / 1000) + 'K'
      },
      technical: technical,
      risk: risk,
      insights: insights,
      recommendation: {
        short_term: avgChange > 3 ? 'OBSERVE_ONLY' : avgChange < -5 ? 'POTENTIAL_ENTRY' : 'NEUTRAL',
        mid_term: 'ACCUMULATE_ON_DIPS',
        long_term: 'HOLD_STRONG_HANDS'
      }
    });
  }
  
  // 配置
  if (path === '/api/config' || path === '/config') {
    return res.status(200).json({
      observer: 'THE MACHINE',
      config: {
        watchlist: ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT'],
        alerts: {
          drop_threshold: -5,
          rise_threshold: 5,
          volatility_threshold: 10
        },
        analysis_mode: 'MULTI_FACTOR',
        risk_model: 'CONSERVATIVE'
      },
      personality: {
        approach: 'ANALYTICAL_DETACHMENT',
        communication: 'PRECISE_CONCISE',
        motto: 'I SEE PATTERNS. I DO NOT JUDGE.'
      }
    });
  }
  
  // 404
  return res.status(404).json({
    error: 'NOT_OBSERVED',
    message: 'This endpoint does not exist.',
    observed_paths: ['/', '/api/status', '/api/market', '/api/signals', '/api/analysis', '/api/config']
  });
};

// === HELPER FUNCTIONS ===

async function fetchBinanceData(symbol) {
  return new Promise((resolve) => {
    const url = `https://api.binance.com/api/v3/ticker/24hr?symbol=${symbol.replace('/', '')}`;
    
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const t = JSON.parse(data);
          resolve({
            symbol: symbol,
            price: parseFloat(t.lastPrice) || 0,
            change: parseFloat(t.priceChangePercent) || 0,
            high: parseFloat(t.highPrice) || 0,
            low: parseFloat(t.lowPrice) || 0,
            volume: parseFloat(t.quoteVolume) || 0
          });
        } catch (e) {
          resolve(null);
        }
      });
    }).on('error', () => resolve(null));
  });
}

function getSentiment(change) {
  if (change >= 5) return 'EUPHORIA 🚀';
  if (change >= 2) return 'OPTIMISTIC 😊';
  if (change >= -2) return 'NEUTRAL 😐';
  if (change >= -5) return 'PESSIMISTIC 😟';
  return 'PANIC 📉';
}

function getAction(change) {
  if (change >= 5) return 'WAIT';  // 追高危险
  if (change >= 2) return 'OBSERVE';
  if (change >= -2) return 'NEUTRAL';
  if (change >= -5) return 'MONITOR';
  return 'POTENTIAL_ENTRY';
}

function calculateConfidence(coin) {
  // 基于波动性和变化计算置信度
  const volatility = coin.change;
  const base = 0.6;
  
  if (Math.abs(volatility) > 10) return Math.min(base + 0.2, 0.95);
  if (Math.abs(volatility) > 5) return Math.min(base + 0.1, 0.85);
  return base;
}

function getRiskLevel(change) {
  if (Math.abs(change) > 10) return 'EXTREME';
  if (Math.abs(change) > 5) return 'HIGH';
  if (Math.abs(change) > 2) return 'MEDIUM';
  return 'LOW';
}

function identifyMarketPhase(avgChange, changes) {
  const positives = changes.filter(c => c > 0).length;
  const negatives = changes.filter(c => c < 0).length;
  
  if (positives === negatives) return 'ACCUMULATION';
  if (positives > negatives && avgChange > 2) return 'EXPANSION';
  if (negatives > positives && avgChange < -2) return 'DISTRIBUTION';
  return 'CONSOLIDATION';
}

function generateInsights(coins) {
  const insights = [];
  
  // BTC 主导性
  const btc = coins.find(c => c.symbol === 'BTC/USDT');
  if (btc) {
    if (btc.change > 3) {
      insights.push('BTC leading. Alt follow pattern likely.');
    } else if (btc.change < -3) {
      insights.push('BTC weakness. Risk aversion increasing.');
    }
  }
  
  // 板块轮动
  const alts = coins.filter(c => c.symbol !== 'BTC/USDT');
  const altPerformance = alts.map(c => c.change);
  const avgAlt = altPerformance.reduce((a, b) => a + b, 0) / altPerformance.length;
  
  if (btc && avgAlt > btc.change + 2) {
    insights.push('Alt season signal. DeFi tokens may outperform.');
  }
  
  // 波动性警告
  const highVol = coins.filter(c => Math.abs(c.change) > 5);
  if (highVol.length > 0) {
    insights.push(`High volatility in: ${highVol.map(c => c.symbol).join(', ')}`);
  }
  
  return insights.length > 0 ? insights : ['Market stability observed. No unusual patterns.'];
}
