"""
Vercel serverless function for Sophia's Vocabulary Trainer
"""
import os
import sys
import traceback
from pathlib import Path

try:
    # Add the src directory to the Python path
    src_path = str(Path(__file__).parent.parent / 'src')
    sys.path.insert(0, src_path)
    
    # Also add parent directory
    parent_path = str(Path(__file__).parent.parent)
    sys.path.insert(0, parent_path)
    
    # Try multiple import methods
    try:
        # Method 1: Direct from src
        from src.app import app
    except ImportError:
        try:
            # Method 2: From current directory app module
            from app import app
        except ImportError:
            # Method 3: From api.app
            from api.app import app
    
    # Create a debug endpoint to help diagnose issues
    @app.route('/debug')
    def debug():
        return {
            'status': 'ok',
            'python_version': sys.version,
            'sys_path': sys.path,
            'cwd': os.getcwd(),
            'env_vars': {
                'DATABASE_URL': bool(os.environ.get('DATABASE_URL')),
                'FLASK_ENV': os.environ.get('FLASK_ENV', 'not set')
            },
            'src_path': src_path,
            'templates_exist': os.path.exists(os.path.join(src_path, 'templates')),
            'templates_home_exist': os.path.exists(os.path.join(src_path, 'templates', 'home.html')),
            'dir_contents': os.listdir(src_path) if os.path.exists(src_path) else 'src not found'
        }
    
    # Export the app for Vercel
    handler = app
    
except Exception as e:
    # If there's an error during import, create a minimal error handler
    from flask import Flask, jsonify
    
    handler = Flask(__name__)
    
    @handler.route('/')
    def error_home():
        return jsonify({
            'error': 'Failed to load application',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500
    
    @handler.route('/debug')
    def error_debug():
        return jsonify({
            'error': 'Failed to load application',
            'message': str(e),
            'traceback': traceback.format_exc(),
            'sys_path': sys.path,
            'cwd': os.getcwd()
        }), 500