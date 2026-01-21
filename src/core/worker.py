"""
Worker node implementation for distributed map-reduce.
"""

import os
import pickle
import logging
import time
from flask import Flask, request, jsonify
from typing import Any, Dict, List
import requests

from .base import Mapper, Reducer, Partitioner, HashPartitioner


logger = logging.getLogger(__name__)


class Worker:
    """
    Worker node that executes map and reduce tasks.
    
    Each worker runs a Flask server to receive tasks from the coordinator
    and communicate with other workers during the shuffle phase.
    """
    
    def __init__(self, worker_id: str, host: str, port: int):
        """
        Initialize a worker node.
        
        Args:
            worker_id: Unique identifier for this worker
            host: Host address to bind to
            port: Port number to listen on
        """
        self.worker_id = worker_id
        self.host = host
        self.port = port
        
        # Flask app for HTTP endpoints
        self.app = Flask(__name__)
        self._register_routes()
        
        # Storage for intermediate and final results
        self.intermediate_data: Dict[Any, List[Any]] = {}
        self.final_results: List[tuple] = []
        
        logger.info(f"Worker {worker_id} initialized at {host}:{port}")
    
    def _register_routes(self):
        """Register Flask routes for worker endpoints."""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'worker_id': self.worker_id
            })
        
        @self.app.route('/execute_map', methods=['POST'])
        def execute_map():
            """Execute map task on assigned data."""
            try:
                map_start_time = time.time()
                
                data = request.json
                mapper_class = pickle.loads(bytes.fromhex(data['mapper']))
                partitioner_class = pickle.loads(bytes.fromhex(data['partitioner']))
                input_data = data['input_data']
                worker_addresses = data['worker_addresses']
                
                logger.info(f"[Worker {self.worker_id}] MAP: Processing {len(input_data):,} records...")
                
                # Instantiate mapper and partitioner
                mapper = mapper_class()
                partitioner = partitioner_class()
                
                # Clear previous intermediate data
                self.intermediate_data.clear()
                
                # Execute map phase
                partitioned_data = {i: [] for i in range(len(worker_addresses))}
                total_intermediate = 0
                
                for key, value in input_data:
                    for emitted_key, emitted_value in mapper.map(key, value):
                        partition = partitioner.get_partition(emitted_key, len(worker_addresses))
                        partitioned_data[partition].append((emitted_key, emitted_value))
                        total_intermediate += 1
                
                map_time = time.time() - map_start_time
                logger.info(f"[Worker {self.worker_id}] MAP: Generated {total_intermediate:,} intermediate pairs in {map_time:.2f}s")
                
                # Send partitioned data to appropriate workers (shuffle)
                logger.info(f"[Worker {self.worker_id}] SHUFFLE: Sending to {len(worker_addresses)} workers...")
                shuffle_start_time = time.time()
                
                for partition_id, partition_data in partitioned_data.items():
                    target_worker = worker_addresses[partition_id]
                    
                    if len(partition_data) > 0:
                        logger.info(f"[Worker {self.worker_id}] SHUFFLE: → Worker {partition_id+1}: {len(partition_data):,} pairs")
                    
                    try:
                        response = requests.post(
                            f"{target_worker}/shuffle",
                            json={'data': partition_data},
                            timeout=30
                        )
                        response.raise_for_status()
                    except Exception as e:
                        logger.error(f"Failed to send data to {target_worker}: {e}")
                        raise
                
                shuffle_time = time.time() - shuffle_start_time
                total_time = time.time() - map_start_time
                logger.info(f"[Worker {self.worker_id}] SHUFFLE: Completed in {shuffle_time:.2f}s")
                logger.info(f"[Worker {self.worker_id}] MAP+SHUFFLE: Total time {total_time:.2f}s")
                
                return jsonify({
                    'status': 'success',
                    'worker_id': self.worker_id,
                    'intermediate_count': total_intermediate,
                    'map_time': total_time
                })
                
            except Exception as e:
                logger.error(f"Map execution failed: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/shuffle', methods=['POST'])
        def shuffle():
            """Receive shuffled data from other workers."""
            try:
                data = request.json['data']
                
                # Group data by key
                for key, value in data:
                    if key not in self.intermediate_data:
                        self.intermediate_data[key] = []
                    self.intermediate_data[key].append(value)
                
                return jsonify({'status': 'success'})
                
            except Exception as e:
                logger.error(f"Shuffle failed: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/execute_reduce', methods=['POST'])
        def execute_reduce():
            """Execute reduce task on intermediate data."""
            try:
                reduce_start_time = time.time()
                
                data = request.json
                reducer_class = pickle.loads(bytes.fromhex(data['reducer']))
                
                # Count total intermediate pairs
                total_pairs = sum(len(values) for values in self.intermediate_data.values())
                unique_keys = len(self.intermediate_data)
                
                logger.info(f"[Worker {self.worker_id}] REDUCE: Processing {total_pairs:,} pairs across {unique_keys} unique keys")
                
                # Instantiate reducer
                reducer = reducer_class()
                
                # Clear previous results
                self.final_results.clear()
                
                # Execute reduce phase
                for key, values in self.intermediate_data.items():
                    for result_key, result_value in reducer.reduce(key, values):
                        self.final_results.append((result_key, result_value))
                
                reduce_time = time.time() - reduce_start_time
                logger.info(f"[Worker {self.worker_id}] REDUCE: Output {len(self.final_results)} results in {reduce_time:.2f}s")
                
                return jsonify({
                    'status': 'success',
                    'worker_id': self.worker_id,
                    'input_pairs': total_pairs,
                    'output_count': len(self.final_results),
                    'reduce_time': reduce_time
                })
                
            except Exception as e:
                logger.error(f"Reduce execution failed: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
        
        @self.app.route('/get_results', methods=['GET'])
        def get_results():
            """Return final results to coordinator."""
            return jsonify({
                'results': self.final_results,
                'worker_id': self.worker_id
            })
        
        @self.app.route('/reset', methods=['POST'])
        def reset():
            """Reset worker state."""
            self.intermediate_data.clear()
            self.final_results.clear()
            return jsonify({'status': 'success'})
    
    def start(self):
        """Start the worker Flask server."""
        logger.info(f"Starting worker {self.worker_id} on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=False)


def start_worker(worker_id: str, host: str, port: int):
    """
    Helper function to start a worker node.
    
    Args:
        worker_id: Unique worker identifier
        host: Host address
        port: Port number
    """
    worker = Worker(worker_id, host, port)
    worker.start()
