"""
Tests for core map-reduce components.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.base import HashPartitioner


class TestHashPartitioner:
    """Tests for HashPartitioner."""
    
    def test_partition_distribution(self):
        """Test that partitioner distributes keys across workers."""
        partitioner = HashPartitioner()
        
        keys = [f"zone_{i}" for i in range(100)]
        num_workers = 4
        
        partitions = [partitioner.get_partition(k, num_workers) for k in keys]
        
        # All partitions should be valid
        assert all(0 <= p < num_workers for p in partitions)
        
        # Should have some distribution (not all to one partition)
        unique_partitions = set(partitions)
        assert len(unique_partitions) > 1
    
    def test_deterministic(self):
        """Test that same key always goes to same partition."""
        partitioner = HashPartitioner()
        
        key = "zone_142"
        num_workers = 4
        
        partition1 = partitioner.get_partition(key, num_workers)
        partition2 = partitioner.get_partition(key, num_workers)
        
        assert partition1 == partition2
    
    def test_different_worker_counts(self):
        """Test with different numbers of workers."""
        partitioner = HashPartitioner()
        
        key = "zone_87"
        
        for num_workers in [2, 4, 8, 16]:
            partition = partitioner.get_partition(key, num_workers)
            assert 0 <= partition < num_workers
