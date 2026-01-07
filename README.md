# NYC Taxi Map-Reduce Analysis

**Contemporary Data Processing Systems Project**  
**Politechnika Łódzka, Semestr Zimowy 2025/2026**

Distributed map-reduce system for analyzing 3M NYC Taxi trip records across 2 physical machines (Mac + Windows).

---

## 👥 Team

- **Sergiusz Cudo** - Task 1: Tip Analysis by Pickup Zone
- **Ludwik Janowski** - Task 2: Route Profitability Analysis  
- **Marcin Kopka** - Task 3: Hourly Traffic Distribution
- **Supervisor:** Prof. Tomasz Kowalski

---

## 🚀 Quick Start (Multi-Machine Deployment)

### Prerequisites
- **Machine 1 (Mac):** Python 3.9+, Git, 48MB dataset
- **Machine 2 (Windows):** Python 3.9+, Git
- Both machines on the **same WiFi network**

### Setup

#### 1️⃣ On Mac (Coordinator + Workers 1-2)

```bash
# Clone and setup
git clone <repo-url>
cd Contemporary-Data-Processing-Systems-Project
pip3 install -r requirements.txt

# Download NYC Taxi data (48MB)
cd data
wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet
cd ..

# Get Mac IP address
ifconfig getifaddr en0  # e.g., 192.168.1.16

# Copy config.yaml.example to config.yaml and edit:
cp config.yaml.example config.yaml
nano config.yaml  # Update IPs
```

#### 2️⃣ On Windows PC (Workers 3-4)

```powershell
# Clone project
git clone <repo-url>
cd Contemporary-Data-Processing-Systems-Project

# Install dependencies
pip install -r requirements.txt

# Get Windows IP
ipconfig  # Note IPv4 Address, e.g., 192.168.1.15

# Configure Windows Firewall (Run PowerShell as Administrator!)
.\scripts\setup_windows_firewall.ps1

# Copy config.yaml from Mac (via Git/USB/email)
```

#### 3️⃣ Configure IPs

Edit `config.yaml` on **both machines**:

```yaml
cluster:
  workers:
    - id: "worker-1"
      host: "192.168.1.16"  # Mac IP
      port: 5001
    - id: "worker-2"
      host: "192.168.1.16"  # Mac IP
      port: 5002
    - id: "worker-3"
      host: "192.168.1.15"  # Windows IP
      port: 5001
    - id: "worker-4"
      host: "192.168.1.15"  # Windows IP
      port: 5002

dataset:
  path: "./data/yellow_tripdata_2024-01.parquet"
  max_records: null  # Process all 2.96M records
```

### Run

#### On Windows PC:
```powershell
# Start workers (opens 2 PowerShell windows)
.\scripts\start_windows_workers.ps1
```

#### On Mac:
```bash
# Start Mac workers (opens 2 Terminal windows)
./scripts/start_mac_workers.sh

# Test connectivity to all 4 workers
./scripts/test_workers.sh

# Run Task 1
python3 main.py coordinator --task 1

# Run Task 2
python3 main.py coordinator --task 2

# Run Task 3
python3 main.py coordinator --task 3
```

**Results saved to:** `results_task1.txt`, `results_task2.txt`, `results_task3.txt`

---

## 📊 Tasks

### Task 1: Tip Analysis by Pickup Zone
**Author:** Sergiusz Cudo

Analyzes average tip percentage for each NYC taxi zone.

- **Map:** `(trip) → (pickup_zone_id, tip_percentage)`
- **Reduce:** `(zone_id, [tips]) → (zone_id, avg_tip_pct)`
- **Output:** 577 zones sorted by tip percentage

**Example Result:**
```
Zone 216: 4294.21% avg tip
Zone 265: 3567.86% avg tip
Zone 133: 142.48% avg tip
```

---

### Task 2: Route Profitability
**Author:** Ludwik Janowski

Calculates revenue per mile for pickup→dropoff routes.

- **Map:** `(trip) → ("pickup->dropoff", revenue_per_mile)`
- **Reduce:** `(route, [revenues]) → (route, avg_revenue_per_mile)`
- **Output:** 37,738 routes sorted by profitability

**Example Result:**
```
85->265: $11,260/mile
80->255: $9,355/mile
88->12: $7,900/mile
```

---

### Task 3: Hourly Traffic Distribution
**Author:** Marcin Kopka

Analyzes trip counts by hour of day.

- **Map:** `(trip) → (hour, 1)`
- **Reduce:** `(hour, [counts]) → (hour, total_count)`
- **Output:** 24 hours with trip counts

