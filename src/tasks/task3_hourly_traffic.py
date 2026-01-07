"""
Task 3: Hourly Traffic Distribution Analysis
Author: Marcin Kopka

This task analyzes temporal patterns in taxi usage by counting trips
for each hour of the day (0-23).

Business value: Identify peak hours to optimize driver scheduling and
understand demand patterns throughout the day.
"""

from typing import Any, Iterator, Tuple, List
from datetime import datetime
from ..core.base import Mapper, Reducer


class HourlyTrafficMapper(Mapper):
    """
    Map: Extract hour of day from pickup time and count trips.
    
    Input: (trip_id, trip_record_dict)
    Output: (hour_of_day, 1)
    """
    
    def map(self, key: Any, value: Any) -> Iterator[Tuple[Any, Any]]:
        """
        Extract hour of day from each trip.
        
        Args:
            key: Trip identifier (row index)
            value: Dictionary containing trip data with fields:
                - tpep_pickup_datetime: Pickup timestamp (string or datetime)
                
        Yields:
            (hour_of_day, 1) for counting
        """
        try:
            pickup_time = value.get('tpep_pickup_datetime')
            
            if pickup_time is None:
                return
            
            # Handle both string and datetime objects
            if isinstance(pickup_time, str):
                # Try common datetime formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                    try:
                        dt = datetime.strptime(pickup_time, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    # If no format matched, try ISO format
                    dt = datetime.fromisoformat(pickup_time.replace('Z', '+00:00'))
            else:
                dt = pickup_time
            
            hour = dt.hour
            yield (hour, 1)
            
        except (ValueError, TypeError, KeyError, AttributeError):
            # Skip invalid records
            pass


class HourlyTrafficReducer(Reducer):
    """
    Reduce: Sum trip counts for each hour.
    
    Input: (hour_of_day, [1, 1, 1, ...])
    Output: (hour_of_day, total_trip_count)
    """
    
    def reduce(self, key: Any, values: List[Any]) -> Iterator[Tuple[Any, Any]]:
        """
        Count total trips for each hour.
        
        Args:
            key: Hour of day (0-23)
            values: List of 1's (one per trip)
            
        Yields:
            (hour_of_day, total_trips)
        """
        total_trips = sum(values)
        yield (key, total_trips)
