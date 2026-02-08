"""
Vercel Serverless Handler
"""
import json
import sys
sys.path.insert(0, '.')

def handler(request):
    """Vercel Serverless Handler"""
    
    path = request.get('path', '/') if isinstance(request, dict) else '/'
    
    # Health check
    if path == '/api/health':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'status': 'healthy', 'message': 'Crypto AI Signal Agent API'})
        }
    
    # Root
    if path == '/' or path == '':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'name': 'Crypto AI Signal Agent API',
                'version': '1.0.0',
                'status': 'running',
                'endpoints': {'health': '/api/health', 'market': '/api/market', 'signals': '/api/signals'}
            })
        }
    
    # Market data
    if path == '/api/market':
        try:
            from data_collector import CryptoDataCollector
            import asyncio
            collector = CryptoDataCollector({'exchange': 'binance'})
            summary = asyncio.run(collector.get_market_summary())
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps(summary)
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': str(e)})
            }
    
    # Signals
    if path == '/api/signals':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'status': 'ok',
                'message': 'Signal generation ready',
                'watchlist': ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT', 'DOGE/USDT', 'MATIC/USDT', 'LTC/USDT', 'LINK/USDT']
            })
        }
    
    # 404
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': 'Not found', 'path': path})
    }