**Example Result:**
```
14:00: 141,826 trips (peak)
19:00: 135,955 trips
23:00: 55,539 trips (quietest)
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│  Mac (192.168.1.16)                                 │
│  ┌──────────────┐  ┌─────────┐  ┌─────────┐       │
│  │ Coordinator  │  │Worker-1 │  │Worker-2 │       │
│  │  (Flask)     │  │ :5001   │  │ :5002   │       │
│  └──────┬───────┘  └────┬────┘  └────┬────┘       │
│         │               │HTTP        │HTTP         │
└─────────┼───────────────┼────────────┼─────────────┘
          │               │            │
          │ HTTP          │            │
          ▼               ▼            ▼
┌─────────────────────────────────────────────────────┐
│  Windows PC (192.168.1.15)                          │
│         ┌─────────┐         ┌─────────┐            │
│         │Worker-3 │         │Worker-4 │            │
│         │ :5001   │         │ :5002   │            │
│         └─────────┘         └─────────┘            │
└─────────────────────────────────────────────────────┘
```

**Components:**
- **Coordinator:** Loads data, distributes to workers, aggregates results
- **Workers:** Execute map/reduce tasks, communicate via HTTP
- **Dataset:** 2.96M NYC Taxi records (48 MB Parquet file)

**Performance:**
- Processing: ~40 seconds for 3M records
- Throughput: ~74,000 records/second
- Network: WiFi (Mac ↔ Windows)

---

## 🛠️ Development

### Project Structure
```
Contemporary-Data-Processing-Systems-Project/
├── main.py                  # Entry point
├── config.yaml             # Cluster configuration
├── requirements.txt        # Dependencies
├── scripts/                # Helper scripts
│   ├── start_mac_workers.sh
│   ├── start_windows_workers.ps1
│   ├── test_workers.sh
│   └── setup_windows_firewall.ps1
├── src/
│   ├── core/
│   │   ├── coordinator.py  # Coordinator implementation
│   │   ├── worker.py       # Worker implementation
│   │   └── base.py         # Mapper/Reducer base classes
│   ├── tasks/
│   │   ├── task1_tip_analysis.py
│   │   ├── task2_route_profitability.py
│   │   └── task3_hourly_traffic.py
│   └── utils/
│       └── parquet_loader.py
├── tests/                  # Unit tests (29 tests)
└── data/                   # Dataset directory
```

### Run Tests
```bash
python3 -m pytest tests/ -v
# 29/29 passing
```

### Manual Worker Start
```bash
# Mac - Terminal 1
python3 main.py worker worker-1 --host 0.0.0.0 --port 5001

# Mac - Terminal 2
python3 main.py worker worker-2 --host 0.0.0.0 --port 5002
```

```powershell
# Windows - PowerShell 1
python main.py worker worker-3 --host 0.0.0.0 --port 5001

# Windows - PowerShell 2
python main.py worker worker-4 --host 0.0.0.0 --port 5002
```

---

## 🔧 Troubleshooting

### Windows Firewall Issues
If Mac can't connect to Windows workers:

```powershell
# Run as Administrator
.\scripts\setup_windows_firewall.ps1

# Or manually: Windows Defender Firewall → Advanced Settings
# → Inbound Rules → New Rule → Port → TCP 5001,5002 → Allow
```

### IP Changed After Sleep
IPs may change after restart/WiFi reconnect. Check and update `config.yaml`:

```bash
# Mac
ifconfig getifaddr en0

# Windows
ipconfig
```

### Connection Refused
1. Check workers are running: `./scripts/test_workers.sh`
2. Verify firewall ports 5001-5002 are open
3. Ensure `--host 0.0.0.0` (not `localhost`)
4. Both machines on same WiFi

### "Module not found"
```bash
pip3 install -r requirements.txt  # Mac
pip install -r requirements.txt   # Windows
```

---

## 📦 Dependencies

```
Flask==3.1.0
pandas==2.2.3
pyarrow==18.1.0
requests==2.32.3
PyYAML==6.0.2
dill==0.3.9
pytest==8.3.4
```

---

## 📝 Dataset

**Source:** NYC Taxi & Limousine Commission  
**File:** `yellow_tripdata_2024-01.parquet` (January 2024)  
**Size:** 48 MB  
**Records:** 2,964,624 trips  
**Download:** https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

**Key Fields:**
- `PULocationID`, `DOLocationID` - Pickup/dropoff zones
- `fare_amount`, `tip_amount`, `total_amount` - Payment info
- `trip_distance` - Distance in miles
- `tpep_pickup_datetime` - Pickup timestamp

---

## 🎓 Academic Context

**Course:** Contemporary Data Processing Systems  
**Institution:** Politechnika Łódzka (Lodz University of Technology)  
**Semester:** Winter 2025/2026

**Learning Objectives:**
- Distributed systems design
- Map-Reduce paradigm
- HTTP-based worker communication
- Cross-platform deployment (Mac/Windows)
- Large-scale data processing

---

## 📄 License

Academic project for educational purposes.

**NYC TLC Data License:**  
Data provided by NYC Taxi & Limousine Commission under Open Data initiative.
