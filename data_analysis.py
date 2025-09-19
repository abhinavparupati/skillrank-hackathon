import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3
import re

def analyze_data_quality(df):
    """Analyze data quality and print summary statistics"""
    print("=== DATA QUALITY ANALYSIS ===")
    print(f"Total records: {len(df):,}")
    print(f"Shape: {df.shape}")
    print()
    
    print("=== COLUMN INFO ===")
    print(df.info())
    print()
    
    print("=== MISSING VALUES ===")
    missing = df.isnull().sum()
    print(missing[missing > 0])
    print()
    
    print("=== UNIQUE VALUES PER COLUMN ===")
    for col in df.columns:
        print(f"{col}: {df[col].nunique():,} unique values")
    print()
    
    print("=== SAMPLE DATA ===")
    print(df.head())
    print()
    
    # Check for cancelled orders (negative quantities)
    cancelled = df[df['Quantity'] < 0]
    print(f"Cancelled orders (negative quantities): {len(cancelled):,}")
    
    # Check for missing customer IDs
    missing_customers = df[df['CustomerID'].isnull()]
    print(f"Records with missing Customer IDs: {len(missing_customers):,}")
    
    # Check for missing descriptions
    missing_desc = df[df['Description'].isnull()]
    print(f"Records with missing descriptions: {len(missing_desc):,}")
    
    # Check for zero/negative prices
    zero_price = df[df['UnitPrice'] <= 0]
    print(f"Records with zero/negative prices: {len(zero_price):,}")
    
    print("\n=== COUNTRY DISTRIBUTION ===")
    print(df['Country'].value_counts().head(10))
    
    print("\n=== DATE RANGE ===")
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    print(f"Date range: {df['InvoiceDate'].min()} to {df['InvoiceDate'].max()}")

def main():
    # Load the data
    print("Loading data...")
    try:
        df = pd.read_csv('data.csv', encoding='utf-8')
    except UnicodeDecodeError:
        print("UTF-8 failed, trying latin-1 encoding...")
        df = pd.read_csv('data.csv', encoding='latin-1')
    
    # Analyze data quality
    analyze_data_quality(df)

if __name__ == "__main__":
    main()