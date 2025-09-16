"""
Minimal Flask app for testing
"""
try:
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return jsonify({'message': 'Hello from minimal Flask app'})
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'})
    
    handler = app
    
except Exception as e:
    # If Flask import fails, create a basic handler
    def handler(request):
        return {
            'body': f'Error: {str(e)}',
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'}
        }