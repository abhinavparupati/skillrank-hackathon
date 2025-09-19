# Natural Language to SQL Dashboard

## 🚀 Overview
A full-stack web application that allows users to query retail data using natural language. The system converts English questions into SQL queries using GitHub Models LLM and displays results with intelligent data visualizations.

## ✨ Features
- **Natural Language Queries**: Ask questions in plain English
- **Smart SQL Generation**: LLM-powered query conversion with fallback patterns
- **Interactive Visualizations**: Automatic chart generation with Chart.js
- **Real-time Analytics**: KPI calculations and trend analysis
- **Responsive Design**: Bootstrap-powered UI that works on all devices
- **Error Handling**: Comprehensive error management and user feedback

## 🛠️ Post-Clone Setup Instructions

### Prerequisites
- Python 3.8+ installed
- Git installed
- GitHub Personal Access Token (for LLM features)

### 1. Clone and Navigate
```bash
git clone https://github.com/abhinavparupati/skillrank-hackathon.git
cd skillrank-hackathon
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r dashboard_app/requirements.txt
```

### 3. Configure Environment Variables
```bash
# Copy environment template
cp dashboard_app/backend/.env.example dashboard_app/backend/.env

# Edit .env file and add your GitHub token:
# GITHUB_TOKEN=your_actual_github_token_here
```

### 4. Prepare Sample Database
```bash
# Generate sample retail database (optional - for testing)
python data_processor.py
```

### 5. Start the Backend Server
```bash
cd dashboard_app/backend
python app.py
```
Backend will run at: `http://localhost:5000`

### 6. Start the Frontend Server
Open a new terminal:
```bash
cd dashboard_app/frontend
python -m http.server 3000
```
Frontend will run at: `http://localhost:3000`

### 7. Access the Application
Open your browser and navigate to: `http://localhost:3000`

## 🎯 Usage Examples

### Natural Language Queries
Try these example questions:
- "Show me total sales by month"
- "What are the top 5 customers by revenue?"
- "Which products sell the most?"
- "Show sales trends over time"
- "What's the average order value?"

### API Endpoints
- `POST /api/query` - Natural language to SQL conversion
- `GET /api/kpis` - Key performance indicators
- `GET /api/chart-data` - Chart visualization data

## 🏗️ Architecture

### Backend (`dashboard_app/backend/`)
- **`app.py`** - Main Flask application with REST API
- **`services/`** - Business logic modules
  - `database_service.py` - Database operations
  - `llm_service.py` - GitHub Models LLM integration
- **`utils/`** - Helper utilities
  - `response_formatter.py` - API response formatting
  - `error_handler.py` - Error handling and logging

### Frontend (`dashboard_app/frontend/`)
- **`index.html`** - Main application interface
- **`script.js`** - Interactive functionality and API calls
- **`style.css`** - Responsive styling with Bootstrap

## 📊 Database Schema

The application works with a normalized retail database:

### 1. Customers Table
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,           -- Original CustomerID
    name TEXT NOT NULL,               -- Generated realistic names
    email TEXT UNIQUE NOT NULL,       -- Generated from name + ID
    city TEXT NOT NULL,               -- Derived from Country
    signup_date DATE NOT NULL         -- First order date
);
```
**Records**: 4,338 unique customers

### 2. Products Table
```sql
CREATE TABLE products (
    id TEXT PRIMARY KEY,              -- Original StockCode
    name TEXT NOT NULL,               -- Original Description
    category TEXT NOT NULL,           -- Derived from description keywords
    price DECIMAL(10,2) NOT NULL,     -- Average UnitPrice
    stock INTEGER NOT NULL            -- Simulated based on sales volume
);
```
**Records**: 3,665 unique products across 11 categories

### 3. Orders Table
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,           -- Auto-generated order ID
    customer_id INTEGER NOT NULL,     -- FK to customers.id
    product_id TEXT NOT NULL,         -- FK to products.id
    quantity INTEGER NOT NULL,        -- Original Quantity
    order_date DATE NOT NULL,         -- Original InvoiceDate
    total DECIMAL(10,2) NOT NULL,     -- Calculated (quantity × price)
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```
**Records**: 397,884 orders

### 4. Sales Table
```sql
CREATE TABLE sales (
    id INTEGER PRIMARY KEY,           -- Auto-generated sales ID
    order_id INTEGER NOT NULL,       -- FK to orders.id
    revenue DECIMAL(10,2) NOT NULL,   -- Same as order total
    profit_margin DECIMAL(5,3) NOT NULL, -- Simulated (15-45%)
    sales_date DATE NOT NULL,         -- Same as order date
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
```
**Records**: 397,884 sales records

## 🔧 Development

### Adding New Query Patterns
Edit `dashboard_app/backend/services/llm_service.py` to add new fallback patterns:
```python
QUERY_PATTERNS = {
    'your_pattern': 'SELECT * FROM your_table WHERE condition;'
}
```

### Extending Visualizations
Modify `dashboard_app/frontend/script.js` to add new chart types:
```javascript
function createCustomChart(data) {
    // Your chart implementation
}
```

### Environment Variables
- `GITHUB_TOKEN` - GitHub Models API token (required)
- `DATABASE_PATH` - Path to SQLite database
- `FLASK_ENV` - Development/production mode
- `API_HOST` - Backend host (default: 0.0.0.0)
- `API_PORT` - Backend port (default: 5000)

## 🛡️ Security Features
- Environment variable protection (`.env` excluded from git)
- Input validation and SQL injection prevention
- Error handling without data exposure
- Secure API token management

## 📁 Project Structure
```
skillrank-hackathon/
├── dashboard_app/
│   ├── backend/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── .env.example
│   ├── frontend/
│   │   ├── index.html
│   │   ├── script.js
│   │   └── style.css
│   └── README.md
├── data_processor.py
├── database_inspector.py
├── .gitignore
└── README.md
```

## 🚀 Deployment

### Local Development
Follow the setup instructions above.

### Production Deployment
1. Set `FLASK_ENV=production` in `.env`
2. Use a production WSGI server (gunicorn)
3. Configure reverse proxy (nginx)
4. Set up SSL certificates

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License
This project is available for educational and demonstration purposes.

This project demonstrates:
- ✅ **Full-Stack Development**: Flask backend + JavaScript frontend
- ✅ **AI Integration**: GitHub Models LLM for natural language processing
- ✅ **Data Visualization**: Interactive charts with automatic axis detection
- ✅ **Clean Architecture**: Modular design with separation of concerns
- ✅ **Error Handling**: Comprehensive fallback systems and user feedback
- ✅ **Security**: Proper secret management and input validation
- ✅ **Software Engineering**: Git workflow, documentation, and best practices

Built with modern web technologies and AI-powered natural language understanding!