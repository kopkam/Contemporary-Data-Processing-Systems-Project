# Deployment na Wiele Fizycznych Maszyn

## 🖥️ Architektura Multi-Machine

**Przykładowa konfiguracja:**
- **Maszyna 1 (Coordinator + 2 Workers):** MacBook Marcin
- **Maszyna 2 (2 Workers):** Laptop kolegi / Serwer

---

## 📋 Krok po Kroku

### **1. Przygotowanie Maszyn**

Na **KAŻDEJ** maszynie:

```bash
# Sklonuj repozytorium
git clone <repo-url>
cd Contemporary-Data-Processing-Systems-Project

# Zainstaluj zależności
pip3 install -r requirements.txt

# Pobierz dane (opcjonalnie - może być tylko na coordinator)
cd data/
wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet
cd ..
```

---

### **2. Poznaj IP Adres Każdej Maszyny**

**macOS/Linux:**

```bash
# macOS
ifconfig | grep "inet " | grep -v 127.0.0.1
# lub
ipconfig getifaddr en0  # WiFi

# Linux
hostname -I | awk '{print $1}'
```

**Windows:**

```powershell
# PowerShell lub CMD
ipconfig

# Znajdź "IPv4 Address" dla aktywnego adaptera (WiFi/Ethernet)
# Przykład: 192.168.1.20
```

**Przykładowe wyniki:**
- Maszyna 1 (Mac): 192.168.1.10
- Maszyna 2 (Windows): 192.168.1.20

**WAŻNE:** Wszystkie maszyny muszą być w tej samej sieci (WiFi/LAN)!

---

### **3. Edytuj config.yaml**

**Na KAŻDEJ maszynie edytuj ten sam plik:**

```yaml
cluster:
  coordinator:
    host: "192.168.1.10"  # IP Maszyny 1 (tam gdzie będzie coordinator)
    port: 5000
    
  workers:
    # Workers na Maszynie 1
    - id: "worker-1"
      host: "192.168.1.10"  # IP Maszyny 1
      port: 5001
      data_dir: "./data/worker1"
      
    - id: "worker-2"
      host: "192.168.1.10"  # IP Maszyny 1
      port: 5002
      data_dir: "./data/worker2"
      
    # Workers na Maszynie 2
    - id: "worker-3"
      host: "192.168.1.20"  # IP Maszyny 2
      port: 5001
      data_dir: "./data/worker3"
      
    - id: "worker-4"
      host: "192.168.1.20"  # IP Maszyny 2
      port: 5002
      data_dir: "./data/worker4"

dataset:
  path: "./data/yellow_tripdata_2024-01.parquet"
  max_records: 50000  # Dla testów
```

**💡 Tip:** Możesz mieć różne porty na różnych maszynach (oba 5001) albo różne na tej samej (5001, 5002).

---

### **4. Uruchom Workers**

**Na Maszynie 1 - macOS (192.168.1.10):**

Terminal 1:
```bash
python3 main.py worker worker-1 --host 0.0.0.0 --port 5001
```

Terminal 2:
```bash
python3 main.py worker worker-2 --host 0.0.0.0 --port 5002
```

**Na Maszynie 2 - Windows (192.168.1.20):**

PowerShell/CMD Terminal 1:
```powershell
python main.py worker worker-3 --host 0.0.0.0 --port 5001
```

PowerShell/CMD Terminal 2:
```powershell
python main.py worker worker-4 --host 0.0.0.0 --port 5002
```

**⚠️ WAŻNE:** 
- Użyj `--host 0.0.0.0` żeby worker słuchał na wszystkich interfejsach!
- Na Windows: `python` (bez "3")
- Uruchom każdy worker w osobnym oknie PowerShell/CMD

---

### **5. Uruchom Coordinator**

**Na Maszynie 1** (tam gdzie są dane):

```bash
python3 main.py coordinator --task 1
```

Coordinator:
- ✅ Sprawdzi czy wszystkie 4 workery są dostępne (health check)
- ✅ Załaduje dane z lokalnego pliku Parquet
- ✅ Podzieli dane między 4 workery
- ✅ Uruchomi analizę
- ✅ Zbierze wyniki

---

## 🔥 Firewall / Porty

