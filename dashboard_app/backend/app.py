"""
Main Flask application for the Natural Language to SQL Dashboard.
Implements RESTful API endpoints with proper error handling.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.database_service import DatabaseService
from services.llm_service import LLMService
from utils.response_formatter import ResponseFormatter
from utils.error_handler import ErrorHandler

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize services
db_service = DatabaseService()
llm_service = LLMService()
response_formatter = ResponseFormatter()
error_handler = ErrorHandler()

# Configure app
app.config['JSON_SORT_KEYS'] = False

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/schema', methods=['GET'])
def get_database_schema():
    """Get database schema information"""
    try:
        schema = db_service.get_table_schema()
        return jsonify({
            'success': True,
            'schema': schema
        })
    except Exception as e:
        return error_handler.handle_error(e, 'Failed to retrieve database schema')

@app.route('/api/stats', methods=['GET'])
def get_database_stats():
    """Get database statistics and KPIs"""
    try:
        stats = db_service.get_database_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return error_handler.handle_error(e, 'Failed to retrieve database statistics')

@app.route('/api/query/natural', methods=['POST'])
def natural_language_query():
    """Convert natural language to SQL and execute query"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                'success': False,
                'error': 'Question is required',
                'error_type': 'validation_error'
            }), 400
        
        question = data['question'].strip()
        
        # Validate question
        validation = llm_service.validate_question(question)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'error': validation['message'],
                'error_type': 'validation_error'
            }), 400
        
        # Convert to SQL
        llm_result = llm_service.natural_language_to_sql(question)
        
        if not llm_result['success']:
            return jsonify(llm_result), 500
        
        sql_query = llm_result['sql_query']
        
        # Validate SQL before execution
        validation_result = db_service.validate_query(sql_query)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': f"Generated SQL is invalid: {validation_result['message']}",
                'error_type': 'sql_error',
                'generated_sql': sql_query
            }), 400
        
        # Execute query
        query_result = db_service.execute_query(sql_query)
        
        if not query_result['success']:
            return jsonify({
                'success': False,
                'error': query_result['error'],
                'error_type': query_result['error_type'],
                'generated_sql': sql_query
            }), 500
        
        # Format response
        formatted_response = response_formatter.format_query_response(
            question=question,
            sql_query=sql_query,
            query_result=query_result,
            model_used=llm_result['model_used']
        )
        
        return jsonify(formatted_response)
    
    except Exception as e:
        return error_handler.handle_error(e, 'Failed to process natural language query')

@app.route('/api/query/sql', methods=['POST'])
def execute_sql_query():
    """Execute a direct SQL query"""
    try:
        data = request.get_json()
        
        if not data or 'sql' not in data:
            return jsonify({
                'success': False,
                'error': 'SQL query is required',
                'error_type': 'validation_error'
            }), 400
        
        sql_query = data['sql'].strip()
        
        # Basic validation - only allow SELECT statements
        if not sql_query.upper().strip().startswith('SELECT'):
            return jsonify({
                'success': False,
                'error': 'Only SELECT queries are allowed',
                'error_type': 'security_error'
            }), 400
        
        # Execute query
        result = db_service.execute_query(sql_query)
        
        if not result['success']:
            return jsonify(result), 500
        
        return jsonify(result)
    
    except Exception as e:
        return error_handler.handle_error(e, 'Failed to execute SQL query')

@app.route('/api/suggestions', methods=['GET'])
def get_suggested_questions():
    """Get suggested business questions"""
    try:
        suggestions = llm_service.get_suggested_questions()
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
    except Exception as e:
        return error_handler.handle_error(e, 'Failed to retrieve suggestions')

@app.route('/api/kpis', methods=['GET'])
def get_business_kpis():
    """Get key business performance indicators"""
    try:
        # Get basic stats
        stats = db_service.get_database_stats()
        
        # Get additional KPIs
        kpis = _calculate_business_kpis()
        
        return jsonify({
            'success': True,
            'kpis': {**stats, **kpis}
        })
    
    except Exception as e:
        return error_handler.handle_error(e, 'Failed to calculate business KPIs')

@app.route('/api/charts/data', methods=['POST'])
def get_chart_data():
    """Get data formatted for chart visualization"""
    try:
        data = request.get_json()
        
        if not data or 'chart_type' not in data:
            return jsonify({
                'success': False,
                'error': 'Chart type is required',
                'error_type': 'validation_error'
            }), 400
        
        chart_type = data['chart_type']
        chart_data = _get_predefined_chart_data(chart_type)
        
        return jsonify({
            'success': True,
            'chart_data': chart_data
        })
    
    except Exception as e:
        return error_handler.handle_error(e, 'Failed to retrieve chart data')

def _calculate_business_kpis():
    """Calculate additional business KPIs"""
    kpis = {}
    
    try:
        # Monthly growth
        monthly_growth_query = """
        SELECT 
            strftime('%Y-%m', order_date) as month,
            SUM(total) as revenue
        FROM orders 
        GROUP BY strftime('%Y-%m', order_date)
        ORDER BY month DESC
        LIMIT 2
        """
        
        result = db_service.execute_query(monthly_growth_query)
        if result['success'] and len(result['data']) >= 2:
            current_month = result['data'][0]['revenue']
            previous_month = result['data'][1]['revenue']
            if previous_month > 0:
                growth_rate = ((current_month - previous_month) / previous_month) * 100
                kpis['monthly_growth_rate'] = round(growth_rate, 2)
        
        # Top category
        top_category_query = """
        SELECT p.category, SUM(o.total) as revenue
        FROM products p
        JOIN orders o ON p.id = o.product_id
        GROUP BY p.category
        ORDER BY revenue DESC
        LIMIT 1
        """
        
        result = db_service.execute_query(top_category_query)
        if result['success'] and result['data']:
            kpis['top_category'] = result['data'][0]['category']
            kpis['top_category_revenue'] = result['data'][0]['revenue']
    
    except Exception as e:
        kpis['error'] = str(e)
    
    return kpis

def _get_predefined_chart_data(chart_type):
    """Get predefined chart data based on chart type"""
    chart_queries = {
        'sales_trend': """
            SELECT 
                strftime('%Y-%m', order_date) as month,
                SUM(total) as revenue,
                COUNT(*) as orders
            FROM orders 
            GROUP BY strftime('%Y-%m', order_date)
            ORDER BY month
        """,
        'category_sales': """
            SELECT p.category, SUM(o.total) as revenue
            FROM products p
            JOIN orders o ON p.id = o.product_id
            GROUP BY p.category
            ORDER BY revenue DESC
            LIMIT 10
        """,
        'top_products': """
            SELECT p.name, SUM(o.quantity) as quantity_sold, SUM(o.total) as revenue
            FROM products p
            JOIN orders o ON p.id = o.product_id
            GROUP BY p.id, p.name
            ORDER BY revenue DESC
            LIMIT 10
        """,
        'customer_distribution': """
            SELECT c.city, COUNT(*) as customer_count
            FROM customers c
            GROUP BY c.city
            ORDER BY customer_count DESC
            LIMIT 10
        """
    }
    
    if chart_type in chart_queries:
        result = db_service.execute_query(chart_queries[chart_type])
        if result['success']:
            return result['data']
    
    return []

if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(db_service.db_path):
        print(f"Error: Database not found at {db_service.db_path}")
        print("Please ensure the retail_database.db file exists in the correct location.")
        sys.exit(1)
    
    print("Starting Natural Language to SQL Dashboard API...")
    print(f"Database: {db_service.db_path}")
    print("API will be available at http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)