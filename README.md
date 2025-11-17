# Contemporary Data Processing Systems - Map-Reduce Engine

A distributed task processing system implementing the **map-reduce programming model** for parallel data processing across multiple nodes.

## 🎯 Project Overview

This project implements a complete distributed computing framework that:

- ✅ Distributes processing across **4+ physical nodes** (configurable)
- ✅ Supports **map**, **shuffle**, and **reduce** transformations
- ✅ Implements **direct worker-to-worker communication** during shuffle (no central bottleneck)
- ✅ Provides a flexible API for implementing custom map-reduce problems
- ✅ Includes **two complex examples** (beyond WordCount):
  - **Web Server Log Analysis**: Analyzes access logs to compute endpoint statistics, response times, error rates, and traffic patterns
  - **E-commerce Sales Analysis**: Processes transactions to generate revenue reports, product rankings, and customer insights
- ✅ Offers both **CLI** and **programmatic API** interfaces
- ✅ Features comprehensive monitoring and progress tracking

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Coordinator (Master)                    │
│  - Job orchestration                                        │
│  - Worker registry & health monitoring                      │
│  - Data distribution                                        │
│  - Result collection                                        │
└────────────┬────────────────────────────────────────────────┘
             │
             │ Distributes tasks & monitors
             │
    ┌────────┴────────┬──────────────┬──────────────┐
    │                 │              │              │
┌───▼────┐      ┌────▼───┐     ┌───▼────┐    ┌───▼────┐
│Worker 1│      │Worker 2│     │Worker 3│    │Worker 4│
│        │◄────►│        │◄───►│        │◄──►│        │
│ Map    │      │ Map    │     │ Map    │    │ Map    │
│Shuffle │      │Shuffle │     │Shuffle │    │Shuffle │
│Reduce  │      │Reduce  │     │Reduce  │    │Reduce  │
└────────┘      └────────┘     └────────┘    └────────┘
     ▲              ▲              ▲             ▲
     │              │              │             │
     └──────────────┴──────────────┴─────────────┘
           Direct worker-to-worker 
           communication (shuffle)
```

### Map-Reduce Workflow

1. **Input Distribution**: Coordinator splits input data across workers
2. **Map Phase**: Each worker applies the mapper to its data partition
   - Emits intermediate key-value pairs
3. **Shuffle Phase**: Workers communicate directly to redistribute data
   - Each key is sent to a specific worker (determined by hash partitioning)
   - **No data passes through coordinator** (efficient!)
4. **Reduce Phase**: Each worker aggregates values for its assigned keys
5. **Result Collection**: Coordinator gathers final results from all workers

## 📋 Prerequisites

- Python 3.8+
- Network connectivity between nodes
- Sufficient disk space for intermediate data

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd Contemporary-Data-Processing-Systems-Project

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Edit `config.yaml` to define your cluster topology:

```yaml
cluster:
  coordinator:
    host: "localhost"
    port: 5000
    
  workers:
    - id: "worker-1"
      host: "localhost"
      port: 5001
      data_dir: "./data/worker1"
    
    - id: "worker-2"
      host: "localhost"
      port: 5002
      data_dir: "./data/worker2"
    # ... add more workers
```

**For distributed deployment**: Replace `localhost` with actual IP addresses of your cluster nodes.

### 3. Running the System

#### Option A: Quick Demo (Single Machine)

Run a complete example with automatic cluster startup:

```bash
# Log analysis (10,000 records)
python run_example.py log-analysis 10000

# Sales analysis (5,000 records)
python run_example.py sales-analysis 5000
```

#### Option B: Manual Cluster Management

**Terminal 1 - Start Worker 1:**
```bash
python main.py start-worker worker-1
```

**Terminal 2 - Start Worker 2:**
```bash
python main.py start-worker worker-2
```

**Terminal 3 - Start Worker 3:**
```bash
python main.py start-worker worker-3
```

**Terminal 4 - Start Worker 4:**
```bash
python main.py start-worker worker-4
```

**Terminal 5 - Check Cluster Status:**
```bash
python main.py status
```

#### Option C: Distributed Deployment (4+ Physical Machines)

**On each worker machine:**
```bash
# Machine 1
python main.py start-worker worker-1

# Machine 2
python main.py start-worker worker-2

