#!/usr/bin/env python3
"""
Example: Running a complete map-reduce job programmatically.

This script demonstrates how to use the map-reduce engine to process data
across a distributed cluster. It's more complete than the CLI approach
because it properly initializes worker instances with mappers and reducers.
"""

import logging
import sys
import threading
import time
from pathlib import Path

import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.coordinator import Coordinator
from src.core.worker import Worker
from src.examples.log_analysis import LogAnalysisMapper, LogAnalysisReducer, generate_sample_logs
from src.examples.sales_analysis import SalesAnalysisMapper, SalesAnalysisReducer, generate_sample_sales


def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
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


def run_log_analysis_job(num_records: int = 10000):
    """
    Run the log analysis map-reduce job.
    
    This example:
    1. Starts worker nodes in background threads
    2. Configures each worker with the mapper and reducer
    3. Creates a coordinator and registers workers
    4. Generates sample log data
    5. Executes the map-reduce job
    6. Displays results
    """
    print("="*80)
    print("  Web Server Log Analysis - Map-Reduce Job")
    print("="*80)
    print()
    
    setup_logging()
    
    # Load configuration
    config = load_config()
    
    # Create and start workers
    print("Starting workers...")
    workers = []
    worker_threads = []
    
    for worker_config in config['cluster']['workers']:
        worker = Worker(
            worker_id=worker_config['id'],
            host=worker_config['host'],
            port=worker_config['port'],
            data_dir=worker_config['data_dir']
        )
        
        # Set mapper and reducer for this job
        worker.set_mapper(LogAnalysisMapper())
        worker.set_reducer(LogAnalysisReducer())
        
        workers.append(worker)
        
        # Start worker in background thread
        thread = threading.Thread(target=worker.start, daemon=True)
        thread.start()
        worker_threads.append(thread)
        
        print(f"  ✓ Started {worker_config['id']}")
        time.sleep(0.5)
    
    print()
    
    # Give workers time to start
    print("Waiting for workers to initialize...")
    time.sleep(3)
    print()
    
    # Create coordinator
    coord_config = config['cluster']['coordinator']
    coordinator = Coordinator(
        host=coord_config['host'],
        port=coord_config['port']
    )
    
    # Register workers
    for worker_config in config['cluster']['workers']:
        coordinator.register_worker(
            worker_id=worker_config['id'],
            host=worker_config['host'],
            port=worker_config['port'],
            data_dir=worker_config['data_dir']
        )
    
    print(f"Coordinator initialized with {len(workers)} workers")
    print()
    
    # Generate sample data
    print(f"Generating {num_records} sample log records...")
    input_data = generate_sample_logs(num_records)
    print(f"  ✓ Generated {len(input_data)} log records")
    print()
    
    # Execute the job
    try:
        results = coordinator.execute_job(
            input_data=input_data,
            mapper=LogAnalysisMapper(),
            reducer=LogAnalysisReducer()
        )
        
        # Display results
        print("\n" + "="*80)
        print("  JOB RESULTS")
        print("="*80)
        print()
        
        # Sort results by total requests (descending)
        sorted_results = sorted(results, key=lambda x: x[1].get('total_requests', 0), reverse=True)
        
        print(f"{'Endpoint':<30} {'Requests':<10} {'Avg Time':<12} {'Error Rate':<12} {'Peak Hours'}")
        print("-"*80)
        
        for endpoint, stats in sorted_results[:15]:  # Top 15 endpoints
            peak_hours_str = ', '.join([str(h['hour']) for h in stats['peak_hours'][:3]])
            print(f"{stats['endpoint']:<30} {stats['total_requests']:<10} "
                  f"{stats['response_time_avg_ms']:<12.2f} {stats['error_rate_percent']:<12.2f}% "
                  f"{peak_hours_str}")
        
        print()
        
        # Write full results to file
        output_file = 'log_analysis_results.txt'
        with open(output_file, 'w') as f:
            f.write("Web Server Log Analysis Results\n")
            f.write("="*80 + "\n\n")
            
            for endpoint, stats in sorted_results:
                f.write(f"Endpoint: {stats['endpoint']}\n")
                f.write(f"  Total Requests: {stats['total_requests']}\n")
                f.write(f"  Response Time (avg): {stats['response_time_avg_ms']:.2f} ms\n")
                f.write(f"  Response Time (min): {stats['response_time_min_ms']:.2f} ms\n")
                f.write(f"  Response Time (max): {stats['response_time_max_ms']:.2f} ms\n")
                f.write(f"  Success Count: {stats['success_count']}\n")
                f.write(f"  Error Count: {stats['error_count']}\n")
                f.write(f"  Error Rate: {stats['error_rate_percent']:.2f}%\n")
                f.write(f"  HTTP Methods: {stats['methods']}\n")
                f.write(f"  Status Codes: {stats['status_codes']}\n")
                f.write(f"  Peak Hours: {stats['peak_hours']}\n")
                f.write("\n" + "-"*80 + "\n\n")
        
        print(f"Full results written to: {output_file}")
        print()
        
    except Exception as e:
        print(f"Error executing job: {e}")
        import traceback
        traceback.print_exc()


