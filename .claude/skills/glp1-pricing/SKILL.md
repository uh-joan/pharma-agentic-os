---
name: get_glp1_pricing_data
description: >
  Extract Medicare Part D pricing data for GLP-1 drugs from CMS including OZEMPIC,
  WEGOVY, RYBELSUS, MOUNJARO, ZEPBOUND, and TRULICITY. Retrieves average costs,
  total Medicare spending, beneficiary counts, and coverage status. Use this skill
  when analyzing GLP-1 drug costs, Medicare reimbursement, pricing trends, or
  market access in the diabetes/obesity space. Trigger keywords: "GLP-1 pricing",
  "Medicare cost", "drug spending", "reimbursement", "CMS data".
category: financial
mcp_servers:
  - healthcare_mcp
patterns:
  - json_parsing
  - error_handling
  - data_aggregation
data_scope:
  total_results: 6 drugs
  geographical: US Medicare
  temporal: 2022 (most recent CMS data)
  data_source: CMS Medicare Part D Spending by Drug
created: 2025-12-03
last_updated: 2025-12-03
complexity: medium
execution_time: ~5 seconds
token_efficiency: ~99% reduction vs raw CMS data
---

# get_glp1_pricing_data

## Purpose
Extract Medicare Part D pricing and spending data for major GLP-1 receptor agonist drugs from CMS (Centers for Medicare & Medicaid Services). Provides comprehensive view of Medicare reimbursement, beneficiary utilization, and total spending for the GLP-1 drug class.

## Usage
Use this skill when you need to:
- Analyze GLP-1 drug pricing and reimbursement in Medicare
- Compare Medicare spending across different GLP-1 brands
- Understand beneficiary utilization patterns
- Assess market access and coverage status
- Support pricing strategy or market access decisions
- Analyze competitive dynamics in the diabetes/obesity market

**Trigger keywords**: "GLP-1 pricing", "Medicare cost", "drug spending", "reimbursement", "CMS data", "Part D", "beneficiary count"

## Drugs Covered
- **Semaglutide**: OZEMPIC, WEGOVY, RYBELSUS
- **Tirzepatide**: MOUNJARO, ZEPBOUND
- **Dulaglutide**: TRULICITY

## Data Retrieved
For each drug:
- Generic name
- Average cost per dosage unit
- Total Medicare spending (annual)
- Beneficiary count
- Data availability status
- Most recent year (typically 2022)

## Implementation Details

### MCP Server
Uses `healthcare_mcp` server's `cms_drug_spending` function to query:
- CMS Medicare Part D Spending by Drug dataset
- Queries by generic name (covers multiple brands)
- Returns JSON with spending, beneficiary, and cost data

### Data Processing
1. **Query by generic name**: Groups brands by generic (semaglutide, tirzepatide, dulaglutide)
2. **Parse CMS response**: Extracts spending, beneficiary counts, and costs
3. **Approximate brand splits**: Divides generic totals across brands
4. **Error handling**: Gracefully handles missing data or API errors
5. **Summary generation**: Aggregates total spending and beneficiary counts

### Return Format
```python
{
    'total_drugs_queried': 6,
    'total_drugs_found': 6,
    'total_spending': float,  # Total Medicare spending
    'total_beneficiaries': int,  # Total beneficiary count
    'drugs': {
        'OZEMPIC': {
            'generic_name': 'semaglutide',
            'average_cost_per_unit': float,
            'total_spending': float,
            'beneficiary_count': int,
            'year': 2022,
            'data_available': True
        },
        # ... other drugs
    },
    'summary': str  # Human-readable summary
}
```

## Data Limitations
- **Lag time**: CMS data typically lags 1-2 years (most recent is 2022)
- **Aggregation**: Generic-level data split across brands (approximation)
- **Coverage**: Medicare Part D only (not commercial insurance)
- **Geography**: US Medicare population only

## Example Output
```
GLP-1 Drug Pricing Analysis (Medicare Part D - 2022)

Total brands queried: 6
Brands with data: 6

Total Medicare spending: $5,000,000,000
Total beneficiaries: 500,000

Drugs analyzed:
- Semaglutide: OZEMPIC, WEGOVY, RYBELSUS
- Tirzepatide: MOUNJARO, ZEPBOUND
- Dulaglutide: TRULICITY
```

## Token Efficiency
- **Raw CMS data**: ~50,000 tokens
- **Skill output**: ~500 tokens
- **Reduction**: ~99%

## Related Skills
- `get_glp1_trials` - Clinical trial data
- `get_glp1_fda_drugs` - FDA approval and labeling data
- `get_company_segment_geographic_financials` - Company revenue data

## Notes
- CMS updates Part D spending data annually
- MOUNJARO and ZEPBOUND may have limited historical data (newer approvals)
- Consider checking FDA approval dates when interpreting spending trends
