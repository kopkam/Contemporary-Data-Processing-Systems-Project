"""
Worker node implementation for distributed map-reduce processing.
"""

import logging
import os
import pickle
import socket
import threading
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from flask import Flask, request, jsonify

from .base import Mapper, Reducer, Partitioner, HashPartitioner


logger = logging.getLogger(__name__)


class Worker:
    """
    Worker node that executes map and reduce tasks.
    
    Workers operate independently and communicate directly with each other
    during the shuffle phase for efficient data redistribution.
    """
    
    def __init__(self, worker_id: str, host: str, port: int, data_dir: str):
        """
        Initialize a worker node.
        
        Args:
            worker_id: Unique identifier for this worker
            host: Host address to bind to
            port: Port number to listen on
            data_dir: Directory for storing intermediate data
        """
        self.worker_id = worker_id
        self.host = host
        self.port = port
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Task components
        self.mapper: Mapper = None
        self.reducer: Reducer = None
        self.partitioner: Partitioner = HashPartitioner()
        
        # Worker registry for direct communication
        self.workers: Dict[str, Dict[str, Any]] = {}
        
        # Intermediate data storage
        self.map_output: List[Tuple[Any, Any]] = []
        self.reduce_input: Dict[Any, List[Any]] = defaultdict(list)
        self.reduce_output: List[Tuple[Any, Any]] = []
        
        # Flask app for receiving requests
        self.app = Flask(f"worker-{worker_id}")
        self._setup_routes()
        
        # Status tracking
        self.status = "idle"
        self.current_task = None
        
        logger.info(f"Worker {worker_id} initialized at {host}:{port}")
    
    def _setup_routes(self):
        """Setup Flask routes for worker endpoints."""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({
                'worker_id': self.worker_id,
                'status': self.status,
                'current_task': self.current_task
            })
        
        @self.app.route('/execute_map', methods=['POST'])
        def execute_map():
            """Execute map task on input data."""
            try:
                data = request.json
                input_data = data.get('input_data', [])
                
                self.status = "mapping"
                self.current_task = "map"
                logger.info(f"[{self.worker_id}] Starting map task with {len(input_data)} records")
                
                result = self._execute_map_phase(input_data)
                
                self.status = "idle"
                self.current_task = None
                
                return jsonify({
                    'success': True,
                    'worker_id': self.worker_id,
                    'records_processed': result['records_processed'],
                    'records_emitted': result['records_emitted']
                })
            except Exception as e:
                logger.error(f"[{self.worker_id}] Map task failed: {e}")
                self.status = "error"
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/shuffle', methods=['POST'])
        def receive_shuffle_data():
            """Receive shuffled data from other workers."""
            try:
                data = request.json
                shuffle_data = data.get('data', [])
                source_worker = data.get('source_worker')
                
                logger.info(f"[{self.worker_id}] Receiving {len(shuffle_data)} records from {source_worker}")
                
                # Store received data for reduce phase
                for key, value in shuffle_data:
                    self.reduce_input[key].append(value)
                
                return jsonify({
                    'success': True,
                    'worker_id': self.worker_id,
                    'records_received': len(shuffle_data)
                })
            except Exception as e:
                logger.error(f"[{self.worker_id}] Shuffle receive failed: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/execute_reduce', methods=['POST'])
        def execute_reduce():
            """Execute reduce task on shuffled data."""
            try:
                self.status = "reducing"
                self.current_task = "reduce"
                logger.info(f"[{self.worker_id}] Starting reduce task with {len(self.reduce_input)} keys")
                
                result = self._execute_reduce_phase()
                
                self.status = "idle"
                self.current_task = None
                
                return jsonify({
                    'success': True,
                    'worker_id': self.worker_id,
                    'keys_processed': result['keys_processed'],
                    'records_emitted': result['records_emitted'],
                    'output': result['output']
                })
            except Exception as e:
                logger.error(f"[{self.worker_id}] Reduce task failed: {e}")
                self.status = "error"
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/execute_shuffle', methods=['POST'])
        def execute_shuffle():
            """Execute shuffle phase - send data to appropriate workers."""
            try:
                self.status = "shuffling"
                self.current_task = "shuffle"
                logger.info(f"[{self.worker_id}] Starting shuffle task")
                
                stats = self.shuffle_data()
                
                self.status = "idle"
                self.current_task = None
                
                return jsonify({
                    'success': True,
                    'worker_id': self.worker_id,
                    'shuffle_stats': stats
                })
            except Exception as e:
                logger.error(f"[{self.worker_id}] Shuffle task failed: {e}")
                self.status = "error"
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/set_task', methods=['POST'])
        def set_task():
            """Set the mapper and reducer for the current job."""
            try:
                data = request.json
                mapper_code = data.get('mapper')
                reducer_code = data.get('reducer')
                
                # This is simplified - in production, you'd want secure code execution
                # For now, assume mapper and reducer classes are registered
                
                return jsonify({
                    'success': True,
                    'worker_id': self.worker_id
                })
            except Exception as e:
                logger.error(f"[{self.worker_id}] Set task failed: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/register_workers', methods=['POST'])
        def register_workers():
            """Register other workers for direct communication during shuffle."""
            try:
                data = request.json
                self.workers = data.get('workers', {})
                logger.info(f"[{self.worker_id}] Registered {len(self.workers)} workers")
                
                return jsonify({
                    'success': True,
                    'worker_id': self.worker_id
                })
            except Exception as e:
                logger.error(f"[{self.worker_id}] Worker registration failed: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/clear', methods=['POST'])
        def clear():
            """Clear all intermediate data."""
            self.map_output = []
            self.reduce_input = defaultdict(list)
            self.reduce_output = []
            self.status = "idle"
            self.current_task = None
            
            return jsonify({
                'success': True,
                'worker_id': self.worker_id
            })
    
    def _execute_map_phase(self, input_data: List[Tuple[Any, Any]]) -> Dict[str, int]:
        """
        Execute the map phase on input data.
        
        Args:
            input_data: List of (key, value) tuples to process
            
        Returns:
            Statistics about the map phase execution
        """
        self.map_output = []
        records_processed = 0
        records_emitted = 0
        
        start_time = time.time()
        
        for key, value in input_data:
            records_processed += 1
            
            # Apply mapper
            for intermediate_key, intermediate_value in self.mapper.map(key, value):
                self.map_output.append((intermediate_key, intermediate_value))
                records_emitted += 1
        
        elapsed_time = time.time() - start_time
        logger.info(f"[{self.worker_id}] Map phase completed in {elapsed_time:.2f}s: "
                   f"{records_processed} -> {records_emitted} records")
        
        return {
            'records_processed': records_processed,
            'records_emitted': records_emitted,
            'elapsed_time': elapsed_time
        }
    
    def shuffle_data(self) -> Dict[str, int]:
        """
        Shuffle map output to appropriate workers based on partitioning.
        
        This implements direct worker-to-worker communication for efficient
        data redistribution without going through the coordinator.
        
        Returns:
            Statistics about data sent to each worker
        """
        logger.info(f"[{self.worker_id}] Starting shuffle phase with {len(self.map_output)} records")
        
        # Partition data by destination worker
        partitions: Dict[str, List[Tuple[Any, Any]]] = defaultdict(list)
        num_workers = len(self.workers)
        
        for key, value in self.map_output:
            partition_idx = self.partitioner.get_partition(key, num_workers)
            target_worker_id = list(self.workers.keys())[partition_idx]
            partitions[target_worker_id].append((key, value))
        
        # Send data directly to each worker
        stats = {}
        for target_worker_id, data in partitions.items():
            if target_worker_id == self.worker_id:
                # Keep local data
                for key, value in data:
                    self.reduce_input[key].append(value)
                stats[target_worker_id] = len(data)
                logger.info(f"[{self.worker_id}] Kept {len(data)} records locally")
            else:
                # Send to remote worker
                worker_info = self.workers[target_worker_id]
                url = f"http://{worker_info['host']}:{worker_info['port']}/shuffle"
                
                try:
                    import requests
                    response = requests.post(url, json={
                        'source_worker': self.worker_id,
                        'data': data
                    }, timeout=30)
                    
                    if response.status_code == 200:
                        stats[target_worker_id] = len(data)
                        logger.info(f"[{self.worker_id}] Sent {len(data)} records to {target_worker_id}")
                    else:
                        logger.error(f"[{self.worker_id}] Failed to send data to {target_worker_id}: {response.text}")
                        
                except Exception as e:
                    logger.error(f"[{self.worker_id}] Error sending data to {target_worker_id}: {e}")
        
        return stats
    
    def _execute_reduce_phase(self) -> Dict[str, Any]:
        """
        Execute the reduce phase on shuffled data.
        
        Returns:
            Statistics and output from the reduce phase
        """
        self.reduce_output = []
        keys_processed = 0
        records_emitted = 0
        
        start_time = time.time()
        
        for key, values in self.reduce_input.items():
            keys_processed += 1
            
            # Apply reducer
            for output_key, output_value in self.reducer.reduce(key, values):
                self.reduce_output.append((output_key, output_value))
                records_emitted += 1
        
        elapsed_time = time.time() - start_time
        logger.info(f"[{self.worker_id}] Reduce phase completed in {elapsed_time:.2f}s: "
                   f"{keys_processed} keys -> {records_emitted} records")
        
        return {
            'keys_processed': keys_processed,
            'records_emitted': records_emitted,
            'elapsed_time': elapsed_time,
            'output': self.reduce_output
        }
    
    def set_mapper(self, mapper: Mapper):
        """Set the mapper for this worker."""
        self.mapper = mapper
        logger.info(f"[{self.worker_id}] Mapper set: {mapper.__class__.__name__}")
    
    def set_reducer(self, reducer: Reducer):
        """Set the reducer for this worker."""
        self.reducer = reducer
        logger.info(f"[{self.worker_id}] Reducer set: {reducer.__class__.__name__}")
    
    def set_partitioner(self, partitioner: Partitioner):
        """Set the partitioner for this worker."""
        self.partitioner = partitioner
        logger.info(f"[{self.worker_id}] Partitioner set: {partitioner.__class__.__name__}")
    
    def start(self):
        """Start the worker server."""
        logger.info(f"[{self.worker_id}] Starting worker server on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, threaded=True)
