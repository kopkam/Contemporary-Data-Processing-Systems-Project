"""
Task 1: Average Tip Percentage by Pickup Zone
Author: Sergiusz Cudo

This task analyzes tipping behavior across different pickup zones in NYC.
It calculates the average tip percentage (tip_amount / fare_amount * 100)
for each pickup location zone.

Business value: Identify zones where passengers tip more generously,
which can help taxi drivers optimize their pickup strategies.
"""

from typing import Any, Iterator, Tuple, List
from ..core.base import Mapper, Reducer


class TipPercentageMapper(Mapper):
    """
    Map: Extract pickup zone and tip percentage from each trip.
    
    Input: (trip_id, trip_record_dict)
    Output: (pickup_zone, tip_percentage)
    """
    
    def map(self, key: Any, value: Any) -> Iterator[Tuple[Any, Any]]:
        """
        Extract tip percentage for each pickup zone.
        
        Args:
            key: Trip identifier (row index)
            value: Dictionary containing trip data with fields:
                - PULocationID: Pickup location zone
                - fare_amount: Base fare
                - tip_amount: Tip given by passenger
                
        Yields:
            (pickup_zone_id, tip_percentage)
        """
        try:
            pickup_zone = value.get('PULocationID')
            fare = float(value.get('fare_amount', 0))
            tip = float(value.get('tip_amount', 0))
            
            # Only process valid trips with positive fare
            if pickup_zone is not None and fare > 0:
                tip_percentage = (tip / fare) * 100.0
                yield (pickup_zone, tip_percentage)
                
        except (ValueError, TypeError, KeyError):
            # Skip invalid records
            pass


class TipPercentageReducer(Reducer):
    """
    Reduce: Calculate average tip percentage for each pickup zone.
    
    Input: (pickup_zone, [tip_percentage1, tip_percentage2, ...])
    Output: (pickup_zone, average_tip_percentage)
    """
    
    def reduce(self, key: Any, values: List[Any]) -> Iterator[Tuple[Any, Any]]:
        """
        Compute average tip percentage for a zone.
        
        Args:
            key: Pickup zone ID
            values: List of tip percentages for this zone
            
        Yields:
            (pickup_zone, average_tip_percentage)
        """
        if values:
            avg_tip_pct = sum(values) / len(values)
            yield (key, round(avg_tip_pct, 2))
