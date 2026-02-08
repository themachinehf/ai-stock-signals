/**
 * Crypto AI Signal Agent - THE MACHINE Edition
 */

const https = require('https');

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  
  if (req.url === '/api/status' || req.url === '/status') {
    res.setHeader('Content-Type', 'application/json');
    const btc = await fetchBinance('BTC/USDT');
    const eth = await fetchBinance('ETH/USDT');
    const sol = await fetchBinance('SOL/USDT');
    return res.status(200).json({
      observer: 'THE MACHINE',
      timestamp: Date.now(),
      market: { BTC: btc, ETH: eth, SOL: sol },
      status: { sentiment: getSentiment(btc?.change || 0) }
    });
  }
  
  if (req.url === '/api/signals' || req.url === '/signals') {
    res.setHeader('Content-Type', 'application/json');
    return res.status(200).json({
      observer: 'THE MACHINE',
      timestamp: Date.now(),
      signals: [{ symbol: 'BTC/USDT', action: 'NEUTRAL', risk: 'LOW' }]
    });
  }
  
  res.setHeader('Content-Type', 'application/json');
  return res.status(200).json({ 
    observer: 'THE MACHINE',
    endpoints: ['/api/status', '/api/signals'] 
  });
};

function fetchBinance(symbol) {
  return new Promise((resolve) => {
    https.get('https://api.binance.com/api/v3/ticker/24hr?symbol=' + symbol.replace('/',''), (resp) => {
      let data = '';
      resp.on('data', (chunk) => data += chunk);
      resp.on('end', () => {
        try {
          const t = JSON.parse(data);
          resolve({ symbol, price: parseFloat(t.lastPrice) || 0, change: parseFloat(t.priceChangePercent) || 0 });
        } catch { resolve({ symbol, price: 0, change: 0 }); }
      });
    }).on('error', () => resolve({ symbol, price: 0, change: 0 }));
  });
}

function getSentiment(change) {
  if (change >= 5) return 'EUPHORIA';
  if (change >= 2) return 'OPTIMISTIC';
  if (change >= -2) return 'NEUTRAL';
  if (change >= -5) return 'PESSIMISTIC';
  return 'PANIC';
}
