"""
Coordinator (master) node implementation for orchestrating map-reduce jobs.
"""

import logging
import time
from typing import Any, Dict, List, Tuple, Type

import requests

from .base import Mapper, Reducer, Partitioner


logger = logging.getLogger(__name__)


class Coordinator:
    """
    Coordinator node that orchestrates the map-reduce job execution.
    
    The coordinator is responsible for:
    - Distributing tasks to workers
    - Monitoring worker health
    - Coordinating the shuffle phase
    - Collecting final results
    """
    
    def __init__(self, host: str, port: int):
        """
        Initialize the coordinator.
        
        Args:
            host: Host address
            port: Port number
        """
        self.host = host
        self.port = port
        self.workers: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"Coordinator initialized at {host}:{port}")
    
    def register_worker(self, worker_id: str, host: str, port: int, data_dir: str):
        """
        Register a worker with the coordinator.
        
        Args:
            worker_id: Unique identifier for the worker
            host: Worker's host address
            port: Worker's port number
            data_dir: Worker's data directory
        """
        self.workers[worker_id] = {
            'id': worker_id,
            'host': host,
            'port': port,
            'data_dir': data_dir,
            'status': 'idle'
        }
        logger.info(f"Registered worker: {worker_id} at {host}:{port}")
    
    def check_workers_health(self) -> Dict[str, bool]:
        """
        Check health status of all workers.
        
        Returns:
            Dictionary mapping worker IDs to health status (True = healthy)
        """
        health_status = {}
        
        for worker_id, worker_info in self.workers.items():
            url = f"http://{worker_info['host']}:{worker_info['port']}/health"
            
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    health_status[worker_id] = True
                    data = response.json()
                    worker_info['status'] = data.get('status', 'unknown')
                else:
                    health_status[worker_id] = False
                    logger.warning(f"Worker {worker_id} health check failed with status {response.status_code}")
            except Exception as e:
                health_status[worker_id] = False
                logger.error(f"Worker {worker_id} health check failed: {e}")
        
        return health_status
    
    def broadcast_worker_registry(self):
        """
        Broadcast the list of all workers to each worker.
        
        This enables direct worker-to-worker communication during shuffle.
        """
        logger.info("Broadcasting worker registry to all workers")
        
        for worker_id, worker_info in self.workers.items():
            url = f"http://{worker_info['host']}:{worker_info['port']}/register_workers"
            
            try:
                response = requests.post(url, json={'workers': self.workers}, timeout=10)
                
                if response.status_code == 200:
                    logger.info(f"Successfully registered workers with {worker_id}")
                else:
                    logger.error(f"Failed to register workers with {worker_id}: {response.text}")
            except Exception as e:
                logger.error(f"Error registering workers with {worker_id}: {e}")
    
    def distribute_data(self, data: List[Tuple[Any, Any]]) -> Dict[str, List[Tuple[Any, Any]]]:
        """
        Distribute input data across workers.
        
        Args:
            data: Input data as list of (key, value) tuples
            
        Returns:
            Dictionary mapping worker IDs to their data partitions
        """
        num_workers = len(self.workers)
        chunk_size = len(data) // num_workers
        
        distributions = {}
        worker_ids = list(self.workers.keys())
        
        for i, worker_id in enumerate(worker_ids):
            start_idx = i * chunk_size
            if i == num_workers - 1:
                # Last worker gets remaining data
                end_idx = len(data)
            else:
                end_idx = (i + 1) * chunk_size
            
            distributions[worker_id] = data[start_idx:end_idx]
            logger.info(f"Assigned {len(distributions[worker_id])} records to {worker_id}")
        
        return distributions
    
    def execute_job(self, 
                   input_data: List[Tuple[Any, Any]],
                   mapper: Mapper,
                   reducer: Reducer,
                   partitioner: Partitioner = None) -> List[Tuple[Any, Any]]:
        """
        Execute a complete map-reduce job.
        
        Args:
            input_data: Input data as list of (key, value) tuples
            mapper: Mapper instance
            reducer: Reducer instance
            partitioner: Partitioner instance (optional)
            
        Returns:
            Final output as list of (key, value) tuples
        """
        logger.info("="*80)
        logger.info("Starting Map-Reduce Job Execution")
        logger.info(f"Input records: {len(input_data)}")
        logger.info(f"Workers: {len(self.workers)}")
        logger.info("="*80)
        
        start_time = time.time()
        
        # Step 1: Check worker health
        logger.info("\n[STEP 1] Checking worker health...")
        health_status = self.check_workers_health()
        healthy_workers = sum(health_status.values())
        
        if healthy_workers < len(self.workers):
            logger.warning(f"Only {healthy_workers}/{len(self.workers)} workers are healthy")
        
        if healthy_workers == 0:
            raise RuntimeError("No healthy workers available!")
        
        # Step 2: Broadcast worker registry for direct communication
        logger.info("\n[STEP 2] Broadcasting worker registry...")
        self.broadcast_worker_registry()
        
        # Step 3: Distribute input data
        logger.info("\n[STEP 3] Distributing input data...")
        data_distribution = self.distribute_data(input_data)
        
        # Step 4: Execute map phase
        logger.info("\n[STEP 4] Executing MAP phase...")
        map_phase_start = time.time()
        map_stats = {}
        
        for worker_id, worker_data in data_distribution.items():
            if not health_status.get(worker_id, False):
                logger.warning(f"Skipping unhealthy worker: {worker_id}")
                continue
            
            worker_info = self.workers[worker_id]
            url = f"http://{worker_info['host']}:{worker_info['port']}/execute_map"
            
            try:
                response = requests.post(url, json={'input_data': worker_data}, timeout=120)
                
                if response.status_code == 200:
                    result = response.json()
                    map_stats[worker_id] = result
                    logger.info(f"  ✓ {worker_id}: {result['records_processed']} → {result['records_emitted']} records")
                else:
                    logger.error(f"  ✗ {worker_id}: Map failed - {response.text}")
            except Exception as e:
                logger.error(f"  ✗ {worker_id}: Map failed - {e}")
        
        map_phase_time = time.time() - map_phase_start
        logger.info(f"Map phase completed in {map_phase_time:.2f}s")
        
        # Step 5: Execute shuffle phase (workers communicate directly)
        logger.info("\n[STEP 5] Executing SHUFFLE phase...")
        logger.info("Workers will communicate directly with each other...")
        shuffle_phase_start = time.time()
        
        # Trigger shuffle on each worker
        for worker_id in self.workers:
            if not health_status.get(worker_id, False):
                continue
            
            worker_info = self.workers[worker_id]
            url = f"http://{worker_info['host']}:{worker_info['port']}/execute_shuffle"
            
            try:
                response = requests.post(url, json={}, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    shuffle_stats = result.get('shuffle_stats', {})
                    total_sent = sum(shuffle_stats.values())
                    logger.info(f"  ✓ {worker_id}: Shuffled {total_sent} records")
                else:
                    logger.error(f"  ✗ {worker_id}: Shuffle failed - {response.text}")
            except Exception as e:
                logger.error(f"  ✗ {worker_id}: Shuffle failed - {e}")
        
        shuffle_phase_time = time.time() - shuffle_phase_start
        logger.info(f"Shuffle phase completed in {shuffle_phase_time:.2f}s")
        
        # Step 6: Execute reduce phase
        logger.info("\n[STEP 6] Executing REDUCE phase...")
        reduce_phase_start = time.time()
        reduce_stats = {}
        all_outputs = []
        
        for worker_id in self.workers:
            if not health_status.get(worker_id, False):
                continue
            
            worker_info = self.workers[worker_id]
            url = f"http://{worker_info['host']}:{worker_info['port']}/execute_reduce"
            
            try:
                response = requests.post(url, json={}, timeout=120)
                
                if response.status_code == 200:
                    result = response.json()
                    reduce_stats[worker_id] = result
                    all_outputs.extend(result.get('output', []))
                    logger.info(f"  ✓ {worker_id}: {result['keys_processed']} keys → {result['records_emitted']} records")
                else:
                    logger.error(f"  ✗ {worker_id}: Reduce failed - {response.text}")
            except Exception as e:
                logger.error(f"  ✗ {worker_id}: Reduce failed - {e}")
        
        reduce_phase_time = time.time() - reduce_phase_start
        logger.info(f"Reduce phase completed in {reduce_phase_time:.2f}s")
        
        # Summary
        total_time = time.time() - start_time
        logger.info("\n" + "="*80)
        logger.info("Job Execution Summary")
        logger.info("="*80)
        logger.info(f"Total execution time: {total_time:.2f}s")
        logger.info(f"  - Map phase:     {map_phase_time:.2f}s")
        logger.info(f"  - Shuffle phase: {shuffle_phase_time:.2f}s")
        logger.info(f"  - Reduce phase:  {reduce_phase_time:.2f}s")
        logger.info(f"Final output records: {len(all_outputs)}")
        logger.info("="*80 + "\n")
        
        return all_outputs
    
    def clear_all_workers(self):
        """Clear intermediate data from all workers."""
        logger.info("Clearing all workers...")
        
        for worker_id, worker_info in self.workers.items():
            url = f"http://{worker_info['host']}:{worker_info['port']}/clear"
            
            try:
                response = requests.post(url, json={}, timeout=10)
                if response.status_code == 200:
                    logger.info(f"Cleared worker: {worker_id}")
            except Exception as e:
                logger.error(f"Failed to clear worker {worker_id}: {e}")
