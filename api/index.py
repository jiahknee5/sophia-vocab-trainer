"""
Vercel serverless function entry point
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the app from root
from app import app

# Export for Vercel
handler = app