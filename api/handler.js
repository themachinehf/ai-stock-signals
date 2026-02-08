/**
 * Crypto AI Signal Agent - THE MACHINE Edition
 */

const https = require('https');

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  
  const url = (req.url || '/').split('?')[0];
  
  // Root
  if (url === '/') {
    res.setHeader('Content-Type', 'text/html');
    return res.status(200).send('<h1>THE MACHINE</h1><p>Loading...</p><script>setInterval(async()=>{try{const r=await fetch("/api/status");const j=await r.json();let h="<h3>MARKET</h3>";Object.entries(j.market||{}).forEach((e=>{if(e[1]){const r=e[1],s=r.change>=0?"color:#4ade80":"color:#f87171";h+="<div>"+e[0]+":$"+r.price.toLocaleString()+" <span style=\""+s+"\">"+(r.change>=0?"+":"")+r.change.toFixed(2)+"%</span></div>"}}));document.body.innerHTML=h}catch(e){}},5000)</script>');
  }
  
  // API
  if (url.startsWith('/api/')) {
    res.setHeader('Content-Type', 'application/json');
    const btc = await fetchBinance('BTC/USDT');
    const eth = await fetchBinance('ETH/USDT');
    const sol = await fetchBinance('SOL/USDT');
    return res.status(200).json({
      timestamp: Date.now(),
      observer: 'THE MACHINE',
      market: { BTC: btc, ETH: eth, SOL: sol },
      status: { market_sentiment: getSentiment(btc?.change||0) }
    });
  }
  
  return res.status(404).json({error:'NOT_FOUND'});
};

function fetchBinance(symbol) {
  return new Promise(resolve => {
    https.get('https://api.binance.com/api/v3/ticker/24hr?symbol='+symbol.replace('/',''), res => {
      let d=''; res.on('data', c => d+=c); res.on('end', () => {
        try { const t=JSON.parse(d); resolve({symbol,price:parseFloat(t.lastPrice)||0,change:parseFloat(t.priceChangePercent)||0}); } catch { resolve(null); }
      });
    }).on('error', () => resolve(null));
  });
}

function getSentiment(c) {
  if (c>=5) return 'EUPHORIA'; if (c>=2) return 'OPTIMISTIC'; if (c>=-2) return 'NEUTRAL'; if (c>=-5) return 'PESSIMISTIC'; return 'PANIC';
}
