/**
 * Crypto AI Signal Agent - THE MACHINE Edition
 */

const http = require('http');

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');
  
  const url = (req.url || '/').split('?')[0];
  
  // Health check - Railway needs this
  if (url === '/' || url === '/health') {
    res.writeHead(200);
    res.end(JSON.stringify({ status: 'ok', observer: 'THE MACHINE' }));
    return;
  }
  
  // Status
  if (url === '/api/status' || url === '/status') {
    res.writeHead(200);
    res.end(JSON.stringify({
      observer: 'THE MACHINE',
      timestamp: Date.now(),
      market: { 
        BTC: { price: 69443, change: -1.41 }, 
        ETH: { price: 2096, change: 1.80 }, 
        SOL: { price: 87.71, change: 0.39 } 
      },
      status: { sentiment: 'NEUTRAL' }
    }));
    return;
  }
  
  // Signals
  if (url === '/api/signals' || url === '/signals') {
    res.writeHead(200);
    res.end(JSON.stringify({
      observer: 'THE MACHINE',
      timestamp: Date.now(),
      signals: [{ symbol: 'BTC/USDT', action: 'NEUTRAL', risk: 'LOW' }]
    }));
    return;
  }
  
  // Default
  res.writeHead(200);
  res.end(JSON.stringify({ observer: 'THE MACHINE', endpoints: ['/api/status', '/api/signals'] }));
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log('THE MACHINE listening on port ' + PORT);
});
