/**
 * Crypto AI Signal Agent - THE MACHINE Edition
 */

module.exports = (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');
  
  if (req.url === '/api/status' || req.url === '/status') {
    return res.status(200).json({
      observer: 'THE MACHINE',
      timestamp: Date.now(),
      market: { BTC: { price: 69443, change: -1.41 }, ETH: { price: 2096, change: 1.80 }, SOL: { price: 87.71, change: 0.39 } },
      status: { sentiment: 'NEUTRAL' }
    });
  }
  
  if (req.url === '/api/signals' || req.url === '/signals') {
    return res.status(200).json({
      observer: 'THE MACHINE',
      timestamp: Date.now(),
      signals: [{ symbol: 'BTC/USDT', action: 'NEUTRAL', risk: 'LOW' }]
    });
  }
  
  return res.status(200).json({ observer: 'THE MACHINE', endpoints: ['/api/status', '/api/signals'] });
};
