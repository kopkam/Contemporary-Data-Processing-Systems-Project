# 🎯 Getting Started - First Steps

Welcome! This guide will get you running in 5 minutes.

## Option 1: Automatic Quick Start (Recommended)

```bash
./quickstart.sh
```

This script will:
1. Check Python installation
2. Install dependencies
3. Run tests
4. Execute a quick demo
5. Show you next steps

## Option 2: Manual Quick Start

### Step 1: Install Dependencies (30 seconds)
```bash
pip install -r requirements.txt
```

### Step 2: Run Tests (1 minute)
```bash
python test_system.py
```

Expected output:
```
================================================================================
  Map-Reduce System Unit Tests
================================================================================

Testing Mapper...
  ✓ Mapper test passed

Testing Reducer...
  ✓ Reducer test passed

...

================================================================================
  Test Results: 6 passed, 0 failed
================================================================================

✓ All tests passed! System is ready to use.
```

### Step 3: Run Your First Job (1 minute)
```bash
python run_example.py log-analysis 1000
```

This will:
- Start 4 workers automatically
- Generate 1,000 sample log records
- Process them using map-reduce
- Display results

Expected output:
```
================================================================================
  Web Server Log Analysis - Map-Reduce Job
================================================================================

Starting workers...
  ✓ Started worker-1
  ✓ Started worker-2
  ✓ Started worker-3
  ✓ Started worker-4

...

================================================================================
  JOB RESULTS
================================================================================

Endpoint                       Requests   Avg Time     Error Rate   Peak Hours
--------------------------------------------------------------------------------
/api/products                  243        187.32 ms    3.21%        10, 14, 16
/api/users                     189        145.67 ms    2.15%        11, 13, 15
...
```

### Step 4: Check Results File
```bash
cat log_analysis_results.txt
```

## What Just Happened?

1. **4 workers started** in background threads
2. **1,000 log records generated** and distributed (250 per worker)
3. **MAP phase**: Each worker parsed its logs
4. **SHUFFLE phase**: Workers exchanged data directly
5. **REDUCE phase**: Each worker aggregated its assigned endpoints
6. **Results collected** and formatted

## Try Different Things

### Larger Dataset
```bash
python run_example.py log-analysis 10000
```

### Different Problem
```bash
python run_example.py sales-analysis 5000
```

### Check Cluster Status
```bash
python main.py status
```

## Understanding the Output

The map-reduce job produces:
- **Console output**: Summary statistics and progress
- **Results file**: Detailed analysis (`log_analysis_results.txt`)
- **Log file**: Technical logs (`mapreduce.log`)

## Next Steps

### 1. Understand the Architecture
Read: `ARCHITECTURE.md` for detailed diagrams

### 2. Review Your Problem
Read: `PRESENTATION_SKETCH.md` for presentation guide

### 3. Deploy to Multiple Machines
Read: `SETUP.md` for distributed deployment

### 4. Create Your Own Problem
See: `src/examples/log_analysis.py` as template

## Common First-Time Issues

### "Module not found" errors
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### "Port already in use"
**Solution:** Change ports in `config.yaml` or kill existing process
```bash
# Find process using port 5001
lsof -ti:5001 | xargs kill
```

### Tests fail
**Solution:** Check Python version (need 3.8+)
```bash
python --version
```

## File Guide

| File | When to Use |
|------|-------------|
| `README.md` | Complete documentation |
| `QUICKSTART.md` | Quick reference guide |
| `SETUP.md` | Detailed setup for multiple machines |
| `ARCHITECTURE.md` | Understanding how it works |
| `PRESENTATION_SKETCH.md` | Preparing for presentation |
| `PROJECT_SUMMARY.md` | Project overview |

## Getting Help

1. **Check logs**: `tail -f mapreduce.log`
2. **Run tests**: `python test_system.py`
3. **Verify config**: Review `config.yaml`
4. **Read docs**: Start with `README.md`

## Success Indicators

✅ Tests pass  
✅ Demo runs successfully  
✅ Results file is generated  
✅ Output shows all 4 workers active  
✅ Timing statistics are reasonable  

## You're Ready When...

- [ ] `python test_system.py` passes
- [ ] `python run_example.py log-analysis 1000` works
- [ ] You can see results in `log_analysis_results.txt`
- [ ] You understand map → shuffle → reduce flow
- [ ] You've read `PRESENTATION_SKETCH.md`

**Time to complete: ~5 minutes**

---

**Questions?** Review the relevant documentation file above or check `mapreduce.log` for errors.

**Ready for more?** Try implementing your own problem using the examples as templates!
