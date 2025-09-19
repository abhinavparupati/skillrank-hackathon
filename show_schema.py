import sqlite3

def show_schema():
    conn = sqlite3.connect('retail_database.db')
    cursor = conn.cursor()
    
    print("=== DATABASE SCHEMA ===")
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\n{table_name.upper()} TABLE:")
        print("-" * 40)
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            not_null = "NOT NULL" if col[3] else ""
            pk = "PRIMARY KEY" if col[5] else ""
            print(f"  {col_name}: {col_type} {not_null} {pk}".strip())
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  Records: {count:,}")
    
    conn.close()

if __name__ == "__main__":
    show_schema()