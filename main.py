#!/usr/bin/env python3
"""
Main entry point for the Map-Reduce distributed processing system.

This script provides CLI commands for:
- Starting coordinator and worker nodes
- Running map-reduce jobs
- Managing the cluster
"""

import logging
import sys
import threading
import time
from pathlib import Path

import click
import yaml
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.coordinator import Coordinator
from src.core.worker import Worker
from src.examples.log_analysis import LogAnalysisMapper, LogAnalysisReducer, generate_sample_logs
from src.examples.sales_analysis import SalesAnalysisMapper, SalesAnalysisReducer, generate_sample_sales


def setup_logging(level: str = "INFO"):
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('mapreduce.log')
        ]
    )


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


@click.group()
def cli():
    """Contemporary Data Processing Systems - Map-Reduce Engine"""
    pass


@cli.command()
@click.option('--config', default='config.yaml', help='Path to configuration file')
@click.option('--log-level', default='INFO', help='Logging level')
def start_coordinator(config, log_level):
    """Start the coordinator (master) node."""
    setup_logging(log_level)
    
    print(f"{Fore.CYAN}{'='*80}")
    print(f"  Map-Reduce Coordinator")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    config_data = load_config(config)
    coord_config = config_data['cluster']['coordinator']
    
    coordinator = Coordinator(
        host=coord_config['host'],
        port=coord_config['port']
    )
    
    # Register workers
    for worker_config in config_data['cluster']['workers']:
        coordinator.register_worker(
            worker_id=worker_config['id'],
            host=worker_config['host'],
            port=worker_config['port'],
            data_dir=worker_config['data_dir']
        )
    
    print(f"{Fore.GREEN}✓ Coordinator started at {coord_config['host']}:{coord_config['port']}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Registered {len(config_data['cluster']['workers'])} workers{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}Coordinator is running. Use Ctrl+C to stop.{Style.RESET_ALL}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Shutting down coordinator...{Style.RESET_ALL}")


@cli.command()
@click.argument('worker_id')
@click.option('--config', default='config.yaml', help='Path to configuration file')
@click.option('--log-level', default='INFO', help='Logging level')
def start_worker(worker_id, config, log_level):
    """Start a worker node."""
    setup_logging(log_level)
    
    config_data = load_config(config)
    
    # Find worker configuration
    worker_config = None
    for wc in config_data['cluster']['workers']:
        if wc['id'] == worker_id:
            worker_config = wc
            break
    
    if not worker_config:
        print(f"{Fore.RED}Error: Worker '{worker_id}' not found in configuration{Style.RESET_ALL}")
        sys.exit(1)
    
    print(f"{Fore.CYAN}{'='*80}")
    print(f"  Worker: {worker_id}")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    worker = Worker(
        worker_id=worker_config['id'],
        host=worker_config['host'],
        port=worker_config['port'],
        data_dir=worker_config['data_dir']
    )
    
    print(f"{Fore.GREEN}✓ Worker '{worker_id}' starting at {worker_config['host']}:{worker_config['port']}{Style.RESET_ALL}\n")
    print(f"{Fore.YELLOW}Worker is running. Use Ctrl+C to stop.{Style.RESET_ALL}\n")
    
    try:
        worker.start()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Shutting down worker...{Style.RESET_ALL}")


@cli.command()
@click.option('--config', default='config.yaml', help='Path to configuration file')
@click.option('--log-level', default='INFO', help='Logging level')
def start_cluster(config, log_level):
    """Start the entire cluster (coordinator + all workers) in one process."""
    setup_logging(log_level)
    
    print(f"{Fore.CYAN}{'='*80}")
    print(f"  Starting Map-Reduce Cluster")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    config_data = load_config(config)
    
    # Start workers in separate threads
    worker_threads = []
    workers = []
    
    for worker_config in config_data['cluster']['workers']:
        worker = Worker(
            worker_id=worker_config['id'],
            host=worker_config['host'],
            port=worker_config['port'],
            data_dir=worker_config['data_dir']
        )
        
        # Set mapper and reducer (will be used later)
        workers.append(worker)
        
        # Start worker in thread
        thread = threading.Thread(target=worker.start, daemon=True)
        thread.start()
        worker_threads.append(thread)
        
        print(f"{Fore.GREEN}✓ Started worker: {worker_config['id']} at {worker_config['host']}:{worker_config['port']}{Style.RESET_ALL}")
        time.sleep(0.5)  # Brief delay to avoid port conflicts
    
    print(f"\n{Fore.GREEN}✓ All workers started successfully{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Cluster is running. Use Ctrl+C to stop.{Style.RESET_ALL}\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Shutting down cluster...{Style.RESET_ALL}")


