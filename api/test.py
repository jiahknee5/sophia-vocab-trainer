"""
Minimal test endpoint to debug Vercel
"""

def handler(request):
    """Simple test handler"""
    return {
        'body': 'Hello from test endpoint',
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        }
    }