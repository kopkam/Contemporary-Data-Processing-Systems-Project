"""
Web Server Log Analysis - A complex map-reduce example

This example analyzes web server access logs to compute various statistics:
- Request counts per endpoint
- Response time statistics per endpoint
- Error rates per endpoint
- Traffic patterns by hour

Input format: Log lines with format:
    timestamp, ip_address, method, endpoint, status_code, response_time_ms

Example:
    2024-11-17 10:23:45, 192.168.1.100, GET, /api/users, 200, 145
    2024-11-17 10:24:12, 192.168.1.101, POST, /api/orders, 201, 289
    2024-11-17 10:24:30, 192.168.1.102, GET, /api/products, 500, 3421
"""

import json
from datetime import datetime
from typing import Any, Iterator, List, Tuple

from ..core.base import Mapper, Reducer


class LogAnalysisMapper(Mapper):
    """
    Maps log entries to endpoint statistics.
    
    For each log line, emits:
    - (endpoint, stats_dict) where stats_dict contains:
        - request_count: 1
        - response_times: [response_time]
        - error_count: 1 if status >= 400 else 0
        - hour: hour of day
    """
    
    def map(self, key: Any, value: Any) -> Iterator[Tuple[Any, Any]]:
        """
        Parse log line and emit endpoint statistics.
        
        Args:
            key: Line number (ignored)
            value: Log line string
        """
        try:
            # Parse log line
            parts = [p.strip() for p in value.split(',')]
            
            if len(parts) < 6:
                return  # Skip malformed lines
            
            timestamp_str = parts[0]
            ip_address = parts[1]
            method = parts[2]
            endpoint = parts[3]
            status_code = int(parts[4])
            response_time = float(parts[5])
            
            # Parse timestamp
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            hour = timestamp.hour
            
            # Create statistics record
            stats = {
                'request_count': 1,
                'response_times': [response_time],
                'error_count': 1 if status_code >= 400 else 0,
                'success_count': 1 if status_code < 400 else 0,
                'hours': [hour],
                'methods': {method: 1},
                'status_codes': {str(status_code): 1}
            }
            
            # Emit endpoint as key
            yield (endpoint, stats)
            
        except Exception as e:
            # Skip lines that can't be parsed
            pass


class LogAnalysisReducer(Reducer):
    """
    Aggregates statistics for each endpoint.
    
    Combines all statistics for an endpoint and computes:
    - Total request count
    - Average, min, max response times
    - Error rate
    - Peak traffic hours
    """
    
    def reduce(self, key: Any, values: List[Any]) -> Iterator[Tuple[Any, Any]]:
        """
        Aggregate statistics for an endpoint.
        
        Args:
            key: Endpoint path
            values: List of statistics dictionaries
        """
        endpoint = key
        
        # Aggregate values
        total_requests = 0
        all_response_times = []
        total_errors = 0
        total_success = 0
        hour_counts = {}
        method_counts = {}
        status_code_counts = {}
        
        for stats in values:
            total_requests += stats['request_count']
            all_response_times.extend(stats['response_times'])
            total_errors += stats['error_count']
            total_success += stats['success_count']
            
            # Aggregate hours
            for hour in stats['hours']:
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            
            # Aggregate methods
            for method, count in stats['methods'].items():
                method_counts[method] = method_counts.get(method, 0) + count
            
            # Aggregate status codes
            for status, count in stats['status_codes'].items():
                status_code_counts[status] = status_code_counts.get(status, 0) + count
        
        # Calculate statistics
        avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0
        min_response_time = min(all_response_times) if all_response_times else 0
        max_response_time = max(all_response_times) if all_response_times else 0
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        # Find peak hours (top 3)
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Create output record
        result = {
            'endpoint': endpoint,
            'total_requests': total_requests,
            'response_time_avg_ms': round(avg_response_time, 2),
            'response_time_min_ms': round(min_response_time, 2),
            'response_time_max_ms': round(max_response_time, 2),
            'error_count': total_errors,
            'success_count': total_success,
            'error_rate_percent': round(error_rate, 2),
            'methods': method_counts,
            'status_codes': status_code_counts,
            'peak_hours': [{'hour': h, 'requests': c} for h, c in peak_hours]
        }
        
        yield (endpoint, result)


def generate_sample_logs(num_records: int = 10000) -> List[Tuple[int, str]]:
    """
    Generate sample web server logs for testing.
    
    Args:
        num_records: Number of log records to generate
        
    Returns:
        List of (line_number, log_line) tuples
    """
    import random
    from datetime import timedelta
    
    endpoints = [
        '/api/users',
        '/api/products',
        '/api/orders',
        '/api/checkout',
        '/api/search',
        '/api/recommendations',
        '/api/reviews',
        '/api/cart',
        '/dashboard',
        '/login'
    ]
    
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    method_weights = [60, 25, 10, 5]  # GET is most common
    
    status_codes = [200, 201, 204, 400, 401, 404, 500, 503]
    status_weights = [70, 10, 5, 5, 3, 4, 2, 1]  # 200 is most common
    
    logs = []
    base_time = datetime(2024, 11, 17, 0, 0, 0)
    
    for i in range(num_records):
        # Generate timestamp (spread over 24 hours with peak times)
        hour = random.choices(
            range(24),
            weights=[2, 1, 1, 1, 2, 3, 5, 8, 10, 12, 13, 14, 14, 13, 12, 10, 9, 8, 7, 6, 5, 4, 3, 2]
        )[0]
        timestamp = base_time + timedelta(hours=hour, minutes=random.randint(0, 59), seconds=random.randint(0, 59))
        
        # Generate other fields
        ip = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
        method = random.choices(methods, weights=method_weights)[0]
        endpoint = random.choice(endpoints)
        status_code = random.choices(status_codes, weights=status_weights)[0]
        
        # Response time varies by status code
        if status_code >= 500:
            response_time = random.randint(2000, 5000)  # Slower for errors
        elif status_code >= 400:
            response_time = random.randint(100, 500)
        else:
            response_time = random.randint(50, 300)
        
        log_line = f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}, {ip}, {method}, {endpoint}, {status_code}, {response_time}"
        logs.append((i, log_line))
    
    return logs
