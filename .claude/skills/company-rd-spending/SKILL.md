---
name: get_company_rd_spending
description: >
  Extract quarterly R&D spending time series from SEC EDGAR filings with revenue
  context and year-over-year growth analysis. Provides strategic insights into
  company investment patterns, R&D intensity trends, and innovation commitment.
---
# get_company_rd_spending


## Sample Queries

Examples of user queries that would trigger reuse of this skill:

1. `@agent-pharma-search-specialist What is Medtronic's R&D spending trend over the last 8 quarters?`
2. `@agent-pharma-search-specialist Analyze Pfizer's R&D intensity and innovation investment patterns from SEC filings`
3. `@agent-pharma-search-specialist Track Abbott's year-over-year R&D spending growth from EDGAR data`
4. `@agent-pharma-search-specialist Compare Eli Lilly's R&D expenditure as a percentage of revenue`
5. `@agent-pharma-search-specialist Extract Bristol Myers Squibb's quarterly R&D spending and calculate R&D intensity`


## Purpose

Extracts quarterly R&D spending data from SEC EDGAR filings to analyze research investment patterns, calculate R&D intensity (% of revenue), and track year-over-year growth trends.

## Usage

**Basic Usage**:
```python
from .claude.skills.company_rd_spending.scripts.get_company_rd_spending import get_company_rd_spending

# Get 2 years of R&D data for Medtronic
result = get_company_rd_spending(ticker="MDT", quarters=8)
print(result['summary'])
```

**Command Line**:
```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/company-rd-spending/scripts/get_company_rd_spending.py MDT 8
```

**Parameters**:
- `ticker` (str): Company ticker symbol (e.g., "MDT", "ABBV", "PFE")
- `quarters` (int): Number of recent quarters to analyze (default 8)

**Returns**:
```python
{
    'total_quarters': int,           # Number of quarters retrieved
    'company_name': str,             # Official SEC entity name
    'data': [                        # List of quarterly records
        {
            'end_date': str,         # Fiscal quarter end (YYYY-MM-DD)
            'rd_expense': int,       # R&D spending in USD
            'revenue': int,          # Total revenue in USD
            'rd_intensity': float,   # R&D as % of revenue
            'yoy_growth': float,     # YoY growth vs same quarter prior year
            'form': str,             # SEC form (10-Q or 10-K)
            'frame': str             # Fiscal frame (e.g., CY2024Q2)
        }
    ],
    'summary': str                   # Formatted table for display
}
```

## Implementation Details

**Data Source**: SEC EDGAR Company Facts API (US-GAAP taxonomy)

**XBRL Concepts Extracted**:
- `ResearchAndDevelopmentExpense` - Primary R&D spending concept
- `Revenues` / `RevenueFromContractWithCustomerExcludingAssessedTax` - Revenue context

**Calculations**:
- **R&D Intensity**: (R&D Expense / Revenue) × 100
- **YoY Growth**: ((Current Q - Same Q Prior Year) / Same Q Prior Year) × 100

## Use Cases

- Compare R&D investment levels across competitors
- Identify companies increasing/decreasing innovation spend
- Assess pipeline commitment through spending trends
- Evaluate R&D efficiency and productivity
- Track R&D intensity vs industry benchmarks

## Limitations

- Only available for US public companies (SEC filers)
- Requires standard US-GAAP taxonomy reporting
- YoY growth requires 4+ quarters of historical data

## Verification Results

All checks passed ✓:
- Execution successful
- Data retrieved (8 quarters for MDT)
- Complete dataset
- Standalone executable
- Valid schema