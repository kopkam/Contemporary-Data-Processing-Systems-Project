"""
NYC Taxi Parquet data loader.

Loads NYC Taxi trip data from Parquet files using PyArrow.
"""

import logging
from typing import List, Tuple, Optional
import pandas as pd
import pyarrow.parquet as pq


logger = logging.getLogger(__name__)


def load_nyc_taxi_data(
    file_path: str,
    max_records: Optional[int] = None,
    columns: Optional[List[str]] = None
) -> List[Tuple[int, dict]]:
    """
    Load NYC Taxi data from a Parquet file.
    
    Args:
        file_path: Path to the Parquet file
        max_records: Maximum number of records to load (None = all)
        columns: List of column names to load (None = all)
        
    Returns:
        List of (row_index, record_dict) tuples suitable for map-reduce input
        
    Example:
        >>> data = load_nyc_taxi_data('taxi_data.parquet', max_records=1000)
        >>> print(len(data))
        1000
        >>> print(data[0])
        (0, {'VendorID': 1, 'tpep_pickup_datetime': '2023-01-01 00:15:00', ...})
    """
    logger.info(f"Loading NYC Taxi data from {file_path}")
    
    try:
        # Read Parquet file using PyArrow for efficiency
        if columns:
            df = pq.read_table(file_path, columns=columns).to_pandas()
        else:
            df = pd.read_parquet(file_path)
        
        # Limit records if specified
        if max_records:
            df = df.head(max_records)
        
        logger.info(f"Loaded {len(df)} records from Parquet file")
        logger.info(f"Columns: {list(df.columns)}")
        
        # Convert to list of (index, dict) tuples
        # Convert all values to native Python types for JSON serialization
        data = []
        for idx, row in df.iterrows():
            record = {}
            for col, val in row.items():
                # Convert pandas Timestamp to string
                if pd.api.types.is_datetime64_any_dtype(type(val)) or hasattr(val, 'isoformat'):
                    record[col] = str(val) if pd.notna(val) else None
                # Convert pandas NA/NaT to None
                elif pd.isna(val):
                    record[col] = None
                # Convert numpy types to Python types
                elif hasattr(val, 'item'):
                    record[col] = val.item()
                else:
                    record[col] = val
            data.append((idx, record))
        
        return data
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Failed to load Parquet file: {e}")
        raise


def create_sample_data(num_records: int = 100) -> List[Tuple[int, dict]]:
    """
    Create sample NYC Taxi data for testing without a real Parquet file.
    
    Args:
        num_records: Number of sample records to generate
        
    Returns:
        List of (row_index, record_dict) tuples
    """
    import random
    from datetime import datetime, timedelta
    
    logger.info(f"Creating {num_records} sample taxi records")
    
    data = []
    base_time = datetime(2024, 1, 1, 0, 0, 0)
    
    for i in range(num_records):
        # Random pickup time within 24 hours
        pickup_time = base_time + timedelta(hours=random.randint(0, 23), 
                                           minutes=random.randint(0, 59))
        
        # Random zones (1-263 in NYC)
        pickup_zone = random.randint(1, 263)
        dropoff_zone = random.randint(1, 263)
        
        # Random trip metrics
        distance = round(random.uniform(0.5, 20.0), 2)
        fare = round(distance * random.uniform(2.5, 4.0), 2)
        tip = round(fare * random.uniform(0.0, 0.25), 2)
        total = round(fare + tip + random.uniform(0, 5), 2)
        
        record = {
            'VendorID': random.randint(1, 2),
            'tpep_pickup_datetime': pickup_time.strftime('%Y-%m-%d %H:%M:%S'),
            'tpep_dropoff_datetime': (pickup_time + timedelta(minutes=int(distance * 3))).strftime('%Y-%m-%d %H:%M:%S'),
            'PULocationID': pickup_zone,
            'DOLocationID': dropoff_zone,
            'trip_distance': distance,
            'fare_amount': fare,
            'tip_amount': tip,
            'total_amount': total,
            'passenger_count': random.randint(1, 4)
        }
        
        data.append((i, record))
    
    return data
