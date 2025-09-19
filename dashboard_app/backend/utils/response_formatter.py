"""
Response formatter utility for standardizing API responses.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class ResponseFormatter:
    """Formats API responses consistently"""
    
    def format_query_response(self, question: str, sql_query: str, 
                            query_result: Dict, model_used: str) -> Dict[str, Any]:
        """Format natural language query response"""
        return {
            'success': True,
            'query': {
                'question': question,
                'sql_query': sql_query,
                'model_used': model_used
            },
            'result': {
                'data': query_result['data'],
                'columns': query_result.get('columns', []),
                'row_count': len(query_result['data']),
                'execution_time_ms': query_result.get('execution_time_ms', 0)
            },
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'response_type': 'natural_language_query'
            }
        }
    
    def format_chart_data(self, data: List[Dict], chart_type: str,
                         chart_config: Optional[Dict] = None) -> Dict[str, Any]:
        """Format data for chart visualization"""
        return {
            'success': True,
            'chart_data': {
                'type': chart_type,
                'data': data,
                'config': chart_config or {},
                'suggested_visualization': self._suggest_visualization(data, chart_type)
            },
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'response_type': 'chart_data'
            }
        }
    
    def format_kpi_data(self, kpis: Dict[str, Any]) -> Dict[str, Any]:
        """Format KPI data with proper categorization"""
        formatted_kpis = {
            'financial': {},
            'operational': {},
            'customer': {}
        }
        
        # Categorize KPIs
        financial_metrics = ['total_revenue', 'average_order_value', 'monthly_growth_rate', 
                           'top_category_revenue', 'total_profit']
        
        operational_metrics = ['total_orders', 'total_products', 'low_stock_count',
                             'orders_per_day', 'inventory_turnover']
        
        customer_metrics = ['total_customers', 'customer_lifetime_value', 'new_customers',
                          'customer_retention_rate', 'customers_per_city']
        
        for key, value in kpis.items():
            if key in financial_metrics:
                formatted_kpis['financial'][key] = self._format_metric_value(key, value)
            elif key in operational_metrics:
                formatted_kpis['operational'][key] = self._format_metric_value(key, value)
            elif key in customer_metrics:
                formatted_kpis['customer'][key] = self._format_metric_value(key, value)
            else:
                # Uncategorized metrics
                if 'other' not in formatted_kpis:
                    formatted_kpis['other'] = {}
                formatted_kpis['other'][key] = self._format_metric_value(key, value)
        
        return {
            'success': True,
            'kpis': formatted_kpis,
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'response_type': 'kpi_data'
            }
        }
    
    def format_suggestions(self, suggestions: List[str]) -> Dict[str, Any]:
        """Format suggested questions"""
        categorized_suggestions = {
            'sales': [],
            'customers': [],
            'products': [],
            'general': []
        }
        
        # Simple keyword-based categorization
        for suggestion in suggestions:
            suggestion_lower = suggestion.lower()
            if any(word in suggestion_lower for word in ['sales', 'revenue', 'profit', 'order']):
                categorized_suggestions['sales'].append(suggestion)
            elif any(word in suggestion_lower for word in ['customer', 'buyer', 'client']):
                categorized_suggestions['customers'].append(suggestion)
            elif any(word in suggestion_lower for word in ['product', 'item', 'stock', 'inventory']):
                categorized_suggestions['products'].append(suggestion)
            else:
                categorized_suggestions['general'].append(suggestion)
        
        return {
            'success': True,
            'suggestions': categorized_suggestions,
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'response_type': 'suggestions'
            }
        }
    
    def _format_metric_value(self, metric_name: str, value: Any) -> Dict[str, Any]:
        """Format individual metric value with appropriate formatting"""
        formatted_value = {
            'value': value,
            'formatted': str(value),
            'type': type(value).__name__
        }
        
        # Apply specific formatting based on metric type
        if 'revenue' in metric_name or 'value' in metric_name or 'profit' in metric_name:
            if isinstance(value, (int, float)):
                formatted_value['formatted'] = f"${value:,.2f}"
                formatted_value['type'] = 'currency'
        
        elif 'rate' in metric_name or 'percentage' in metric_name:
            if isinstance(value, (int, float)):
                formatted_value['formatted'] = f"{value:.1f}%"
                formatted_value['type'] = 'percentage'
        
        elif 'count' in metric_name or 'total' in metric_name:
            if isinstance(value, (int, float)):
                formatted_value['formatted'] = f"{int(value):,}"
                formatted_value['type'] = 'count'
        
        return formatted_value
    
    def _suggest_visualization(self, data: List[Dict], chart_type: str) -> Dict[str, str]:
        """Suggest appropriate visualization type based on data"""
        if not data:
            return {'type': 'empty', 'reason': 'No data available'}
        
        first_row = data[0]
        columns = list(first_row.keys())
        
        # Simple heuristics for visualization suggestions
        if len(columns) == 2:
            if any('date' in col.lower() or 'month' in col.lower() for col in columns):
                return {'type': 'line_chart', 'reason': 'Time series data detected'}
            else:
                return {'type': 'bar_chart', 'reason': 'Two-dimensional categorical data'}
        
        elif len(columns) > 2:
            return {'type': 'table', 'reason': 'Multi-dimensional data best displayed as table'}
        
        return {'type': chart_type, 'reason': 'Using requested chart type'}
    
    def format_error_response(self, error_message: str, error_type: str = 'general_error',
                            status_code: int = 500, additional_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Format error response consistently"""
        response = {
            'success': False,
            'error': error_message,
            'error_type': error_type,
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'response_type': 'error'
            }
        }
        
        if additional_context:
            response['context'] = additional_context
        
        return response