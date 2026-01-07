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
        
        for i in range(self.num_workers):
            start = i * chunk_size
            end = start + chunk_size if i < self.num_workers - 1 else len(input_data)
            splits.append(input_data[start:end])
        
        return splits
    
    def _execute_map_phase(self, data_splits: List[List[tuple]], mapper_hex: str, partitioner_hex: str):
        """Execute map phase on all workers."""
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = []
            
            for i, (worker_addr, data_split) in enumerate(zip(self.worker_addresses, data_splits)):
                payload = {
                    'mapper': mapper_hex,
                    'partitioner': partitioner_hex,
                    'input_data': data_split,
                    'worker_addresses': self.worker_addresses
                }
                
                future = executor.submit(
                    requests.post,
                    f"{worker_addr}/execute_map",
                    json=payload,
                    timeout=self.timeout
                )
                futures.append(future)
            
            # Wait for all map tasks to complete
            for i, future in enumerate(as_completed(futures)):
                try:
                    response = future.result()
                    response.raise_for_status()
                    logger.info(f"Map task {i+1}/{self.num_workers} completed")
                except Exception as e:
                    logger.error(f"Map task failed: {e}")
                    raise
    
    def _execute_reduce_phase(self, reducer_hex: str):
        """Execute reduce phase on all workers."""
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = []
            
            for worker_addr in self.worker_addresses:
                payload = {'reducer': reducer_hex}
                
                future = executor.submit(
                    requests.post,
                    f"{worker_addr}/execute_reduce",
                    json=payload,
                    timeout=self.timeout
                )
                futures.append(future)
            
            # Wait for all reduce tasks to complete
            for i, future in enumerate(as_completed(futures)):
                try:
                    response = future.result()
                    response.raise_for_status()
                    logger.info(f"Reduce task {i+1}/{self.num_workers} completed")
                except Exception as e:
                    logger.error(f"Reduce task failed: {e}")
                    raise
    
    def _collect_results(self) -> List[tuple]:
        """Collect final results from all workers."""
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
                    results = response.json()['results']
                    all_results.extend(results)
                except Exception as e:
                    logger.error(f"Failed to collect results: {e}")
                    raise
        
        return all_results
