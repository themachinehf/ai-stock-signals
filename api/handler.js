/**
 * Crypto AI Signal Agent - THE MACHINE Edition
 */

const https = require('https');

module.exports = async (req, res) => {
  const url = (req.url || '/').split('?')[0];
  const method = req.method;
  
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  if (method === 'OPTIONS') return res.status(200).end();
  
  // Root - serve HTML
  if (url === '/' || url === '') {
    res.setHeader('Content-Type', 'text/html');
    return res.status(200).send(generateHTML());
  }
  
  // API endpoints
  if (url.startsWith('/api/')) {
    res.setHeader('Content-Type', 'application/json');
    
    if (url === '/api/status' || url === '/status') {
      const btc = await fetchBinance('BTC/USDT');
      const eth = await fetchBinance('ETH/USDT');
      const sol = await fetchBinance('SOL/USDT');
      return res.status(200).json({
        timestamp: Date.now(), 
        observer: 'THE MACHINE',
        market: { BTC: btc, ETH: eth, SOL: sol },
        status: { market_sentiment: getSentiment(btc?.change || 0) }
      });
    }
    
    if (url === '/api/analysis' || url === '/analysis') {
      const btc = await fetchBinance('BTC/USDT');
      const change = btc?.change || 0;
      return res.status(200).json({
        timestamp: Date.now(), 
        observer: 'THE MACHINE',
        summary: { 
          market_phase: 'ACCUMULATION', 
          dominant_trend: change > 2 ? 'BULLISH' : change < -2 ? 'BEARISH' : 'NEUTRAL' 
        },
        risk: { overall: Math.abs(change) > 5 ? 'HIGH' : Math.abs(change) > 2 ? 'MEDIUM' : 'LOW' }
      });
    }
    
    if (url === '/api/signals' || url === '/signals') {
      return res.status(200).json({
        observer: 'THE MACHINE', 
        timestamp: Date.now(),
        signals: [{ symbol: 'BTC/USDT', action: 'NEUTRAL', risk_level: 'LOW', confidence: 0.6 }]
      });
    }
    
    return res.status(404).json({ error: 'NOT_FOUND' });
  }
  
  return res.status(404).json({ error: 'NOT_FOUND' });
};

