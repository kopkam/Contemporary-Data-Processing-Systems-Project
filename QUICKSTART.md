# NYC Taxi Map-Reduce - Quick Start Guide

## ✅ Projekt gotowy!

**Status:** Wszystkie testy przechodzą (29/29) ✅

---

## 🚀 Szybki Test

```bash
# Weryfikacja działania (bez uruchamiania klastra)
python3 verify.py
```

> **💡 Dane Parquet:** System automatycznie używa danych testowych. Prawdziwe pliki NYC Taxi wrzuć do katalogu `data/`. Zobacz [data/README.md](data/README.md) po szczegóły.

---

## 🏃 Uruchomienie Pełnego Systemu

### Opcja 1: Skrypt demonstracyjny (najłatwiejsze)

```bash
# Automatyczne uruchomienie workerów + analiza
python3 run_example.py 1    # Zadanie 1: Napiwki
python3 run_example.py 2    # Zadanie 2: Rentowność tras
python3 run_example.py 3    # Zadanie 3: Ruch godzinowy
```

### Opcja 2: Ręczne uruchomienie (prezentacja)

**Terminal 1-4 (Workery):**
```bash
python3 main.py worker worker-1 --port 5001
python3 main.py worker worker-2 --port 5002
python3 main.py worker worker-3 --port 5003
python3 main.py worker worker-4 --port 5004
```

**Terminal 5 (Coordinator):**
```bash
# Zadanie 1 (Sergiusz) - Analiza napiwków
python3 main.py coordinator --task 1

# Zadanie 2 (Ludwik) - Rentowność tras
python3 main.py coordinator --task 2

# Zadanie 3 (Marcin) - Ruch godzinowy
python3 main.py coordinator --task 3
```

---

## 📊 Trzy Indywidualne Zadania

### 1️⃣ Średnie napiwki wg strefy (Sergiusz Cudo)
- **Pytanie:** Które strefy NYC mają najwyższe napiwki?
- **Map:** `(zone, tip_percentage)`
- **Reduce:** `(zone, avg_tip_pct)`

### 2️⃣ Rentowność tras (Ludwik Janowski)  
- **Pytanie:** Które trasy (pickup→dropoff) są najbardziej opłacalne?
- **Map:** `((pickup, dropoff), revenue_per_mile)`
- **Reduce:** `((pickup, dropoff), avg_rpm)`

### 3️⃣ Ruch w ciągu dnia (Marcin Kopka)
- **Pytanie:** Kiedy są godziny szczytu dla taksówek?
- **Map:** `(hour, 1)`
- **Reduce:** `(hour, total_trips)`

---

## 🧪 Testy

```bash
# Wszystkie testy
python3 -m pytest tests/ -v

# Tylko jeden task
python3 -m pytest tests/test_task1.py -v
```

**Wynik:** 29/29 testów przechodzi ✅

---

## 📂 Struktura Projektu

```
├── src/
│   ├── core/           # Silnik Map-Reduce
│   ├── tasks/          # 3 zadania analityczne
│   └── utils/          # Ładowanie danych Parquet
├── tests/              # Testy jednostkowe
├── docs/               # Dokumentacja
├── main.py             # CLI
├── run_example.py      # Przykłady
└── config.yaml         # Konfiguracja
```

---

## 📖 Dokumentacja

- **README.md** - Ten plik
- **docs/SETUP.md** - Szczegółowa instalacja
- **docs/ARCHITECTURE.md** - Architektura systemu
- **docs/PRESENTATION_SKETCH.md** - Plan prezentacji

---

## 🎯 Na Prezentację (14.01.2026)

1. **Pokazać testy:** `python3 -m pytest tests/ -v`
2. **Uruchomić verify.py:** `python3 verify.py`
3. **Demo live:** `python3 run_example.py 1`
4. **Pokazać wyniki dla 3 tasków**

---

## 🔧 Wymagania

- Python 3.9+
- Pakiety: flask, pandas, pyarrow, requests, pytest

```bash
pip3 install -r requirements.txt
```

---

## 📊 Wydajność

- **Dataset:** 1000 rekordów testowych
- **Workery:** 4 węzły
- **Czas:** ~0.5s
- **Throughput:** ~2000 rekordów/s

---

## ✨ Kluczowe Cechy

- ✅ Pełna implementacja Map-Reduce
- ✅ 3 niezależne zadania analityczne
- ✅ Obsługa plików Parquet (NYC Taxi)
- ✅ Komunikacja peer-to-peer (shuffle)
- ✅ 29 testów jednostkowych
- ✅ Skalowalna architektura (4+ węzłów)

---

## 📧 Zespół

- **Sergiusz Cudo** - Task 1 (Napiwki)
- **Ludwik Janowski** - Task 2 (Rentowność)
- **Marcin Kopka** - Task 3 (Ruch czasowy)

**Prowadzący:** Prof. Tomasz Kowalski

**Uczelnia:** Politechnika Łódzka, Semestr Zimowy 2025/2026
