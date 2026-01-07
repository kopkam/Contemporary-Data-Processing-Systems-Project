"""
Tests for Task 2: Route Profitability
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tasks.task2_route_profitability import RouteProfitabilityMapper, RouteProfitabilityReducer


class TestRouteProfitabilityMapper:
    """Tests for RouteProfitabilityMapper."""
    
    def test_valid_route(self):
        """Test mapping a valid trip."""
        mapper = RouteProfitabilityMapper()
        
        record = {
            'PULocationID': 230,
            'DOLocationID': 234,
            'trip_distance': 5.0,
            'total_amount': 25.0
        }
        
        result = list(mapper.map(0, record))
        
        assert len(result) == 1
        assert result[0][0] == (230, 234)  # Route tuple
        assert result[0][1] == 5.0  # $25 / 5 miles = $5/mile
    
    def test_high_revenue_per_mile(self):
        """Test route with high revenue per mile."""
        mapper = RouteProfitabilityMapper()
        
        record = {
            'PULocationID': 161,
            'DOLocationID': 234,
            'trip_distance': 2.0,
            'total_amount': 100.0
        }
        
        result = list(mapper.map(0, record))
        
        assert result[0][1] == 50.0  # $100 / 2 miles
    
    def test_zero_distance(self):
        """Test trip with zero distance (should be skipped)."""
        mapper = RouteProfitabilityMapper()
        
        record = {
            'PULocationID': 142,
            'DOLocationID': 87,
            'trip_distance': 0.0,
            'total_amount': 10.0
        }
        
        result = list(mapper.map(0, record))
        
        assert len(result) == 0
    
    def test_missing_zone(self):
        """Test trip with missing zone information."""
        mapper = RouteProfitabilityMapper()
        
        record = {
            'PULocationID': None,
            'DOLocationID': 234,
            'trip_distance': 5.0,
            'total_amount': 25.0
        }
        
        result = list(mapper.map(0, record))
        
        assert len(result) == 0


class TestRouteProfitabilityReducer:
    """Tests for RouteProfitabilityReducer."""
    
    def test_average_revenue_per_mile(self):
        """Test average calculation for route."""
        reducer = RouteProfitabilityReducer()
        
        route = (230, 234)
        values = [5.0, 6.0, 4.0, 5.0]
        
        result = list(reducer.reduce(route, values))
        
        assert len(result) == 1
        assert result[0][0] == route
        assert result[0][1] == 5.0  # (5+6+4+5)/4
    
    def test_route_tuple_preserved(self):
        """Test that route tuple is preserved correctly."""
        reducer = RouteProfitabilityReducer()
        
        route = (161, 234)
        result = list(reducer.reduce(route, [45.5]))
        
        assert result[0][0] == (161, 234)
        assert result[0][1] == 45.5
