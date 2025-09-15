#!/usr/bin/env python3
"""Simple server starter for Sophia's Vocabulary Trainer"""

import os
import sys
import subprocess

# Change to the src directory
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, 'src')
os.chdir(src_dir)

# Add src to Python path
sys.path.insert(0, src_dir)

# Get Tailscale IP if available
try:
    result = subprocess.run(['tailscale', 'ip', '-4'], capture_output=True, text=True)
    tailscale_ip = result.stdout.strip() if result.returncode == 0 else None
except:
    tailscale_ip = None

print("🚀 Starting Sophia's Vocabulary Trainer...")
print("=" * 50)
print("\n📡 Access the app at:")
print("  • Local: http://localhost:5005")
if tailscale_ip:
    print(f"  • Tailscale: http://{tailscale_ip}:5005")
print("\nPress Ctrl+C to stop the server")
print("=" * 50)

# Import and run the app
from app import app
app.run(host='0.0.0.0', port=5005, debug=True, use_reloader=False)