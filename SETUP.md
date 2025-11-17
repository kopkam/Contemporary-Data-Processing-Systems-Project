# Setup Instructions

## For Local Testing (Single Machine)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run a demo:**
   ```bash
   python run_example.py log-analysis 10000
   ```

   This will:
   - Start 4 workers in background threads
   - Generate 10,000 sample log records
   - Distribute and process them using map-reduce
   - Display results

## For Distributed Deployment (4+ Machines)

### Prerequisites
- 4+ machines with Python 3.8+ installed
- Network connectivity between all machines
- Same codebase deployed on all machines

### Configuration

1. **Identify your machines:**
   - Machine 1: 192.168.1.10 (Worker 1)
   - Machine 2: 192.168.1.11 (Worker 2)
   - Machine 3: 192.168.1.12 (Worker 3)
   - Machine 4: 192.168.1.13 (Worker 4)
   - Machine 5: 192.168.1.14 (Coordinator - can run jobs)

2. **Update config.yaml on ALL machines:**
   ```yaml
   cluster:
     coordinator:
       host: "192.168.1.14"
       port: 5000
       
     workers:
       - id: "worker-1"
         host: "192.168.1.10"
         port: 5001
         data_dir: "./data/worker1"
         
       - id: "worker-2"
         host: "192.168.1.11"
         port: 5002
         data_dir: "./data/worker2"
         
       - id: "worker-3"
         host: "192.168.1.12"
         port: 5003
         data_dir: "./data/worker3"
         
       - id: "worker-4"
         host: "192.168.1.13"
         port: 5004
         data_dir: "./data/worker4"
   ```

3. **Configure firewall rules:**
   On each worker machine, allow incoming connections on the worker port:
   ```bash
   # Example for Ubuntu/Debian
   sudo ufw allow 5001/tcp  # Adjust port for each worker
   
   # Example for CentOS/RHEL
   sudo firewall-cmd --add-port=5001/tcp --permanent
   sudo firewall-cmd --reload
   ```

### Starting the Cluster

1. **On Machine 1 (192.168.1.10):**
   ```bash
   cd Contemporary-Data-Processing-Systems-Project
   python main.py start-worker worker-1
   ```

2. **On Machine 2 (192.168.1.11):**
   ```bash
   cd Contemporary-Data-Processing-Systems-Project
   python main.py start-worker worker-2
   ```

3. **On Machine 3 (192.168.1.12):**
   ```bash
   cd Contemporary-Data-Processing-Systems-Project
   python main.py start-worker worker-3
   ```

4. **On Machine 4 (192.168.1.13):**
   ```bash
   cd Contemporary-Data-Processing-Systems-Project
   python main.py start-worker worker-4
   ```

5. **On Machine 5 (Coordinator - 192.168.1.14):**
   ```bash
   cd Contemporary-Data-Processing-Systems-Project
   
   # Check cluster status
   python main.py status
   
   # Run a job
   python run_example.py log-analysis 100000
   ```

### Monitoring

**Check worker status:**
```bash
python main.py status
```

Expected output:
```
================================================================================
  Cluster Status
================================================================================

Coordinator: 192.168.1.14:5000

Workers:
  ✓ worker-1: idle
  ✓ worker-2: idle
  ✓ worker-3: idle
  ✓ worker-4: idle
```

**View logs:**
```bash
# On any machine
tail -f mapreduce.log
```

### Troubleshooting Distributed Setup

**Workers can't connect:**
1. Verify IP addresses: `ip addr show`
2. Test connectivity: `ping 192.168.1.10`
3. Test port: `telnet 192.168.1.10 5001`
4. Check firewall: `sudo ufw status` or `sudo firewall-cmd --list-all`

**Worker not responding:**
1. Check if process is running: `ps aux | grep python`
2. Check logs: `tail -f mapreduce.log`
3. Restart worker: Kill process and restart with `python main.py start-worker worker-X`

**Shuffle phase errors:**
- Ensure all workers can reach each other (bidirectional communication)
- Check network bandwidth if processing large datasets
- Verify no proxy/NAT issues between machines

## Performance Tuning

### For Large Datasets

1. **Increase worker count** (8-16 workers recommended for very large jobs)
2. **Adjust buffer size** in `config.yaml`:
   ```yaml
   execution:
     shuffle_buffer_size: 500  # Increase from 100 MB
   ```

3. **Use faster storage** for `data_dir` (SSD recommended)

### For High-Throughput

1. **Use dedicated network** between workers
2. **Increase worker resources** (CPU, RAM)
3. **Optimize mapper/reducer logic** (avoid heavy computations in map phase)

## Example Workflows

### Workflow 1: Quick Test
```bash
# Generate and process 1,000 records (fast)
python run_example.py log-analysis 1000
```

### Workflow 2: Medium Load
```bash
# 100,000 records (~5-10 seconds on 4 workers)
python run_example.py log-analysis 100000
```

### Workflow 3: Large Scale
```bash
# 1,000,000 records (stress test)
python run_example.py log-analysis 1000000
```

### Workflow 4: Different Problem
```bash
# Run sales analysis instead
python run_example.py sales-analysis 50000
```

## Next Steps

1. **Implement your own map-reduce problem** (see README.md)
2. **Scale to more workers** (update config.yaml)
3. **Test on real datasets** (replace sample data generators)
4. **Profile performance** (analyze logs for bottlenecks)

## Support

For issues:
1. Check logs: `mapreduce.log`
2. Verify configuration: `config.yaml`
3. Test connectivity: `python main.py status`
4. Review README.md for troubleshooting tips
