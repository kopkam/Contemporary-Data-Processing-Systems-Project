# Map-Reduce Architecture & Data Flow

## System Architecture

This document provides detailed diagrams and explanations of the map-reduce engine architecture and data flow.

## High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                         COORDINATOR NODE                           │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Job Orchestration & Control                             │   │
│  │  - Distribute input data across workers                  │   │
│  │  - Monitor worker health & status                        │   │
│  │  - Coordinate job phases (map → shuffle → reduce)        │   │
│  │  - Collect final results                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                    │
└─────────────────────┬──────────────────────────────────────────────┘
                      │
         ┌────────────┼────────────┬────────────┐
         │            │            │            │
         ▼            ▼            ▼            ▼
    ┌────────┐   ┌────────┐   ┌────────┐   ┌────────┐
    │Worker 1│   │Worker 2│   │Worker 3│   │Worker 4│
    │        │   │        │   │        │   │        │
    │ Data   │   │ Data   │   │ Data   │   │ Data   │
    │Partition│  │Partition│  │Partition│  │Partition│
    │   1    │   │   2    │   │   3    │   │   4    │
    └────────┘   └────────┘   └────────┘   └────────┘
```

## Detailed Component Architecture

### Worker Node Internal Structure

```
┌─────────────────────────────────────────────────────────┐
│                     WORKER NODE                          │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │          HTTP Server (Flask)                     │  │
│  │  Routes:                                         │  │
│  │  - /health          - Health check               │  │
│  │  - /execute_map     - Execute map phase          │  │
│  │  - /shuffle         - Receive shuffle data       │  │
│  │  - /execute_reduce  - Execute reduce phase       │  │
│  │  - /set_task        - Configure mapper/reducer   │  │
│  │  - /register_workers - Register peer workers     │  │
│  └──────────────────────────────────────────────────┘  │
│                          │                              │
│  ┌───────────────────────┴──────────────────────────┐  │
│  │          Processing Engine                       │  │
│  │  ┌────────────┐  ┌────────────┐  ┌───────────┐ │  │
│  │  │   Mapper   │  │ Partitioner│  │  Reducer  │ │  │
│  │  └────────────┘  └────────────┘  └───────────┘ │  │
│  └──────────────────────────────────────────────────┘  │
│                          │                              │
│  ┌───────────────────────┴──────────────────────────┐  │
│  │          Data Storage                            │  │
│  │  - Input data partition                          │  │
│  │  - Map output (intermediate results)             │  │
│  │  - Reduce input (after shuffle)                  │  │
│  │  - Reduce output (final results)                 │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Data Flow Phases

### Phase 1: Input Distribution

```
Input Dataset (10,000 records)
         │
         ▼
    Coordinator
    Distribution
         │
    ┌────┼────┬────┐
    │    │    │    │
    ▼    ▼    ▼    ▼
  2500 2500 2500 2500  (records per worker)
    │    │    │    │
  W1   W2   W3   W4
```

**Example:** Log Analysis with 10,000 records
- Worker 1: Records 0-2499
- Worker 2: Records 2500-4999
- Worker 3: Records 5000-7499
- Worker 4: Records 7500-9999

### Phase 2: MAP Phase

Each worker independently processes its partition:

```
Worker 1:                    Worker 2:
Input:                       Input:
  log1, log2, log3...          log2500, log2501...
       │                            │
       ▼                            ▼
   Mapper.map()                 Mapper.map()
       │                            │
       ▼                            ▼
Map Output:                  Map Output:
  (/api/users, stats)          (/api/products, stats)
  (/api/orders, stats)         (/api/users, stats)
  (/api/products, stats)       (/dashboard, stats)
  ...                          ...
```

**Key Points:**
- Each worker processes only its data partition
- Mapper emits intermediate key-value pairs
- No communication between workers during map phase
- Output is stored locally on each worker

### Phase 3: SHUFFLE Phase (Direct Worker-to-Worker)

This is the most critical phase - data is redistributed based on keys:

