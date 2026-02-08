/**
 * Crypto AI Signal Agent - THE MACHINE Edition
 * 
 * Usage:
 * - Run as server: node api/handler.js
 * - Export for testing: require('./api/handler.js')
 */

const http = require('http');

// Handler function for cron jobs / testing
function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');
  
  const url = (req.url || '/').split('?')[0];
  
  // Health check
  if (url === '/' || url === '/health') {
    res.status(200).json({ status: 'ok', observer: 'THE MACHINE' });
    return;
  }
  
  // Status
  if (url === '/api/status' || url === '/status') {
    res.status(200).json({
      observer: 'THE MACHINE',
      timestamp: Date.now(),
      market: { 
        BTC: { price: 69443, change: -1.41 }, 
        ETH: { price: 2096, change: 1.80 }, 
        SOL: { price: 87.71, change: 0.39 } 
      },
      status: { sentiment: 'NEUTRAL' }
    });
    return;
  }
  
  // Signals
  if (url === '/api/signals' || url === '/signals') {
    res.status(200).json({
      observer: 'THE MACHINE',
      timestamp: Date.now(),
      signals: [{ symbol: 'BTC/USDT', action: 'NEUTRAL', risk: 'LOW' }]
    });
    return;
  }
  
  // Default
  res.status(200).json({ observer: 'THE MACHINE', endpoints: ['/api/status', '/api/signals'] });
}

// Export for testing/cron
module.exports = handler;

// Run as server if executed directly
if (require.main === module) {
  const PORT = process.env.PORT || 3000;
  http.createServer(handler).listen(PORT, () => {
    console.log('THE MACHINE listening on port ' + PORT);
  });
}
