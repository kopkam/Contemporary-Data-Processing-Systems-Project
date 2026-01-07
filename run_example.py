#!/usr/bin/env python3
"""
Programmatic example of running NYC Taxi analysis tasks.

This script demonstrates how to run the map-reduce tasks programmatically
without using the CLI. Useful for testing and integration.
"""

import logging
import sys
import time
import multiprocessing
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.worker import Worker
from src.core.coordinator import Coordinator
from src.utils.parquet_loader import create_sample_data

from src.tasks.task1_tip_analysis import TipPercentageMapper, TipPercentageReducer
from src.tasks.task2_route_profitability import RouteProfitabilityMapper, RouteProfitabilityReducer
from src.tasks.task3_hourly_traffic import HourlyTrafficMapper, HourlyTrafficReducer


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def start_worker_process(worker_id: str, port: int):
    """Start a worker in a separate process."""
    worker = Worker(worker_id, 'localhost', port)
    worker.start()


def run_example_task(task_num: int, num_records: int = 1000):
    """
    Run a specific task with sample data.
    
    Args:
        task_num: Task number (1, 2, or 3)
        num_records: Number of sample records to generate
    """
    # Worker configuration
    worker_configs = [
        ('worker-1', 5001),
        ('worker-2', 5002),
        ('worker-3', 5003),
        ('worker-4', 5004),
    ]
    
    # Start workers in separate processes
    logger.info("Starting worker nodes...")
    processes = []
    
    for worker_id, port in worker_configs:
        p = multiprocessing.Process(
            target=start_worker_process,
            args=(worker_id, port)
        )
        p.start()
        processes.append(p)
    
    # Give workers time to start
    time.sleep(3)
    
    try:
        # Create coordinator
        worker_addresses = [f"http://localhost:{port}" for _, port in worker_configs]
        coordinator = Coordinator(worker_addresses)
        
        # Generate sample data
        logger.info(f"Generating {num_records} sample taxi records...")
        input_data = create_sample_data(num_records)
        
        # Select task
        tasks = {
            1: ("Tip Analysis by Pickup Zone", TipPercentageMapper, TipPercentageReducer),
            2: ("Route Profitability Analysis", RouteProfitabilityMapper, RouteProfitabilityReducer),
            3: ("Hourly Traffic Distribution", HourlyTrafficMapper, HourlyTrafficReducer),
        }
        
        task_name, mapper_class, reducer_class = tasks[task_num]
        
        logger.info(f"\n{'='*70}")
        logger.info(f"Running Task {task_num}: {task_name}")
        logger.info(f"{'='*70}\n")
        
        # Run the job
        start_time = time.time()
        results = coordinator.run_job(
            input_data=input_data,
            mapper_class=mapper_class,
            reducer_class=reducer_class
        )
        elapsed_time = time.time() - start_time
        
        # Display results
        logger.info(f"\n{'='*70}")
        logger.info(f"Results for Task {task_num}: {task_name}")
        logger.info(f"{'='*70}")
        
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
        
        print(f"\nTop 15 results:")
        print(f"{'-'*70}")
        
        for i, (key, value) in enumerate(sorted_results[:15], 1):
            if task_num == 1:
                print(f"{i:2d}. Zone {key}: {value}% average tip")
            elif task_num == 2:
                pickup, dropoff = key
                print(f"{i:2d}. Zone {pickup} → {dropoff}: ${value}/mile")
            else:  # task 3
                print(f"{i:2d}. Hour {key:02d}:00: {value} trips")
        
        print(f"{'-'*70}")
        print(f"Total results: {len(results)}")
        print(f"Execution time: {elapsed_time:.2f} seconds")
        print(f"Throughput: {num_records/elapsed_time:.0f} records/second")
        
    finally:
        # Shutdown workers
        logger.info("\nShutting down workers...")
        for p in processes:
            p.terminate()
            p.join(timeout=5)
            if p.is_alive():
                p.kill()


def run_all_tasks():
    """Run all three tasks sequentially."""
    for task_num in [1, 2, 3]:
        logger.info(f"\n\n{'#'*70}")
        logger.info(f"# TASK {task_num}")
        logger.info(f"{'#'*70}\n")
        
        run_example_task(task_num, num_records=1000)
        
        # Wait between tasks
        if task_num < 3:
            logger.info("\nWaiting 5 seconds before next task...\n")
            time.sleep(5)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        task = int(sys.argv[1])
        if task in [1, 2, 3]:
            run_example_task(task)
        else:
            print("Usage: python run_example.py [1|2|3]")
            print("  1 = Tip Analysis")
            print("  2 = Route Profitability")
            print("  3 = Hourly Traffic")
            sys.exit(1)
    else:
        # Run all tasks
        run_all_tasks()
