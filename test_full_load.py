#!/usr/bin/env python3
"""Test loading all NYC Taxi records"""
import time
import sys
sys.path.insert(0, '.')

from src.utils.parquet_loader import load_nyc_taxi_data

print('⏳ Ładowanie WSZYSTKICH rekordów NYC Taxi (styczeń 2024)...')
start = time.time()
data = load_nyc_taxi_data('data/yellow_tripdata_2024-01.parquet', max_records=None)
elapsed = time.time() - start

print(f'✅ Załadowano {len(data):,} rekordów w {elapsed:.2f}s')
print(f'📊 Średnio {len(data)/elapsed:,.0f} rekordów/sekundę')
print(f'\n🔍 Pierwszy rekord:')
print(f'   Zone: {data[0][1]["PULocationID"]} → {data[0][1]["DOLocationID"]}')
print(f'   Fare: ${data[0][1]["fare_amount"]}')
print(f'   Tip: ${data[0][1]["tip_amount"]}')
print(f'   Distance: {data[0][1]["trip_distance"]} miles')
