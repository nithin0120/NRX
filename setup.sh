#!/bin/bash

echo "Neural Remix Engine - Setup"
echo "============================"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo ""
echo "Creating necessary directories..."
mkdir -p uploads outputs cache

echo ""
echo "Setup complete!"
echo ""
echo "To start the application:"
echo "1. Run: ./run_dev.sh"
echo "2. In another terminal, run: cd frontend && npm start"
echo ""
echo "Or use Docker: docker-compose up"

