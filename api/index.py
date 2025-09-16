"""
Vercel serverless function entry point
"""
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the Flask app
from app import app

# Vercel expects the variable to be named 'app'
# This is the WSGI application
app = app