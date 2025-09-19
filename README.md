# Retail Data Processing - Project Summary

## Overview
Successfully converted the raw CSV transaction data into a clean, normalized SQLite database with four well-structured tables as requested.

## Data Transformation Summary

### Source Data
- **File**: `data.csv`
- **Original Records**: 541,909 transactions
- **Data Range**: December 2010 - December 2011
- **Format**: Transaction-level retail data

### Data Cleaning Applied
- Removed 135,080 records with missing Customer IDs (B2B transactions)
- Removed 10,624 cancelled orders (negative quantities)
- Removed 2,517 records with invalid prices (≤ 0)
- **Final Clean Dataset**: 397,884 valid transactions

## Database Schema

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

## Data Quality Features

### ✅ Data Integrity
- All foreign key relationships validated (0 orphaned records)
- No duplicate primary keys
- No null values in required fields
- Proper data types and constraints

### ✅ Business Logic
- **Product Categories**: 11 logical categories derived from descriptions
- **Customer Names**: Realistic names generated deterministically
- **Email Addresses**: Unique emails following realistic patterns
- **Profit Margins**: Realistic margins (15-45%) simulated
- **Stock Levels**: Estimated based on sales velocity

### ✅ Analytics Ready
- Proper indexes for query performance
- Normalized schema for efficient joins
- Date fields for time-series analysis
- Categories for product analysis

## Key Statistics

| Metric | Value |
|--------|--------|
| **Total Revenue** | £8,911,407.90 |
| **Average Order Value** | £22.40 |
| **Top Category** | General Merchandise (53% of sales) |
| **Date Range** | Dec 2010 - Dec 2011 |
| **Countries** | 37 different countries |
| **Top Customer Spend** | £280,206 (Michael Taylor) |

## Files Created

1. **`data_analysis.py`** - Initial data exploration and quality assessment
2. **`data_processor.py`** - Complete ETL pipeline for data transformation
3. **`database_inspector.py`** - Database validation and sample queries
4. **`retail_database.db`** - Final SQLite database with normalized tables

## Usage Examples

### Connect to Database
```python
import sqlite3
conn = sqlite3.connect('retail_database.db')
```

### Sample Queries
```sql
-- Top customers by revenue
SELECT c.name, SUM(o.total) as revenue
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id
ORDER BY revenue DESC;

-- Sales by category
SELECT p.category, SUM(o.total) as revenue
FROM products p
JOIN orders o ON p.id = o.product_id
GROUP BY p.category
ORDER BY revenue DESC;

-- Monthly sales trends
SELECT strftime('%Y-%m', order_date) as month, 
       COUNT(*) as orders, SUM(total) as revenue
FROM orders
GROUP BY month
ORDER BY month;
```

## Success Criteria Met

✅ **Clean Data**: All invalid records removed, consistent formatting
✅ **Normalized Structure**: Four properly related tables
✅ **Data Quality**: No orphaned records, all relationships valid
✅ **SQLite Import**: All data successfully loaded with constraints
✅ **Analytics Ready**: Indexed and optimized for queries

The database is now ready for business intelligence, reporting, and analytics applications!