```
Step 1: Partition by Hash

Worker 1 Map Output:          Worker 2 Map Output:
  (/api/users, stats) ──────► hash("/api/users") % 4 = 2
  (/api/orders, stats) ─────► hash("/api/orders") % 4 = 1
  (/api/products, stats) ───► hash("/api/products") % 4 = 3

Step 2: Direct Communication

Worker 1:
  - Keeps: hash % 4 = 0 keys
  - Sends to W2: hash % 4 = 1 keys  ────┐
  - Sends to W3: hash % 4 = 2 keys  ────┼──┐
  - Sends to W4: hash % 4 = 3 keys  ────┼──┼──┐
                                        │  │  │
Worker 2:                               │  │  │
  - Keeps: hash % 4 = 1 keys            │  │  │
  - Sends to W1: hash % 4 = 0 keys  ◄───┘  │  │
  - Sends to W3: hash % 4 = 2 keys  ───────┼──┤
  - Sends to W4: hash % 4 = 3 keys  ───────┼──┼──┐
                                           │  │  │
Worker 3:                                  │  │  │
  - Keeps: hash % 4 = 2 keys               │  │  │
  - Sends to W1: hash % 4 = 0 keys  ◄──────┘  │  │
  - Sends to W2: hash % 4 = 1 keys  ◄──────────┘  │
  - Sends to W4: hash % 4 = 3 keys  ──────────────┼──┐
                                                  │  │
Worker 4:                                         │  │
  - Keeps: hash % 4 = 3 keys                      │  │
  - Sends to W1: hash % 4 = 0 keys  ◄─────────────┘  │
  - Sends to W2: hash % 4 = 1 keys  ◄────────────────┘
  - Sends to W3: hash % 4 = 2 keys  ◄────────────────┘

Step 3: Result

Worker 1 Reduce Input:        Worker 2 Reduce Input:
  All keys with hash % 4 = 0    All keys with hash % 4 = 1
  (from all 4 workers)          (from all 4 workers)

Worker 3 Reduce Input:        Worker 4 Reduce Input:
  All keys with hash % 4 = 2    All keys with hash % 4 = 3
  (from all 4 workers)          (from all 4 workers)
```

**Critical Feature:** Workers communicate DIRECTLY with each other
- No data passes through the coordinator
- Eliminates central bottleneck
- Scales better with more workers

### Phase 4: REDUCE Phase

Each worker reduces keys assigned to it:

```
Worker 1:
Reduce Input:
  /login: [stats1, stats2, stats3, ...]
  /dashboard: [stats1, stats2, ...]
       │
       ▼
  Reducer.reduce()
       │
       ▼
Reduce Output:
  (/login, {total_requests: 1245, avg_time: 156ms, ...})
  (/dashboard, {total_requests: 892, avg_time: 234ms, ...})
```

**Key Points:**
- Each key is processed by exactly ONE worker
- Reducer aggregates all values for a key
- Results are independent (no communication needed)

### Phase 5: Result Collection

```
Worker 1 Results ──┐
Worker 2 Results ──┼──► Coordinator ──► Final Output
Worker 3 Results ──┤                    (aggregated results)
Worker 4 Results ──┘
```

## Concrete Example: Log Analysis

### Input (10 records example)

```
Record 1: "2024-11-17 10:00:00, 192.168.1.1, GET, /api/users, 200, 150"
Record 2: "2024-11-17 10:00:05, 192.168.1.2, POST, /api/orders, 201, 250"
Record 3: "2024-11-17 10:00:10, 192.168.1.3, GET, /api/users, 200, 140"
Record 4: "2024-11-17 10:00:15, 192.168.1.4, GET, /api/products, 200, 180"
Record 5: "2024-11-17 10:00:20, 192.168.1.5, GET, /api/users, 500, 3000"
Record 6: "2024-11-17 10:00:25, 192.168.1.6, POST, /api/orders, 201, 270"
Record 7: "2024-11-17 10:00:30, 192.168.1.7, GET, /api/products, 200, 170"
Record 8: "2024-11-17 10:00:35, 192.168.1.8, GET, /api/users, 200, 130"
Record 9: "2024-11-17 10:00:40, 192.168.1.9, GET, /api/products, 404, 50"
Record 10: "2024-11-17 10:00:45, 192.168.1.10, GET, /api/orders, 200, 200"
```

### Distribution (2 workers for simplicity)

```
Worker 1: Records 1-5
Worker 2: Records 6-10
```

### MAP Phase Output

```
Worker 1 Output:
  (/api/users, {request_count:1, response_times:[150], error_count:0, ...})
  (/api/orders, {request_count:1, response_times:[250], error_count:0, ...})
  (/api/users, {request_count:1, response_times:[140], error_count:0, ...})
  (/api/products, {request_count:1, response_times:[180], error_count:0, ...})
  (/api/users, {request_count:1, response_times:[3000], error_count:1, ...})

Worker 2 Output:
  (/api/orders, {request_count:1, response_times:[270], error_count:0, ...})
  (/api/products, {request_count:1, response_times:[170], error_count:0, ...})
  (/api/users, {request_count:1, response_times:[130], error_count:0, ...})
  (/api/products, {request_count:1, response_times:[50], error_count:1, ...})
  (/api/orders, {request_count:1, response_times:[200], error_count:0, ...})
```

### SHUFFLE Phase (hash-based partitioning)

