#!/usr/bin/env python3
"""
Test script to verify the map-reduce system is working correctly.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_mapper():
    """Test the mapper implementation."""
    print("Testing Mapper...")
    
    from src.examples.log_analysis import LogAnalysisMapper
    
    mapper = LogAnalysisMapper()
    test_log = "2024-11-17 10:23:45, 192.168.1.100, GET, /api/users, 200, 145"
    
    results = list(mapper.map(1, test_log))
    
    assert len(results) == 1, "Mapper should emit one record"
    key, value = results[0]
    assert key == "/api/users", f"Expected key '/api/users', got '{key}'"
    assert value['request_count'] == 1, "Request count should be 1"
    assert 145 in value['response_times'], "Response time should be in list"
    
    print("  ✓ Mapper test passed")
    return True


def test_reducer():
    """Test the reducer implementation."""
    print("Testing Reducer...")
    
    from src.examples.log_analysis import LogAnalysisReducer
    
    reducer = LogAnalysisReducer()
    
    # Simulate shuffled data
    test_values = [
        {'request_count': 1, 'response_times': [150], 'error_count': 0, 'success_count': 1, 
         'hours': [10], 'methods': {'GET': 1}, 'status_codes': {'200': 1}},
        {'request_count': 1, 'response_times': [200], 'error_count': 1, 'success_count': 0,
         'hours': [11], 'methods': {'POST': 1}, 'status_codes': {'500': 1}},
        {'request_count': 1, 'response_times': [120], 'error_count': 0, 'success_count': 1,
         'hours': [10], 'methods': {'GET': 1}, 'status_codes': {'200': 1}}
    ]
    
    results = list(reducer.reduce("/api/test", test_values))
    
    assert len(results) == 1, "Reducer should emit one record per key"
    key, value = results[0]
    assert key == "/api/test", f"Expected key '/api/test', got '{key}'"
    assert value['total_requests'] == 3, "Total requests should be 3"
    # Use round() to handle floating-point precision
    expected_avg = round((150 + 200 + 120) / 3, 2)
    assert value['response_time_avg_ms'] == expected_avg, f"Average should be {expected_avg}, got {value['response_time_avg_ms']}"
    assert value['error_count'] == 1, "Error count should be 1"
    assert value['success_count'] == 2, "Success count should be 2"
    
    print("  ✓ Reducer test passed")
    return True


def test_partitioner():
    """Test the hash partitioner."""
    print("Testing Partitioner...")
    
    from src.core.base import HashPartitioner
    
    partitioner = HashPartitioner()
    
    # Test that same keys always go to same partition
    key = "/api/users"
    partition1 = partitioner.get_partition(key, 4)
    partition2 = partitioner.get_partition(key, 4)
    
    assert partition1 == partition2, "Same key should always map to same partition"
    assert 0 <= partition1 < 4, "Partition should be in valid range"
    
    # Test distribution
    keys = [f"/api/endpoint{i}" for i in range(100)]
    partitions = [partitioner.get_partition(k, 4) for k in keys]
    
    # Check that all partitions are used
    unique_partitions = set(partitions)
    assert len(unique_partitions) > 1, "Multiple partitions should be used"
    
    # Check reasonable distribution (not perfect, but should be somewhat balanced)
    for i in range(4):
        count = partitions.count(i)
        assert count > 0, f"Partition {i} should receive some keys"
    
    print("  ✓ Partitioner test passed")
    return True


def test_data_generation():
    """Test sample data generation."""
    print("Testing Data Generation...")
    
    from src.examples.log_analysis import generate_sample_logs
    from src.examples.sales_analysis import generate_sample_sales
    
    # Test log generation
    logs = generate_sample_logs(100)
    assert len(logs) == 100, "Should generate 100 log records"
    assert all(len(log) == 2 for log in logs), "Each record should be (key, value) tuple"
    
    # Test sales generation
    sales = generate_sample_sales(50)
    assert len(sales) == 50, "Should generate 50 sales records"
    assert all(len(sale) == 2 for sale in sales), "Each record should be (key, value) tuple"
    
    print("  ✓ Data generation test passed")
    return True


def test_worker_initialization():
    """Test that workers can be initialized."""
    print("Testing Worker Initialization...")
    
    from src.core.worker import Worker
    from src.examples.log_analysis import LogAnalysisMapper, LogAnalysisReducer
    
    worker = Worker(
        worker_id="test-worker",
        host="localhost",
        port=9999,
        data_dir="./test_data"
    )
    
    assert worker.worker_id == "test-worker", "Worker ID should be set correctly"
    assert worker.host == "localhost", "Host should be set correctly"
    assert worker.port == 9999, "Port should be set correctly"
    
    # Test setting mapper and reducer
    mapper = LogAnalysisMapper()
    reducer = LogAnalysisReducer()
    
    worker.set_mapper(mapper)
    worker.set_reducer(reducer)
    
    assert worker.mapper is not None, "Mapper should be set"
    assert worker.reducer is not None, "Reducer should be set"
    
    print("  ✓ Worker initialization test passed")
    
    # Cleanup
    import shutil
    if Path("./test_data").exists():
        shutil.rmtree("./test_data")
    
    return True


def test_coordinator_initialization():
    """Test that coordinator can be initialized."""
    print("Testing Coordinator Initialization...")
    
    from src.core.coordinator import Coordinator
    
    coordinator = Coordinator(host="localhost", port=5000)
    
    assert coordinator.host == "localhost", "Host should be set correctly"
    assert coordinator.port == 5000, "Port should be set correctly"
    assert len(coordinator.workers) == 0, "Should start with no workers"
    
    # Test worker registration
    coordinator.register_worker(
        worker_id="worker-1",
        host="localhost",
        port=5001,
        data_dir="./data/worker1"
    )
    
    assert len(coordinator.workers) == 1, "Should have 1 registered worker"
    assert "worker-1" in coordinator.workers, "Worker should be registered"
    
    print("  ✓ Coordinator initialization test passed")
    return True


def run_all_tests():
    """Run all unit tests."""
    print("="*80)
    print("  Map-Reduce System Unit Tests")
    print("="*80)
    print()
    
    tests = [
        ("Mapper", test_mapper),
        ("Reducer", test_reducer),
        ("Partitioner", test_partitioner),
        ("Data Generation", test_data_generation),
        ("Worker Initialization", test_worker_initialization),
        ("Coordinator Initialization", test_coordinator_initialization)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"  ✗ {test_name} test FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()
    
    print("="*80)
    print(f"  Test Results: {passed} passed, {failed} failed")
    print("="*80)
    print()
    
    if failed == 0:
        print("✓ All tests passed! System is ready to use.")
        return True
    else:
        print("✗ Some tests failed. Please review errors above.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
