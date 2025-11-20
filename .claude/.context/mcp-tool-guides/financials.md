# Financials MCP Server - Complete API Guide

**Server**: `financials-mcp-server`
**Tool**: `financial-intelligence`
**Data Sources**: Yahoo Finance + Federal Reserve Economic Data (FRED)
**Response Format**: JSON
**Coverage**: Real-time market data + 800,000+ economic series

---

## 🔴 CRITICAL METHOD CATEGORIES

### Three Method Categories

```python
# Category 1: Stock Analysis (11 methods)
# Use for: Company fundamentals, pricing, financial metrics
method = "stock_profile"  # Or stock_summary, stock_financials, etc.

# Category 2: Advanced Analytics (4 methods)
# Use for: News sentiment, peer comparison, screening, correlation
method = "stock_news"  # Or stock_peers, stock_screener, stock_correlation

# Category 3: Economic Data (14 methods)
# Use for: Market indices, economic indicators, FRED data
method = "market_indices"  # Or economic_indicators, fred_series_search, etc.
```

---

## Quick Reference

### Stock Analysis Methods (11 total)

| Method | Purpose | Key Data |
|--------|---------|----------|
| `stock_profile` | Company details | Industry, employees, business summary |
| `stock_summary` | Key metrics | Market cap, P/E, EPS, beta |
| `stock_pricing` | Real-time prices | Current price, volume, daily ranges |
| `stock_financials` | Cash flow & ratios | Income highlights, balance sheet |
| `stock_revenue_breakdown` | Segment analysis | Revenue by business & geography |
| `stock_earnings_history` | Historical EPS | Earnings trends & analysis |
| `stock_estimates` | Analyst forecasts | EPS/revenue estimates, targets |
| `stock_recommendations` | Analyst ratings | Buy/hold/sell consensus |
| `stock_esg` | ESG scores | Environmental, social, governance |
| `stock_dividends` | Dividend history | Yield, payout ratios |
| `stock_technicals` | Technical indicators | Moving averages, volatility |

### Economic Data Methods (14 FRED methods)

| Method | Purpose | Example |
|--------|---------|---------|
| `fred_series_search` | Find economic series | Search "unemployment", "GDP" |
| `fred_series_data` | Get specific series | Fetch UNRATE (unemployment rate) |
| `fred_categories` | Browse categories | Hierarchical economic data structure |
| `fred_releases` | Economic calendar | Release schedules |
| `economic_indicators` | Macro dashboard | GDP, unemployment, inflation, rates |
| `market_indices` | Major indices | S&P 500, NASDAQ, DOW, VIX |

---

## Common Search Patterns

### Pattern 1: Company Financial Analysis
```python
from mcp.servers.financials_mcp import financial_intelligence

# Get comprehensive company profile
profile = financial_intelligence(
    method="stock_profile",
    symbol="PFE"  # Pfizer
)

print(f"{profile['companyName']}")
print(f"Industry: {profile['industry']}")
print(f"Employees: {profile['fullTimeEmployees']:,}")
print(f"\nBusiness Summary:")
print(profile['longBusinessSummary'])

# Get key financial metrics
summary = financial_intelligence(
    method="stock_summary",
    symbol="PFE"
)

print(f"\nKey Metrics:")
print(f"Market Cap: ${summary['marketCap']:,.0f}")
print(f"P/E Ratio: {summary['trailingPE']:.2f}")
print(f"Dividend Yield: {summary['dividendYield']:.2%}")
```

### Pattern 2: Sector Peer Comparison
```python
# Get peer analysis
peers = financial_intelligence(
    method="stock_peers",
    symbol="PFE"
)

print("Pfizer vs Pharma Peers:")
print(f"{'Company':<20} {'Market Cap':<15} {'P/E':<8} {'Div Yield'}")
print("-" * 55)

for peer in peers['peers']:
    name = peer['symbol']
    mcap = peer['marketCap']
    pe = peer.get('pe', 'N/A')
    div_yield = peer.get('dividendYield', 0)

    print(f"{name:<20} ${mcap:>13,.0f} {pe:>7} {div_yield:>7.2%}")
```

### Pattern 3: Economic Indicators Dashboard
```python
# Get comprehensive macro dashboard
indicators = financial_intelligence(
    method="economic_indicators",
    symbol=""  # Not needed for economic data
)

print("Economic Dashboard:")
print(f"GDP Growth: {indicators['gdp_growth']:.2%}")
print(f"Unemployment: {indicators['unemployment_rate']:.1f}%")
print(f"Inflation (CPI): {indicators['inflation_rate']:.2%}")
print(f"10-Year Treasury: {indicators['10y_treasury']:.2%}")
print(f"Fed Funds Rate: {indicators['fed_funds_rate']:.2%}")
```

### Pattern 4: FRED Economic Data Search
```python
# Search for specific economic series
search = financial_intelligence(
    method="fred_series_search",
    symbol="unemployment rate"
)

print("Unemployment Rate Series:")
for series in search['series'][:5]:
    series_id = series['id']
    title = series['title']
    print(f"{series_id}: {title}")

# Get specific series data
data = financial_intelligence(
    method="fred_series_data",
    symbol="UNRATE"  # Unemployment rate
)

print(f"\nCurrent Unemployment Rate: {data['latest_value']:.1f}%")
```

### Pattern 5: News Sentiment Analysis
```python
# Get stock-specific news with sentiment
news = financial_intelligence(
    method="stock_news",
    symbol="PFE",
    search_type="stock"  # Or "general" for broader search
)

print("Recent Pfizer News:")
for article in news['articles'][:5]:
    title = article['title']
    sentiment = article.get('sentiment', 'neutral')
    published = article['publishedAt']

    sentiment_emoji = {"positive": "✅", "negative": "❌", "neutral": "➖"}
    print(f"\n{sentiment_emoji.get(sentiment, '')} {title}")
    print(f"   {published}")
```

---

## Token Usage Guidelines

| Method Category | Approx. Tokens | Recommendation |
|----------------|---------------|----------------|
| Stock profile/summary | 300-800 | ✅ Efficient for fundamentals |
| Stock financials | 1,000-2,000 | ✅ Good for detailed analysis |
| Stock news | 500-1,500 | ⚠️ Depends on article count |
| Economic indicators | 400-600 | ✅ Efficient dashboard |
| FRED series search | 200-500 | ✅ Good for discovery |
| FRED series data | 300-1,000 | ✅ Depends on timeframe |

**Token Optimization Tips**:
1. Use specific methods (stock_summary vs stock_financials) based on need
2. Limit news article counts when possible
3. Use FRED series search before fetching full series
4. Cache economic indicator data (changes infrequently)
5. Use market_indices for quick market overview

---

## Summary

**Financials MCP Server** provides real-time market and economic data:

✅ **26 total methods** covering stocks, analytics, and economic data
✅ **Yahoo Finance integration** for real-time market data
✅ **FRED integration** for 800,000+ economic series
✅ **News sentiment analysis** for market intelligence
✅ **Peer comparison** and stock screening capabilities

**Critical Pattern**: Choose method based on data need (profile vs pricing vs financials vs economic)

**Token Efficient**: Use specific methods, limit article counts, cache economic data

**Perfect For**: Company financial analysis, market monitoring, economic research, competitive analysis, investment research
