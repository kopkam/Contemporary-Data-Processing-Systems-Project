"""
Tests for Task 1: Tip Analysis
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tasks.task1_tip_analysis import TipPercentageMapper, TipPercentageReducer


class TestTipPercentageMapper:
    """Tests for TipPercentageMapper."""
    
    def test_valid_trip(self):
        """Test mapping a valid trip record."""
        mapper = TipPercentageMapper()
        
        record = {
            'PULocationID': 142,
            'fare_amount': 10.0,
            'tip_amount': 2.0
        }
        
        result = list(mapper.map(0, record))
        
        assert len(result) == 1
        assert result[0][0] == 142  # Zone ID
        assert result[0][1] == 20.0  # 20% tip
    
    def test_zero_tip(self):
        """Test trip with no tip."""
        mapper = TipPercentageMapper()
        
        record = {
            'PULocationID': 87,
            'fare_amount': 15.0,
            'tip_amount': 0.0
        }
        
        result = list(mapper.map(0, record))
        
        assert len(result) == 1
        assert result[0][1] == 0.0
    
    def test_invalid_zero_fare(self):
        """Test trip with zero fare (should be skipped)."""
        mapper = TipPercentageMapper()
        
        record = {
            'PULocationID': 142,
            'fare_amount': 0.0,
            'tip_amount': 2.0
        }
        
        result = list(mapper.map(0, record))
        
        assert len(result) == 0  # Should skip invalid record
    
    def test_missing_fields(self):
        """Test trip with missing fields."""
        mapper = TipPercentageMapper()
        
        record = {
            'PULocationID': 142
            # Missing fare_amount and tip_amount
        }
        
        result = list(mapper.map(0, record))
        
        assert len(result) == 0  # Should skip


class TestTipPercentageReducer:
    """Tests for TipPercentageReducer."""
    
    def test_average_calculation(self):
        """Test average tip percentage calculation."""
        reducer = TipPercentageReducer()
        
        values = [20.0, 15.0, 25.0, 18.0]
        
        result = list(reducer.reduce(142, values))
        
        assert len(result) == 1
        assert result[0][0] == 142
        assert result[0][1] == 19.5  # (20+15+25+18)/4
    
    def test_single_value(self):
        """Test with single tip value."""
        reducer = TipPercentageReducer()
        
        result = list(reducer.reduce(87, [22.5]))
        
        assert len(result) == 1
        assert result[0][1] == 22.5
    
    def test_empty_values(self):
        """Test with empty values list."""
        reducer = TipPercentageReducer()
        
        result = list(reducer.reduce(142, []))
        
        assert len(result) == 0  # Should produce no output
