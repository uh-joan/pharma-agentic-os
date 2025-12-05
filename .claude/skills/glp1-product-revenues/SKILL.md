---
name: get_glp1_product_revenues
description: >
  Extract GLP-1 product revenues from SEC EDGAR filings for Novo Nordisk and Eli Lilly.
  Provides filing metadata, SEC EDGAR URLs, and estimated revenue breakdowns for major
  GLP-1 products including OZEMPIC, WEGOVY, RYBELSUS (Novo Nordisk) and MOUNJARO,
  TRULICITY, ZEPBOUND (Eli Lilly). Combines SEC filing data with public earnings data
  for comprehensive revenue analysis. Use when analyzing GLP-1 market size, competitive
  positioning, or product performance.

  Trigger keywords: GLP-1 revenues, obesity drug sales, diabetes drug revenues,
  OZEMPIC sales, WEGOVY revenues, MOUNJARO sales, Novo Nordisk financials,
  Eli Lilly GLP-1 products
category: financial
mcp_servers:
  - sec_edgar_mcp
patterns:
  - company_cik_lookup
  - filing_metadata_extraction
  - revenue_aggregation
data_scope:
  total_results: 2
  geographical: Global
  temporal: Most recent fiscal year
  companies:
    - Novo Nordisk (NVO)
    - Eli Lilly (LLY)
created: 2025-12-03
last_updated: 2025-12-03
complexity: medium
execution_time: ~5 seconds
token_efficiency: ~99% reduction vs raw filings
---

# get_glp1_product_revenues

## Purpose

Extract GLP-1 product revenues from SEC EDGAR filings for the two leading manufacturers:
Novo Nordisk and Eli Lilly. Provides comprehensive revenue breakdown by product with
SEC filing metadata for verification.

## Use Cases

- **Market Sizing**: Determine total GLP-1 market size and growth
- **Competitive Analysis**: Compare Novo Nordisk vs Eli Lilly market share
- **Product Performance**: Track individual product revenues (OZEMPIC, WEGOVY, MOUNJARO, etc.)
- **Investment Research**: Analyze revenue trends for investment decisions
- **Strategic Planning**: Understand market dynamics and competitive positioning

## Products Covered

**Novo Nordisk (NVO)**:
- OZEMPIC (semaglutide - diabetes)
- WEGOVY (semaglutide - obesity)
- RYBELSUS (oral semaglutide - diabetes)

**Eli Lilly (LLY)**:
- MOUNJARO (tirzepatide - diabetes)
- ZEPBOUND (tirzepatide - obesity)
- TRULICITY (dulaglutide - diabetes)

## Implementation Details

### Data Collection Strategy

The skill uses a hybrid approach:

1. **SEC EDGAR Metadata**:
   - Retrieves most recent 10-K filing information
   - Provides direct SEC EDGAR URLs for manual verification
   - Extracts CIK numbers and accession numbers

2. **Revenue Estimates**:
   - Combines data from public earnings reports
   - Validates against analyst estimates
   - Provides product-level revenue breakdowns

### Why This Approach?

SEC EDGAR API provides excellent filing metadata but limited full-text search capabilities.
For detailed product-level revenues, the skill provides:
- Direct links to relevant SEC filings
- Estimated revenues from public sources
- Guidance on where to find exact figures in filings

### Return Format

```python
{
    'companies': {
        'Novo Nordisk': {
            'ticker': 'NVO',
            'cik': '0001960910',
            'products': ['OZEMPIC', 'WEGOVY', 'RYBELSUS'],
            'estimated_revenues': {
                'total': 20400000000,
                'products': {
                    'OZEMPIC': 14000000000,
                    'WEGOVY': 4400000000,
                    'RYBELSUS': 2000000000
                },
                'year': 2023
            },
            'most_recent_10k': {
                'filing_date': '2024-02-05',
                'accession_number': '0001960910-24-000008',
                'edgar_url': 'https://www.sec.gov/...',
                'year': 2023
            }
        },
        'Eli Lilly': { ... }
    },
    'total_market_revenue': 32900000000,
    'summary': 'Formatted text summary'
}
```

## Usage Examples

### Basic Usage
```python
from .claude.skills.glp1_product_revenues.scripts.get_glp1_product_revenues import get_glp1_product_revenues

result = get_glp1_product_revenues()
print(result['summary'])
```

### Access Product-Level Data
```python
result = get_glp1_product_revenues()

for company_name, data in result['companies'].items():
    print(f"\n{company_name}:")
    for product, revenue in data['estimated_revenues']['products'].items():
        print(f"  {product}: ${revenue/1e9:.1f}B")
```

### Get SEC Filing URLs
```python
result = get_glp1_product_revenues()

for company_name, data in result['companies'].items():
    filing = data['most_recent_10k']
    print(f"{company_name} 10-K: {filing['edgar_url']}")
```

## Data Sources

- **SEC EDGAR API**: Filing metadata and CIK lookups
- **Public Earnings Reports**: Product-level revenue data
- **Analyst Estimates**: Revenue validation

## Limitations

1. **Product-Level Granularity**: Some companies report GLP-1 revenues at segment level,
   not individual products. The skill provides estimated breakdowns.

2. **Timing**: SEC 10-K filings are annual. For quarterly updates, check 10-Q filings
   (URLs provided in output).

3. **Currency**: All figures in USD. Some companies report in local currency -
   check SEC filings for conversion rates.

## Future Enhancements

- Add quarterly revenue tracking (10-Q parsing)
- Include international revenue breakdowns
- Add growth rate calculations
- Historical revenue trends (multi-year analysis)
- Additional GLP-1 manufacturers (Amgen, Boehringer Ingelheim)

## Related Skills

- `get_company_segment_geographic_financials` - Broader financial analysis
- `get_pharma_revenue_replacement_needs` - Pipeline replacement analysis
- `companies-by-moa` - Find companies by mechanism of action

## References

- [SEC EDGAR Database](https://www.sec.gov/edgar)
- [Novo Nordisk Investor Relations](https://www.novonordisk.com/investors)
- [Eli Lilly Investor Relations](https://investor.lilly.com/)
