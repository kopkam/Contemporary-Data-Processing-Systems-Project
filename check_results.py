#!/usr/bin/env python3
"""Check results aggregation"""
import sys
sys.path.insert(0, '.')

# Simulate what we got
results = [
    (216, 10623.68),
    (265, 3557.89),
    (54, 96.23),
    (102, 63.25),
    (1, 57.95),
    (265, 53.53),  # duplicate!
    (1, 47.12),    # duplicate!
]

print("Raw results (with duplicates):")
for zone, tip in results:
    print(f"  Zone {zone}: {tip}%")

print("\n675 unique zones from workers, but with duplicates in final list")
print("This means reduce didn't fully aggregate!")
