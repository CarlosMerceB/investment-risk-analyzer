"""
Configuration file for Investment Risk Analyzer
Define all assets to track and update settings
"""

# Asset tickers to track
ASSETS = {
    # Major Indices (4)
    '^GSPC': 'S&P 500',
    '^DJI': 'Dow Jones',
    '^IXIC': 'NASDAQ',
    '^STOXX50E': 'Euro Stoxx 50',
    
    # Tech Stocks (6)
    'AAPL': 'Apple',
    'MSFT': 'Microsoft',
    'GOOGL': 'Google',
    'AMZN': 'Amazon',
    'NVDA': 'NVIDIA',
    'META': 'Meta',
    
    # Banks (3)
    'JPM': 'JP Morgan',
    'BAC': 'Bank of America',
    'SAN.MC': 'Banco Santander',
    
    # Precious Metals & Commodities (3)
    'GLD': 'Gold ETF',
    'SLV': 'Silver ETF',
    'CL=F': 'Crude Oil',
    
    # Crypto (2)
    'BTC-USD': 'Bitcoin',
    'ETH-USD': 'Ethereum',
}

# Database configuration
DB_PATH = r'C:\Users\carlo\Desktop\Project_Investment_Risk\data\raw\market_data.db'

# Update settings
HISTORICAL_PERIOD = '2y'   # Fetch 2 years of historical data initially