/**
 * Crypto AI Signal Agent - THE MACHINE Edition
 */

const https = require('https');

module.exports = async (req, res) => {
  const url = (req.url || '/').split('?')[0];
  res.setHeader('Access-Control-Allow-Origin', '*');
  
  if (url === '/') {
    res.setHeader('Content-Type', 'text/html');
    return res.status(200).send('<html><head><title>THE MACHINE</title></head><body style="background:#0a0a0f;color:#e8e6e1;font-family:monospace;text-align:center;padding:50px"><h1 style="color:#c9a962;letter-spacing:5px">THE MACHINE</h1><p>CRYPTO AI SIGNAL AGENT</p><p style="color:#8a8a9a">"I see patterns. I do not judge."</p><div id="d" style="margin:30px auto;max-width:500px;text-align:left">LOADING...</div><script>setInterval(async()=>{const d=document.getElementById("d");try{const r=await fetch("/api/status");const j=await r.json();let h="<h3>MARKET</h3>";Object.entries(j.market||{}).forEach((e=>{if(e[1]){const r=e[1],s=r.change>=0?"color:#4ade80":"color:#f87171";h+="<div style=\\"display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #2a2a3a\\"><span>"+e[0]+"</span><span>$"+r.price.toLocaleString()+"</span><span style=\\""+s+ "\\">"+(r.change>=0?"+":"")+r.change.toFixed(2)+"%</span></div>"}}));d.innerHTML=h}catch(e){d.innerHTML="ERROR"}},5000)</script></body></html>');
  }
  
  if (url.startsWith('/api/')) {
    res.setHeader('Content-Type', 'application/json');
    const btc = await fetchBinance('BTC/USDT');
    if (url === '/api/status' || url === '/status') {
      const eth = await fetchBinance('ETH/USDT');
      const sol = await fetchBinance('SOL/USDT');
      return res.status(200).json({timestamp:Date.now(),observer:'THE MACHINE',market:{BTC:btc,ETH:eth,SOL:sol},status:{market_sentiment:getSentiment(btc?.change||0)}});
    }
    return res.status(200).json({observer:'THE MACHINE',signals:[{symbol:'BTC/USDT',action:'NEUTRAL',risk:'LOW'}]});
  }
  return res.status(404).json({error:'NOT_FOUND'});
};

function fetchBinance(symbol) {
  return new Promise(resolve => {
    https.get('https://api.binance.com/api/v3/ticker/24hr?symbol='+symbol.replace('/',''), res => {
      let d=''; res.on('data', chunk => d+=chunk); res.on('end', () => {
        try { const t=JSON.parse(d); resolve({symbol,price:parseFloat(t.lastPrice)||0,change:parseFloat(t.priceChangePercent)||0}); } catch { resolve(null); }
      });
    }).on('error', () => resolve(null));
  });
}

function getSentiment(c) {
  if (c>=5) return 'EUPHORIA'; if (c>=2) return 'OPTIMISTIC'; if (c>=-2) return 'NEUTRAL'; if (c>=-5) return 'PESSIMISTIC'; return 'PANIC';
}
