"""
Worker node implementation for distributed map-reduce.
"""

import os
import pickle
import logging
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
    
    def __init__(self, worker_id: str, host: str, port: int, data_dir: str = None):
        """
        Initialize a worker node.
        
        Args:
            worker_id: Unique identifier for this worker
            host: Host address to bind to
            port: Port number to listen on
            data_dir: Directory for temporary data storage
        """
        self.worker_id = worker_id
        self.host = host
        self.port = port
        self.data_dir = data_dir or f"./data/{worker_id}"
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
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
                data = request.json
                mapper_class = pickle.loads(bytes.fromhex(data['mapper']))
                partitioner_class = pickle.loads(bytes.fromhex(data['partitioner']))
                input_data = data['input_data']
                worker_addresses = data['worker_addresses']
                
                # Instantiate mapper and partitioner
                mapper = mapper_class()
                partitioner = partitioner_class()
                
                # Clear previous intermediate data
                self.intermediate_data.clear()
                
                # Execute map phase
                partitioned_data = {i: [] for i in range(len(worker_addresses))}
                
                for key, value in input_data:
                    for emitted_key, emitted_value in mapper.map(key, value):
                        partition = partitioner.get_partition(emitted_key, len(worker_addresses))
                        partitioned_data[partition].append((emitted_key, emitted_value))
                
                # Send partitioned data to appropriate workers (shuffle)
                for partition_id, partition_data in partitioned_data.items():
                    target_worker = worker_addresses[partition_id]
                    
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
                
                return jsonify({'status': 'success', 'worker_id': self.worker_id})
                
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
                data = request.json
                reducer_class = pickle.loads(bytes.fromhex(data['reducer']))
                
                # Instantiate reducer
                reducer = reducer_class()
                
                # Clear previous results
                self.final_results.clear()
                
                # Execute reduce phase
                for key, values in self.intermediate_data.items():
                    for result_key, result_value in reducer.reduce(key, values):
                        self.final_results.append((result_key, result_value))
                
                return jsonify({'status': 'success', 'worker_id': self.worker_id})
                
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


def start_worker(worker_id: str, host: str, port: int, data_dir: str = None):
    """
    Helper function to start a worker node.
    
    Args:
        worker_id: Unique worker identifier
        host: Host address
        port: Port number
        data_dir: Data directory path
    """
    worker = Worker(worker_id, host, port, data_dir)
    worker.start()
