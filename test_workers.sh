#!/bin/bash
# Test connectivity to all workers
# Run this from the coordinator machine

echo "🔍 Testing Worker Connectivity"
echo "=============================="
echo ""

# Read IPs from config (simplified - assumes default config)
WORKERS=(
    "192.168.1.10:5001"
    "192.168.1.10:5002"
    "192.168.1.20:5001"
    "192.168.1.20:5002"
)

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