**macOS:**

```bash
# Sprawdź czy firewall jest włączony
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Jeśli potrzeba, pozwól Python na połączenia przychodzące
# (System wyświetli dialog przy pierwszym uruchomieniu - kliknij "Allow")
```

**Linux:**

```bash
# Otwórz porty 5001-5002
sudo ufw allow 5001
sudo ufw allow 5002

# Lub wyłącz firewall tymczasowo (tylko do testów!)
sudo ufw disable
```

**Windows (WAŻNE!):**

```powershell
# Uruchom PowerShell jako Administrator!

# Metoda 1: Dodaj reguły dla konkretnych portów
netsh advfirewall firewall add rule name="MapReduce Worker 5001" dir=in action=allow protocol=TCP localport=5001
netsh advfirewall firewall add rule name="MapReduce Worker 5002" dir=in action=allow protocol=TCP localport=5002

# Metoda 2: Dodaj regułę dla Python.exe
netsh advfirewall firewall add rule name="Python MapReduce" dir=in action=allow program="C:\Users\<USER>\AppData\Local\Programs\Python\Python312\python.exe" enable=yes

# Sprawdź reguły
netsh advfirewall firewall show rule name="MapReduce Worker 5001"
```

**Lub GUI (Windows - łatwiejsze):**
1. Wyszukaj "Windows Defender Firewall" w Start
2. Kliknij "Advanced settings"
3. Kliknij "Inbound Rules" → "New Rule"
4. Type: Port → Next
5. TCP → Specific local ports: `5001, 5002` → Next
6. Allow the connection → Next
7. Zaznacz wszystkie profile → Next
8. Name: "MapReduce Workers" → Finish

---

## 🧪 Test Połączenia

**Z Maca (Maszyna 1), przetestuj połączenie do Windows (Maszyna 2):**

```bash
# Test czy worker-3 na Windows odpowiada
curl http://192.168.1.20:5001/health

# Powinno zwrócić:
# {"status":"healthy","worker_id":"worker-3"}
```

**Z Windows (Maszyna 2), przetestuj Mac (Maszyna 1):**

PowerShell (v7+):
```powershell
curl http://192.168.1.10:5001/health
```

Lub PowerShell (starsza wersja):
```powershell
Invoke-WebRequest -Uri http://192.168.1.10:5001/health

# Lub użyj przeglądarki:
# Otwórz http://192.168.1.10:5001/health
```

Lub CMD:
```cmd
# Jeśli masz curl (Windows 10+)
curl http://192.168.1.10:5001/health

# Albo użyj telnet do testu portu
telnet 192.168.1.10 5001
```

Jeśli dostajesz `Connection refused` lub timeout:
- ✅ Sprawdź czy worker działa
- ✅ Sprawdź firewall (NAJCZĘSTSZY PROBLEM na Windows!)
- ✅ Sprawdź czy IP są poprawne (`ipconfig` na Windows)
- ✅ Sprawdź czy jesteście w tej samej sieci (to samo WiFi)
- ✅ Pinguj drugą maszynę: `ping 192.168.1.20`

---

## 📊 Przykładowy Output

```
Worker http://192.168.1.10:5001 is healthy
Worker http://192.168.1.10:5002 is healthy
Worker http://192.168.1.20:5001 is healthy
Worker http://192.168.1.20:5002 is healthy

Loading NYC Taxi data from ./data/yellow_tripdata_2024-01.parquet
Loaded 50,000 records from Parquet file

Executing map phase...
Map task 1/4 completed
Map task 2/4 completed
Map task 3/4 completed
Map task 4/4 completed

Executing reduce phase...
Reduce task 1/4 completed
...
```

---

## 🚀 Alternatywa: Screen/tmux

Jeśli masz SSH do drugiej maszyny, możesz uruchomić wszystko z jednej:

**Na Maszynie 1:**

```bash
# Uruchom lokalne workery
python3 main.py worker worker-1 --host 0.0.0.0 --port 5001 &
python3 main.py worker worker-2 --host 0.0.0.0 --port 5002 &

# SSH do Maszyny 2 i uruchom workery
ssh user@192.168.1.20 "cd ~/Contemporary-Data-Processing-Systems-Project && python3 main.py worker worker-3 --host 0.0.0.0 --port 5001" &
ssh user@192.168.1.20 "cd ~/Contemporary-Data-Processing-Systems-Project && python3 main.py worker worker-4 --host 0.0.0.0 --port 5002" &

# Odczekaj 3 sekundy
sleep 3

# Uruchom coordinator
python3 main.py coordinator --task 1
```

