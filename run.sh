#!/bin/bash

# Navigate to project directory
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "🚀 Starting Sophia's Vocabulary Trainer..."
echo "Project directory: $PROJECT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Activate virtual environment
if [ -d "venv" ]; then
    echo "Activating local virtual environment..."
    source venv/bin/activate
elif [ -f "/Volumes/project_chimera/project_chimera_env/bin/activate" ]; then
    echo "Activating Project Chimera environment..."
    source /Volumes/project_chimera/project_chimera_env/bin/activate
else
    echo "⚠️  No virtual environment found. Using system Python."
fi

# Check if requirements are installed
echo "Checking dependencies..."
if ! python -c "import flask" 2>/dev/null; then
    echo "Installing requirements..."
    pip install -r requirements.txt || {
        echo "❌ Error: Failed to install requirements"
        exit 1
    }
fi

# Run the server
echo "Starting server..."
python start_server.py