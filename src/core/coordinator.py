"""
Coordinator (master) node for managing map-reduce jobs.
"""

import pickle
import logging
import time
from typing import List, Type, Any
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import Mapper, Reducer, Partitioner, HashPartitioner


logger = logging.getLogger(__name__)


class Coordinator:
    """
    Coordinator node that orchestrates map-reduce jobs across worker nodes.
    
    Responsibilities:
    - Distribute input data to workers
    - Coordinate map phase execution
    - Monitor shuffle phase
    - Coordinate reduce phase execution
    - Collect and aggregate final results
    """
    
    def __init__(self, worker_addresses: List[str], timeout: int = 60):
        """
        Initialize the coordinator.
        
        Args:
            worker_addresses: List of worker URLs (e.g., ["http://localhost:5001", ...])
            timeout: Timeout for worker operations in seconds
        """
        self.worker_addresses = worker_addresses
        self.timeout = timeout
        self.num_workers = len(worker_addresses)
        
        logger.info(f"Coordinator initialized with {self.num_workers} workers")
        self._check_worker_health()
    
    def _check_worker_health(self):
        """Check if all workers are healthy and responsive."""
        logger.info("Checking worker health...")
        
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = {
                executor.submit(self._health_check, addr): addr 
                for addr in self.worker_addresses
            }
            
            for future in as_completed(futures):
                addr = futures[future]
                try:
                    future.result()
                    logger.info(f"Worker {addr} is healthy")
                except Exception as e:
                    logger.error(f"Worker {addr} health check failed: {e}")
                    raise RuntimeError(f"Worker {addr} is not responsive")
    
    def _health_check(self, worker_addr: str):
        """Perform health check on a single worker."""
        response = requests.get(f"{worker_addr}/health", timeout=5)
        response.raise_for_status()
        return response.json()
    
    def run_job(
        self,
        input_data: List[tuple],
        mapper_class: Type[Mapper],
        reducer_class: Type[Reducer],
        partitioner_class: Type[Partitioner] = HashPartitioner
    ) -> List[tuple]:
        """
        Execute a complete map-reduce job.
        
        Args:
            input_data: List of (key, value) tuples to process
            mapper_class: Class implementing Mapper interface
            reducer_class: Class implementing Reducer interface
            partitioner_class: Class implementing Partitioner interface
            
        Returns:
            List of (key, value) tuples representing final results
        """
        logger.info(f"Starting map-reduce job with {len(input_data)} input records")
        
        # Reset all workers
        self._reset_workers()
        
        # Distribute input data across workers
        data_splits = self._split_data(input_data)
        
        # Serialize mapper, reducer, and partitioner
        mapper_hex = pickle.dumps(mapper_class).hex()
        reducer_hex = pickle.dumps(reducer_class).hex()
        partitioner_hex = pickle.dumps(partitioner_class).hex()
        
        # Map phase
        logger.info("Executing map phase...")
        self._execute_map_phase(data_splits, mapper_hex, partitioner_hex)
        
        # Reduce phase
        logger.info("Executing reduce phase...")
        self._execute_reduce_phase(reducer_hex)
        
        # Collect results
        logger.info("Collecting results...")
        results = self._collect_results()
        
        logger.info(f"Job completed. Generated {len(results)} output records")
        return results
    
    def _reset_workers(self):
        """Reset all workers to clean state."""
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = [
                executor.submit(requests.post, f"{addr}/reset", timeout=10)
                for addr in self.worker_addresses
            ]
            
            for future in as_completed(futures):
                future.result()  # Ensure all resets complete
    
    def _split_data(self, input_data: List[tuple]) -> List[List[tuple]]:
        """
        Split input data across workers.
        
        Args:
            input_data: Complete input dataset
            
        Returns:
            List of data chunks, one per worker
        """
        chunk_size = len(input_data) // self.num_workers
        splits = []
        
        logger.info(f"Splitting {len(input_data):,} records across {self.num_workers} workers...")
        
        for i in range(self.num_workers):
            start = i * chunk_size
            end = start + chunk_size if i < self.num_workers - 1 else len(input_data)
            split_data = input_data[start:end]
            splits.append(split_data)
            logger.info(f"  Worker {i+1}: records {start:,}-{end:,} ({len(split_data):,} records)")
        
        logger.info(f"Dataset split complete: {self.num_workers} partitions created")
        return splits
    
    def _execute_map_phase(self, data_splits: List[List[tuple]], mapper_hex: str, partitioner_hex: str):
        """Execute map phase on all workers."""
        map_start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = []
            
            for i, (worker_addr, data_split) in enumerate(zip(self.worker_addresses, data_splits)):
                payload = {
                    'mapper': mapper_hex,
                    'partitioner': partitioner_hex,
                    'input_data': data_split,
                    'worker_addresses': self.worker_addresses
                }
                
                logger.info(f"Worker {i+1}: Starting map phase with {len(data_split):,} records")
                
                future = executor.submit(
                    requests.post,
                    f"{worker_addr}/execute_map",
                    json=payload,
                    timeout=self.timeout
                )
                futures.append(future)
            
            # Wait for all map tasks to complete
            completed_count = 0
            for future in as_completed(futures):
                try:
                    response = future.result()
                    response.raise_for_status()
                    result_data = response.json()
                    completed_count += 1
                    
                    worker_id = result_data.get('worker_id', 'unknown')
                    intermediate_count = result_data.get('intermediate_count', 0)
                    map_time = result_data.get('map_time', 0)
                    
                    logger.info(f"Worker {worker_id}: Completed map phase in {map_time:.2f}s → {intermediate_count:,} intermediate pairs")
                    logger.info(f"Map progress: {completed_count}/{self.num_workers} workers completed")
                except Exception as e:
                    logger.error(f"Map task failed: {e}")
                    raise
        
        map_total_time = time.time() - map_start_time
        logger.info(f"All workers completed map phase in {map_total_time:.2f}s")
    
    def _execute_reduce_phase(self, reducer_hex: str):
        """Execute reduce phase on all workers."""
        reduce_start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = []
            
            for i, worker_addr in enumerate(self.worker_addresses):
                payload = {'reducer': reducer_hex}
                
                logger.info(f"Worker {i+1}: Starting reduce phase")
                
                future = executor.submit(
                    requests.post,
                    f"{worker_addr}/execute_reduce",
                    json=payload,
                    timeout=self.timeout
                )
                futures.append(future)
            
            # Wait for all reduce tasks to complete
            completed_count = 0
            for future in as_completed(futures):
                try:
                    response = future.result()
                    response.raise_for_status()
                    result_data = response.json()
                    completed_count += 1
                    
                    worker_id = result_data.get('worker_id', 'unknown')
                    input_pairs = result_data.get('input_pairs', 0)
                    output_count = result_data.get('output_count', 0)
                    reduce_time = result_data.get('reduce_time', 0)
                    
                    logger.info(f"Worker {worker_id}: Reduced {input_pairs:,} pairs → {output_count} unique keys in {reduce_time:.2f}s")
                    logger.info(f"Reduce progress: {completed_count}/{self.num_workers} workers completed")
                except Exception as e:
                    logger.error(f"Reduce task failed: {e}")
                    raise
        
        reduce_total_time = time.time() - reduce_start_time
        logger.info(f"All workers completed reduce phase in {reduce_total_time:.2f}s")
    
    def _collect_results(self) -> List[tuple]:
        """Collect final results from all workers and merge duplicates."""
        all_results = []
        
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = {
                executor.submit(requests.get, f"{addr}/get_results", timeout=30): addr
                for addr in self.worker_addresses
            }
            
            for future in as_completed(futures):
                try:
                    response = future.result()
                    response.raise_for_status()
                    worker_data = response.json()
                    results = worker_data['results']
                    worker_id = worker_data.get('worker_id', 'unknown')
                    
                    logger.info(f"Collected from Worker {worker_id}: {len(results)} results")
                    all_results.extend(results)
                except Exception as e:
                    logger.error(f"Failed to collect results: {e}")
                    raise
        
        # Final merge: combine duplicate keys from different workers
        merged = {}
        for key, value in all_results:
            if key not in merged:
                merged[key] = []
            merged[key].append(value)
        
        # Merge duplicate keys intelligently:
        # - For counts (large integers): SUM (e.g., trip counts in Task 3)
        # - For percentages/averages (small floats): AVERAGE (e.g., tip%, $/mile in Task 1/2)
        logger.info(f"Merging results: {len(all_results)} raw results from all workers")
        
        final_results = []
        for key, values in merged.items():
            if len(values) == 1:
                # No duplicates, use as-is
                final_results.append((key, values[0]))
            else:
                # Multiple values from different workers - need to merge
                if values and isinstance(values[0], (int, float)):
                    # Heuristic: if values look like counts (integers > 100), sum them
                    # Otherwise (percentages, averages), take average
                    if all(isinstance(v, int) or (isinstance(v, float) and v > 100) for v in values):
                        # Looks like counts - SUM (Task 3: hourly trip counts)
                        merged_value = sum(values)
                        final_results.append((key, int(merged_value)))
                    else:
                        # Looks like averages/percentages - AVERAGE (Task 1/2: tip%, $/mile)
                        avg_value = sum(values) / len(values)
                        final_results.append((key, round(avg_value, 2)))
                else:
                    # For non-numeric, take first (shouldn't happen)
                    final_results.append((key, values[0]))
        
        logger.info(f"Final results: {len(final_results)} unique keys")
        return final_results
