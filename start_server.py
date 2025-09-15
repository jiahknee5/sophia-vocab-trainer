#!/usr/bin/env python3
"""
Start Sophia's Vocabulary Trainer Server
Configured for Tailscale access
"""

import os
import sys
import socket
import subprocess

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

def get_tailscale_ip():
    """Get the Tailscale IP address if available"""
    try:
        result = subprocess.run(['tailscale', 'ip', '-4'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except:
        return None

def get_local_ip():
    """Get the local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def main():
    print("🚀 Starting Sophia's Vocabulary Trainer Server...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('src/app.py'):
        print("❌ Error: Cannot find src/app.py")
        print("Please run this script from the project root directory")
        sys.exit(1)
    
    # Get IP addresses
    local_ip = get_local_ip()
    tailscale_ip = get_tailscale_ip()
    
    print("\n📡 Server will be accessible at:")
    print(f"  • Local: http://localhost:5005")
    print(f"  • Network: http://{local_ip}:5005")
    if tailscale_ip:
        print(f"  • Tailscale: http://{tailscale_ip}:5005")
    print("\n✨ Share the Tailscale URL with Sophia for remote access!")
    print("=" * 50)
    print("\nPress Ctrl+C to stop the server\n")
    
    # Change to src directory
    os.chdir('src')
    
    # Import and run the app
    try:
        from app import app, db
        
        # Ensure database is created
        with app.app_context():
            db.create_all()
            print("✓ Database initialized")
        
        # Run the app
        app.run(host='0.0.0.0', port=5005, debug=True)
        
    except ImportError as e:
        print(f"❌ Error importing app: {e}")
        print("\nMake sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()