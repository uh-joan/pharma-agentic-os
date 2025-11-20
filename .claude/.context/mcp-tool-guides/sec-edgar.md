# SEC EDGAR MCP Server - Complete API Guide

**Server**: `sec-mcp-server`
**Tool**: `sec-edgar`
**Data Source**: U.S. Securities and Exchange Commission EDGAR database
**Response Format**: JSON
**Coverage**: 13,000+ public companies, 30+ million filings since 1994

---

## 🔴 CRITICAL: CIK WORKFLOW PATTERN

### MANDATORY Two-Step Workflow

**Nearly all SEC EDGAR queries require CIK (Central Index Key), not ticker symbols.**

```python
# ✅ CORRECT: Ticker → CIK → Query
# Step 1: Convert ticker to CIK
cik_result = get_company_cik(ticker="AAPL")
cik = cik_result['cik']  # "0000320193"

# Step 2: Use CIK for all subsequent queries
filings = get_company_submissions(cik_or_ticker=cik)
facts = get_company_facts(cik_or_ticker=cik)

# ❌ WRONG: Direct ticker usage (may fail)
filings = get_company_submissions(cik_or_ticker="AAPL")  # Unreliable
```

### CIK Format Requirements

```python
# ✅ CORRECT: 10-digit with leading zeros
cik = "0000320193"  # Apple
cik = "0001318605"  # Tesla

# ❌ WRONG: Without leading zeros
cik = "320193"      # Will fail
cik = "1318605"     # Will fail
```

### Why CIK is Required

1. **Unique Identifier**: Tickers can change (company renames, mergers)
2. **SEC Standard**: EDGAR API uses CIK as primary key
3. **Historical Data**: CIK remains constant across ticker changes
4. **Reliability**: Direct ticker queries may fail or return wrong company

---

## Quick Reference

### Available Methods (11 total)

| Method | Purpose | CIK Required? | Common Use |
|--------|---------|---------------|------------|
| `search_companies` | Find companies by name | No | Initial search |
| `get_company_cik` | Convert ticker to CIK | No | **STEP 1** for all queries |
| `get_company_submissions` | Complete filing history | Yes | Get accession numbers |
| `get_company_facts` | All XBRL financial data | Yes | Comprehensive financials |
| `get_company_concept` | Specific financial metric | Yes | Time series for one metric |
| `get_frames_data` | Cross-company aggregation | No | Industry benchmarking |
| `filter_filings` | Filter by form type/date | No | Narrow filing results |
| `get_dimensional_facts` | XBRL with dimensional context | Yes | Segment/geography breakdown |
| `search_facts_by_value` | Find facts by target value | Yes | Revenue/cost matching |
| `build_fact_table` | Comprehensive fact analysis | Yes | Multi-dimensional tables |
| `time_series_dimensional_analysis` | Subsegment time series | Yes | Geographic/segment trends |

### Common Filing Types

| Form | Purpose | Frequency | Key Content |
|------|---------|-----------|-------------|
| `10-K` | Annual report | Annual | Full financials, MD&A, risk factors, business overview |
| `10-Q` | Quarterly report | Quarterly | Interim financials, updates |
| `8-K` | Current report | Event-driven | M&A, executive changes, material events |
| `20-F` | Foreign annual | Annual | Non-US company annual report |
| `DEF 14A` | Proxy statement | Annual | Executive compensation, board votes |
| `S-1` | IPO registration | One-time | IPO prospectus |
| `4` | Insider trading | Per transaction | Stock purchases/sales by insiders |
| `3` | Initial insider ownership | One-time | New insider stock holdings |

### Common XBRL Concepts (US GAAP)

| Tag | Concept | Financial Statement |
|-----|---------|---------------------|
| `Assets` | Total assets | Balance sheet |
| `Revenues` | Total revenues/sales | Income statement |
| `NetIncomeLoss` | Net income | Income statement |
| `StockholdersEquity` | Shareholders' equity | Balance sheet |
| `Cash` | Cash and equivalents | Balance sheet |
| `Liabilities` | Total liabilities | Balance sheet |
| `OperatingIncomeLoss` | Operating income | Income statement |
| `CostOfRevenue` | Cost of goods sold | Income statement |
| `ResearchAndDevelopmentExpense` | R&D expense | Income statement |
| `GrossProfit` | Gross profit | Income statement |

---

## Token Usage Guidelines

| Method | Approx. Tokens | Recommendation |
|--------|---------------|----------------|
| `search_companies` | 100-300 | ✅ Efficient for discovery |
| `get_company_cik` | 50-100 | ✅ Always use first |
| `get_company_submissions` | 2,000-5,000 | ⚠️ Filter immediately |
| `get_company_facts` | 10,000-30,000 | 🔴 Use get_company_concept instead |
| `get_company_concept` | 500-2,000 | ✅ Recommended for single metrics |
| `get_frames_data` | 5,000-50,000 | ⚠️ Use for benchmarking only |
| `filter_filings` | 200-1,000 | ✅ Essential for narrowing |
| Dimensional methods | 500-5,000 | ✅ Good for segment analysis |

**Token Optimization Tips**:
1. ALWAYS get CIK first (`get_company_cik`)
2. Use `get_company_concept` for single metrics (not `get_company_facts`)
3. Filter filings by form type and date range
4. Filter for 10-K only when analyzing annual data
5. Use `filter_filings` immediately after `get_company_submissions`

---

## Summary

**SEC EDGAR MCP Server** provides comprehensive access to U.S. public company filings and financial data:

✅ **11 powerful methods** from basic search to dimensional analysis
✅ **CIK workflow** ensures reliable company identification
✅ **XBRL standardization** for structured financial data
✅ **Dimensional analysis** for segment/geography breakdowns
✅ **Cross-company queries** for industry benchmarking
✅ **30+ filing types** from 10-K annual reports to 8-K M&A events

**Critical Pattern**: Ticker → CIK → Query (always STEP 1)

**Token Efficient**: Use `get_company_concept` (500-2k tokens) instead of `get_company_facts` (10-30k tokens)

**Perfect For**: Financial analysis, competitive intelligence, M&A tracking, segment performance, industry benchmarking, regulatory compliance monitoring