def run_sales_analysis_job(num_records: int = 5000):
    """Run the sales analysis map-reduce job."""
    print("="*80)
    print("  E-commerce Sales Analysis - Map-Reduce Job")
    print("="*80)
    print()
    
    setup_logging()
    
    # Load configuration
    config = load_config()
    
    # Create and start workers
    print("Starting workers...")
    workers = []
    worker_threads = []
    
    for worker_config in config['cluster']['workers']:
        worker = Worker(
            worker_id=worker_config['id'],
            host=worker_config['host'],
            port=worker_config['port'],
            data_dir=worker_config['data_dir']
        )
        
        # Set mapper and reducer for this job
        worker.set_mapper(SalesAnalysisMapper())
        worker.set_reducer(SalesAnalysisReducer())
        
        workers.append(worker)
        
        # Start worker in background thread
        thread = threading.Thread(target=worker.start, daemon=True)
        thread.start()
        worker_threads.append(thread)
        
        print(f"  ✓ Started {worker_config['id']}")
        time.sleep(0.5)
    
    print()
    
    # Give workers time to start
    print("Waiting for workers to initialize...")
    time.sleep(3)
    print()
    
    # Create coordinator
    coord_config = config['cluster']['coordinator']
    coordinator = Coordinator(
        host=coord_config['host'],
        port=coord_config['port']
    )
    
    # Register workers
    for worker_config in config['cluster']['workers']:
        coordinator.register_worker(
            worker_id=worker_config['id'],
            host=worker_config['host'],
            port=worker_config['port'],
            data_dir=worker_config['data_dir']
        )
    
    print(f"Coordinator initialized with {len(workers)} workers")
    print()
    
    # Generate sample data
    print(f"Generating {num_records} sample sales transactions...")
    input_data = generate_sample_sales(num_records)
    print(f"  ✓ Generated {len(input_data)} transactions")
    print()
    
    # Execute the job
    try:
        results = coordinator.execute_job(
            input_data=input_data,
            mapper=SalesAnalysisMapper(),
            reducer=SalesAnalysisReducer()
        )
        
        # Organize results by type
        category_results = [r for r in results if r[0].startswith('category_summary:')]
        product_results = [r for r in results if r[0].startswith('product_summary:')]
        region_results = [r for r in results if r[0].startswith('region_summary:')]
        customer_results = [r for r in results if r[0].startswith('customer_summary:')]
        
        # Display results
        print("\n" + "="*80)
        print("  SALES ANALYSIS RESULTS")
        print("="*80)
        print()
        
        # Category summary
        print("Top Categories by Revenue:")
        print("-"*80)
        sorted_categories = sorted(category_results, key=lambda x: x[1]['total_revenue'], reverse=True)
        for _, stats in sorted_categories:
            print(f"  {stats['category']:<20} ${stats['total_revenue']:>12,.2f}  "
                  f"({stats['total_transactions']} transactions, {stats['total_units_sold']} units)")
        print()
        
        # Region summary
        print("Revenue by Region:")
        print("-"*80)
        sorted_regions = sorted(region_results, key=lambda x: x[1]['total_revenue'], reverse=True)
        for _, stats in sorted_regions:
            print(f"  {stats['region']:<20} ${stats['total_revenue']:>12,.2f}  "
                  f"({stats['total_transactions']} transactions)")
        print()
        
        # Top products
        print("Top 10 Products by Revenue:")
        print("-"*80)
        sorted_products = sorted(product_results, key=lambda x: x[1]['total_revenue'], reverse=True)[:10]
        for _, stats in sorted_products:
            print(f"  {stats['product_id']:<15} {stats['category']:<20} "
                  f"${stats['total_revenue']:>10,.2f}  ({stats['total_units_sold']} units)")
        print()
        
        # Write full results to file
        output_file = 'sales_analysis_results.txt'
        with open(output_file, 'w') as f:
            f.write("E-commerce Sales Analysis Results\n")
            f.write("="*80 + "\n\n")
            
            f.write("CATEGORY SUMMARY\n")
            f.write("-"*80 + "\n")
            for _, stats in sorted_categories:
                f.write(f"{stats['category']}: ${stats['total_revenue']:,.2f} "
                       f"({stats['total_transactions']} txns, {stats['total_units_sold']} units)\n")
            
            f.write("\n\nREGION SUMMARY\n")
            f.write("-"*80 + "\n")
            for _, stats in sorted_regions:
                f.write(f"{stats['region']}: ${stats['total_revenue']:,.2f} "
                       f"({stats['total_transactions']} txns)\n")
            
            f.write("\n\nPRODUCT SUMMARY\n")
            f.write("-"*80 + "\n")
            for _, stats in sorted_products:
                f.write(f"{stats['product_id']} ({stats['category']}): "
                       f"${stats['total_revenue']:,.2f} ({stats['total_units_sold']} units)\n")
        
        print(f"Full results written to: {output_file}")
        print()
        
    except Exception as e:
        print(f"Error executing job: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        job_type = sys.argv[1]
        num_records = int(sys.argv[2]) if len(sys.argv) > 2 else None
        
        if job_type == 'log-analysis':
            run_log_analysis_job(num_records or 10000)
        elif job_type == 'sales-analysis':
            run_sales_analysis_job(num_records or 5000)
        else:
            print(f"Unknown job type: {job_type}")
            print("Usage: python run_example.py [log-analysis|sales-analysis] [num_records]")
    else:
        print("Usage: python run_example.py [log-analysis|sales-analysis] [num_records]")
        print("\nExamples:")
        print("  python run_example.py log-analysis 10000")
        print("  python run_example.py sales-analysis 5000")
