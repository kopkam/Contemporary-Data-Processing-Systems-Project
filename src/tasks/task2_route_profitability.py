"""
Task 2: Route Profitability Analysis
Author: Ludwik Janowski

This task analyzes the profitability of different taxi routes by calculating
revenue per mile for each pickup-dropoff zone pair.

Business value: Identify the most profitable routes to help drivers maximize
their earnings per unit of distance traveled.
"""

from typing import Any, Iterator, Tuple, List
from ..core.base import Mapper, Reducer


class RouteProfitabilityMapper(Mapper):
    """
    Map: Extract route and calculate revenue per mile.
    
    Input: (trip_id, trip_record_dict)
    Output: ((pickup_zone, dropoff_zone), revenue_per_mile)
    """
    
    def map(self, key: Any, value: Any) -> Iterator[Tuple[Any, Any]]:
        """
        Calculate revenue per mile for each route.
        
        Args:
            key: Trip identifier (row index)
            value: Dictionary containing trip data with fields:
                - PULocationID: Pickup zone
                - DOLocationID: Dropoff zone
                - trip_distance: Distance in miles
                - total_amount: Total fare including tips and tolls
                
        Yields:
            ((pickup_zone, dropoff_zone), revenue_per_mile)
        """
        try:
            pickup_zone = value.get('PULocationID')
            dropoff_zone = value.get('DOLocationID')
            distance = float(value.get('trip_distance', 0))
            revenue = float(value.get('total_amount', 0))
            
            # Only process trips with positive distance and revenue
            if (pickup_zone is not None and 
                dropoff_zone is not None and 
                distance > 0 and 
                revenue > 0):
                
                revenue_per_mile = revenue / distance
                # Use string key for JSON serialization (instead of tuple)
                route = f"{pickup_zone}->{dropoff_zone}"
                yield (route, revenue_per_mile)
                
        except (ValueError, TypeError, KeyError):
            # Skip invalid records
            pass


class RouteProfitabilityReducer(Reducer):
    """
    Reduce: Calculate average revenue per mile for each route.
    
    Input: (route_string, [revenue_per_mile1, ...])
    Output: (route_string, avg_revenue_per_mile)
    """
    
    def reduce(self, key: Any, values: List[Any]) -> Iterator[Tuple[Any, Any]]:
        """
        Compute average revenue per mile for a route.
        
        Args:
            key: Route string "pickup_zone->dropoff_zone"
            values: List of revenue_per_mile values for this route
            
        Yields:
            (route_string, average_revenue_per_mile)
        """
        if values:
            avg_revenue_per_mile = sum(values) / len(values)
            yield (key, round(avg_revenue_per_mile, 2))
