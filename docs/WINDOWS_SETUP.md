# Windows Worker Setup - Quick Guide

## 🪟 Setup na Windows PC (Maszyna 2)

### **Krok 1: Sklonuj Projekt**

Otwórz PowerShell:

```powershell
cd C:\Users\<TWOJ_USER>\Desktop
git clone <repository-url>
cd Contemporary-Data-Processing-Systems-Project
```

---

### **Krok 2: Zainstaluj Zależności**

```powershell
pip install -r requirements.txt
```

Jeśli nie masz Pythona:
- Pobierz z https://www.python.org/downloads/
- Zaznacz "Add Python to PATH" podczas instalacji!

---

### **Krok 3: Znajdź IP Windows PC**

```powershell
ipconfig
```

Znajdź **"IPv4 Address"** dla WiFi/Ethernet (np. `192.168.1.20`)

---

### **Krok 4: Skonfiguruj Firewall**

**WAŻNE!** Bez tego Mac nie będzie mógł połączyć się z workerami!

**Metoda 1 - Automatyczna (ZALECANA):**

Kliknij prawym na PowerShell → **"Run as Administrator"**

```powershell
.\setup_windows_firewall.ps1
```

**Metoda 2 - Ręczna (GUI):**

1. Wyszukaj "Windows Defender Firewall" w Start
2. Kliknij "Advanced settings"
3. Lewy panel: "Inbound Rules" → "New Rule..."
4. Type: **Port** → Next
5. **TCP**, Specific local ports: `5001, 5002` → Next
6. **Allow the connection** → Next
7. Zaznacz wszystkie (Domain, Private, Public) → Next
8. Name: `MapReduce Workers` → Finish

---

### **Krok 5: Skopiuj config.yaml z Maca**

**Opcja A - Przez Git:**
```powershell
git pull  # Jeśli Mac już zcommitował config
```

**Opcja B - Ręcznie:**
- Skopiuj `config.yaml` z Maca przez pendrive/email
- Umieść w katalogu projektu

**Lub stwórz ręcznie:** (zastąp IP!)

```yaml
cluster:
  workers:
    - id: "worker-1"
      host: "192.168.1.10"  # IP Maca
      port: 5001
    - id: "worker-2"
      host: "192.168.1.10"  # IP Maca
      port: 5002
    - id: "worker-3"
      host: "192.168.1.20"  # IP Windows (TWOJE!)
      port: 5001
    - id: "worker-4"
      host: "192.168.1.20"  # IP Windows (TWOJE!)
      port: 5002

dataset:
  path: "./data/yellow_tripdata_2024-01.parquet"
  max_records: 50000
  columns: null

execution:
  task_timeout: 300
  max_retries: 3
```

---

### **Krok 6: Uruchom Workers**

**Metoda 1 - Automatyczna:**

```powershell
.\start_windows_workers.ps1
```

To otworzy 2 nowe okna PowerShell z worker-3 i worker-4.

**Metoda 2 - Ręczna:**

Otwórz **2 osobne okna PowerShell**:

**PowerShell Okno 1:**
```powershell
cd C:\Users\<USER>\Desktop\Contemporary-Data-Processing-Systems-Project
python main.py worker worker-3 --host 0.0.0.0 --port 5001
```

**PowerShell Okno 2:**
```powershell
cd C:\Users\<USER>\Desktop\Contemporary-Data-Processing-Systems-Project
python main.py worker worker-4 --host 0.0.0.0 --port 5002
```

Zobaczysz:
```
* Serving Flask app 'src.core.worker'
* Running on http://0.0.0.0:5001
```

**✅ Workers działają!**

---

### **Krok 7: Test**

W nowym oknie PowerShell:

```powershell
.\test_workers_windows.ps1
```

Lub ręcznie:
```powershell
# Test lokalnych workerów
curl http://localhost:5001/health
curl http://localhost:5002/health

# Test workerów na Macu (zastąp IP!)
curl http://192.168.1.10:5001/health
curl http://192.168.1.10:5002/health
```

Wszystkie powinny zwrócić: `{"status":"healthy","worker_id":"worker-X"}`

---

### **Krok 8: Uruchom Coordinator (na Macu)**

Teraz wróć na Maca i uruchom:

```bash
python3 main.py coordinator --task 1
```

Coordinator:
- Połączy się z 4 workerami (2 na Macu, 2 na Windows!)
- Podzieli dane między nimi
- Uruchomi analizę
- Wyświetli wyniki

---

## 🐛 Troubleshooting Windows

### "python: command not found"

Python nie jest w PATH:
```powershell
# Znajdź Python
where python

# Jeśli nic nie znajdzie, dodaj do PATH lub użyj pełnej ścieżki:
C:\Users\<USER>\AppData\Local\Programs\Python\Python312\python.exe main.py ...
```

### "Connection refused" z Maca

1. **Sprawdź firewall** (najczęstszy problem!):
   ```powershell
   netsh advfirewall show allprofiles state
   ```

2. **Test portu z Windows:**
   ```powershell
   Test-NetConnection -ComputerName localhost -Port 5001
   ```

3. **Pinguj Maca:**
   ```powershell
   ping 192.168.1.10
   ```

4. **Sprawdź czy worker działa:**
   ```powershell
   Get-Process | Where-Object {$_.ProcessName -like "*python*"}
   ```

### Workers się nie widzą

Upewnij się że:
- [ ] Obie maszyny w tym samym WiFi
- [ ] Windows Firewall ma reguły dla portów 5001-5002
- [ ] Workers startują z `--host 0.0.0.0` (nie localhost!)
- [ ] config.yaml ma prawidłowe IP

### Antywirus blokuje

Dodaj wyjątek dla:
- Python.exe
- Folder projektu
- Porty 5001-5002

---

## 💡 Pro Tips dla Windows

1. **PowerShell 7:**
   Nowsza wersja ma `curl` wbudowany. Pobierz z:
   https://github.com/PowerShell/PowerShell/releases

2. **Windows Terminal:**
   Lepszy niż zwykły CMD/PowerShell:
   https://aka.ms/terminal

3. **Git Bash:**
   Jeśli wolisz bash zamiast PowerShell:
   https://git-scm.com/downloads

4. **Monitorowanie:**
   ```powershell
   # Zobacz użycie CPU/RAM
   Get-Process python | Format-Table CPU, PM, ProcessName
   ```

---

## 📋 Checklist

- [ ] Python zainstalowany (3.9+)
- [ ] Git zainstalowany
- [ ] Projekt sklonowany
- [ ] `pip install -r requirements.txt` wykonane
- [ ] Windows Firewall skonfigurowany (porty 5001-5002)
- [ ] IP Windows PC znany (ipconfig)
- [ ] config.yaml ma prawidłowe IP
- [ ] Workers startują z `--host 0.0.0.0`
- [ ] Test health check działa
- [ ] Obie maszyny w tym samym WiFi

Gotowe! 🎉
