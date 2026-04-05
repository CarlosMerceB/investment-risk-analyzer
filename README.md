# Investment Risk Analyzer

Portfolio risk analysis dashboard built with Python, SQLite, and Power BI. Pulls 2 years of market data for 18 assets, runs them through three portfolio strategies, and visualizes the risk-return tradeoffs in an interactive dashboard.

The short version: the Balanced Portfolio wins — best downside-adjusted returns (Sortino of 1.85), nearly doubled the initial capital, and keeps the worst-case scenario at a manageable -26%.

---

## What It Does

The project compares three investment strategies (Conservative, Balanced, Aggressive) across 18 financial assets over a 2-year window (2024–2026). A Python script pulls historical price data via the yfinance API, stores everything in a SQLite database (~9,000 records), and a Power BI dashboard handles the analytics and visualization layer.

Assets covered: S&P 500, NASDAQ, Dow Jones, Euro Stoxx 50, Apple, Microsoft, Google, Amazon, NVIDIA, Meta, JP Morgan, Bank of America, Santander, Gold ETF, Silver ETF, Gold Futures, Bitcoin, Ethereum, Energy ETF, and Crude Oil.

Risk metrics calculated include Sharpe Ratio, Sortino Ratio, Maximum Drawdown, Value at Risk (95%), and annualized volatility. The dashboard also runs scenario stress tests — bull market, correction, worst case, and recovery requirements.

---

## Results

| Portfolio | Total Return | Volatility | Max Drawdown | Sortino |
|-----------|-------------|------------|--------------|---------|
| Conservative | 65% | 20% | -18% | — |
| Balanced | 99% | 29% | -26% | 1.85 |
| Aggressive | 113% | 45% | -38% | — |

The Aggressive portfolio has the highest raw return, but once you adjust for downside risk the Balanced portfolio comes out on top. It also only needs a 35% recovery to break even after a drawdown, versus 61% for Aggressive.

---

## Tech Stack

**Python side:** yfinance for data acquisition, pandas for processing, SQLite for storage. The pipeline is straightforward — fetch, transform, load.

**BI side:** Power BI Desktop with a proper data model (fact table + dimensions), DAX measures for all the risk calculations, and a custom date table for time intelligence.

---

## Project Structure

```
investment-risk-analyzer/
├── src/
│   ├── config.py              # Asset tickers, portfolio weights, settings
│   ├── fetch_data.py          # Pulls data from yfinance → SQLite
│   ├── check_database.py      # Quick data quality checks
│   └── requirements.txt
├── data/
│   └── sample_data.csv        # Sample export (full DB not in repo)
├── dashboards/
│   ├── screenshots/
│   └── Investment_Risk_Analyzer.pbix
└── docs/
    └── BUSINESS_SUMMARY.md
```

---

## Setup

You'll need Python 3.8+ and Power BI Desktop.

```bash
git clone https://github.com/yourusername/investment-risk-analyzer.git
cd investment-risk-analyzer/src
pip install -r requirements.txt
python fetch_data.py
```

Then open the `.pbix` file in Power BI, point the data source to your local database path, and hit Refresh.

For daily updates, you can schedule `fetch_data.py` through Windows Task Scheduler to run after market close.

---

## Database

Three tables:

**price_data** — the fact table. Stores OHLCV data per ticker per date. Primary key is (ticker, date).

**Portfolio_Config** — dimension table mapping each asset to a portfolio strategy with its allocation weight and dollar amount.

**DateTable** — complete 731-day calendar for Power BI time intelligence.

---

## Dashboard

Two pages:

**Executive Summary** — portfolio value cards, cumulative growth vs S&P 500 benchmark, asset allocation breakdown, and year-over-year indicators.

**Risk Analysis** — efficient frontier plot, full risk metrics table, Sharpe vs Sortino comparison, scenario analysis results, and an investor suitability matrix.

---

## DAX Examples

Weekend-aware current price (handles non-trading days):

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

Portfolio Sharpe Ratio (risk-free rate at 4%):

```dax
Portfolio Sharpe Ratio = 
VAR RiskFreeRate = 0.04
VAR AnnualReturn = /* CAGR calculation */
VAR PortfolioVol = [Portfolio Volatility] / 100
RETURN
DIVIDE(AnnualReturn - RiskFreeRate, PortfolioVol, 0)
```

---

## What I'd Add Next

Correlation matrix and covariance analysis, Monte Carlo simulation for VaR, alpha/beta vs benchmark, and proper Markowitz efficient frontier optimization. A real-time refresh pipeline and a mobile-friendly version of the dashboard would also be nice.

---

## License

MIT
