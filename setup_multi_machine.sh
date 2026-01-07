#!/bin/bash
# Quick Start: Multi-Machine Deployment
# Run this on MACHINE 1 (Coordinator + 2 workers)

clear
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  NYC Taxi Map-Reduce - Multi-Machine Deployment              ║"
echo "║  Machine 1 Setup (Coordinator + Workers 1-2)                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Get this machine's IP
IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
echo "📍 This machine (Machine 1) IP: $IP"
echo ""

# Ask for Machine 2 IP
read -p "📍 Enter Machine 2 IP address: " MACHINE2_IP

echo ""
echo "Creating config for 2-machine setup..."

# Create config
cat > config.yaml <<EOF
# NYC Taxi Map-Reduce Cluster Configuration
# 2-Machine Setup

cluster:
  coordinator:
    host: "$IP"
    port: 5000
    
  workers:
    # Workers on Machine 1 (this machine)
    - id: "worker-1"
      host: "$IP"
      port: 5001
      data_dir: "./data/worker1"
      
    - id: "worker-2"
      host: "$IP"
      port: 5002
      data_dir: "./data/worker2"
      
    # Workers on Machine 2
    - id: "worker-3"
      host: "$MACHINE2_IP"
      port: 5001
      data_dir: "./data/worker3"
      
    - id: "worker-4"
      host: "$MACHINE2_IP"
      port: 5002
      data_dir: "./data/worker4"

dataset:
  path: "./data/yellow_tripdata_2024-01.parquet"
  max_records: 50000
  columns: null

execution:
  task_timeout: 300
  max_retries: 3
  heartbeat_interval: 10
  shuffle_buffer_size: 100

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "mapreduce.log"
EOF

echo "✅ Config created!"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "📋 Next Steps:"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1️⃣  ON MACHINE 2 ($MACHINE2_IP):"
echo "   a) Clone project:"
echo "      git clone <repo-url>"
echo "      cd Contemporary-Data-Processing-Systems-Project"
echo ""
echo "   b) Install dependencies:"
echo "      pip3 install -r requirements.txt"
echo ""
echo "   c) Copy this config.yaml to Machine 2"
echo "      (or sync via git)"
echo ""
echo "   d) Start workers:"
echo "      Terminal 1: python3 main.py worker worker-3 --host 0.0.0.0 --port 5001"
echo "      Terminal 2: python3 main.py worker worker-4 --host 0.0.0.0 --port 5002"
echo ""
echo "2️⃣  ON THIS MACHINE (Machine 1):"
echo "   a) Start local workers:"
echo "      Terminal 1: python3 main.py worker worker-1 --host 0.0.0.0 --port 5001"
echo "      Terminal 2: python3 main.py worker worker-2 --host 0.0.0.0 --port 5002"
echo ""
echo "3️⃣  TEST connectivity:"
echo "      ./test_workers.sh"
echo ""
echo "4️⃣  RUN coordinator:"
echo "      python3 main.py coordinator --task 1"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "💡 Tip: Run 'tmux' or 'screen' to manage multiple terminals"
echo "🔥 Firewall: Make sure ports 5001-5002 are open on both machines"
echo ""
