#!/usr/bin/env python3
"""
Check if the environment is properly set up for Sophia's Vocabulary Trainer
"""

import sys
import os
import subprocess

def check_python():
    """Check Python version"""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("  ⚠️  Python 3.7+ is recommended")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required = {
        'flask': 'Flask web framework',
        'flask_sqlalchemy': 'Flask SQLAlchemy ORM',
        'flask_migrate': 'Flask database migrations',
        'dotenv': 'Environment variable management'
    }
    
    all_good = True
    for package, description in required.items():
        try:
            __import__(package)
            print(f"✓ {description} ({package})")
        except ImportError:
            print(f"✗ Missing: {description} ({package})")
            all_good = False
    
    return all_good

def check_tailscale():
    """Check if Tailscale is installed and running"""
    try:
        result = subprocess.run(['tailscale', 'status'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Tailscale is installed and running")
            # Try to get IP
            ip_result = subprocess.run(['tailscale', 'ip', '-4'], 
                                     capture_output=True, text=True)
            if ip_result.returncode == 0:
                ip = ip_result.stdout.strip()
                print(f"  Tailscale IP: {ip}")
            return True
        else:
            print("✗ Tailscale is installed but not running")
            print("  Run: tailscale up")
            return False
    except FileNotFoundError:
        print("✗ Tailscale is not installed")
        print("  Install from: https://tailscale.com/download")
        return False

def check_files():
    """Check if all required files exist"""
    required_files = [
        'src/app.py',
        'requirements.txt',
        'run.sh',
        'start_server.py'
    ]
    
    all_good = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ Missing: {file}")
            all_good = False
    
    return all_good

def main():
    print("🔍 Checking Sophia's Vocabulary Trainer Setup")
    print("=" * 50)
    
    print("\n📍 Current directory:", os.getcwd())
    
    print("\n🐍 Python Environment:")
    check_python()
    
    print("\n📦 Dependencies:")
    deps_ok = check_dependencies()
    
    print("\n📁 Project Files:")
    files_ok = check_files()
    
    print("\n🌐 Network:")
    check_tailscale()
    
    print("\n" + "=" * 50)
    
    if deps_ok and files_ok:
        print("✅ Everything looks good!")
        print("\nTo start the server, run: ./run.sh")
    else:
        print("❌ Some issues need to be fixed")
        if not deps_ok:
            print("\nInstall dependencies with: pip install -r requirements.txt")

if __name__ == "__main__":
    main()