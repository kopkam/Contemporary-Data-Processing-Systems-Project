# 📚 Documentation Index

Quick navigation to all project documentation.

## 🚀 Start Here

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[GETTING_STARTED.md](GETTING_STARTED.md)** | Your first 5 minutes with the system | 5 min |
| **[QUICKSTART.md](QUICKSTART.md)** | Quick reference and common commands | 3 min |
| **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** | Complete project overview | 10 min |

## 📖 Main Documentation

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[README.md](README.md)** | Complete project documentation | 20 min |
| **[SETUP.md](SETUP.md)** | Detailed setup for distributed deployment | 15 min |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Deep dive into system design | 25 min |

## 🎓 For Your Presentation

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[PRESENTATION_SKETCH.md](PRESENTATION_SKETCH.md)** | Problem explanation with examples | 15 min |

## 🔧 Configuration & Code

| File | Purpose |
|------|---------|
| **[config.yaml](config.yaml)** | Cluster configuration |
| **[requirements.txt](requirements.txt)** | Python dependencies |
| **[main.py](main.py)** | CLI interface |
| **[run_example.py](run_example.py)** | Example runner |
| **[test_system.py](test_system.py)** | Unit tests |
| **[quickstart.sh](quickstart.sh)** | Automated setup script |

## 📁 Source Code

### Core Engine (`src/core/`)
- **[base.py](src/core/base.py)** - Abstract classes (Mapper, Reducer, Partitioner)
- **[worker.py](src/core/worker.py)** - Worker node implementation
- **[coordinator.py](src/core/coordinator.py)** - Coordinator implementation

### Examples (`src/examples/`)
- **[log_analysis.py](src/examples/log_analysis.py)** - Web server log analysis
- **[sales_analysis.py](src/examples/sales_analysis.py)** - E-commerce sales analysis

## 🎯 By Use Case

### "I want to run this now!"
1. Read: [GETTING_STARTED.md](GETTING_STARTED.md)
2. Run: `./quickstart.sh` or `python run_example.py log-analysis 1000`

### "I need to understand how it works"
1. Read: [README.md](README.md) - Overview
2. Read: [ARCHITECTURE.md](ARCHITECTURE.md) - Details
3. Review: `src/core/` - Implementation

### "I'm preparing my presentation"
1. Read: [PRESENTATION_SKETCH.md](PRESENTATION_SKETCH.md)
2. Review: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
3. Practice: Run live demo with 1000 records

### "I need to deploy on multiple machines"
1. Read: [SETUP.md](SETUP.md)
2. Edit: [config.yaml](config.yaml)
3. Follow: Distribution instructions in SETUP.md

### "I want to create my own problem"
1. Review: `src/examples/log_analysis.py` as template
2. Read: [README.md](README.md) section "Creating Custom Problems"
3. Implement: Your Mapper and Reducer classes

### "Something isn't working"
1. Run: `python test_system.py`
2. Check: `mapreduce.log`
3. Review: [QUICKSTART.md](QUICKSTART.md) troubleshooting section

## 📊 Document Purpose Summary

```
GETTING_STARTED.md ─────► First 5 minutes
          │
          ├─► Run demo
          └─► See it work
          
QUICKSTART.md ──────────► Daily reference
          │
          ├─► Commands
          └─► Tips

README.md ──────────────► Complete guide
          │
          ├─► Features
          ├─► Examples
          └─► API

SETUP.md ───────────────► Distributed setup
          │
          ├─► Multi-machine
          └─► Configuration

ARCHITECTURE.md ────────► Deep technical
          │
          ├─► Data flow
          ├─► Diagrams
          └─► Algorithms

PRESENTATION_SKETCH.md ─► Explain your work
          │
          ├─► Problem definition
          ├─► Data flow example
          └─► Key points

PROJECT_SUMMARY.md ─────► Overview
          │
          ├─► Requirements ✓
          ├─► Features
          └─► How to use
```

## 🎓 Reading Plan

### Minimum (30 minutes)
1. GETTING_STARTED.md
2. QUICKSTART.md
3. PRESENTATION_SKETCH.md

### Recommended (60 minutes)
1. GETTING_STARTED.md
2. README.md
3. PRESENTATION_SKETCH.md
4. PROJECT_SUMMARY.md

### Complete (2 hours)
1. All documents above
2. SETUP.md
3. ARCHITECTURE.md
4. Review source code

## 💡 Tips

- **Start with**: GETTING_STARTED.md
- **Use daily**: QUICKSTART.md
- **Before presenting**: PRESENTATION_SKETCH.md
- **For deployment**: SETUP.md
- **To understand**: ARCHITECTURE.md
- **For overview**: PROJECT_SUMMARY.md or README.md

## 📝 Document Stats

| Document | Words | Focus |
|----------|-------|-------|
| GETTING_STARTED.md | ~800 | Quick start |
| QUICKSTART.md | ~1,200 | Reference |
| README.md | ~3,000 | Complete guide |
| SETUP.md | ~1,500 | Deployment |
| ARCHITECTURE.md | ~4,000 | Technical depth |
| PRESENTATION_SKETCH.md | ~2,500 | Explanation |
| PROJECT_SUMMARY.md | ~1,800 | Overview |

**Total:** ~15,000 words of documentation

## 🔗 Quick Links

- **Run demo**: `python run_example.py log-analysis 1000`
- **Run tests**: `python test_system.py`
- **Auto setup**: `./quickstart.sh`
- **Check status**: `python main.py status`

---

**Not sure where to start?** → [GETTING_STARTED.md](GETTING_STARTED.md)

**Want quick reference?** → [QUICKSTART.md](QUICKSTART.md)

**Preparing presentation?** → [PRESENTATION_SKETCH.md](PRESENTATION_SKETCH.md)

**Need complete info?** → [README.md](README.md)