# Machine 3
python main.py start-worker worker-3

# Machine 4
python main.py start-worker worker-4
```

**On coordinator machine:**
```bash
python run_example.py log-analysis 50000
```

## 📊 Example Problems

### 1. Web Server Log Analysis

**Problem**: Analyze millions of web server access logs to compute:
- Request counts per endpoint
- Average/min/max response times
- Error rates (4xx/5xx responses)
- Peak traffic hours
- HTTP method distribution

**Input Format**:
```
2024-11-17 10:23:45, 192.168.1.100, GET, /api/users, 200, 145
2024-11-17 10:24:12, 192.168.1.101, POST, /api/orders, 201, 289
```

**Map Phase**: Parse logs → Emit `(endpoint, stats)`

**Shuffle Phase**: Group all statistics by endpoint across workers

**Reduce Phase**: Aggregate statistics per endpoint

**Sample Output**:
```
Endpoint                       Requests   Avg Time     Error Rate   Peak Hours
------------------------------------------------------------------------------
/api/products                  2,431      187.32 ms    3.21%        10, 14, 16
/api/users                     1,892      145.67 ms    2.15%        11, 13, 15
/api/orders                    1,543      289.45 ms    5.67%        12, 14, 17
```

### 2. E-commerce Sales Analysis

**Problem**: Analyze transaction data to compute:
- Revenue by product category
- Top-selling products
- Regional sales distribution
- Customer purchase patterns

**Input Format**:
```
TXN001, 2024-11-17 10:30:00, CUST123, PROD456, Electronics, 2, 299.99, North
```

**Map Phase**: Parse transaction → Emit multiple keys:
- `(category:Electronics, revenue_data)`
- `(product:PROD456, sales_data)`
- `(region:North, revenue_data)`
- `(customer:CUST123, purchase_data)`

**Shuffle Phase**: Group all related records by type and identifier

**Reduce Phase**: Aggregate by category, product, region, and customer

**Sample Output**:
```
Top Categories by Revenue:
  Electronics          $1,234,567.89  (5,234 transactions, 8,901 units)
  Clothing             $987,654.32    (8,123 transactions, 15,234 units)
  
Revenue by Region:
  North                $2,345,678.90  (6,789 transactions)
  South                $1,987,654.32  (5,432 transactions)
```

## 🔧 Creating Custom Map-Reduce Problems

### Step 1: Define Your Mapper

```python
from src.core.base import Mapper
from typing import Any, Iterator, Tuple

class MyMapper(Mapper):
    def map(self, key: Any, value: Any) -> Iterator[Tuple[Any, Any]]:
        """
        Process input and emit intermediate key-value pairs.
        
        Args:
            key: Input key (e.g., line number)
            value: Input value (e.g., line content)
            
        Yields:
            (intermediate_key, intermediate_value) tuples
        """
        # Your mapping logic here
        words = value.split()
        for word in words:
            yield (word.lower(), 1)
```

### Step 2: Define Your Reducer

```python
from src.core.base import Reducer
from typing import Any, Iterator, List, Tuple

class MyReducer(Reducer):
    def reduce(self, key: Any, values: List[Any]) -> Iterator[Tuple[Any, Any]]:
        """
        Aggregate values for each key.
        
        Args:
            key: The key to reduce
            values: All values associated with this key
            
        Yields:
            (output_key, output_value) tuples
        """
        # Your reduction logic here
        total = sum(values)
        yield (key, total)
```

### Step 3: Run Your Job

```python
from src.core.coordinator import Coordinator
from src.core.worker import Worker
import threading

# Start workers (in production, these would be on separate machines)
workers = []
for worker_config in config['cluster']['workers']:
    worker = Worker(...)
    worker.set_mapper(MyMapper())
    worker.set_reducer(MyReducer())
    workers.append(worker)
    
    thread = threading.Thread(target=worker.start, daemon=True)
    thread.start()

# Create coordinator and execute job
coordinator = Coordinator(...)
results = coordinator.execute_job(
    input_data=my_data,
    mapper=MyMapper(),
    reducer=MyReducer()
)

# Process results
for key, value in results:
    print(f"{key}: {value}")
