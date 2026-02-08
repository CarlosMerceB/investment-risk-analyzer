# DAX Measures Documentation - Investment Risk Analyzer

This document contains all DAX measures used in the Investment Risk Analyzer Power BI dashboard. Each measure includes the formula, explanation, and usage context.

---

## Date-Aware Measures

### Current Price
**Purpose:** Returns the most recent trading price up to the selected date, handling weekends and holidays.

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

**Key Features:**
- Uses LASTNONBLANK to find most recent trading day
- Handles weekend gaps (carries forward Friday's price)
- Works with date slicers and time series charts

---

### Starting Price
**Purpose:** Always returns the price on February 1, 2024 (project start date).

```dax
Starting Price = 
CALCULATE(
    AVERAGE(price_data[close]),
    price_data[date] = DATE(2024, 2, 1),
    ALL(DateTable)
)
```

**Key Features:**
- Fixed reference point for all return calculations
- Ignores date filters (ALL function)
- Ensures consistent baseline across all analyses

---

## Return Metrics

### Total Return %
**Purpose:** Calculates cumulative return from start date to current date.

```dax
Total Return % = 
VAR CurrentDate = MAX(DateTable[Date])
VAR StartPrice = [Starting Price]
VAR LastKnownPrice = 
    CALCULATE(
        LASTNONBLANKVALUE(
            DateTable[Date], 
            IF([Current Price] = 0, BLANK(), [Current Price])
        ),
        DateTable[Date] <= CurrentDate
    )
RETURN
IF(
    ISBLANK(StartPrice) || ISBLANK(LastKnownPrice),
    BLANK(),
    DIVIDE(LastKnownPrice - StartPrice, StartPrice)
)
```

**Key Features:**
- Filters out zero values (data quality)
- Returns BLANK for missing data (prevents division errors)
- Format as percentage in Power BI

**Example:** 
- Start: $100
- Current: $150
- Return: 50%

---

## Risk Metrics

### Volatility Full Period
**Purpose:** Annualized standard deviation of daily returns from start to current date.

```dax
Volatility Full Period = 
VAR CurrentDate = MAX(DateTable[Date])
VAR StartDate = DATE(2024, 2, 1)
VAR VolatilityCalc = 
    CALCULATE(
        STDEVX.P(
            FILTER(
                price_data,
                price_data[date] >= StartDate && 
                price_data[date] <= CurrentDate &&
                NOT(ISBLANK(price_data[Daily_Return]))
            ),
            price_data[Daily_Return]
        ) * SQRT(252) * 100,
        ALL(DateTable)
    )
RETURN
IF(ISBLANK(VolatilityCalc), BLANK(), VolatilityCalc)
```

**Formula Breakdown:**
- `STDEVX.P`: Standard deviation of daily returns
- `SQRT(252)`: Annualize (252 trading days per year)
- `* 100`: Convert to percentage

**Interpretation:**
- 20%: Low volatility (stable)
- 30%: Moderate volatility (S&P 500 typical)
- 50%: High volatility (individual stocks)
- 80%+: Very high volatility (crypto)

---

### Sharpe Ratio
**Purpose:** Risk-adjusted return using total volatility.

```dax
Sharpe Ratio = 
VAR RiskFreeRate = 0.04
VAR CurrentDate = MAX(DateTable[Date])
VAR StartDate = DATE(2024, 2, 1)
VAR Years = DIVIDE(CurrentDate - StartDate, 365.25, 0)
VAR TotalReturn = [Total Return %]
VAR AnnualReturn = 
    IF(
        Years > 0,
        POWER(1 + TotalReturn, 1/Years) - 1,
        BLANK()
    )
VAR VolatilityDecimal = [Volatility Full Period] / 100
RETURN
IF(
    NOT(ISBLANK(AnnualReturn)) && NOT(ISBLANK(VolatilityDecimal)) && VolatilityDecimal > 0,
    DIVIDE(AnnualReturn - RiskFreeRate, VolatilityDecimal, 0),
    BLANK()
)
```

**Formula:** (Return - Risk-Free Rate) / Volatility

**Risk-Free Rate:** 4% (US Treasury Bills)

**Interpretation:**
- < 0: Terrible (losing vs bonds)
- 0-0.5: Poor
- 0.5-1.0: Acceptable
- 1.0-2.0: Good
- 2.0-3.0: Excellent
- > 3.0: Suspicious (check data)

---

### Sortino Ratio
**Purpose:** Risk-adjusted return using only downside volatility.

```dax
Portfolio Sortino Ratio = 
VAR RiskFreeRate = 0.04
VAR CurrentDate = MAX(DateTable[Date])
VAR StartDate = DATE(2024, 2, 1)
VAR Years = DIVIDE(CurrentDate - StartDate, 365.25, 0)
VAR PortfolioReturn = [Portfolio Total Return %]
VAR AnnualReturn = 
    IF(
        Years > 0 && NOT(ISBLANK(PortfolioReturn)),
        POWER(1 + PortfolioReturn, 1/Years) - 1,
        BLANK()
    )
VAR DownsideDeviation = 
    SUMX(
        Portfolio_Config,
        VAR Ticker = Portfolio_Config[ticker]
        VAR AssetWeight = Portfolio_Config[weight]
        VAR AssetDownsideVol = 
            CALCULATE(
                STDEVX.P(
                    FILTER(
                        price_data,
                        price_data[date] >= StartDate &&
                        price_data[date] <= CurrentDate &&
                        price_data[Daily_Return] < 0
                    ),
                    price_data[Daily_Return]
                ) * SQRT(252) * 100,
                price_data[ticker] = Ticker
            )
        RETURN
        IF(NOT(ISBLANK(AssetDownsideVol)), AssetWeight * AssetDownsideVol, 0)
    )
VAR DownsideVolDecimal = DownsideDeviation / 100
RETURN
IF(
    NOT(ISBLANK(AnnualReturn)) && NOT(ISBLANK(DownsideVolDecimal)) && DownsideVolDecimal > 0,
    DIVIDE(AnnualReturn - RiskFreeRate, DownsideVolDecimal, 0),
    BLANK()
)
```

**Key Difference from Sharpe:**
- Only counts negative daily returns in volatility calculation
- Ignores upside volatility (which is good for investors)
- Typically 20-50% higher than Sharpe in bull markets

**Interpretation:**
- Always higher than Sharpe (if returns are positive)
- Larger gap = more upside volatility
- Better measure of investor pain

---

### Maximum Drawdown
**Purpose:** Worst peak-to-trough decline during the period.

```dax
Portfolio Max Drawdown % = 
VAR MaxDate = MAX('DateTable'[Date])
VAR PortfolioValues = 
    ADDCOLUMNS(
        FILTER(
            ALL('DateTable'[Date]),
            'DateTable'[Date] <= MaxDate
        ),
        "@CurrentDate", 'DateTable'[Date],
        "@Value", [Portfolio Current Value]
    )
VAR Drawdowns = 
    ADDCOLUMNS(
        PortfolioValues,
        "@RunningMax", 
            VAR CurrentDt = [@CurrentDate]
            RETURN
            MAXX(
                FILTER(PortfolioValues, [@CurrentDate] <= CurrentDt),
                [@Value]
            )
    )
VAR Result = 
    MINX(
        Drawdowns,
        DIVIDE([@Value] - [@RunningMax], [@RunningMax], 0)
    )
RETURN Result
```

**Formula:** (Trough Price - Peak Price) / Peak Price

**Interpretation:**
- 0 to -10%: Very low risk
- -10% to -20%: Low risk
- -20% to -35%: Moderate (S&P 500 typical)
- -35% to -50%: High risk
- -50% to -80%: Very high risk
- > -80%: Extreme (potential bankruptcy)

---

### Value at Risk (95%)
**Purpose:** Maximum expected loss in one year with 95% confidence.

```dax
Portfolio VaR 95% = 
VAR AnnualReturn = 
    VAR Years = DIVIDE(MAX(DateTable[Date]) - DATE(2024, 2, 1), 365.25, 0)
    VAR TotalReturn = [Portfolio Total Return %]
    RETURN
    IF(Years > 0, POWER(1 + TotalReturn, 1/Years) - 1, BLANK())
VAR VolatilityDecimal = [Portfolio Volatility] / 100
RETURN
IF(
    NOT(ISBLANK(AnnualReturn)) && NOT(ISBLANK(VolatilityDecimal)),
    (AnnualReturn - (1.645 * VolatilityDecimal)) * -1,
    BLANK()
)
```

**Formula:** Return - (1.645 × Volatility)

**1.645:** Z-score for 95% confidence (one-tailed)

**Interpretation:**
- VaR of 15% means: "95% chance we won't lose more than 15% in a year"
- 5% chance we lose MORE than 15%
- Used by banks for capital requirements

---

## Portfolio Measures

### Portfolio Current Value
**Purpose:** Sum of all asset positions at current value.

```dax
Portfolio Current Value = 
VAR CurrentDate = MAX(DateTable[Date])
VAR PortfolioValue = 
    SUMX(
        Portfolio_Config,
        VAR Ticker = Portfolio_Config[ticker]
        VAR InitialInv = Portfolio_Config[initial_investment]
        VAR AssetReturn = 
            CALCULATE(
                [Total Return %],
                price_data[ticker] = Ticker
            )
        VAR CurrentValue = 
            IF(
                NOT(ISBLANK(AssetReturn)),
                InitialInv * (1 + AssetReturn),
                InitialInv
            )
        RETURN CurrentValue
    )
RETURN IF(ISBLANK(PortfolioValue), BLANK(), PortfolioValue)
```

**Example:**
- AAPL: $20k invested, +39% return = $27,800
- MSFT: $10k invested, +28% return = $12,800
- Total: $40,600

---

### Portfolio Total Return %
**Purpose:** Overall portfolio return from initial investment.

```dax
Portfolio Total Return % = 
VAR InitialValue = SUM(Portfolio_Config[initial_investment])
VAR CurrentValue = [Portfolio Current Value]
RETURN
IF(
    NOT(ISBLANK(CurrentValue)) && InitialValue > 0,
    DIVIDE(CurrentValue - InitialValue, InitialValue, 0),
    BLANK()
)
```

---

### Portfolio Volatility
**Purpose:** Weighted average volatility of portfolio assets.

```dax
Portfolio Volatility = 
SUMX(
    Portfolio_Config,
    VAR Ticker = Portfolio_Config[ticker]
    VAR AssetWeight = Portfolio_Config[weight]
    VAR AssetVol = 
        CALCULATE(
            [Volatility Full Period],
            price_data[ticker] = Ticker
        )
    RETURN
    IF(NOT(ISBLANK(AssetVol)), AssetWeight * AssetVol, 0)
)
```

**Note:** This is a simplified calculation. True portfolio volatility requires correlation matrix.

**Example:**
- 40% S&P 500 at 16% vol = 6.4%
- 30% Gold at 20% vol = 6.0%
- 20% AAPL at 28% vol = 5.6%
- 10% MSFT at 24% vol = 2.4%
- **Portfolio Volatility: 20.4%**

---

### Portfolio YoY Growth %
**Purpose:** Year-over-year growth rate (1-year return).

```dax
Portfolio YoY Growth % = 
VAR CurrentDate = MAX(DateTable[Date])
VAR OneYearAgo = CurrentDate - 365
VAR CurrentValue = [Portfolio Current Value]
VAR ValueOneYearAgo = 
    CALCULATE(
        [Portfolio Current Value],
        DateTable[Date] = OneYearAgo
    )
VAR ValueOneYearAgoAdjusted = 
    IF(
        ISBLANK(ValueOneYearAgo),
        CALCULATE(
            LASTNONBLANKVALUE(
                DateTable[Date],
                [Portfolio Current Value]
            ),
            DateTable[Date] <= OneYearAgo,
            DateTable[Date] >= OneYearAgo - 7
        ),
        ValueOneYearAgo
    )
RETURN
IF(
    NOT(ISBLANK(CurrentValue)) && NOT(ISBLANK(ValueOneYearAgoAdjusted)) && ValueOneYearAgoAdjusted > 0,
    DIVIDE(CurrentValue - ValueOneYearAgoAdjusted, ValueOneYearAgoAdjusted, 0),
    BLANK()
)
```

**Use Case:** Card visual showing recent performance momentum.

---

## Scenario Analysis Measures

### Asset Max Drawdown %
**Purpose:** Historical worst drawdown for individual asset.

```dax
Asset Max Drawdown % = 
VAR CurrentTicker = SELECTEDVALUE(price_data[ticker])
RETURN
IF(
    NOT(ISBLANK(CurrentTicker)),
    MINX(
        FILTER(
            ALL(price_data),
            price_data[ticker] = CurrentTicker
        ),
        VAR CurrentDate = price_data[date]
        VAR CurrentPrice = price_data[close]
        VAR RunningMax = 
            CALCULATE(
                MAX(price_data[close]),
                FILTER(
                    ALL(price_data),
                    price_data[ticker] = CurrentTicker &&
                    price_data[date] <= CurrentDate
                )
            )
        RETURN
        DIVIDE(CurrentPrice - RunningMax, RunningMax, 0)
    ),
    BLANK()
)
```

---

### Portfolio Value Worst Case
**Purpose:** Portfolio value if all assets hit their historical worst simultaneously.

```dax
Portfolio Value Worst Case = 
SUMX(
    Portfolio_Config,
    VAR Ticker = Portfolio_Config[ticker]
    VAR InitialInv = Portfolio_Config[initial_investment]
    VAR AssetReturn = CALCULATE([Total Return %], price_data[ticker] = Ticker)
    VAR AssetMaxDD = CALCULATE([Asset Max Drawdown %], price_data[ticker] = Ticker)
    VAR CurrentValue = InitialInv * (1 + AssetReturn)
    VAR WorstCaseValue = CurrentValue * (1 + AssetMaxDD)
    RETURN WorstCaseValue
)
```

**Example:**
- Current portfolio value: $200k
- NVDA hit -60% worst drawdown historically
- Bitcoin hit -73% worst drawdown
- Worst case value: $132k (-34% overall)

---

### Worst Case Loss %
**Purpose:** Percentage loss in worst-case scenario.

```dax
Worst Case Loss % = 
DIVIDE(
    [Portfolio Value Worst Case] - [Portfolio Current Value],
    [Portfolio Current Value],
    0
)
```

---

### Recovery Needed %
**Purpose:** Return required to recover from worst case to current value.

```dax
Recovery Needed % = 
VAR Current = [Portfolio Current Value]
VAR WorstCase = [Portfolio Value Worst Case]
RETURN
IF(
    NOT(ISBLANK(Current)) && NOT(ISBLANK(WorstCase)) && WorstCase > 0,
    DIVIDE(Current - WorstCase, WorstCase, 0),
    BLANK()
)
```

**Key Insight:** Recovery is always harder than the loss!

**Example:**
- Lose 50%: $100k → $50k
- Need +100% to recover: $50k → $100k

---

### Bull Market Scenario (+20%)
**Purpose:** Portfolio value if market rises 20%.

```dax
Portfolio Value Bull Market = 
[Portfolio Current Value] * 1.20
```

---

### Correction Scenario (-10%)
**Purpose:** Portfolio value in a market correction.

```dax
Portfolio Value Correction = 
[Portfolio Current Value] * 0.90
```

---

## Calculated Columns

### Daily_Return
**Purpose:** Percentage change from previous trading day.

```dax
Daily_Return = 
VAR PrevClose = 
    CALCULATE(
        AVERAGE(price_data[close]),
        FILTER(
            ALL(price_data), 
            price_data[ticker] = EARLIER(price_data[ticker]) &&
            price_data[date] = EARLIER(price_data[date]) - 1
        )
    )
RETURN
IF(ISBLANK(PrevClose), BLANK(), DIVIDE(price_data[close] - PrevClose, PrevClose, 0))
```

**Note:** This is a calculated column, not a measure. It's computed once per row and stored.

---

## Performance Tips

**Optimization Best Practices:**

1. **Use Variables:** Store intermediate calculations in VAR to avoid recomputation
2. **CALCULATE Filters:** Use specific filters instead of relationships for portfolio measures
3. **LASTNONBLANK:** Essential for handling weekends in time series
4. **ALL() vs ALLEXCEPT():** Use ALL() when you need to ignore specific filters
5. **Error Handling:** Always check for BLANK values before division

**Common Pitfalls:**

- Don't use `ALL(DateTable)` inside portfolio measures (breaks date context)
- Always format return % and volatility % as percentages in Power BI
- Use `SELECTEDVALUE` when you need explicit ticker filtering
- Remember that SUMX iterates row by row (can be slow with large datasets)

---

**Last Updated:** February 2026

**Total Measures:** 20+

**Complexity:** Intermediate to Advanced DAX