```
Assume:
  hash("/api/users") % 2 = 0    → Worker 1
  hash("/api/orders") % 2 = 1   → Worker 2
  hash("/api/products") % 2 = 0 → Worker 1

Worker 1 receives:
  /api/users: [stats from W1 + stats from W2]
  /api/products: [stats from W1 + stats from W2]

Worker 2 receives:
  /api/orders: [stats from W1 + stats from W2]
```

### REDUCE Phase Input (after shuffle)

```
Worker 1 Reduce Input:
  /api/users: [
    {request_count:1, response_times:[150], error_count:0},
    {request_count:1, response_times:[140], error_count:0},
    {request_count:1, response_times:[3000], error_count:1},
    {request_count:1, response_times:[130], error_count:0}
  ]
  /api/products: [
    {request_count:1, response_times:[180], error_count:0},
    {request_count:1, response_times:[170], error_count:0},
    {request_count:1, response_times:[50], error_count:1}
  ]

Worker 2 Reduce Input:
  /api/orders: [
    {request_count:1, response_times:[250], error_count:0},
    {request_count:1, response_times:[270], error_count:0},
    {request_count:1, response_times:[200], error_count:0}
  ]
```

### REDUCE Phase Output

```
Worker 1 Output:
  (/api/users, {
    total_requests: 4,
    response_time_avg_ms: 855.0,
    response_time_min_ms: 130.0,
    response_time_max_ms: 3000.0,
    error_count: 1,
    error_rate_percent: 25.0
  })
  (/api/products, {
    total_requests: 3,
    response_time_avg_ms: 133.33,
    response_time_min_ms: 50.0,
    response_time_max_ms: 180.0,
    error_count: 1,
    error_rate_percent: 33.33
  })

Worker 2 Output:
  (/api/orders, {
    total_requests: 3,
    response_time_avg_ms: 240.0,
    response_time_min_ms: 200.0,
    response_time_max_ms: 270.0,
    error_count: 0,
    error_rate_percent: 0.0
  })
```

### Final Result (collected by coordinator)

```
[
  (/api/users, {...}),
  (/api/products, {...}),
  (/api/orders, {...})
]
```

## Communication Protocols

### Coordinator → Worker

```
POST /execute_map
Body: {
  "input_data": [
    (key1, value1),
    (key2, value2),
    ...
  ]
}
Response: {
  "success": true,
  "records_processed": 2500,
  "records_emitted": 3200
}
```

### Worker → Worker (Shuffle)

```
POST http://worker-2:5002/shuffle
Body: {
  "source_worker": "worker-1",
  "data": [
    (key1, value1),
    (key2, value2),
    ...
  ]
}
Response: {
  "success": true,
  "records_received": 800
}
```

### Coordinator → Worker (Reduce)

```
POST /execute_reduce
Body: {}
Response: {
  "success": true,
  "keys_processed": 3,
  "records_emitted": 3,
  "output": [
    (key1, result1),
    (key2, result2),
    (key3, result3)
  ]
}
```

## Scalability Considerations

### Adding More Workers

With 8 workers instead of 4:
- Each worker processes 1/8 of input (better parallelism)
- Shuffle distributes keys across 8 partitions (better load balancing)
- More network connections during shuffle (8×8 = 64 potential paths)

### Network Traffic During Shuffle

For N workers:
- Maximum connections: N×(N-1) = N²-N
- Each worker sends to up to (N-1) other workers
- Direct communication avoids O(N²) coordinator bottleneck

### Example with 4 Workers:
```
Total shuffle connections: 4×3 = 12 potential paths
Each worker: Sends to 3, receives from 3

With coordinator bottleneck (traditional):
  4 workers → 1 coordinator → 4 workers = 8 hops
  
With direct communication (our implementation):
  1 worker → 1 worker = 1 hop
  
Speedup: 8x fewer network hops!
```

## Fault Tolerance (Not Yet Implemented)

Potential enhancements:
1. **Worker failure detection**: Health checks during job execution
2. **Task retry**: Reassign failed map/reduce tasks
3. **Checkpointing**: Save intermediate results
4. **Replication**: Store data on multiple workers

## Performance Metrics

The system tracks:
- **Map phase time**: Time to process all map tasks
- **Shuffle phase time**: Time to redistribute data
- **Reduce phase time**: Time to aggregate results
- **Total job time**: End-to-end execution time
- **Records processed/emitted**: At each phase
- **Throughput**: Records per second

Example output:
```
Total execution time: 12.45s
  - Map phase:     4.23s (2,365 records/sec)
  - Shuffle phase: 3.12s
  - Reduce phase:  2.89s
Final output records: 10
```
