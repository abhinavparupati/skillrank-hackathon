import pandas as pd
import numpy as np
from datetime import datetime, date
import sqlite3
import re
import hashlib
import random
from pathlib import Path

class RetailDataProcessor:
    def __init__(self, csv_file='data.csv', db_file='retail_database.db'):
        self.csv_file = csv_file
        self.db_file = db_file
        self.df = None
        
    def load_data(self):
        """Load and clean the raw CSV data"""
        print("Loading data...")
        try:
            self.df = pd.read_csv(self.csv_file, encoding='utf-8')
        except UnicodeDecodeError:
            print("UTF-8 failed, trying latin-1 encoding...")
            self.df = pd.read_csv(self.csv_file, encoding='latin-1')
            
        print(f"Loaded {len(self.df):,} records")
        return self.df
    
    def clean_data(self):
        """Clean the data by removing invalid records"""
        print("\nCleaning data...")
        initial_count = len(self.df)
        
        # Remove records with missing customer IDs (B2B transactions without customer tracking)
        self.df = self.df[self.df['CustomerID'].notna()]
        print(f"Removed {initial_count - len(self.df):,} records with missing Customer IDs")
        
        # Remove cancelled orders (negative quantities)
        self.df = self.df[self.df['Quantity'] > 0]
        print(f"Remaining after removing cancelled orders: {len(self.df):,}")
        
        # Remove records with invalid prices
        self.df = self.df[self.df['UnitPrice'] > 0]
        print(f"Remaining after removing invalid prices: {len(self.df):,}")
        
        # Clean descriptions
        self.df['Description'] = self.df['Description'].fillna('Unknown Product')
        self.df['Description'] = self.df['Description'].str.strip()
        
        # Convert data types
        self.df['CustomerID'] = self.df['CustomerID'].astype(int)
        self.df['InvoiceDate'] = pd.to_datetime(self.df['InvoiceDate'])
        
        # Remove test data and invalid invoice numbers
        self.df = self.df[~self.df['InvoiceNo'].str.startswith('C')]  # Remove credit notes
        
        print(f"Final cleaned dataset: {len(self.df):,} records")
        return self.df
    
    def generate_customers_table(self):
        """Generate customers table with derived fields"""
        print("\nGenerating customers table...")
        
        # Get unique customers with their first order date
        customer_data = self.df.groupby('CustomerID').agg({
            'InvoiceDate': 'min',  # First order date as signup date
            'Country': 'first'     # Country (assuming customers don't move)
        }).reset_index()
        
        customers = []
        for _, row in customer_data.iterrows():
            customer_id = int(row['CustomerID'])
            country = row['Country']
            signup_date = row['InvoiceDate'].date()
            
            # Generate realistic name
            name = self._generate_customer_name(customer_id)
            
            # Generate email based on name and customer ID
            email = self._generate_email(name, customer_id)
            
            # Use country as city (simplified)
            city = country
            
            customers.append({
                'id': customer_id,
                'name': name,
                'email': email,
                'city': city,
                'signup_date': signup_date
            })
        
        customers_df = pd.DataFrame(customers)
        print(f"Generated {len(customers_df):,} unique customers")
        return customers_df
    
    def generate_products_table(self):
        """Generate products table with categories"""
        print("\nGenerating products table...")
        
        # Get unique products, handling cases where same StockCode has different descriptions
        # Use the most common description for each StockCode
        product_data = self.df.groupby('StockCode').agg({
            'Description': lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0],
            'UnitPrice': 'mean',
            'Quantity': 'sum'  # Total quantity sold (for stock estimation)
        }).reset_index()
        
        products = []
        for _, row in product_data.iterrows():
            stock_code = row['StockCode']
            description = row['Description']
            avg_price = round(row['UnitPrice'], 2)
            total_sold = row['Quantity']
            
            # Derive category from description
            category = self._categorize_product(description)
            
            # Simulate current stock (based on sales volume)
            stock = self._estimate_stock(total_sold)
            
            products.append({
                'id': stock_code,
                'name': description,
                'category': category,
                'price': avg_price,
                'stock': stock
            })
        
        products_df = pd.DataFrame(products)
        print(f"Generated {len(products_df):,} unique products")
        return products_df
    
    def generate_orders_table(self):
        """Generate orders table from transactions"""
        print("\nGenerating orders table...")
        
        orders = []
        order_id = 1
        
        for _, row in self.df.iterrows():
            total = round(row['Quantity'] * row['UnitPrice'], 2)
            
            orders.append({
                'id': order_id,
                'customer_id': int(row['CustomerID']),
                'product_id': row['StockCode'],
                'quantity': int(row['Quantity']),
                'order_date': row['InvoiceDate'].date(),
                'total': total
            })
            order_id += 1
        
        orders_df = pd.DataFrame(orders)
        print(f"Generated {len(orders_df):,} order records")
        return orders_df
    
    def generate_sales_table(self, orders_df):
        """Generate sales table with profit margins"""
        print("\nGenerating sales table...")
        
        sales = []
        sales_id = 1
        
        for _, row in orders_df.iterrows():
            revenue = row['total']
            # Generate realistic profit margin (15-45%)
            profit_margin = round(random.uniform(0.15, 0.45), 3)
            
            sales.append({
                'id': sales_id,
                'order_id': row['id'],
                'revenue': revenue,
                'profit_margin': profit_margin,
                'sales_date': row['order_date']
            })
            sales_id += 1
        
        sales_df = pd.DataFrame(sales)
        print(f"Generated {len(sales_df):,} sales records")
        return sales_df
    
    def _generate_customer_name(self, customer_id):
        """Generate realistic customer names"""
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'Chris', 'Lisa', 
                      'Mark', 'Anna', 'Paul', 'Sophie', 'James', 'Kate', 'Tom', 'Lucy',
                      'Robert', 'Helen', 'Peter', 'Grace', 'Steve', 'Olivia', 'Daniel', 'Amy']
        last_names = ['Smith', 'Johnson', 'Brown', 'Taylor', 'Anderson', 'Thomas', 'Jackson',
                     'White', 'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson',
                     'Clark', 'Rodriguez', 'Lewis', 'Lee', 'Walker', 'Hall', 'Allen', 'Young']
        
        # Use customer_id as seed for consistent name generation
        random.seed(customer_id)
        first = random.choice(first_names)
        last = random.choice(last_names)
        return f"{first} {last}"
    
    def _generate_email(self, name, customer_id):
        """Generate email from name and customer ID"""
        # Clean name for email
        clean_name = name.lower().replace(' ', '.')
        domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'email.com']
        
        random.seed(customer_id)
        domain = random.choice(domains)
        
        # Add customer ID to ensure uniqueness
        return f"{clean_name}.{customer_id}@{domain}"
    
    def _categorize_product(self, description):
        """Categorize products based on description keywords"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['heart', 'love', 'valentine', 'wedding']):
            return 'Gifts & Romance'
        elif any(word in description_lower for word in ['christmas', 'xmas', 'santa', 'reindeer']):
            return 'Christmas & Seasonal'
        elif any(word in description_lower for word in ['bag', 'handbag', 'purse', 'tote']):
            return 'Bags & Accessories'
        elif any(word in description_lower for word in ['candle', 'light', 't-light', 'lantern']):
            return 'Lighting & Candles'
        elif any(word in description_lower for word in ['mug', 'cup', 'tea', 'coffee', 'plate']):
            return 'Kitchen & Dining'
        elif any(word in description_lower for word in ['frame', 'picture', 'photo']):
            return 'Home Decor'
        elif any(word in description_lower for word in ['cake', 'baking', 'kitchen']):
            return 'Baking & Kitchen'
        elif any(word in description_lower for word in ['toy', 'game', 'children', 'kids']):
            return 'Toys & Games'
        elif any(word in description_lower for word in ['fabric', 'textile', 'towel']):
            return 'Textiles & Fabrics'
        elif any(word in description_lower for word in ['garden', 'outdoor', 'plant']):
            return 'Garden & Outdoor'
        else:
            return 'General Merchandise'
    
    def _estimate_stock(self, total_sold):
        """Estimate current stock based on sales volume"""
        # High-selling items have lower stock, low-selling items have higher stock
        if total_sold > 1000:
            return random.randint(10, 50)
        elif total_sold > 500:
            return random.randint(25, 100)
        elif total_sold > 100:
            return random.randint(50, 200)
        else:
            return random.randint(100, 500)
    
    def create_database_schema(self):
        """Create SQLite database with proper schema"""
        print(f"\nCreating database: {self.db_file}")
        
        # Remove existing database
        if Path(self.db_file).exists():
            Path(self.db_file).unlink()
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create customers table
        cursor.execute('''
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            city TEXT NOT NULL,
            signup_date DATE NOT NULL
        )
        ''')
        
        # Create products table
        cursor.execute('''
        CREATE TABLE products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            stock INTEGER NOT NULL
        )
        ''')
        
        # Create orders table
        cursor.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            order_date DATE NOT NULL,
            total DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
        ''')
        
        # Create sales table
        cursor.execute('''
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            revenue DECIMAL(10,2) NOT NULL,
            profit_margin DECIMAL(5,3) NOT NULL,
            sales_date DATE NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX idx_orders_customer_id ON orders(customer_id)')
        cursor.execute('CREATE INDEX idx_orders_product_id ON orders(product_id)')
        cursor.execute('CREATE INDEX idx_orders_date ON orders(order_date)')
        cursor.execute('CREATE INDEX idx_sales_order_id ON sales(order_id)')
        cursor.execute('CREATE INDEX idx_sales_date ON sales(sales_date)')
        
        conn.commit()
        conn.close()
        print("Database schema created successfully")
    
    def load_data_to_database(self, customers_df, products_df, orders_df, sales_df):
        """Load all data into SQLite database"""
        print(f"\nLoading data into database: {self.db_file}")
        
        conn = sqlite3.connect(self.db_file)
        
        # Load data into tables
        customers_df.to_sql('customers', conn, if_exists='append', index=False)
        print(f"Loaded {len(customers_df):,} customers")
        
        products_df.to_sql('products', conn, if_exists='append', index=False)
        print(f"Loaded {len(products_df):,} products")
        
        orders_df.to_sql('orders', conn, if_exists='append', index=False)
        print(f"Loaded {len(orders_df):,} orders")
        
        sales_df.to_sql('sales', conn, if_exists='append', index=False)
        print(f"Loaded {len(sales_df):,} sales records")
        
        conn.close()
        print("All data loaded successfully")
    
    def validate_database(self):
        """Validate database integrity and relationships"""
        print(f"\nValidating database: {self.db_file}")
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Check table counts
        tables = ['customers', 'products', 'orders', 'sales']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count:,} records")
        
        # Check foreign key relationships
        cursor.execute('''
        SELECT COUNT(*) FROM orders o 
        LEFT JOIN customers c ON o.customer_id = c.id 
        WHERE c.id IS NULL
        ''')
        orphaned_customers = cursor.fetchone()[0]
        print(f"Orders with invalid customer_id: {orphaned_customers}")
        
        cursor.execute('''
        SELECT COUNT(*) FROM orders o 
        LEFT JOIN products p ON o.product_id = p.id 
        WHERE p.id IS NULL
        ''')
        orphaned_products = cursor.fetchone()[0]
        print(f"Orders with invalid product_id: {orphaned_products}")
        
        cursor.execute('''
        SELECT COUNT(*) FROM sales s 
        LEFT JOIN orders o ON s.order_id = o.id 
        WHERE o.id IS NULL
        ''')
        orphaned_sales = cursor.fetchone()[0]
        print(f"Sales with invalid order_id: {orphaned_sales}")
        
        # Summary statistics
        cursor.execute('SELECT MIN(signup_date), MAX(signup_date) FROM customers')
        min_signup, max_signup = cursor.fetchone()
        print(f"Customer signup date range: {min_signup} to {max_signup}")
        
        cursor.execute('SELECT MIN(order_date), MAX(order_date) FROM orders')
        min_order, max_order = cursor.fetchone()
        print(f"Order date range: {min_order} to {max_order}")
        
        cursor.execute('SELECT SUM(total) FROM orders')
        total_revenue = cursor.fetchone()[0]
        print(f"Total revenue: £{total_revenue:,.2f}")
        
        cursor.execute('SELECT COUNT(DISTINCT category) FROM products')
        categories = cursor.fetchone()[0]
        print(f"Product categories: {categories}")
        
        conn.close()
        print("Database validation completed")
    
    def process_all(self):
        """Execute the complete data processing pipeline"""
        print("=== RETAIL DATA PROCESSING PIPELINE ===")
        
        # Load and clean data
        self.load_data()
        self.clean_data()
        
        # Generate normalized tables
        customers_df = self.generate_customers_table()
        products_df = self.generate_products_table()
        orders_df = self.generate_orders_table()
        sales_df = self.generate_sales_table(orders_df)
        
        # Create database and load data
        self.create_database_schema()
        self.load_data_to_database(customers_df, products_df, orders_df, sales_df)
        
        # Validate results
        self.validate_database()
        
        print(f"\n=== PROCESSING COMPLETE ===")
        print(f"Database created: {self.db_file}")
        print("Data has been successfully normalized and imported!")

def main():
    processor = RetailDataProcessor()
    processor.process_all()

if __name__ == "__main__":
    main()