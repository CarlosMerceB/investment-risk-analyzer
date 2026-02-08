"""
Database inspection tool
Check what data we have in the database
"""

import sqlite3
import pandas as pd
from config import DB_PATH, ASSETS

def check_database():
    """Check database contents and quality"""
    
    print("\n" + "="*60)
    print("DATABASE INSPECTION")
    print("="*60 + "\n")
    
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Count records per asset
    print("📊 RECORDS PER ASSET:")
    print("-"*60)
    query = """
        SELECT 
            ticker,
            asset_name,
            COUNT(*) as records,
            MIN(date) as first_date,
            MAX(date) as last_date
        FROM price_data
        GROUP BY ticker, asset_name
        ORDER BY ticker
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    print(f"\n📈 Total assets: {len(df)}")
    print(f"📈 Total records: {df['records'].sum():,}")
    
    # 2. Latest prices
    print("\n\n💰 LATEST CLOSING PRICES:")
    print("-"*60)
    query = """
        SELECT 
            ticker,
            asset_name,
            date,
            close as price,
            volume
        FROM price_data
        WHERE (ticker, date) IN (
            SELECT ticker, MAX(date)
            FROM price_data
            GROUP BY ticker
        )
        ORDER BY ticker
    """
    df_latest = pd.read_sql_query(query, conn)
    print(df_latest.to_string(index=False))
    
    # 3. Check for missing assets
    print("\n\n🔍 MISSING ASSETS CHECK:")
    print("-"*60)
    stored_tickers = set(df['ticker'].tolist())
    configured_tickers = set(ASSETS.keys())
    missing = configured_tickers - stored_tickers
    
    if missing:
        print(f"⚠️  Missing {len(missing)} assets:")
        for ticker in missing:
            print(f"   - {ticker} ({ASSETS[ticker]})")
    else:
        print(f"✅ All {len(configured_tickers)} configured assets have data")
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ Inspection complete")
    print("="*60 + "\n")

if __name__ == '__main__':
    check_database()