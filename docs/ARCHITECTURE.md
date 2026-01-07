# Architecture Documentation

## System Overview

This document describes the architecture of the NYC Taxi Map-Reduce analysis system.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      COORDINATOR NODE                        │
│  - Job orchestration                                        │
│  - Data distribution                                        │
│  - Result aggregation                                       │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
    ┌────────▼────────┐              ┌───────▼────────┐
    │   WORKER 1      │              │   WORKER 2      │
    │  - Map tasks    │◄────────────►│  - Map tasks    │
    │  - Reduce tasks │  Shuffle     │  - Reduce tasks │
    └────────┬────────┘              └───────┬─────────┘
             │                                │
    ┌────────▼────────┐              ┌───────▼────────┐
    │   WORKER 3      │              │   WORKER 4      │
    │  - Map tasks    │◄────────────►│  - Map tasks    │
    │  - Reduce tasks │  Shuffle     │  - Reduce tasks │
    └─────────────────┘              └─────────────────┘
```

---

## Core Components

### 1. Coordinator (Master Node)

**Location:** `src/core/coordinator.py`

**Responsibilities:**
- **Job Orchestration:** Manages the complete lifecycle of map-reduce jobs
- **Data Distribution:** Splits input data across worker nodes
- **Health Monitoring:** Checks worker availability before job execution
- **Phase Coordination:** Synchronizes map and reduce phases
- **Result Collection:** Gathers and aggregates final results from workers

**Key Methods:**
```python
def run_job(input_data, mapper_class, reducer_class, partitioner_class)
    - Main entry point for executing a map-reduce job
    
def _execute_map_phase(data_splits, mapper_hex, partitioner_hex)
    - Distributes map tasks to workers
    
def _execute_reduce_phase(reducer_hex)
    - Triggers reduce execution on all workers
    
def _collect_results()
    - Retrieves final results from all workers
```

**Communication:**
- Uses HTTP REST API to communicate with workers
- Employs thread pool for parallel worker communication
- Implements timeout and retry mechanisms

---

### 2. Worker Nodes

**Location:** `src/core/worker.py`

**Responsibilities:**
- **Task Execution:** Runs map and reduce operations
- **Data Shuffling:** Exchanges intermediate data with other workers
- **State Management:** Maintains intermediate and final results
- **HTTP Server:** Provides REST endpoints for coordinator/worker communication

**Key Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/execute_map` | POST | Execute map phase |
| `/shuffle` | POST | Receive shuffled data |
| `/execute_reduce` | POST | Execute reduce phase |
| `/get_results` | GET | Return final results |
| `/reset` | POST | Clear worker state |

**Data Flow Within Worker:**
```
Input Data
    ↓
MAP: Apply mapper.map()
    ↓
PARTITION: Determine target workers
    ↓
SHUFFLE: Send to workers (HTTP POST)
    ↓
ACCUMULATE: Receive from other workers
    ↓
REDUCE: Apply reducer.reduce()
    ↓
Output Results
```

---

### 3. Base Classes

**Location:** `src/core/base.py`

**Abstract Classes:**

#### Mapper
```python
class Mapper(ABC):
    def map(self, key: Any, value: Any) -> Iterator[Tuple[Any, Any]]:
        """Transform input records into intermediate key-value pairs."""
```

#### Reducer
```python
class Reducer(ABC):
    def reduce(self, key: Any, values: List[Any]) -> Iterator[Tuple[Any, Any]]:
        """Aggregate values for each key."""
```

#### Partitioner
```python
class Partitioner(ABC):
    def get_partition(self, key: Any, num_partitions: int) -> int:
        """Determine which worker receives a given key."""
```

**Default Implementation:**
- `HashPartitioner`: Uses hash-based distribution for load balancing

---

## Data Processing Pipeline

### Phase 1: Initialization

1. Coordinator loads configuration and input data
2. Data is split evenly across N workers
3. Mapper and Reducer classes are serialized (pickle)

### Phase 2: Map Phase

**Coordinator:**
1. Sends map task to each worker with:
   - Serialized mapper class
   - Serialized partitioner class
   - Data partition
   - List of all worker addresses

**Each Worker:**
1. Deserializes mapper and partitioner
2. For each input record:
   - Calls `mapper.map(key, value)`
   - For each emitted (k, v):
     - Calls `partitioner.get_partition(k, num_workers)` → worker_id
     - Buffers (k, v) for target worker
3. Sends buffered data to corresponding workers via HTTP POST to `/shuffle`

### Phase 3: Shuffle Phase

**Peer-to-Peer Communication:**
- Workers send intermediate data directly to each other
- No coordinator involvement
- Uses HTTP POST to `/shuffle` endpoint

**Each Worker:**
1. Receives shuffled data from multiple workers
2. Groups received (k, v) pairs by key
3. Stores in `intermediate_data: Dict[key, List[values]]`

### Phase 4: Reduce Phase

**Coordinator:**
1. Sends reduce task to all workers
2. Waits for completion

**Each Worker:**
1. Deserializes reducer class
2. For each key in `intermediate_data`:
   - Calls `reducer.reduce(key, values)`
   - Collects output (k, v) pairs
3. Stores results in `final_results`

### Phase 5: Result Collection

**Coordinator:**
1. Sends GET request to `/get_results` on all workers
2. Merges results from all workers
3. Returns complete result set

---

## Task Implementations

