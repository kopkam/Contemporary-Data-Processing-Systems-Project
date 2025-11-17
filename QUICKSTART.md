# Quick Reference Guide

## Quick Commands

### Run Tests
```bash
python test_system.py
```

### Run Log Analysis (Quick)
```bash
python run_example.py log-analysis 1000
```

### Run Sales Analysis (Quick)
```bash
python run_example.py sales-analysis 500
```

### Check Cluster Status
```bash
python main.py status
```

### Start Individual Worker
```bash
python main.py start-worker worker-1
```

## Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| Import errors | Run `pip install -r requirements.txt` |
| Port already in use | Change ports in `config.yaml` or kill process: `lsof -ti:5001 \| xargs kill` |
| Workers can't connect | Check firewall, verify IP addresses in config |
| Out of memory | Reduce dataset size or increase workers |

## File Overview

| File | Purpose |
|------|---------|
| `main.py` | CLI interface for managing cluster |
| `run_example.py` | Run complete examples |
| `test_system.py` | Unit tests |
| `config.yaml` | Cluster configuration |
| `src/core/worker.py` | Worker node implementation |
| `src/core/coordinator.py` | Coordinator implementation |
| `src/core/base.py` | Abstract classes (Mapper, Reducer) |
| `src/examples/log_analysis.py` | Web server log analysis example |
| `src/examples/sales_analysis.py` | Sales analysis example |

## Configuration Quick Edit

Edit `config.yaml` to change:
- Worker count (add/remove worker entries)
- Ports (change `port` values)
- IP addresses (change `host` values for distributed deployment)
- Data directories (change `data_dir` values)

## Performance Tuning

**For faster processing:**
1. Add more workers in `config.yaml`
2. Increase `shuffle_buffer_size` in config
3. Use SSD for `data_dir`
4. Run on machines with fast network

**For debugging:**
1. Reduce dataset size (use 100-1000 records)
2. Set `log-level` to DEBUG: `python main.py --log-level DEBUG ...`
3. Check `mapreduce.log` file

## Expected Performance

| Dataset Size | Workers | Expected Time |
|--------------|---------|---------------|
| 1,000 records | 4 | ~1-2 seconds |
| 10,000 records | 4 | ~3-5 seconds |
| 100,000 records | 4 | ~15-30 seconds |
| 1,000,000 records | 4 | ~2-5 minutes |

*Times are approximate and depend on hardware*

## Creating Your Own Problem

1. **Create a new file** in `src/examples/my_problem.py`

2. **Define Mapper:**
   ```python
   from src.core.base import Mapper
   
   class MyMapper(Mapper):
       def map(self, key, value):
           # Your logic here
           yield (new_key, new_value)
   ```

3. **Define Reducer:**
   ```python
   from src.core.base import Reducer
   
   class MyReducer(Reducer):
       def reduce(self, key, values):
           # Your aggregation logic
           result = aggregate(values)
           yield (key, result)
   ```

4. **Use in run_example.py:**
   ```python
   from src.examples.my_problem import MyMapper, MyReducer
   
   # ... in execute function
   mapper = MyMapper()
   reducer = MyReducer()
   ```

## Useful Commands

```bash
# Check Python version
python --version

# Install dependencies
pip install -r requirements.txt

# Check if port is in use (macOS/Linux)
lsof -i :5001

# Kill process on port (macOS/Linux)
lsof -ti:5001 | xargs kill

# View real-time logs
tail -f mapreduce.log

# Clean up data directories
rm -rf data/

# Test network connectivity between machines
ping 192.168.1.10
telnet 192.168.1.10 5001
```

## Architecture Summary

```
Input Data
    ↓
Coordinator (distributes data)
    ↓
Workers (MAP phase)
    ↓
Workers ←→ Workers (SHUFFLE phase - direct communication)
    ↓
Workers (REDUCE phase)
    ↓
Coordinator (collects results)
    ↓
Output
```

## Key Principles

1. **Map**: Transform input → intermediate key-value pairs
2. **Shuffle**: Redistribute data by key (hash-based partitioning)
3. **Reduce**: Aggregate values for each key
4. **Direct Communication**: Workers talk to each other during shuffle (no coordinator bottleneck)

## Next Steps

1. ✓ Run `python test_system.py` to verify installation
2. ✓ Run `python run_example.py log-analysis 1000` for quick test
3. ✓ Review output files: `log_analysis_results.txt`
4. ✓ Implement your own problem using the examples as templates
5. ✓ Deploy to multiple physical machines for true distributed processing

## Support Resources

- **README.md** - Complete documentation
- **SETUP.md** - Detailed setup instructions
- **ARCHITECTURE.md** - Deep dive into system design
- **Log files** - `mapreduce.log` for debugging
