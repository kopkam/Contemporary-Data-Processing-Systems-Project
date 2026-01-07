"""
Base classes for map-reduce operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Iterator, Tuple, List


class Mapper(ABC):
    """
    Abstract base class for map operations.
    
    Mappers process input data and emit key-value pairs.
    """
    
    @abstractmethod
    def map(self, key: Any, value: Any) -> Iterator[Tuple[Any, Any]]:
        """
        Map function to process input and emit intermediate key-value pairs.
        
        Args:
            key: Input key (e.g., row index)
            value: Input value (e.g., taxi trip record as dict)
            
        Yields:
            Tuples of (intermediate_key, intermediate_value)
        """
        pass


class Reducer(ABC):
    """
    Abstract base class for reduce operations.
    
    Reducers aggregate values for each key after the shuffle phase.
    """
    
    @abstractmethod
    def reduce(self, key: Any, values: List[Any]) -> Iterator[Tuple[Any, Any]]:
        """
        Reduce function to aggregate values for a given key.
        
        Args:
            key: The key to reduce
            values: List of all values associated with this key
            
        Yields:
            Tuples of (output_key, output_value)
        """
        pass


class Partitioner(ABC):
    """
    Abstract base class for partitioning logic.
    
    Partitioners determine which worker receives which intermediate keys during shuffle.
    """
    
    @abstractmethod
    def get_partition(self, key: Any, num_partitions: int) -> int:
        """
        Determine the partition (worker) for a given key.
        
        Args:
            key: The key to partition
            num_partitions: Total number of partitions (workers)
            
        Returns:
            Partition index (0 to num_partitions-1)
        """
        pass


class HashPartitioner(Partitioner):
    """Default hash-based partitioner."""
    
    def get_partition(self, key: Any, num_partitions: int) -> int:
        """Use hash function to distribute keys across partitions."""
        return hash(str(key)) % num_partitions
