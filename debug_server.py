#!/usr/bin/env python3
"""Debug server startup for Sophia's Vocabulary Trainer"""

import os
import sys
import socket
import traceback

print("🔍 Debugging Sophia's Vocabulary Trainer Server...")
print("=" * 60)

# Check current directory
print(f"Current directory: {os.getcwd()}")

# Check if we're in the right place
project_root = os.path.dirname(os.path.abspath(__file__))
print(f"Project root: {project_root}")

# Check if src directory exists
src_path = os.path.join(project_root, 'src')
if os.path.exists(src_path):
    print(f"✓ Found src directory: {src_path}")
else:
    print(f"✗ src directory not found at: {src_path}")
    sys.exit(1)

# Check if app.py exists
app_path = os.path.join(src_path, 'app.py')
if os.path.exists(app_path):
    print(f"✓ Found app.py: {app_path}")
else:
    print(f"✗ app.py not found at: {app_path}")
    sys.exit(1)

# Change to src directory
os.chdir(src_path)
sys.path.insert(0, src_path)
print(f"Changed to src directory: {os.getcwd()}")

# Check Python version
print(f"\nPython version: {sys.version}")

# Check if Flask is installed
try:
    import flask
    print(f"✓ Flask installed: version {flask.__version__ if hasattr(flask, '__version__') else 'unknown'}")
except ImportError as e:
    print(f"✗ Flask not installed: {e}")
    sys.exit(1)

# Check other dependencies
deps = ['flask_sqlalchemy', 'flask_migrate', 'dotenv']
for dep in deps:
    try:
        __import__(dep)
        print(f"✓ {dep} installed")
    except ImportError:
        print(f"✗ {dep} not installed")

# Check if port 5005 is available
def is_port_open(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result != 0
    except:
        return True

print(f"\nPort 5005 available: {'✓ Yes' if is_port_open(5005) else '✗ No (already in use)'}")

# Try to import and run the app
print("\n" + "=" * 60)
print("Attempting to start the server...")
print("=" * 60)

try:
    from app import app, db
    
    # Test database initialization
    with app.app_context():
        print("✓ App context created successfully")
        try:
            db.create_all()
            print("✓ Database tables created/verified")
        except Exception as e:
            print(f"✗ Database error: {e}")
    
    # Get network info
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"\n🚀 Starting server...")
    print(f"Local: http://localhost:5005")
    print(f"Network: http://{local_ip}:5005")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)
    
    # Run the app with explicit settings
    app.run(
        host='0.0.0.0',
        port=5005,
        debug=True,
        use_reloader=False,
        threaded=True
    )
    
except Exception as e:
    print(f"\n❌ Error starting server:")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)