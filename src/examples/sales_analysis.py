"""
E-commerce Sales Analysis - Advanced map-reduce example

Analyzes sales transaction data to compute:
- Revenue by product category
- Top-selling products
- Customer purchase patterns
- Regional sales distribution

Input format: Transaction records with format:
    transaction_id, timestamp, customer_id, product_id, category, quantity, unit_price, region

Example:
    TXN001, 2024-11-17 10:30:00, CUST123, PROD456, Electronics, 2, 299.99, North
"""

from typing import Any, Iterator, List, Tuple
from datetime import datetime
import random

from ..core.base import Mapper, Reducer


class SalesAnalysisMapper(Mapper):
    """
    Maps transaction records to category and product statistics.
    
    Emits multiple key-value pairs per transaction:
    - (category:CATEGORY_NAME, revenue_data)
    - (product:PRODUCT_ID, sales_data)
    - (region:REGION_NAME, revenue_data)
    """
    
    def map(self, key: Any, value: Any) -> Iterator[Tuple[Any, Any]]:
        """Parse transaction and emit multiple statistics."""
        try:
            parts = [p.strip() for p in value.split(',')]
            
            if len(parts) < 8:
                return
            
            transaction_id = parts[0]
            timestamp_str = parts[1]
            customer_id = parts[2]
            product_id = parts[3]
            category = parts[4]
            quantity = int(parts[5])
            unit_price = float(parts[6])
            region = parts[7]
            
            total_amount = quantity * unit_price
            
            # Emit category statistics
            yield (f"category:{category}", {
                'type': 'category',
                'revenue': total_amount,
                'transaction_count': 1,
                'units_sold': quantity
            })
            
            # Emit product statistics
            yield (f"product:{product_id}", {
                'type': 'product',
                'category': category,
                'revenue': total_amount,
                'units_sold': quantity,
                'transaction_count': 1
            })
            
            # Emit region statistics
            yield (f"region:{region}", {
                'type': 'region',
                'revenue': total_amount,
                'transaction_count': 1,
                'units_sold': quantity
            })
            
            # Emit customer statistics
            yield (f"customer:{customer_id}", {
                'type': 'customer',
                'total_spent': total_amount,
                'transaction_count': 1,
                'categories': [category]
            })
            
        except Exception as e:
            pass


class SalesAnalysisReducer(Reducer):
    """Aggregates sales statistics by key type (category, product, region, customer)."""
    
    def reduce(self, key: Any, values: List[Any]) -> Iterator[Tuple[Any, Any]]:
        """Aggregate statistics based on key type."""
        key_parts = key.split(':', 1)
        
        if len(key_parts) != 2:
            return
        
        key_type, key_name = key_parts
        
        if key_type == 'category':
            yield from self._reduce_category(key_name, values)
        elif key_type == 'product':
            yield from self._reduce_product(key_name, values)
        elif key_type == 'region':
            yield from self._reduce_region(key_name, values)
        elif key_type == 'customer':
            yield from self._reduce_customer(key_name, values)
    
    def _reduce_category(self, category: str, values: List[Any]) -> Iterator[Tuple[Any, Any]]:
        """Aggregate category statistics."""
        total_revenue = sum(v['revenue'] for v in values)
        total_transactions = sum(v['transaction_count'] for v in values)
        total_units = sum(v['units_sold'] for v in values)
        
        result = {
            'category': category,
            'total_revenue': round(total_revenue, 2),
            'total_transactions': total_transactions,
            'total_units_sold': total_units,
            'avg_transaction_value': round(total_revenue / total_transactions, 2) if total_transactions > 0 else 0
        }
        
        yield (f"category_summary:{category}", result)
    
    def _reduce_product(self, product_id: str, values: List[Any]) -> Iterator[Tuple[Any, Any]]:
        """Aggregate product statistics."""
        total_revenue = sum(v['revenue'] for v in values)
        total_units = sum(v['units_sold'] for v in values)
        total_transactions = sum(v['transaction_count'] for v in values)
        category = values[0]['category'] if values else 'Unknown'
        
        result = {
            'product_id': product_id,
            'category': category,
            'total_revenue': round(total_revenue, 2),
            'total_units_sold': total_units,
            'total_transactions': total_transactions
        }
        
        yield (f"product_summary:{product_id}", result)
    
    def _reduce_region(self, region: str, values: List[Any]) -> Iterator[Tuple[Any, Any]]:
        """Aggregate regional statistics."""
        total_revenue = sum(v['revenue'] for v in values)
        total_transactions = sum(v['transaction_count'] for v in values)
        total_units = sum(v['units_sold'] for v in values)
        
        result = {
            'region': region,
            'total_revenue': round(total_revenue, 2),
            'total_transactions': total_transactions,
            'total_units_sold': total_units
        }
        
        yield (f"region_summary:{region}", result)
    
    def _reduce_customer(self, customer_id: str, values: List[Any]) -> Iterator[Tuple[Any, Any]]:
        """Aggregate customer statistics."""
        total_spent = sum(v['total_spent'] for v in values)
        total_transactions = sum(v['transaction_count'] for v in values)
        all_categories = []
        for v in values:
            all_categories.extend(v['categories'])
        unique_categories = len(set(all_categories))
        
        result = {
            'customer_id': customer_id,
            'total_spent': round(total_spent, 2),
            'total_transactions': total_transactions,
            'unique_categories_purchased': unique_categories,
            'avg_order_value': round(total_spent / total_transactions, 2) if total_transactions > 0 else 0
        }
        
        yield (f"customer_summary:{customer_id}", result)


def generate_sample_sales(num_records: int = 5000) -> List[Tuple[int, str]]:
    """Generate sample sales transaction data."""
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Books', 'Sports', 'Toys']
    regions = ['North', 'South', 'East', 'West', 'Central']
    
    products_by_category = {
        'Electronics': [(f'PROD{100+i}', random.uniform(50, 1000)) for i in range(20)],
        'Clothing': [(f'PROD{200+i}', random.uniform(20, 200)) for i in range(30)],
        'Home & Garden': [(f'PROD{300+i}', random.uniform(15, 500)) for i in range(25)],
        'Books': [(f'PROD{400+i}', random.uniform(10, 50)) for i in range(40)],
        'Sports': [(f'PROD{500+i}', random.uniform(25, 300)) for i in range(20)],
        'Toys': [(f'PROD{600+i}', random.uniform(10, 100)) for i in range(30)]
    }
    
    transactions = []
    base_time = datetime(2024, 11, 17, 0, 0, 0)
    
    for i in range(num_records):
        txn_id = f"TXN{i+1:06d}"
        
        # Random time
        hours = random.randint(0, 23)
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        timestamp = base_time.replace(hour=hours, minute=minutes, second=seconds)
        
        # Random customer (simulate repeat customers)
        customer_id = f"CUST{random.randint(1, 500):04d}"
        
        # Random product
        category = random.choice(categories)
        product_id, unit_price = random.choice(products_by_category[category])
        
        # Random quantity (most orders are small)
        quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 30, 12, 5, 3])[0]
        
        # Random region
        region = random.choice(regions)
        
        txn_line = f"{txn_id}, {timestamp.strftime('%Y-%m-%d %H:%M:%S')}, {customer_id}, {product_id}, {category}, {quantity}, {unit_price:.2f}, {region}"
        transactions.append((i, txn_line))
    
    return transactions
