#!/bin/bash
# Quick setup script for Machine 2 (remote workers)
# Run this on the second physical machine

echo "🔧 Setting up Worker Node (Machine 2)"
echo "======================================"

# Get IP
IP=$(hostname -I | awk '{print $1}')
echo "📍 This machine IP: $IP"

# Check if project exists
if [ ! -d "Contemporary-Data-Processing-Systems-Project" ]; then
    echo "❌ Project not found. Clone it first:"
    echo "   git clone <repo-url>"
    exit 1
fi

cd Contemporary-Data-Processing-Systems-Project

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Create data directory
mkdir -p data/worker3 data/worker4

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start workers on this machine, run:"
echo ""
echo "   Terminal 1:"
echo "   python3 main.py worker worker-3 --host 0.0.0.0 --port 5001"
echo ""
echo "   Terminal 2:"
echo "   python3 main.py worker worker-4 --host 0.0.0.0 --port 5002"
echo ""
echo "📝 Don't forget to update config.yaml on Machine 1 with this IP: $IP"
