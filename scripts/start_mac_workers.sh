#!/bin/bash
# Start Mac workers in separate Terminal windows
# Automatically launches worker-1 and worker-2

# Get project root directory (parent of scripts folder)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting Mac Workers (worker-1, worker-2)"
echo "============================================="
echo ""

# Check if config.yaml exists
if [ ! -f "$PROJECT_DIR/config.yaml" ]; then
    echo "❌ Error: config.yaml not found!"
    echo "   Copy config.yaml.example to config.yaml and edit with your IPs"
    exit 1
fi

# Get Mac IP
MAC_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)
echo "📍 Mac IP: $MAC_IP"
echo ""

# Start worker-1 in new Terminal window
echo "▶️  Starting worker-1 (port 5001)..."
osascript -e "tell application \"Terminal\"
    do script \"cd '$PROJECT_DIR' && echo '🔷 Worker 1 (Mac - Port 5001)' && echo '' && python3 main.py worker worker-1 --host 0.0.0.0 --port 5001\"
    activate
end tell" >/dev/null 2>&1

sleep 1

# Start worker-2 in new Terminal window
echo "▶️  Starting worker-2 (port 5002)..."
osascript -e "tell application \"Terminal\"
    do script \"cd '$PROJECT_DIR' && echo '🔷 Worker 2 (Mac - Port 5002)' && echo '' && python3 main.py worker worker-2 --host 0.0.0.0 --port 5002\"
    activate
end tell" >/dev/null 2>&1

sleep 1

echo ""
echo "✅ Workers launched in separate Terminal windows!"
echo ""
echo "📋 Next Steps:"
echo "  1. Make sure Windows workers are running (on Windows PC)"
echo "  2. Test connectivity: ./test_workers.sh"
echo "  3. Run coordinator: python3 main.py coordinator --task 1"
echo ""
