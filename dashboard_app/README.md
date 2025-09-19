# Natural Language to SQL Dashboard

A powerful web application that converts natural language questions into SQL queries and provides interactive data visualization. Built with Flask backend and vanilla JavaScript frontend.

## 🚀 Features

### Core Functionality
- **Natural Language to SQL**: Convert plain English questions to SQL queries using GitHub Models LLM
- **Interactive Dashboard**: Pre-built visualizations for key business metrics
- **Real-time Query Execution**: Execute queries and see results instantly
- **Data Visualization**: Create charts from query results (Bar, Line, Pie, Doughnut)
- **Query History**: Track and reuse previous queries
- **Suggested Questions**: AI-powered question suggestions
- **CSV Export**: Export query results to CSV format

### Technical Features
- **RESTful API**: Clean, documented API endpoints
- **Error Handling**: Comprehensive error management and user feedback
- **Security**: SQL injection protection and query validation
- **Responsive Design**: Mobile-friendly interface
- **Real-time Status**: Connection status monitoring

## 📋 Prerequisites

- Python 3.8 or higher
- GitHub account with access to GitHub Models
- Modern web browser

## 🛠️ Installation

### 1. Clone and Setup
```bash
# Navigate to the project directory
cd dashboard_app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy environment template
copy .env.example .env

# Edit .env file and add your GitHub token
GITHUB_TOKEN=your_actual_github_token_here
```

### 3. Database Setup
Ensure the `retail_database.db` file is in the project root directory. The database should contain the following tables:
- `customers`: Customer information
- `products`: Product catalog
- `orders`: Order transactions
- `sales`: Sales records

## 🚀 Running the Application

### Start the Backend API
```bash
# From the backend directory
python app.py
```
The API will be available at `http://localhost:5000`

### Start the Frontend
```bash
# From the frontend directory
# Open index.html in a web browser or use a local server:
python -m http.server 3000
```
The frontend will be available at `http://localhost:3000`

## 📖 Usage

### Natural Language Queries
Ask questions in plain English:
- "What are our top selling products?"
- "Show me total revenue by month"
- "Which customers have the highest order values?"
- "What's the average order value?"

### API Endpoints

#### Health Check
```
GET /api/health
```

#### Natural Language Query
```
POST /api/query/natural
Content-Type: application/json

{
    "question": "What are our top selling products?"
}
```

#### Direct SQL Query
```
POST /api/query/sql
Content-Type: application/json

{
    "sql": "SELECT name, SUM(quantity) FROM products p JOIN orders o ON p.id = o.product_id GROUP BY name ORDER BY SUM(quantity) DESC LIMIT 10"
}
```

#### Database Schema
```
GET /api/schema
```

#### Business KPIs
```
GET /api/kpis
```

#### Suggested Questions
```
GET /api/suggestions
```

#### Chart Data
```
POST /api/charts/data
Content-Type: application/json

{
    "chart_type": "sales_trend"
}
```

## 🏗️ Architecture

### Backend Structure
```
backend/
├── app.py                 # Main Flask application
├── services/
│   ├── database_service.py    # Database operations
│   └── llm_service.py         # LLM integration
├── utils/
│   ├── response_formatter.py  # API response formatting
│   └── error_handler.py       # Error management
└── requirements.txt       # Python dependencies
```

### Frontend Structure
```
frontend/
├── index.html             # Main application UI
├── style.css             # Custom styles
└── script.js             # Application logic
```

## 🔧 Configuration

### GitHub Models Setup
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Create a new token with appropriate permissions
3. Add the token to your `.env` file

### Database Configuration
The application expects a SQLite database with the following schema:

```sql
-- Customers table
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    city TEXT,
    signup_date DATE
);

-- Products table
CREATE TABLE products (
    id TEXT PRIMARY KEY,
    name TEXT,
    category TEXT,
    price DECIMAL,
    stock INTEGER
);

-- Orders table
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    product_id TEXT,
    quantity INTEGER,
    order_date DATE,
    total DECIMAL,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Sales table
CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    order_id INTEGER,
    revenue DECIMAL,
    profit_margin DECIMAL,
    sales_date DATE,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
```

## 🔍 Troubleshooting

### Common Issues

**Database not found error:**
- Ensure `retail_database.db` is in the correct location
- Check the `DATABASE_PATH` in your `.env` file

**API connection failed:**
- Verify the backend is running on port 5000
- Check firewall settings
- Ensure GitHub token is valid

**LLM service errors:**
- Verify GitHub token has correct permissions
- Check internet connectivity
- Validate the GitHub Models API is accessible

### Debug Mode
Enable debug logging by setting `FLASK_DEBUG=True` in your environment.

## 📊 Sample Queries

The application supports various types of business questions:

### Sales Analysis
- "What is our total revenue this year?"
- "Show me monthly sales trends"
- "Which products have the highest profit margins?"

### Customer Insights
- "Who are our top 10 customers by revenue?"
- "Which cities have the most customers?"
- "Show me new customer signups by month"

### Product Performance
- "What are our best selling products?"
- "Which product categories are most popular?"
- "Show me products with low stock levels"

### Operational Metrics
- "What's our average order value?"
- "How many orders do we process per day?"
- "Show me seasonal sales patterns"

## 🛡️ Security

- SQL injection protection through parameterized queries
- Input validation and sanitization
- Read-only database operations for user queries
- Error message sanitization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review the API documentation
- Open an issue on GitHub

## 🔮 Future Enhancements

- Advanced chart customization
- Export to multiple formats (PDF, Excel)
- Query optimization suggestions
- User authentication and permissions
- Scheduled reports
- Advanced analytics and forecasting