---

## 🎯 Najłatwiejsza Konfiguracja (Mac + Windows w jednym WiFi)

**Mac (Twój MacBook - Maszyna 1):**
- IP: 192.168.1.10
- Worker-1 na porcie 5001
- Worker-2 na porcie 5002
- Coordinator
- Dane Parquet

**Windows PC (Maszyna 2):**
- IP: 192.168.1.20
- Worker-3 na porcie 5001
- Worker-4 na porcie 5002

**config.yaml** (ten sam na obu):
```yaml
workers:
  - id: "worker-1"
    host: "192.168.1.10"
    port: 5001
  - id: "worker-2"
    host: "192.168.1.10"
    port: 5002
  - id: "worker-3"
    host: "192.168.1.20"  # Windows PC
    port: 5001
  - id: "worker-4"
    host: "192.168.1.20"  # Windows PC
    port: 5002
```

### Krok po kroku:

**1. Na Windows PC:**
```powershell
# PowerShell
cd C:\Users\<TWOJ_USER>\Desktop
git clone <repo-url>
cd Contemporary-Data-Processing-Systems-Project
pip install -r requirements.txt

# Skopiuj config.yaml z Maca (przez pendrive lub git)

# Otwórz 2 okna PowerShell i uruchom:
# Okno 1:
python main.py worker worker-3 --host 0.0.0.0 --port 5001

# Okno 2:
python main.py worker worker-4 --host 0.0.0.0 --port 5002
```

**2. Na Macu:**
```bash
# Terminal 1:
python3 main.py worker worker-1 --host 0.0.0.0 --port 5001

# Terminal 2:
python3 main.py worker worker-2 --host 0.0.0.0 --port 5002

# Terminal 3 - Coordinator:
python3 main.py coordinator --task 1
```

---

## ⚡ Demo na Prezentacji

**Efektowne:**

1. Pokażcie 2 laptopy obok siebie
2. Na każdym terminal z workerami
3. Logi pokazują wymianę danych między maszynami
4. Na końcu wyniki agregowane z 2 lokalizacji fizycznych

**Mniej efektowne ale działa:**

Wszystko na localhost (jak teraz) - też jest OK dla prezentacji.

---

## 🐛 Troubleshooting

### Workers się nie widzą

```bash
# Sprawdź routing
ping 192.168.1.20

# Sprawdź czy port jest otwarty
nc -zv 192.168.1.20 5001

# Zobacz logi workerów
# Powinny pokazywać requesty od coordinatora
```

### "Connection refused"

- Worker nie działa lub nie nasłuchuje na 0.0.0.0
- Firewall blokuje
- Zły port/IP w config.yaml

### "Map task failed"

- Prawdopodobnie worker padł podczas przetwarzania
- Sprawdź logi workerów
- Może za mało RAM (3M rekordów to ~2GB pamięci)

---

## 💡 Pro Tips

1. **Sync config.yaml**: Użyj `git` żeby mieć ten sam config na obu maszynach
2. **Symlink do danych**: Tylko jedna maszyna (coordinator) potrzebuje pliku Parquet
3. **Monitoring**: Uruchom `htop` na workerach żeby widzieć użycie CPU/RAM
4. **Logi**: Dodaj `> worker.log 2>&1` żeby zapisywać logi
5. **Testuj lokalnie pierwszy**: Upewnij się że działa na localhost przed multi-machine

---

## 📝 Checklist Przed Prezentacją

- [ ] Config.yaml ma prawidłowe IP
- [ ] Workery startują na 0.0.0.0 (nie localhost)
- [ ] Health check przechodzi dla wszystkich workerów
- [ ] Firewall przepuszcza porty 5001-5002
- [ ] Obie maszyny w tej samej sieci
- [ ] Dane Parquet są na maszynie z coordinator
- [ ] Test run działa

Powodzenia! 🚀
