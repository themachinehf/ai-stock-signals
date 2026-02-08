/**
 * Crypto AI Signal Agent - THE MACHINE Edition
 * Using OKX API
 */

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  
  if (req.url === '/api/status' || req.url === '/status') {
    res.setHeader('Content-Type', 'application/json');
    const [btc, eth, sol] = await Promise.all([
      fetchOKX('BTC-USDT'),
      fetchOKX('ETH-USDT'),
      fetchOKX('SOL-USDT')
    ]);
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

async function fetchOKX(symbol) {
  const https = require('https');
  return new Promise((resolve) => {
    const url = `https://www.okx.com/api/v5/market/ticker?instId=${symbol}`;
    https.get(url, (resp) => {
      let data = '';
      resp.on('data', (chunk) => data += chunk);
      resp.on('end', async () => {
        try {
          const json = JSON.parse(data);
          if (json.data && json.data[0]) {
            const t = json.data[0];
            const change = parseFloat(t.sodUtc8) ? ((parseFloat(t.last) - parseFloat(t.sodUtc8)) / parseFloat(t.sodUtc8)) * 100 : 0;
            resolve({ symbol: symbol.replace('-', '/'), price: parseFloat(t.last) || 0, change: change });
          } else {
            resolve({ symbol: symbol.replace('-', '/'), price: 0, change: 0 });
          }
        } catch (e) {
          resolve({ symbol: symbol.replace('-', '/'), price: 0, change: 0 });
        }
      });
    }).on('error', () => resolve({ symbol: symbol.replace('-', '/'), price: 0, change: 0 }));
  });
}

function getSentiment(change) {
  if (change >= 5) return 'EUPHORIA';
  if (change >= 2) return 'OPTIMISTIC';
  if (change >= -2) return 'NEUTRAL';
  if (change >= -5) return 'PESSIMISTIC';
  return 'PANIC';
}