function generateHTML() {
  return '<!DOCTYPE html>' +
'<html lang="en">' +
'<head>' +
'<meta charset="UTF-8">' +
'<meta name="viewport" content="width=device-width, initial-scale=1.0">' +
'<title>THE MACHINE | Crypto AI Agent</title>' +
'<style>' +
'*{margin:0;padding:0;box-sizing:border-box}' +
':root{--bg-primary:#0a0a0f;--bg-secondary:#12121a;--bg-card:#1a1a24;--text-primary:#e8e6e1;--text-secondary:#8a8a9a;--accent:#c9a962;--success:#4ade80;--danger:#f87171}' +
'body{font-family:"Courier New",monospace;background:var(--bg-primary);color:var(--text-primary);min-height:100vh}' +
'.header{background:linear-gradient(180deg,var(--bg-secondary) 0%,var(--bg-primary) 100%);border-bottom:1px solid var(--accent);padding:2rem;text-align:center}' +
'.header h1{font-size:1.5rem;font-weight:400;color:var(--accent);letter-spacing:0.3em;text-transform:uppercase}' +
'.header .subtitle{color:var(--text-secondary);font-size:0.8rem;margin-top:0.5rem}' +
'.header .motto{color:var(--accent);font-size:0.7rem;margin-top:1rem;font-style:italic}' +
'.container{max-width:1200px;margin:0 auto;padding:2rem}' +
'.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:1.5rem;margin-top:2rem}' +
'.card{background:var(--bg-card);border:1px solid #2a2a3a;padding:1.5rem}' +
'.card:hover{border-color:var(--accent)}' +
'.card-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;padding-bottom:0.75rem;border-bottom:1px solid #2a2a3a}' +
'.card-title{color:var(--accent);font-size:0.9rem;letter-spacing:0.1em;text-transform:uppercase}' +
'.card-badge{font-size:0.7rem;padding:0.25rem 0.5rem;background:var(--bg-secondary);border-radius:3px}' +
'.coin-row{display:flex;justify-content:space-between;align-items:center;padding:0.75rem 0;border-bottom:1px solid #2a2a3a}' +
'.coin-row:last-child{border-bottom:none}' +
'.coin-symbol{font-weight:bold}' +
'.coin-change{padding:0.25rem 0.5rem;border-radius:3px;font-size:0.85rem}' +
'.change-positive{background:rgba(74,222,128,0.1);color:var(--success)}' +
'.change-negative{background:rgba(248,113,113,0.1);color:var(--danger)}' +
'.loading{text-align:center;padding:3rem;color:var(--text-secondary)}' +
'.loading::after{content:"";display:inline-block;width:20px;height:20px;border:2px solid var(--accent);border-top-color:transparent;border-radius:50%;animation:spin 1s linear infinite;margin-left:1rem}' +
'@keyframes spin{to{transform:rotate(360deg)}}' +
'.timestamp{text-align:center;color:var(--text-secondary);font-size:0.7rem;margin-top:3rem;padding:1rem;border-top:1px solid #2a2a3a}' +
'.refresh-btn{position:fixed;bottom:2rem;right:2rem;background:var(--accent);color:var(--bg-primary);border:none;padding:1rem;border-radius:50%;cursor:pointer;font-size:1.2rem}' +
'</style>' +
'</head>' +
'<body>' +
'<header class="header">' +
'<h1>THE MACHINE</h1>' +
'<p class="subtitle">CRYPTO AI SIGNAL AGENT</p>' +
'<p class="motto">"I see patterns. I do not judge."</p>' +
'</header>' +
'<main class="container"><div id="app"><div class="loading">OBSERVING MARKET DATA...</div></div></main>' +
'<button class="refresh-btn" onclick="refreshData()">R</button>' +
'<footer class="timestamp"><span id="ts">--</span> | POWERED BY THE MACHINE</footer>' +
'<script>' +
'async function fetchData(url){try{return await fetch(url).then(r=>r.json())}catch(e){return null}}' +
'async function refreshData(){' +
'document.getElementById("app").innerHTML=\'<div class="loading">OBSERVING...</div>\';' +
'const s=await fetchData("/api/status"),a=await fetchData("/api/analysis"),g=await fetchData("/api/signals");' +
'renderDashboard(s,a,g);' +
'}' +
'function renderDashboard(s,a,g){' +
'document.getElementById("ts").textContent=new Date().toLocaleString();' +
'const n={BTC:{price:69443,change:-1.41},ETH:{price:2096,change:1.80},SOL:{price:87.71,change:0.39}};' +
'const m=s?.market||n;' +
'let marketRows="";' +
'Object.entries(m).forEach((e=>{' +
'if(e[1]){' +
'const t=e[1],a=t.change>=0,n=a?"change-positive":"change-negative";' +
'marketRows+=`<div class="coin-row"><span class="coin-symbol">${e[0]}</span><span class="coin-price">$${t.price.toLocaleString()}</span><span class="coin-change ${n}">${a?"+":""}${t.change.toFixed(2)}%</span></div>`;' +
'}' +
'}));' +
'let signalRows="";' +
'if(g?.signals){' +
'g.signals.forEach((e=>{' +
'signalRows+=`<div class="coin-row"><span class="coin-symbol">${e.symbol}</span><span class="coin-change">${e.action}</span></div>`;' +
'}));' +
'}' +
'document.getElementById("app").innerHTML=`' +
'<div class="grid">' +
'<div class="card"><div class="card-header"><span class="card-title">Market</span><span class="card-badge">${s?.status?.market_sentiment||"NEUTRAL"}</span></div>${marketRows}</div>' +
'<div class="card"><div class="card-header"><span class="card-title">Analysis</span><span class="card-badge">${a?.summary?.dominant_trend||"---"}</span></div>' +
'<div style="padding:0.75rem 0;border-bottom:1px solid #2a2a3a"><div style="color:var(--text-secondary);font-size:0.75rem">PHASE</div><div>${a?.summary?.market_phase||"---"}</div></div>' +
'<div style="padding:0.75rem 0"><div style="color:var(--text-secondary);font-size:0.75rem">RISK</div><div>${a?.risk?.overall||"---"}</div></div></div>' +
'<div class="card"><div class="card-header"><span class="card-title">Signals</span><span class="card-badge">${g?.total_signals||0} ACTIVE</span></div>${signalRows||\'<p style="color:var(--text-secondary)">NO SIGNALS</p>\'}</div>' +
'</div>`;' +
'}' +
'setInterval(refreshData,60000);' +
'refreshData();' +
'</script></body></html>';
}

function fetchBinance(symbol) {
  return new Promise(resolve => {
    https.get('https://api.binance.com/api/v3/ticker/24hr?symbol=' + symbol.replace('/', ''), res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const t = JSON.parse(data);
          resolve({ symbol, price: parseFloat(t.lastPrice) || 0, change: parseFloat(t.priceChangePercent) || 0 });
        } catch { resolve(null); }
      });
    }).on('error', () => resolve(null));
  });
}

function getSentiment(change) {
  if (change >= 5) return 'EUPHORIA';
  if (change >= 2) return 'OPTIMISTIC';
  if (change >= -2) return 'NEUTRAL';
  if (change >= -5) return 'PESSIMISTIC';
  return 'PANIC';
}
