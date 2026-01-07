#!/bin/bash
# Test connectivity to all workers
# Run this from the coordinator machine

echo "🔍 Testing Worker Connectivity"
echo "=============================="
echo ""

# Read worker addresses from config.yaml using Python
CONFIG_FILE="config.yaml"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Error: config.yaml not found!"
    echo "   Copy config.yaml.example and edit with your IPs"
    exit 1
fi

# Extract workers using Python
WORKERS=($(python3 -c "
import yaml
with open('$CONFIG_FILE') as f:
    config = yaml.safe_load(f)
    for w in config['cluster']['workers']:
        print(f\"{w['host']}:{w['port']}\")
"))

echo "📡 Testing workers..."
echo ""

for worker in "${WORKERS[@]}"; do
    echo -n "Testing $worker ... "
    
    # Try to connect
    response=$(curl -s -m 2 "http://$worker/health" 2>/dev/null)
    
    if [ $? -eq 0 ] && [[ $response == *"healthy"* ]]; then
        echo "✅ OK"
    else
        echo "❌ FAILED"
        echo "   Make sure worker is running:"
        echo "   python3 main.py worker <id> --host 0.0.0.0 --port <port>"
    fi
done

echo ""
echo "🎯 If all workers are OK, you can run:"
echo "   python3 main.py coordinator --task 1"
