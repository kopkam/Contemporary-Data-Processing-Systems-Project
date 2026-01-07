# NYC Taxi Map-Reduce Analysis

**Contemporary Data Processing Systems Project**  
**Politechnika Łódzka, Semestr Zimowy 2025/2026**

## 📋 Project Overview

This project implements a distributed map-reduce system for analyzing NYC Taxi & Limousine Commission trip data. The system processes large-scale taxi trip records using parallel computation across multiple worker nodes.

### Team Members
- **Sergiusz Cudo** - Task 1: Tip Analysis by Pickup Zone
- **Ludwik Janowski** - Task 2: Route Profitability Analysis
- **Marcin Kopka** - Task 3: Hourly Traffic Distribution

### Supervisor
- **Prof. Tomasz Kowalski** (tomasz.kowalski@p.lodz.pl)

---

## 🎯 Individual Tasks

### Task 1: Average Tip Percentage by Pickup Zone
**Author:** Sergiusz Cudo

**Objective:** Analyze tipping behavior across different pickup zones in NYC.

**Map Phase:**
- Input: `(trip_id, trip_record)`
- Output: `(pickup_zone_id, tip_percentage)`
- Calculation: `tip_percentage = (tip_amount / fare_amount) × 100`

**Reduce Phase:**
- Input: `(pickup_zone_id, [tip_pct1, tip_pct2, ...])`
- Output: `(pickup_zone_id, average_tip_percentage)`

**Business Value:** Identifies zones where passengers tip more generously, helping taxi drivers optimize pickup strategies.

---

### Task 2: Route Profitability Analysis
**Author:** Ludwik Janowski

**Objective:** Calculate revenue per mile for different pickup-dropoff zone pairs.

**Map Phase:**
- Input: `(trip_id, trip_record)`
- Output: `((pickup_zone, dropoff_zone), revenue_per_mile)`
- Calculation: `revenue_per_mile = total_amount / trip_distance`

**Reduce Phase:**
- Input: `((pickup_zone, dropoff_zone), [rpm1, rpm2, ...])`
- Output: `((pickup_zone, dropoff_zone), avg_revenue_per_mile)`

**Business Value:** Identifies most profitable routes to maximize driver earnings per unit distance.

---

### Task 3: Hourly Traffic Distribution
**Author:** Marcin Kopka

**Objective:** Analyze temporal patterns in taxi usage by counting trips per hour.

**Map Phase:**
- Input: `(trip_id, trip_record)`
- Output: `(hour_of_day, 1)`
- Extraction: Extract hour (0-23) from `tpep_pickup_datetime`

**Reduce Phase:**
- Input: `(hour_of_day, [1, 1, 1, ...])`
- Output: `(hour_of_day, total_trip_count)`

**Business Value:** Identifies peak hours for optimizing driver scheduling and understanding demand patterns.

---

## 🏗️ Architecture

### System Components

1. **Coordinator (Master Node)**
   - Orchestrates job execution
   - Distributes data to workers
   - Collects and aggregates results

2. **Worker Nodes (4+)**
   - Execute map and reduce tasks
   - Communicate via HTTP REST API
   - Direct peer-to-peer shuffle

3. **Data Loader**
   - Reads NYC Taxi Parquet files using PyArrow
   - Handles data partitioning

### Map-Reduce Flow

```
Input Data (Parquet)
    ↓
Coordinator splits data
    ↓
Workers: MAP phase (parallel)
    ↓
Shuffle phase (worker-to-worker)
    ↓
Workers: REDUCE phase (parallel)
    ↓
Coordinator collects results
    ↓
Final Output
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone <repository-url>
cd Contemporary-Data-Processing-Systems-Project

# Install dependencies
pip install -r requirements.txt
```

### Running with Sample Data

**Option 1: Using CLI (Recommended)**

```bash
# Terminal 1: Start workers
python main.py worker worker-1 --port 5001 &
python main.py worker worker-2 --port 5002 &
python main.py worker worker-3 --port 5003 &
python main.py worker worker-4 --port 5004 &

# Terminal 2: Run Task 1 (Tip Analysis)
python main.py coordinator --task 1

# Or Task 2 (Route Profitability)
python main.py coordinator --task 2

# Or Task 3 (Hourly Traffic)
python main.py coordinator --task 3
```

**Option 2: Using run_example.py**

```bash
# Run specific task
python run_example.py 1  # Tip Analysis
python run_example.py 2  # Route Profitability
python run_example.py 3  # Hourly Traffic

# Run all tasks sequentially
python run_example.py
```

### Using Real NYC Taxi Data

1. Download NYC Taxi Parquet file:
   ```bash
   # Example: Yellow Taxi Trip Data
   # https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
   ```

2. Update `config.yaml`:
   ```yaml
   dataset:
     path: "./data/yellow_tripdata_2024-01.parquet"
     max_records: null  # Use all records
   ```

3. Run analysis:
   ```bash
   python main.py coordinator --task 1
   ```

---

## 📊 Dataset

**Source:** NYC Taxi & Limousine Commission Trip Record Data

**Format:** Parquet (columnar storage)

**Key Fields:**
- `VendorID`: Taxi vendor identifier
- `tpep_pickup_datetime`: Pickup timestamp
- `tpep_dropoff_datetime`: Dropoff timestamp
- `PULocationID`: Pickup location zone ID
- `DOLocationID`: Dropoff location zone ID
- `trip_distance`: Trip distance in miles
- `fare_amount`: Base fare
- `tip_amount`: Tip amount
- `total_amount`: Total fare (including tips, tolls, etc.)

**Download:** https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

---

## 📁 Project Structure

```
Contemporary-Data-Processing-Systems-Project/
├── README.md
├── requirements.txt
├── config.yaml
├── main.py                  # CLI entry point
├── run_example.py          # Programmatic examples
├── src/
│   ├── core/
│   │   ├── base.py         # Abstract Mapper/Reducer/Partitioner
│   │   ├── worker.py       # Worker node implementation
│   │   └── coordinator.py  # Coordinator implementation
│   ├── tasks/
│   │   ├── task1_tip_analysis.py           # Sergiusz's task
│   │   ├── task2_route_profitability.py    # Ludwik's task
│   │   └── task3_hourly_traffic.py         # Marcin's task
│   └── utils/
│       └── parquet_loader.py  # Data loading utilities
└── docs/
    ├── SETUP.md
    ├── ARCHITECTURE.md
    └── PRESENTATION_SKETCH.md
```

---

## 🧪 Testing

```bash
# Run with sample data (1000 records)
python run_example.py 1

# Expected output:
# Top results showing zones with highest average tip percentages
```

---

## 📝 Configuration

Edit `config.yaml` to customize:
- Worker node addresses
- Dataset path and size limits
- Task execution timeouts
- Logging settings

---

## 🤝 Contributing

This is an academic project for Contemporary Data Processing Systems course.

---

## 📄 License

Academic project - Politechnika Łódzka

---

## 📧 Contact

For questions or issues:
- Sergiusz Cudo
- Ludwik Janowski
- Marcin Kopka

**Course:** Contemporary Data Processing Systems  
**Institution:** Politechnika Łódzka  
**Semester:** Winter 2025/2026
