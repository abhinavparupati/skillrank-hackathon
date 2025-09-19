"""
Database service for SQLite connection and query execution.
Handles all database operations with proper error handling.
"""
import sqlite3
import pandas as pd
from typing import Dict, List, Any, Tuple
import os
from contextlib import contextmanager

class DatabaseService:
    def __init__(self, db_path: str = None):
        if db_path:
            self.db_path = db_path
        else:
            # Navigate from backend/services/ to project root
            backend_dir = os.path.dirname(os.path.dirname(__file__))  # Go up from services/ to backend/
            project_root = os.path.dirname(os.path.dirname(backend_dir))  # Go up from dashboard_app/ to project root
            self.db_path = os.path.join(project_root, 'retail_database.db')
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """
        Execute a SQL query and return results with metadata
        """
        try:
            with self.get_connection() as conn:
                if params:
                    cursor = conn.execute(query, params)
                else:
                    cursor = conn.execute(query)
                
                # Get column names
                columns = [description[0] for description in cursor.description] if cursor.description else []
                
                # Fetch all results
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                data = []
                for row in rows:
                    data.append(dict(zip(columns, row)))
                
                return {
                    'success': True,
                    'data': data,
                    'columns': columns,
                    'row_count': len(data),
                    'query': query
                }
        
        except sqlite3.Error as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'database_error',
                'query': query
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': 'unknown_error',
                'query': query
            }
    
    def get_table_schema(self) -> Dict[str, List[Dict]]:
        """Get schema information for all tables"""
        schema = {}
        try:
            with self.get_connection() as conn:
                # Get all table names
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    # Get column information for each table
                    cursor = conn.execute(f"PRAGMA table_info({table})")
                    columns = []
                    for row in cursor.fetchall():
                        columns.append({
                            'name': row[1],
                            'type': row[2],
                            'not_null': bool(row[3]),
                            'primary_key': bool(row[5])
                        })
                    schema[table] = columns
            
            return schema
        except Exception as e:
            return {}
    
    def get_sample_data(self, table: str, limit: int = 5) -> Dict[str, Any]:
        """Get sample data from a table"""
        query = f"SELECT * FROM {table} LIMIT {limit}"
        return self.execute_query(query)
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate a SQL query without executing it"""
        try:
            with self.get_connection() as conn:
                # Use EXPLAIN to validate without execution
                cursor = conn.execute(f"EXPLAIN {query}")
                return {'valid': True, 'message': 'Query is valid'}
        except sqlite3.Error as e:
            return {'valid': False, 'message': str(e)}
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get overall database statistics"""
        stats = {}
        try:
            with self.get_connection() as conn:
                # Get table counts
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[f"{table}_count"] = cursor.fetchone()[0]
                
                # Get some business metrics
                business_metrics = self._get_business_metrics(conn)
                stats.update(business_metrics)
            
            return stats
        except Exception as e:
            return {'error': str(e)}
    
    def _get_business_metrics(self, conn) -> Dict[str, Any]:
        """Calculate key business metrics"""
        metrics = {}
        try:
            # Total revenue
            cursor = conn.execute("SELECT SUM(total) FROM orders")
            metrics['total_revenue'] = cursor.fetchone()[0] or 0
            
            # Total orders
            cursor = conn.execute("SELECT COUNT(*) FROM orders")
            metrics['total_orders'] = cursor.fetchone()[0] or 0
            
            # Active customers (customers with orders)
            cursor = conn.execute("SELECT COUNT(DISTINCT customer_id) FROM orders")
            metrics['active_customers'] = cursor.fetchone()[0] or 0
            
            # Total products
            cursor = conn.execute("SELECT COUNT(*) FROM products")
            metrics['total_products'] = cursor.fetchone()[0] or 0
            
            # Average order value
            if metrics['total_orders'] > 0:
                metrics['avg_order_value'] = metrics['total_revenue'] / metrics['total_orders']
            else:
                metrics['avg_order_value'] = 0
            
        except Exception as e:
            metrics['error'] = str(e)
        
        return metrics