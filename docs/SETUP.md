# Setup Guide

## Prerequisites

- **Python:** 3.9 or higher
- **pip:** Latest version
- **Operating System:** Linux, macOS, or Windows

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Contemporary-Data-Processing-Systems-Project
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies installed:**
- `flask` - Web framework for worker nodes
- `requests` - HTTP client for inter-node communication
- `pandas` - Data manipulation
- `pyarrow` - Parquet file support
- `pyyaml` - Configuration parsing
- `click` - CLI utilities
- `pytest` - Testing framework

### 4. Verify Installation

```bash
python -c "import flask, pandas, pyarrow; print('All dependencies installed successfully')"
```

---

## Configuration

### Edit config.yaml

The default configuration runs all workers on localhost. For distributed deployment:

```yaml
cluster:
  workers:
    - id: "worker-1"
      host: "192.168.1.10"  # Replace with actual IP
      port: 5001
      
    - id: "worker-2"
      host: "192.168.1.11"
      port: 5001
    # ... etc
```

### Dataset Setup

**Option 1: Use Sample Data (Testing)**

No setup required - sample data is generated automatically.

**Option 2: Use Real NYC Taxi Data**

1. Download Parquet file from NYC TLC:
   ```bash
   mkdir -p data
   cd data
   # Download from https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
   # Example: wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet
   ```

2. Update `config.yaml`:
   ```yaml
   dataset:
     path: "./data/yellow_tripdata_2024-01.parquet"
     max_records: null  # null = use all records
   ```

---

## Running the System

### Local Testing (Single Machine)

**Terminal 1 - Start Workers:**
```bash
python main.py worker worker-1 --port 5001 &
python main.py worker worker-2 --port 5002 &
python main.py worker worker-3 --port 5003 &
python main.py worker worker-4 --port 5004 &
```

**Terminal 2 - Run Coordinator:**
```bash
# Task 1: Tip Analysis
python main.py coordinator --task 1

# Task 2: Route Profitability
python main.py coordinator --task 2

# Task 3: Hourly Traffic
python main.py coordinator --task 3
```

### Quick Test with run_example.py

```bash
# This automatically starts workers and runs a task
python run_example.py 1  # Task 1
python run_example.py 2  # Task 2
python run_example.py 3  # Task 3
```

---

## Distributed Deployment (Multiple Machines)

### On Each Worker Machine:

1. Clone repository and install dependencies
2. Start worker:
   ```bash
   python main.py worker worker-1 --host 0.0.0.0 --port 5001
   ```

### On Coordinator Machine:

1. Update `config.yaml` with worker IP addresses
2. Run coordinator:
   ```bash
   python main.py coordinator --task 1
   ```

---

## Troubleshooting

### Workers Not Starting

**Issue:** `Address already in use`

**Solution:**
```bash
# Find process using the port
lsof -i :5001
# Kill the process
kill -9 <PID>
```

### Connection Errors

**Issue:** `Connection refused` when coordinator tries to reach workers

**Solution:**
1. Ensure workers are running: `curl http://localhost:5001/health`
2. Check firewall settings
3. Verify `config.yaml` has correct addresses

### Import Errors

**Issue:** `ModuleNotFoundError`

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Parquet File Errors

**Issue:** `File not found` or `Failed to load Parquet file`

**Solution:**
1. Check file path in `config.yaml`
2. Verify file exists: `ls -lh data/*.parquet`
3. Test loading manually:
   ```python
   import pandas as pd
   df = pd.read_parquet('data/yellow_tripdata_2024-01.parquet')
   print(df.head())
   ```

---

## Performance Tuning

### Increase Worker Count

Edit `config.yaml` to add more workers for better parallelization:

```yaml
workers:
  - id: "worker-5"
    host: "localhost"
    port: 5005
```

### Adjust Timeout Settings

For large datasets:

```yaml
execution:
  task_timeout: 600  # 10 minutes
```

### Limit Data for Testing

```yaml
dataset:
  max_records: 10000  # Process only 10k records
```

---

## Next Steps

1. ✅ Verify installation
2. ✅ Run quick test with `run_example.py`
3. ✅ Download real NYC Taxi data
4. ✅ Run full analysis on real data
5. ✅ Review results in `results_task*.txt`

For architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md)
