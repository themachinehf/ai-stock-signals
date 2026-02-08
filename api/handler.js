/**
 * Crypto AI Signal Agent API - Vercel Serverless
 */

const https = require('https');

module.exports = async (req, res) => {
  const path = req.url || '/';
  
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  // Health check
  if (path === '/api/health' || path === '/health') {
    return res.status(200).json({
      status: 'healthy',
      message: 'Crypto AI Signal Agent API'
    });
  }
  
  // Root
  if (path === '/' || path === '') {
    return res.status(200).json({
      name: 'Crypto AI Signal Agent API',
      version: '1.0.0',
      status: 'running',
      endpoints: {
        health: '/api/health',
        market: '/api/market',
        signals: '/api/signals'
      }
    });
  }
  
  // Market data (fetch from Binance)
  if (path === '/api/market' || path === '/market') {
    try {
      const marketData = await fetchMarketData();
      return res.status(200).json(marketData);
    } catch (error) {
      return res.status(500).json({ error: error.message });
    }
  }
  
  // Signals list
  if (path === '/api/signals' || path === '/signals') {
    return res.status(200).json({
      status: 'ok',
      message: 'Signal generation ready',
      watchlist: ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT', 'DOGE/USDT', 'MATIC/USDT', 'LTC/USDT', 'LINK/USDT']
    });
  }
  
  // 404
  return res.status(404).json({ error: 'Not found', path });
};

async function fetchMarketData() {
  return new Promise((resolve, reject) => {
    https.get('https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT', (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          console.log('Binance response:', data);
          const ticker = JSON.parse(data);
          const change = parseFloat(ticker.priceChangePercent) || 0;
          resolve({
            status: 'ok',
            btc_price: parseFloat(ticker.lastPrice) || 0,
            btc_change: change,
            market_sentiment: getSentiment(change),
            timestamp: Date.now()
          });
        } catch (e) {
          console.error('Parse error:', e);
          // Return mock data if API fails
          resolve({
            status: 'ok_mock',
            btc_price: 69443,
            btc_change: -1.41,
            market_sentiment: '中性 😐',
            timestamp: Date.now(),
            note: 'Using mock data - Binance API unavailable'
          });
        }
      });
    }).on('error', (e) => {
      console.error('API error:', e);
      resolve({
        status: 'ok_mock',
        btc_price: 69443,
        btc_change: -1.41,
        market_sentiment: '中性 😐',
        timestamp: Date.now(),
        note: 'Using mock data - API error'
      });
    });
  });
}

function getSentiment(change) {
  if (change >= 5) return '极度乐观 🚀';
  if (change >= 2) return '乐观 😊';
  if (change >= -2) return '中性 😐';
  if (change >= -5) return '悲观 😟';
  return '极度悲观 📉';
}
