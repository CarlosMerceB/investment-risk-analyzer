# Investment Risk Analyzer - Portfolio Management Dashboard

A comprehensive portfolio risk analysis system built with Python, SQLite, and Power BI. Tracks 18 financial assets across multiple portfolios, calculating advanced risk metrics including Sharpe Ratio, Sortino Ratio, and Value at Risk.

---

## Project Overview

This project analyzes three investment strategies (Conservative, Balanced, Aggressive) over a 2-year period (2024-2026), demonstrating data engineering, financial modeling, and business intelligence capabilities.

**Key Results:**
- Balanced Portfolio identified as optimal strategy (Sortino Ratio: 1.85)
- 99% total return with 29% volatility and -26% worst-case scenario
- Comprehensive risk-adjusted performance analysis across multiple metrics

- ## Dashboard Preview

### Page 1: Executive Summary
![Executive Summary](dashboards/screenshots/page1_executive.png)

### Page 2: Risk Analysis
![Risk Analysis](dashboards/screenshots/page2_risk_analysis.png).

---

## Technical Stack

**Data Acquisition & Processing:**
- Python 3.x
- yfinance API (market data)
- pandas (data manipulation)
- SQLite (data storage)

**Analytics & Visualization:**
- Power BI Desktop
- DAX (Data Analysis Expressions)
- Custom date table for time intelligence

**Assets Tracked (18 total):**
- 4 Indices: S&P 500, NASDAQ, Dow Jones, Euro Stoxx 50
- 6 Tech Stocks: Apple, Microsoft, Google, Amazon, NVIDIA, Meta
- 3 Banks: JP Morgan, Bank of America, Santander
- 3 Precious Metals: Gold ETF, Silver ETF, Gold Futures
- 2 Cryptocurrencies: Bitcoin, Ethereum
- 2 Energy: Energy ETF, Crude Oil

---

## Project Structure

```
investment-risk-analyzer/
├── src/
│   ├── config.py                 # Asset configuration & settings
│   ├── fetch_data.py            # Data fetching & database population
│   ├── check_database.py        # Data quality verification
│   └── requirements.txt         # Python dependencies
│
├── data/
│   └── sample_data.csv          # Sample dataset (full DB not uploaded)
│
├── dashboards/
│   ├── screenshots/             # Dashboard images
│   └── Investment_Risk_Analyzer.pbix
│
├── docs/
│   ├── README.md               # This file
│   └── BUSINESS_SUMMARY.md     # Business analysis
│
└── .gitignore
```

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- Power BI Desktop

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/investment-risk-analyzer.git
cd investment-risk-analyzer
```

### Step 2: Install Dependencies

```bash
cd src/
pip install -r requirements.txt
```

### Step 3: Initialize Database

```bash
python fetch_data.py
```

This fetches 2 years of historical data and creates the SQLite database (9,000+ records).

### Step 4: Open Dashboard

1. Open `Investment_Risk_Analyzer.pbix` in Power BI Desktop
2. Update data source path if needed
3. Click "Refresh"

---

## Database Schema

### price_data (Fact Table)

| Column | Type | Description |
|--------|------|-------------|
| ticker | TEXT | Asset ticker (e.g., AAPL, BTC-USD) |
| asset_name | TEXT | Readable name |
| date | DATE | Trading date |
| open, high, low, close | REAL | OHLC prices |
| volume | INTEGER | Trading volume |

Primary Key: (ticker, date)

### Portfolio_Config (Dimension)

| Column | Type | Description |
|--------|------|-------------|
| portfolio_name | TEXT | Strategy name |
| ticker | TEXT | Asset ticker |
| weight | REAL | Allocation weight |
| initial_investment | REAL | Dollar amount |

### DateTable (Dimension)

Complete calendar table for time intelligence (731 days).

---

## Key Features

### Risk Metrics Calculated

**Sharpe Ratio:** Risk-adjusted return using total volatility
**Sortino Ratio:** Risk-adjusted return using downside volatility only
**Maximum Drawdown:** Worst peak-to-trough decline
**Value at Risk (95%):** Maximum expected loss with 95% confidence
**Volatility:** Annualized standard deviation

### Portfolio Analysis

**Three Strategies:**
- Conservative: 65% return, 20% volatility, -18% worst case
- Balanced: 99% return, 29% volatility, -26% worst case (RECOMMENDED)
- Aggressive: 113% return, 45% volatility, -38% worst case

### Scenario Testing

Stress tests include:
- Bull market scenario (+20%)
- Market correction (-10%)
- Worst case (all assets hit max drawdown)
- Recovery requirements

---

## DAX Measures (Sample)

### Current Price (Weekend-Aware)
```dax
Current Price = 
VAR SelectedDate = MAX(DateTable[Date])
RETURN
CALCULATE(
    AVERAGE(price_data[close]),
    LASTNONBLANK(
        FILTER(
            ALL(price_data[date]),
            price_data[date] <= SelectedDate
        ),
        CALCULATE(COUNT(price_data[close]))
    )
)
```

### Portfolio Sharpe Ratio
```dax
Portfolio Sharpe Ratio = 
VAR RiskFreeRate = 0.04
VAR AnnualReturn = /* ... CAGR calculation ... */
VAR PortfolioVol = [Portfolio Volatility] / 100
RETURN
DIVIDE(AnnualReturn - RiskFreeRate, PortfolioVol, 0)
```

---

## Data Updates

### Manual Refresh
```bash
python fetch_data.py  # Updates database
# Then refresh Power BI
```

### Automated (Optional)
Set up Windows Task Scheduler to run daily at 6 PM after market close.

---

## Dashboard Pages

**Page 1: Executive Summary**
- Portfolio value cards
- Growth chart vs S&P 500 benchmark
- Asset allocation pie chart
- YoY growth indicators

**Page 2: Risk Analysis**
- Efficient frontier scatter plot
- Risk metrics table (Sharpe, Sortino, Max DD, VaR)
- Sharpe vs Sortino comparison
- Scenario analysis
- Investor suitability matrix

---

## Skills Demonstrated

**Technical:**
- Python API integration (yfinance)
- ETL pipeline development
- Database design (SQLite)
- Advanced DAX calculations
- Power BI data modeling
- Time series analysis

**Financial:**
- Portfolio construction
- Risk metrics (Sharpe, Sortino, VaR, Drawdown)
- Scenario analysis & stress testing
- Performance attribution

**Business:**
- Investment strategy comparison
- Risk-return optimization
- Stakeholder communication
- Decision frameworks

---

## Results Summary

The Balanced Portfolio emerged as the optimal strategy with:
- Highest Sortino Ratio (1.85) = best downside protection
- 99% total returns (nearly doubled capital)
- Moderate 29% volatility
- Manageable -26% worst-case scenario
- 35% recovery requirement (vs 61% for Aggressive)

Suitable for 70% of growth-focused investors.

---

## Future Enhancements

- Correlation matrix & covariance analysis
- Monte Carlo simulation for VaR
- Beta and alpha vs benchmark
- Efficient frontier optimization (Markowitz)
- Real-time data refresh
- Mobile dashboard version

---

## Author

**Carlos** - Business Intelligence Analyst
**Date:** February 2026
**Purpose:** Portfolio project for BI/BA/Strategy Analyst roles

Demonstrates end-to-end analytics: data acquisition, modeling, analysis, and visualization with emphasis on financial risk management.

---

## License

MIT License - See LICENSE file for details.
