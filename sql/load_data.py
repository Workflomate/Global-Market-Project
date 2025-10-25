import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE")
}

def load_data():
    conn = None
    cursor = None
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print(f" Connected to MySQL as {DB_CONFIG['user']}")

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        info_path = os.path.join(base_dir, "data", "indexInfo.csv")
        data_path = os.path.join(base_dir, "data", "indexData.csv")

        print(" Reading CSV files...")
        info = pd.read_csv(info_path)
        data = pd.read_csv(data_path)
        print(f"   - indexInfo.csv: {len(info)} rows")
        print(f"   - indexData.csv: {len(data)} rows")

        index_codes = info['Index'].unique().tolist()
        

        print("\n Deleting old index_data records...")
        if index_codes:
            placeholders = ','.join(['%s'] * len(index_codes))
            delete_data_query = f"DELETE FROM index_data WHERE index_code IN ({placeholders})"
            cursor.execute(delete_data_query, index_codes)
            print(f"     Deleted {cursor.rowcount} old index_data records")


        print("\n Deleting old index_info records...")
        if index_codes:
            placeholders = ','.join(['%s'] * len(index_codes))
            delete_info_query = f"DELETE FROM index_info WHERE index_code IN ({placeholders})"
            cursor.execute(delete_info_query, index_codes)
            print(f"     Deleted {cursor.rowcount} old index_info records")


        print("\n Loading index_info...")
        info_data = []
        for _, row in info.iterrows():
            info_data.append((
                row['Index'],
                row['Region'] if pd.notna(row['Region']) else None,
                row['Exchange'] if pd.notna(row['Exchange']) else None,
                row['Currency'] if pd.notna(row['Currency']) else None
            ))
        
        cursor.executemany("""
            INSERT INTO index_info (index_code, region, exchange, currency)
            VALUES (%s, %s, %s, %s)
        """, info_data)
        print(f"    Inserted {len(info_data)} index_info records")

        print("\n Loading index_data...")
        data_records = []
        for _, row in data.iterrows():
            data_records.append((
                row['Index'],
                row['Date'] if pd.notna(row['Date']) else None,
                row['Open'] if pd.notna(row['Open']) else None,
                row['High'] if pd.notna(row['High']) else None,
                row['Low'] if pd.notna(row['Low']) else None,
                row['Close'] if pd.notna(row['Close']) else None,
                row['Adj Close'] if pd.notna(row['Adj Close']) else None,
                row['Volume'] if pd.notna(row['Volume']) else None
            ))
        
        batch_size = 1000
        total_inserted = 0
        for i in range(0, len(data_records), batch_size):
            batch = data_records[i:i + batch_size]
            cursor.executemany("""
                INSERT INTO index_data (index_code, date, open, high, low, close, adj_close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, batch)
            total_inserted += len(batch)
            print(f"    Inserted batch {i//batch_size + 1}: {len(batch)} records (Total: {total_inserted})")
        
        print(f"    Total index_data records inserted: {len(data_records)}")

        conn.commit()
        print("\n Data loaded successfully!")

    except mysql.connector.Error as db_err:
        if conn:
            conn.rollback()
        print(f"\n MySQL Error: {db_err}")
        raise
    
    except FileNotFoundError as file_err:
        print(f"\n File Error: {file_err}")
        print("   Make sure CSV files exist in the 'data' folder")
        raise
    
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\n Unexpected Error: {e}")
        raise
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print(" Database connection closed")

if __name__ == "__main__":
    load_data()