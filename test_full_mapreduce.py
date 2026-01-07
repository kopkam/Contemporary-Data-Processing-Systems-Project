#!/usr/bin/env python3
"""
Full-scale test: Task 1 on ALL 3M records with distributed system
"""
import time
import sys
import multiprocessing
sys.path.insert(0, '.')

from src.core.worker import Worker
from src.core.coordinator import Coordinator
from src.utils.parquet_loader import load_nyc_taxi_data
from src.tasks.task1_tip_analysis import TipPercentageMapper, TipPercentageReducer

def worker_proc(worker_id, port):
    w = Worker(worker_id, 'localhost', port)
    w.start()

if __name__ == '__main__':
    print('🚀 NYC TAXI FULL-SCALE MAP-REDUCE TEST')
    print('='*70)
    
    # Start 4 workers
    print('\n📡 Starting 4 worker nodes...')
    procs = []
    for i, port in enumerate([5001, 5002, 5003, 5004], 1):
        p = multiprocessing.Process(target=worker_proc, args=(f'worker-{i}', port))
        p.start()
        procs.append(p)
    
    time.sleep(3)
    
    try:
        # Load ALL data
        print('\n📥 Loading ALL NYC Taxi records (2,964,624 records)...')
        load_start = time.time()
        data = load_nyc_taxi_data('data/yellow_tripdata_2024-01.parquet', max_records=None)
        load_time = time.time() - load_start
        print(f'   ✅ Loaded {len(data):,} records in {load_time:.2f}s')
        
        # Run analysis
        addrs = [f'http://localhost:{p}' for p in [5001, 5002, 5003, 5004]]
        coord = Coordinator(addrs)
        
        print('\n🔄 Running Task 1: Tip Analysis by Zone')
        print('   (This will take 1-2 minutes...)')
        
        job_start = time.time()
        results = coord.run_job(data, TipPercentageMapper, TipPercentageReducer)
        job_time = time.time() - job_start
        
        # Post-aggregation: merge results from different workers for same key
        # Each worker may have reduced different subsets of the same zone
        from collections import defaultdict
        final_aggregation = defaultdict(list)
        for zone, avg_tip in results:
            final_aggregation[zone].append(avg_tip)
        
        # Calculate overall average for each zone
        final_results = []
        for zone, tip_percentages in final_aggregation.items():
            overall_avg = sum(tip_percentages) / len(tip_percentages)
            final_results.append((zone, overall_avg))
        
        total_time = load_time + job_time
        
        print('\n' + '='*70)
        print('✅ JOB COMPLETE!')
        print('='*70)
        print(f'\n📊 Performance Metrics:')
        print(f'   Load time:       {load_time:.2f}s')
        print(f'   Job time:        {job_time:.2f}s')
        print(f'   Total time:      {total_time:.2f}s')
        print(f'   Throughput:      {len(data)/job_time:,.0f} records/second')
        print(f'   Records/worker:  {len(data)/4:,.0f}')
        
        print(f'\n🎯 Results:')
        print(f'   Raw results:     {len(results)} (from all workers)')
        print(f'   Unique zones:    {len(final_results)}')
        
        sorted_results = sorted(final_results, key=lambda x: x[1], reverse=True)
        
        print('\n🏆 Top 15 zones by average tip percentage:')
        print('-'*70)
        for i, (zone, tip_pct) in enumerate(sorted_results[:15], 1):
            print(f'   {i:2d}. Zone {zone:3d}: {tip_pct:6.2f}%')
        
        print('\n📉 Bottom 5 zones:')
        print('-'*70)
        for i, (zone, tip_pct) in enumerate(sorted_results[-5:], 1):
            print(f'   {i}. Zone {zone:3d}: {tip_pct:6.2f}%')
        
    finally:
        print('\n🛑 Shutting down workers...')
        for p in procs:
            p.terminate()
            p.join(timeout=2)
            if p.is_alive():
                p.kill()
        print('✅ Done!')