@cli.command()
@click.argument('job_type', type=click.Choice(['log-analysis', 'sales-analysis']))
@click.option('--config', default='config.yaml', help='Path to configuration file')
@click.option('--num-records', default=10000, help='Number of sample records to generate')
@click.option('--log-level', default='INFO', help='Logging level')
@click.option('--output', default='results.txt', help='Output file for results')
def run_job(job_type, config, num_records, log_level, output):
    """Run a map-reduce job on the cluster."""
    setup_logging(log_level)
    
    print(f"{Fore.CYAN}{'='*80}")
    print(f"  Running Map-Reduce Job: {job_type}")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    config_data = load_config(config)
    coord_config = config_data['cluster']['coordinator']
    
    # Create coordinator
    coordinator = Coordinator(
        host=coord_config['host'],
        port=coord_config['port']
    )
    
    # Register workers
    for worker_config in config_data['cluster']['workers']:
        coordinator.register_worker(
            worker_id=worker_config['id'],
            host=worker_config['host'],
            port=worker_config['port'],
            data_dir=worker_config['data_dir']
        )
    
    print(f"{Fore.GREEN}✓ Coordinator initialized{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Registered {len(config_data['cluster']['workers'])} workers{Style.RESET_ALL}\n")
    
    # Wait a moment for workers to be ready
    print(f"{Fore.YELLOW}Waiting for workers to be ready...{Style.RESET_ALL}")
    time.sleep(2)
    
    # Prepare job
    if job_type == 'log-analysis':
        print(f"{Fore.CYAN}Generating {num_records} sample log records...{Style.RESET_ALL}")
        input_data = generate_sample_logs(num_records)
        mapper = LogAnalysisMapper()
        reducer = LogAnalysisReducer()
        print(f"{Fore.GREEN}✓ Data generated{Style.RESET_ALL}\n")
        
    elif job_type == 'sales-analysis':
        print(f"{Fore.CYAN}Generating {num_records} sample sales transactions...{Style.RESET_ALL}")
        input_data = generate_sample_sales(num_records)
        mapper = SalesAnalysisMapper()
        reducer = SalesAnalysisReducer()
        print(f"{Fore.GREEN}✓ Data generated{Style.RESET_ALL}\n")
    
    # Set mapper and reducer on workers (via HTTP)
    import requests
    for worker_config in config_data['cluster']['workers']:
        worker_url = f"http://{worker_config['host']}:{worker_config['port']}"
        
        # Create worker-side instances
        # For simplicity, we'll create instances and pass them via the coordinator
        # In production, you might serialize the classes or use a registry
    
    # Note: For this demo, we need to set mapper/reducer directly on worker instances
    # This would typically be done via a registry or by sending serialized code
    # For now, we'll execute the job through the coordinator which will handle distribution
    
    print(f"{Fore.CYAN}Starting job execution...{Style.RESET_ALL}\n")
    
    # Execute job (note: in real implementation, workers need mapper/reducer instances)
    # For this demo, we'll need to manually set them on worker instances
    # This is a limitation of the HTTP-based approach - in practice, you'd use
    # serialization or a plugin system
    
    print(f"{Fore.YELLOW}Note: This demo requires workers to have mapper/reducer set.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}In production, use a plugin system or code serialization.{Style.RESET_ALL}\n")
    
    # For demo purposes, show what would happen
    print(f"{Fore.GREEN}Job would process:{Style.RESET_ALL}")
    print(f"  - Input records: {len(input_data)}")
    print(f"  - Workers: {len(config_data['cluster']['workers'])}")
    print(f"  - Records per worker: ~{len(input_data) // len(config_data['cluster']['workers'])}")
    
    print(f"\n{Fore.CYAN}To run the job properly, use the Python API (see examples).{Style.RESET_ALL}")


@cli.command()
@click.option('--config', default='config.yaml', help='Path to configuration file')
def status(config):
    """Check the status of all cluster nodes."""
    config_data = load_config(config)
    
    print(f"{Fore.CYAN}{'='*80}")
    print(f"  Cluster Status")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    import requests
    
    # Check coordinator
    coord_config = config_data['cluster']['coordinator']
    print(f"{Fore.CYAN}Coordinator:{Style.RESET_ALL} {coord_config['host']}:{coord_config['port']}")
    
    # Check workers
    print(f"\n{Fore.CYAN}Workers:{Style.RESET_ALL}")
    for worker_config in config_data['cluster']['workers']:
        url = f"http://{worker_config['host']}:{worker_config['port']}/health"
        
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                status_color = Fore.GREEN if data['status'] == 'idle' else Fore.YELLOW
                print(f"  {status_color}✓{Style.RESET_ALL} {worker_config['id']}: {data['status']}")
            else:
                print(f"  {Fore.RED}✗{Style.RESET_ALL} {worker_config['id']}: Error (HTTP {response.status_code})")
        except Exception as e:
            print(f"  {Fore.RED}✗{Style.RESET_ALL} {worker_config['id']}: Not reachable")
    
    print()


if __name__ == '__main__':
    cli()
