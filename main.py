#!/usr/bin/env python3
"""
NYC Taxi Map-Reduce Analysis - Main Entry Point

Usage:
    python main.py worker <worker_id> [--host HOST] [--port PORT]
    python main.py coordinator --task <1|2|3> [--config CONFIG]
    
Examples:
    # Start a worker
    python main.py worker worker-1 --port 5001
    
    # Run Task 1 (Tip Analysis) as coordinator
    python main.py coordinator --task 1
    
    # Run Task 2 (Route Profitability) with custom config
    python main.py coordinator --task 2 --config my_config.yaml
"""

import argparse
import logging
import sys
import yaml
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.worker import start_worker
from src.core.coordinator import Coordinator
from src.utils.parquet_loader import load_nyc_taxi_data, create_sample_data

from src.tasks.task1_tip_analysis import TipPercentageMapper, TipPercentageReducer
from src.tasks.task2_route_profitability import RouteProfitabilityMapper, RouteProfitabilityReducer
from src.tasks.task3_hourly_traffic import HourlyTrafficMapper, HourlyTrafficReducer


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = 'config.yaml') -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def run_worker(args):
    """Start a worker node."""
    logger.info(f"Starting worker {args.worker_id}")
    
    host = args.host or 'localhost'
    port = args.port
    
    if not port:
        logger.error("Port is required for worker mode")
        sys.exit(1)
    
    start_worker(args.worker_id, host, port)


def run_coordinator(args):
    """Run a map-reduce job as coordinator."""
    # Load configuration
    config = load_config(args.config)
    
    # Get worker addresses
    worker_addresses = [
        f"http://{w['host']}:{w['port']}"
        for w in config['cluster']['workers']
    ]
    
    logger.info(f"Coordinator connecting to {len(worker_addresses)} workers")
    
    # Create coordinator
    coordinator = Coordinator(
        worker_addresses=worker_addresses,
        timeout=config['execution'].get('task_timeout', 300)
    )
    
    # Load data
    dataset_config = config['dataset']
    data_path = dataset_config.get('path')
    max_records = dataset_config.get('max_records')
    
    if data_path and Path(data_path).exists():
        logger.info(f"Loading data from {data_path}")
        input_data = load_nyc_taxi_data(
            data_path,
            max_records=max_records,
            columns=dataset_config.get('columns')
        )
    else:
        logger.warning(f"Data file {data_path} not found, using sample data")
        input_data = create_sample_data(num_records=max_records or 1000)
    
    # Select task
    task_map = {
        1: ("Tip Analysis", TipPercentageMapper, TipPercentageReducer),
        2: ("Route Profitability", RouteProfitabilityMapper, RouteProfitabilityReducer),
        3: ("Hourly Traffic", HourlyTrafficMapper, HourlyTrafficReducer)
    }
    
    task_num = args.task
    if task_num not in task_map:
        logger.error(f"Invalid task number: {task_num}. Choose 1, 2, or 3")
        sys.exit(1)
    
    task_name, mapper_class, reducer_class = task_map[task_num]
    
    logger.info(f"Running Task {task_num}: {task_name}")
    logger.info(f"Input: {len(input_data)} records")
    
    # Run the job
    results = coordinator.run_job(
        input_data=input_data,
        mapper_class=mapper_class,
        reducer_class=reducer_class
    )
    
    # Display results
    logger.info(f"\n{'='*60}")
    logger.info(f"Task {task_num}: {task_name} - Results")
    logger.info(f"{'='*60}")
    
    # Sort and display top results
    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
    
    print(f"\nTop 20 results:")
    print(f"{'-'*60}")
    
    for i, (key, value) in enumerate(sorted_results[:20], 1):
        print(f"{i:2d}. {key}: {value}")
    
    print(f"{'-'*60}")
    print(f"Total unique keys: {len(results)}")
    
    # Save results to file
    output_file = f"results_task{task_num}.txt"
    with open(output_file, 'w') as f:
        f.write(f"Task {task_num}: {task_name}\n")
        f.write(f"{'='*60}\n\n")
        
        for key, value in sorted_results:
            f.write(f"{key}: {value}\n")
    
    logger.info(f"\nResults saved to {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='NYC Taxi Map-Reduce Analysis System'
    )
    
    subparsers = parser.add_subparsers(dest='mode', help='Operating mode')
    
    # Worker mode
    worker_parser = subparsers.add_parser('worker', help='Start a worker node')
    worker_parser.add_argument('worker_id', help='Unique worker identifier')
    worker_parser.add_argument('--host', default='localhost', help='Host to bind to')
    worker_parser.add_argument('--port', type=int, required=True, help='Port to listen on')
    
    # Coordinator mode
    coord_parser = subparsers.add_parser('coordinator', help='Run as coordinator')
    coord_parser.add_argument(
        '--task',
        type=int,
        required=True,
        choices=[1, 2, 3],
        help='Task to run: 1=Tip Analysis, 2=Route Profitability, 3=Hourly Traffic'
    )
    coord_parser.add_argument(
        '--config',
        default='config.yaml',
        help='Configuration file path'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'worker':
        run_worker(args)
    elif args.mode == 'coordinator':
        run_coordinator(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
