"""
Main data fetching script for Investment Risk Analyzer
Downloads market data and stores in SQLite database
"""

import yfinance as yf
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import time
import logging
from config import ASSETS, DB_PATH, HISTORICAL_PERIOD

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_fetch.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def create_database_tables():
    """Create the database tables if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_data (
            ticker TEXT NOT NULL,
            asset_name TEXT NOT NULL,
            date DATE NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (ticker, date)
        )
    ''')
    
    conn.commit()
    conn.close()
    logging.info("Database tables created/verified")

def fetch_asset_data(ticker, asset_name, period='1mo'):
    """Fetch data for a single asset"""
    logging.info(f"Fetching {ticker} ({asset_name})...")
    
    try:
        # Calculate date range
        end = datetime.now()
        
        if period == '1mo':
            start = end - timedelta(days=30)
        elif period == '2y':
            start = end - timedelta(days=730)
        else:
            start = end - timedelta(days=30)
        
        # Download data
        data = yf.download(
            ticker,
            start=start,
            end=end,
            progress=False,
            auto_adjust=False
        )
        
        if data.empty:
            logging.warning(f"No data for {ticker}")
            return None
        
        # CRITICAL FIX: Flatten MultiIndex columns
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        # Reset index to make Date a column
        data = data.reset_index()
        
        # Add ticker and asset name
        data['ticker'] = ticker
        data['asset_name'] = asset_name
        
        # Rename columns
        data.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace=True)
        
        # Select only needed columns
        data = data[['ticker', 'asset_name', 'date', 'open', 'high', 'low', 'close', 'volume']]
        
        # Convert date to date object (not datetime)
        data['date'] = pd.to_datetime(data['date']).dt.date
        
        logging.info(f"SUCCESS - Got {len(data)} records for {ticker}")
        return data
        
    except Exception as e:
        logging.error(f"ERROR fetching {ticker}: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return None

def save_to_database(df, ticker):
    """Save DataFrame to SQLite database"""
    if df is None or df.empty:
        logging.warning(f"No data to save for {ticker}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Delete existing data for this ticker
        cursor = conn.cursor()
        cursor.execute("DELETE FROM price_data WHERE ticker = ?", (ticker,))
        
        # Insert new data
        df.to_sql('price_data', conn, if_exists='append', index=False)
        
        conn.commit()
        logging.info(f"SAVED {len(df)} records for {ticker}")
        return True
        
    except Exception as e:
        logging.error(f"ERROR saving {ticker}: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        conn.rollback()
        return False
    finally:
        conn.close()

def fetch_all_assets(period='1mo'):
    """Fetch data for all configured assets"""
    logging.info("="*60)
    logging.info(f"Starting data fetch for {len(ASSETS)} assets")
    logging.info(f"Period: {period}")
    logging.info("="*60)
    
    success_count = 0
    fail_count = 0
    
    for ticker, asset_name in ASSETS.items():
        df = fetch_asset_data(ticker, asset_name, period)
        
        if df is not None:
            saved = save_to_database(df, ticker)
            if saved:
                success_count += 1
            else:
                fail_count += 1
        else:
            fail_count += 1
        
        time.sleep(3)
    
    logging.info("="*60)
    logging.info(f"Completed: {success_count} successful, {fail_count} failed")
    logging.info("="*60)
    
    return success_count, fail_count

if __name__ == '__main__':
    create_database_tables()
    fetch_all_assets(period='2y') 