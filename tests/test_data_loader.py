"""
Tests for data loading utilities.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.parquet_loader import create_sample_data


class TestDataLoader:
    """Tests for data loading functions."""
    
    def test_create_sample_data_count(self):
        """Test that correct number of records is generated."""
        data = create_sample_data(num_records=100)
        
        assert len(data) == 100
    
    def test_sample_data_structure(self):
        """Test structure of generated sample data."""
        data = create_sample_data(num_records=10)
        
        # Check that each record is a tuple (index, dict)
        for idx, record in data:
            assert isinstance(idx, int)
            assert isinstance(record, dict)
    
    def test_sample_data_fields(self):
        """Test that required fields are present in sample data."""
        data = create_sample_data(num_records=5)
        
        required_fields = [
            'VendorID',
            'tpep_pickup_datetime',
            'PULocationID',
            'DOLocationID',
            'trip_distance',
            'fare_amount',
            'tip_amount',
            'total_amount'
        ]
        
        for _, record in data:
            for field in required_fields:
                assert field in record
    
    def test_sample_data_valid_zones(self):
        """Test that zone IDs are in valid range."""
        data = create_sample_data(num_records=50)
        
        for _, record in data:
            assert 1 <= record['PULocationID'] <= 263
            assert 1 <= record['DOLocationID'] <= 263
    
    def test_sample_data_positive_values(self):
        """Test that financial values are positive."""
        data = create_sample_data(num_records=50)
        
        for _, record in data:
            assert record['trip_distance'] > 0
            assert record['fare_amount'] > 0
            assert record['tip_amount'] >= 0
            assert record['total_amount'] > 0
