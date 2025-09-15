"""
Vercel serverless function for Sophia's Vocabulary Trainer
"""
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import the Flask app
from app import app

# Export the app for Vercel
handler = app