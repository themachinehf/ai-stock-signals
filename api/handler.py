"""
Vercel Serverless Handler - Simple Test
"""
import json

def handler(request):
    """Simple Vercel Handler - Test"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({
            'status': 'healthy',
            'message': 'Crypto AI Signal Agent API',
            'test': 'ok'
        })
    }
