#!/usr/bin/env python3
"""
Quick verification script - runs Task 1 with sample data
"""

import time
import sys
sys.path.insert(0, '.')

from src.utils.parquet_loader import create_sample_data
from src.tasks.task1_tip_analysis import TipPercentageMapper, TipPercentageReducer

# Generate sample data
print("Generating 1000 sample taxi records...")
data = create_sample_data(1000)

# Test Task 1 mapper
print("\nTesting Task 1 Mapper...")
mapper = TipPercentageMapper()
map_results = []

for key, value in data[:100]:  # Test first 100
    for emitted in mapper.map(key, value):
        map_results.append(emitted)

print(f"Mapped {len(map_results)} records")
print(f"Sample output: {map_results[:5]}")

# Test Task 1 reducer  
print("\nTesting Task 1 Reducer...")
reducer = TipPercentageReducer()

# Group by zone
from collections import defaultdict
grouped = defaultdict(list)
for zone, tip_pct in map_results:
    grouped[zone].append(tip_pct)

reduce_results = []
for zone, tips in grouped.items():
    for result in reducer.reduce(zone, tips):
        reduce_results.append(result)

print(f"Reduced to {len(reduce_results)} zones")
print("\nTop 10 zones by average tip percentage:")
for i, (zone, avg_tip) in enumerate(sorted(reduce_results, key=lambda x: x[1], reverse=True)[:10], 1):
    print(f"{i}. Zone {zone}: {avg_tip}%")

print("\n✅ Task 1 verification complete!")
print("\nTo run the full distributed system:")
print("  python3 run_example.py 1")
