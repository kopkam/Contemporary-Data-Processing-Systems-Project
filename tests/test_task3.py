"""
Tests for Task 3: Hourly Traffic
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tasks.task3_hourly_traffic import HourlyTrafficMapper, HourlyTrafficReducer


class TestHourlyTrafficMapper:
    """Tests for HourlyTrafficMapper."""
    
    def test_morning_pickup(self):
        """Test extraction of morning hour."""
        mapper = HourlyTrafficMapper()
        
        record = {
            'tpep_pickup_datetime': '2024-01-15 08:30:00'
        }
        
        result = list(mapper.map(0, record))
        
        assert len(result) == 1
        assert result[0][0] == 8  # Hour
        assert result[0][1] == 1  # Count
    
    def test_evening_pickup(self):
        """Test extraction of evening hour."""
        mapper = HourlyTrafficMapper()
        
        record = {
            'tpep_pickup_datetime': '2024-01-15 19:45:00'
        }
        
        result = list(mapper.map(0, record))
        
        assert result[0][0] == 19  # 7 PM
    
    def test_midnight_pickup(self):
        """Test midnight hour (0)."""
        mapper = HourlyTrafficMapper()
        
        record = {
            'tpep_pickup_datetime': '2024-01-15 00:15:00'
        }
        
        result = list(mapper.map(0, record))
        
        assert result[0][0] == 0
    
    def test_datetime_object(self):
        """Test with datetime object instead of string."""
        mapper = HourlyTrafficMapper()
        
        record = {
            'tpep_pickup_datetime': datetime(2024, 1, 15, 14, 30, 0)
        }
        
        result = list(mapper.map(0, record))
        
        assert result[0][0] == 14
    
    def test_missing_datetime(self):
        """Test with missing pickup time."""
        mapper = HourlyTrafficMapper()
        
        record = {}
        
        result = list(mapper.map(0, record))
        
        assert len(result) == 0


class TestHourlyTrafficReducer:
    """Tests for HourlyTrafficReducer."""
    
    def test_sum_trips(self):
        """Test trip counting for an hour."""
        reducer = HourlyTrafficReducer()
        
        hour = 18
        values = [1, 1, 1, 1, 1]  # 5 trips
        
        result = list(reducer.reduce(hour, values))
        
        assert len(result) == 1
        assert result[0][0] == 18
        assert result[0][1] == 5
    
    def test_large_count(self):
        """Test with many trips."""
        reducer = HourlyTrafficReducer()
        
        hour = 17
        values = [1] * 10000  # 10,000 trips
        
        result = list(reducer.reduce(hour, values))
        
        assert result[0][1] == 10000
    
    def test_single_trip(self):
        """Test with single trip."""
        reducer = HourlyTrafficReducer()
        
        result = list(reducer.reduce(3, [1]))
        
        assert result[0][1] == 1
