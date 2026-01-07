# Scripts / Skrypty

Helper scripts for multi-machine deployment / Skrypty pomocnicze dla uruchomienia na wielu maszynach

## 🍎 macOS (Coordinator + Workers 1-2)

### Start Workers
```bash
./scripts/start_mac_workers.sh
```
Automatically launches worker-1 and worker-2 in separate Terminal windows.

### Test Connectivity
```bash
./scripts/test_workers.sh
```
Tests connection to all 4 workers (Mac + Windows).

---

## 🪟 Windows (Workers 3-4)

### Setup (First Time Only)

**1. Install Dependencies:**
```powershell
.\scripts\setup_windows_workers.ps1
```

**2. Configure Firewall (Run as Administrator):**
```powershell
.\scripts\setup_windows_firewall.ps1
```

### Start Workers
```powershell
.\scripts\start_windows_workers.ps1
```
Automatically launches worker-3 and worker-4 in separate PowerShell windows.

### Test Connectivity
```powershell
.\scripts\test_workers_windows.ps1
```
Tests connection to all workers from Windows.

---

## 📋 Typical Workflow

**On macOS:**
```bash
# 1. Start Mac workers
./scripts/start_mac_workers.sh

# 2. Wait for Windows workers to start, then test
./scripts/test_workers.sh

# 3. Run coordinator
python3 main.py coordinator --task 1
```

**On Windows:**
```powershell
# 1. Start Windows workers
.\scripts\start_windows_workers.ps1

# 2. Optional: test connectivity
.\scripts\test_workers_windows.ps1
```

---

## 📄 Script Descriptions

| Script | Platform | Purpose |
|--------|----------|---------|
| `start_mac_workers.sh` | macOS | Launch workers 1-2 automatically |
| `start_windows_workers.ps1` | Windows | Launch workers 3-4 automatically |
| `test_workers.sh` | macOS | Test all worker connectivity |
| `test_workers_windows.ps1` | Windows | Test all worker connectivity |
| `setup_windows_workers.ps1` | Windows | Install dependencies |
| `setup_windows_firewall.ps1` | Windows | Configure firewall (admin) |
