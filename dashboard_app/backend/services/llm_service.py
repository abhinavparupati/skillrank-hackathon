"""
LLM service for natural language to SQL conversion using GitHub Models.
Handles prompt engineering and API communication.
"""
import os
import requests
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMService:
    def __init__(self, github_token: str = None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.base_url = "https://models.inference.ai.azure.com"
        self.model = "gpt-4o-mini"  # Using GitHub's available model
        
        # Database schema for context
        self.schema_context = self._get_schema_context()
    
    def _get_schema_context(self) -> str:
        """Generate schema context for the LLM"""
        return """
        Database Schema:
        
        Table: customers
        - id (INTEGER, PRIMARY KEY): Customer unique identifier
        - name (TEXT): Customer full name
        - email (TEXT): Customer email address
        - city (TEXT): Customer city/country
        - signup_date (DATE): Date when customer first signed up
        
        Table: products
        - id (TEXT, PRIMARY KEY): Product stock code
        - name (TEXT): Product name/description
        - category (TEXT): Product category (e.g., 'General Merchandise', 'Gifts & Romance', 'Kitchen & Dining')
        - price (DECIMAL): Product unit price
        - stock (INTEGER): Current stock quantity
        
        Table: orders
        - id (INTEGER, PRIMARY KEY): Order unique identifier
        - customer_id (INTEGER): Foreign key to customers.id
        - product_id (TEXT): Foreign key to products.id
        - quantity (INTEGER): Quantity ordered
        - order_date (DATE): Date of the order
        - total (DECIMAL): Total order amount (quantity * price)
        
        Table: sales
        - id (INTEGER, PRIMARY KEY): Sales record unique identifier
        - order_id (INTEGER): Foreign key to orders.id
        - revenue (DECIMAL): Revenue from the sale
        - profit_margin (DECIMAL): Profit margin percentage (0-1)
        - sales_date (DATE): Date of the sale
        
        Sample Categories: General Merchandise, Gifts & Romance, Lighting & Candles, Kitchen & Dining, Bags & Accessories, Christmas & Seasonal, Baking & Kitchen, Garden & Outdoor, Home Decor, Toys & Games, Textiles & Fabrics
        
        Date Format: Use 'YYYY-MM-DD' format for dates.
        """
    
    def natural_language_to_sql(self, question: str) -> Dict[str, Any]:
        """
        Convert natural language question to SQL query
        """
        try:
            # First try the simple pattern matching for common questions
            simple_sql = self._try_simple_patterns(question)
            if simple_sql:
                return {
                    'success': True,
                    'sql_query': simple_sql,
                    'question': question,
                    'model_used': 'pattern_matching'
                }
            
            # If pattern matching fails, try GitHub Models API
            prompt = self._create_sql_prompt(question)
            
            headers = {
                "Authorization": f"Bearer {self.github_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert SQL developer. Convert natural language questions to SQL queries based on the provided database schema. Always return valid SQLite queries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "model": self.model,
                "temperature": 0.1,
                "max_tokens": 500
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                sql_query = self._extract_sql_from_response(result)
                
                return {
                    'success': True,
                    'sql_query': sql_query,
                    'question': question,
                    'model_used': self.model
                }
            else:
                # Fallback to pattern matching if API fails
                fallback_sql = self._get_fallback_query(question)
                return {
                    'success': True,
                    'sql_query': fallback_sql,
                    'question': question,
                    'model_used': 'fallback_patterns',
                    'note': f'API failed with status {response.status_code}, using fallback'
                }
        
        except requests.RequestException as e:
            # Fallback to pattern matching on network error
            fallback_sql = self._get_fallback_query(question)
            return {
                'success': True,
                'sql_query': fallback_sql,
                'question': question,
                'model_used': 'fallback_patterns',
                'note': f'Network error: {str(e)}, using fallback'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'error_type': 'unknown_error'
            }
    
    def _try_simple_patterns(self, question: str) -> Optional[str]:
        """Try to match question with simple patterns"""
        question_lower = question.lower()
        
        # Top selling products
        if any(phrase in question_lower for phrase in ['top selling', 'best selling', 'top products']):
            return """
            SELECT p.name, SUM(o.quantity) as total_sold, SUM(o.total) as revenue
            FROM products p
            JOIN orders o ON p.id = o.product_id
            GROUP BY p.id, p.name
            ORDER BY total_sold DESC
            LIMIT 10;
            """
        
        # Revenue queries
        if any(phrase in question_lower for phrase in ['total revenue', 'total sales']):
            return "SELECT SUM(total) as total_revenue FROM orders;"
        
        # Customer count
        if any(phrase in question_lower for phrase in ['customer count', 'how many customers', 'total customers']):
            return "SELECT COUNT(*) as total_customers FROM customers;"
        
        # Average order value
        if any(phrase in question_lower for phrase in ['average order', 'avg order']):
            return "SELECT AVG(total) as average_order_value FROM orders;"
        
        # Top customers
        if any(phrase in question_lower for phrase in ['top customers', 'best customers']):
            return """
            SELECT c.name, c.email, SUM(o.total) as total_spent
            FROM customers c
            JOIN orders o ON c.id = o.customer_id
            GROUP BY c.id, c.name, c.email
            ORDER BY total_spent DESC
            LIMIT 10;
            """
        
        # Monthly sales
        if any(phrase in question_lower for phrase in ['monthly sales', 'sales by month', 'monthly revenue']):
            return """
            SELECT strftime('%Y-%m', order_date) as month, 
                   SUM(total) as revenue,
                   COUNT(*) as order_count
            FROM orders
            GROUP BY strftime('%Y-%m', order_date)
            ORDER BY month DESC;
            """
        
        # Category sales
        if any(phrase in question_lower for phrase in ['category sales', 'sales by category']):
            return """
            SELECT p.category, SUM(o.total) as revenue, COUNT(o.id) as order_count
            FROM products p
            JOIN orders o ON p.id = o.product_id
            GROUP BY p.category
            ORDER BY revenue DESC;
            """
        
        return None
    
    def _get_fallback_query(self, question: str) -> str:
        """Get a fallback query when all else fails"""
        question_lower = question.lower()
        
        # Try the simple patterns first
        simple_query = self._try_simple_patterns(question)
        if simple_query:
            return simple_query
        
        # Default fallback queries based on keywords
        if 'product' in question_lower:
            return """
            SELECT p.name, p.category, p.price, p.stock
            FROM products p
            ORDER BY p.name
            LIMIT 20;
            """
        elif 'customer' in question_lower:
            return """
            SELECT c.name, c.email, c.city, c.signup_date
            FROM customers c
            ORDER BY c.signup_date DESC
            LIMIT 20;
            """
        elif 'order' in question_lower:
            return """
            SELECT o.id, c.name as customer_name, p.name as product_name, 
                   o.quantity, o.total, o.order_date
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            JOIN products p ON o.product_id = p.id
            ORDER BY o.order_date DESC
            LIMIT 20;
            """
        else:
            # General overview query
            return """
            SELECT 'Total Revenue' as metric, SUM(total) as value FROM orders
            UNION ALL
            SELECT 'Total Orders' as metric, COUNT(*) as value FROM orders
            UNION ALL
            SELECT 'Total Customers' as metric, COUNT(*) as value FROM customers
            UNION ALL
            SELECT 'Total Products' as metric, COUNT(*) as value FROM products;
            """
    
    def _create_sql_prompt(self, question: str) -> str:
        """Create a well-structured prompt for SQL generation"""
        return f"""
        {self.schema_context}
        
        Instructions:
        1. Convert the following natural language question to a SQL query
        2. Use only the tables and columns defined in the schema above
        3. Return ONLY the SQL query, no explanations or markdown formatting
        4. Ensure the query is valid SQLite syntax
        5. Use appropriate JOINs when data from multiple tables is needed
        6. For date comparisons, use SQLite date functions
        7. For aggregations, use appropriate GROUP BY clauses
        8. Limit results to reasonable numbers (e.g., TOP 10) unless specified otherwise
        
        Question: {question}
        
        SQL Query:
        """
    
    def _extract_sql_from_response(self, response: Dict) -> str:
        """Extract SQL query from LLM response"""
        try:
            content = response['choices'][0]['message']['content'].strip()
            
            # Remove markdown code blocks if present
            if content.startswith('```sql'):
                content = content[6:]
            elif content.startswith('```'):
                content = content[3:]
            
            if content.endswith('```'):
                content = content[:-3]
            
            # Clean up the query
            content = content.strip()
            
            # Ensure it ends with semicolon
            if not content.endswith(';'):
                content += ';'
            
            return content
        
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to extract SQL from response: {e}")
    
    def get_suggested_questions(self) -> List[str]:
        """Return a list of suggested business questions"""
        return [
            "Show me total sales this year",
            "Which products sold the most?",
            "Who are our top 10 customers by revenue?",
            "What's the monthly sales trend?",
            "Which product category is most profitable?",
            "Show me customers who haven't ordered recently",
            "What's our average order value?",
            "Which cities have the most customers?",
            "Show me the top selling products in each category",
            "What's our total revenue by month?"
        ]
    
    def validate_question(self, question: str) -> Dict[str, Any]:
        """Validate if a question can be reasonably converted to SQL"""
        if not question or len(question.strip()) < 5:
            return {
                'valid': False,
                'message': 'Question is too short or empty'
            }
        
        # Check for basic business question keywords
        business_keywords = [
            'sales', 'revenue', 'customers', 'products', 'orders',
            'top', 'total', 'average', 'count', 'show', 'list',
            'most', 'best', 'trend', 'category', 'profit'
        ]
        
        question_lower = question.lower()
        has_business_keyword = any(keyword in question_lower for keyword in business_keywords)
        
        if not has_business_keyword:
            return {
                'valid': True,  # Still try to process it
                'message': 'Question may not be business-related, but will attempt to process'
            }
        
        return {
            'valid': True,
            'message': 'Question looks valid for SQL conversion'
        }