### Task 1: Tip Analysis (Sergiusz Cudo)

**File:** `src/tasks/task1_tip_analysis.py`

**Map Logic:**
```python
(trip_id, trip_record) 
    → (pickup_zone, tip_percentage)
```

**Reduce Logic:**
```python
(pickup_zone, [tip_pct1, tip_pct2, ...]) 
    → (pickup_zone, average_tip_pct)
```

**Key Insight:** Geographic analysis - which zones have highest tips

---

### Task 2: Route Profitability (Ludwik Janowski)

**File:** `src/tasks/task2_route_profitability.py`

**Map Logic:**
```python
(trip_id, trip_record) 
    → ((pickup_zone, dropoff_zone), revenue_per_mile)
```

**Reduce Logic:**
```python
((pickup_zone, dropoff_zone), [rpm1, rpm2, ...]) 
    → ((pickup_zone, dropoff_zone), avg_rpm)
```

**Key Insight:** Economic analysis - which routes are most profitable

---

### Task 3: Hourly Traffic (Marcin Kopka)

**File:** `src/tasks/task3_hourly_traffic.py`

**Map Logic:**
```python
(trip_id, trip_record) 
    → (hour_of_day, 1)
```

**Reduce Logic:**
```python
(hour_of_day, [1, 1, 1, ...]) 
    → (hour_of_day, total_count)
```

**Key Insight:** Temporal analysis - when is demand highest

---

## Data Loading

**Location:** `src/utils/parquet_loader.py`

**Functions:**

### load_nyc_taxi_data()
```python
def load_nyc_taxi_data(file_path, max_records=None, columns=None)
```
- Reads Parquet files using PyArrow for efficiency
- Supports column selection for memory optimization
- Returns list of (index, dict) tuples

### create_sample_data()
```python
def create_sample_data(num_records=100)
```
- Generates synthetic NYC Taxi data for testing
- Useful when real data is unavailable
- Creates realistic distributions

---

## Communication Protocol

### Request/Response Format

**Map Task Request:**
```json
{
  "mapper": "hex_encoded_pickle",
  "partitioner": "hex_encoded_pickle",
  "input_data": [[key1, value1], [key2, value2], ...],
  "worker_addresses": ["http://host1:port1", ...]
}
```

**Shuffle Request:**
```json
{
  "data": [[key1, value1], [key2, value2], ...]
}
```

**Reduce Task Request:**
```json
{
  "reducer": "hex_encoded_pickle"
}
```

**Results Response:**
```json
{
  "results": [[key1, value1], [key2, value2], ...],
  "worker_id": "worker-1"
}
```

---

## Scalability Considerations

### Horizontal Scaling

**Adding Workers:**
1. Update `config.yaml` with new worker entries
2. Start worker process on new machine
3. System automatically distributes load

**Benefits:**
- Linear speedup for map phase
- Better parallelization in reduce phase
- Increased aggregate memory

### Data Partitioning

**Hash-based Partitioning:**
- Ensures even distribution of keys
- Minimizes data skew
- Deterministic assignment

**Configurable:**
- Custom partitioner can be implemented
- Useful for skewed data distributions

### Performance Tuning

**Configuration Parameters:**
```yaml
execution:
  task_timeout: 300          # Adjust for large datasets
  max_retries: 3             # Worker failure handling
  shuffle_buffer_size: 100   # MB per worker
```

---

## Fault Tolerance

### Current Implementation

**Health Checks:**
- Pre-job validation of worker availability
- Coordinator aborts if any worker is unavailable

**Timeout Handling:**
- HTTP requests have configurable timeouts
- Failed requests raise exceptions

### Future Enhancements

Possible improvements:
- Automatic worker restart on failure
- Task retry on individual worker failure
- Checkpoint/resume for long-running jobs
- Speculative execution for stragglers

---

## Security Considerations

**Current State:** 
- HTTP communication (not encrypted)
- No authentication between nodes

**For Production:**
- Use HTTPS for encrypted communication
- Implement API key authentication
- Network isolation (VPN/private network)
- Input validation on all endpoints

---

## Testing Strategy

### Unit Tests
- Test individual mapper/reducer logic
- Verify partitioner distribution
- Mock worker responses

### Integration Tests
- Test coordinator-worker communication
- Verify shuffle phase correctness
- End-to-end job execution

### Performance Tests
- Measure throughput (records/second)
- Test with varying worker counts
- Benchmark different dataset sizes

---

## Deployment Models

### 1. Local Development
- All components on localhost
- Different ports per worker
- Quick testing and debugging

### 2. Multi-Machine Cluster
- Coordinator on master node
- Workers on separate machines
- Production-like environment

### 3. Cloud Deployment
- VMs/containers for each worker
- Load balancer for coordinator
- Auto-scaling worker pool

---

## Performance Metrics

**Measured Metrics:**
- Total execution time
- Map phase duration
- Shuffle data volume
- Reduce phase duration
- Throughput (records/second)

**Example Results:**
```
Dataset: 1,000 records
Workers: 4
Task 1 execution time: ~0.5 seconds
Throughput: ~2,000 records/second
```

---

## References

- Original MapReduce paper: Dean & Ghemawat (2004)
- NYC TLC Trip Record Data: https://www.nyc.gov/tlc
- Apache Parquet format: https://parquet.apache.org/
- Flask documentation: https://flask.palletsprojects.com/
