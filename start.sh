#!/bin/bash

echo "================================================"
echo "  PassportApp - Flask Authentication System"
echo "================================================"
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing/Updating dependencies..."
pip install -r requirements.txt --quiet

echo ""
echo "Starting Flask application..."
echo "Open http://localhost:5000 in your browser"
echo "Press Ctrl+C to stop the server"
echo ""

python run.py