```

## 📁 Project Structure

```
Contemporary-Data-Processing-Systems-Project/
├── config.yaml                 # Cluster configuration
├── requirements.txt            # Python dependencies
├── main.py                     # CLI interface
├── run_example.py              # Example runner script
├── README.md                   # This file
│
├── src/
│   ├── core/                   # Core map-reduce engine
│   │   ├── base.py            # Abstract base classes
│   │   ├── worker.py          # Worker node implementation
│   │   ├── coordinator.py     # Coordinator implementation
│   │   └── __init__.py
│   │
│   ├── examples/              # Example problems
│   │   ├── log_analysis.py   # Web server log analysis
│   │   ├── sales_analysis.py # E-commerce sales analysis
│   │   └── __init__.py
│   │
│   └── __init__.py
│
└── data/                      # Worker data directories (created at runtime)
    ├── worker1/
    ├── worker2/
    ├── worker3/
    └── worker4/
```

## 🔍 Key Features

### Direct Worker-to-Worker Shuffle

Unlike traditional map-reduce implementations where intermediate data flows through a central coordinator, our implementation uses **direct peer-to-peer communication**:

```python
# In Worker.shuffle_data()
for target_worker_id, data in partitions.items():
    if target_worker_id == self.worker_id:
        # Keep local data
        self.reduce_input[key].append(value)
    else:
        # Send directly to remote worker (no coordinator!)
        worker_info = self.workers[target_worker_id]
        url = f"http://{worker_info['host']}:{worker_info['port']}/shuffle"
        requests.post(url, json={'data': data})
```

**Benefits**:
- ✅ Eliminates coordinator bottleneck
- ✅ Better scalability
- ✅ Reduced network latency
- ✅ Load balancing across network

### Hash-Based Partitioning

Ensures even distribution of keys across workers:

```python
class HashPartitioner(Partitioner):
    def get_partition(self, key: Any, num_partitions: int) -> int:
        return hash(key) % num_partitions
```

### Comprehensive Monitoring

- Health checks for all workers
- Progress tracking for each phase (map, shuffle, reduce)
- Timing statistics
- Record counts and throughput metrics

## 🧪 Testing

```bash
# Run with small dataset for testing
python run_example.py log-analysis 100

# Run with larger dataset for performance testing
python run_example.py log-analysis 100000

# Check cluster status
python main.py status
```

## 📈 Performance Considerations

- **Data Size**: The system can handle datasets from thousands to millions of records
- **Worker Count**: More workers = better parallelism (recommended: 4-8 workers)
- **Network**: Fast network between workers improves shuffle performance
- **Memory**: Each worker needs enough RAM to hold its partition + intermediate data

## 🐛 Troubleshooting

### Workers not starting
- Check port availability: `netstat -an | grep <port>`
- Verify firewall settings
- Ensure `data/` directories are writable

### Connection errors during shuffle
- Verify network connectivity between worker nodes
- Check firewall rules allow HTTP traffic on worker ports
- Ensure correct IP addresses in `config.yaml`

### Out of memory errors
- Reduce dataset size
- Increase worker count to distribute load
- Adjust `shuffle_buffer_size` in config

## 📚 Additional Documentation

### Coordinator API

```python
coordinator = Coordinator(host="localhost", port=5000)
coordinator.register_worker(worker_id, host, port, data_dir)
coordinator.check_workers_health()
coordinator.execute_job(input_data, mapper, reducer, partitioner)
```

### Worker API

```python
worker = Worker(worker_id, host, port, data_dir)
worker.set_mapper(mapper_instance)
worker.set_reducer(reducer_instance)
worker.set_partitioner(partitioner_instance)
worker.start()  # Blocks and runs HTTP server
```

## 🎓 Project Requirements Checklist

- ✅ Distributed on 4+ physical nodes (configurable)
- ✅ Processes distributed datasets
- ✅ Supports map, filter, reduce transformations
- ✅ Implements shuffle with direct worker communication
- ✅ Configurable via YAML and CLI
- ✅ Generates output files with results
- ✅ Includes complex examples beyond WordCount
- ✅ Console application with progress monitoring
- ✅ Comprehensive documentation

## 📝 License

This project is created for educational purposes as part of the Contemporary Data Processing Systems course.

## 👥 Contributors

Your Name - Your Group

---

**Happy Distributed Computing! 🚀**