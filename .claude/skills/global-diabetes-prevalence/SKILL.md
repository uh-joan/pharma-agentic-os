---
name: get_global_diabetes_prevalence
description: >
  Fetches authoritative global diabetes prevalence data from WHO and Data Commons.
  Provides both prevalence rates (%) and absolute counts (millions of adults).
  Searches multiple indicators/variables to find the most recent and relevant data.
  Returns data suitable for citation in research reports and competitive analyses.

  Use this skill when you need:
  - Official global diabetes statistics to replace uncited claims
  - WHO prevalence rates for global adult population
  - Data Commons absolute counts of people with diabetes
  - Latest available year for diabetes prevalence data
  - Authoritative sources for healthcare market sizing

  Trigger keywords: "global diabetes", "diabetes prevalence", "how many people diabetes",
  "IDF diabetes statistics", "WHO diabetes data", "worldwide diabetes"
category: epidemiology
mcp_servers:
  - who_mcp
  - datacommons_mcp
patterns:
  - multi_server_query
  - search_and_retrieve
  - latest_data_extraction
data_scope:
  total_results: 2
  geographical: Global
  temporal: Latest available (typically 2019-2021)
created: 2025-12-03
last_updated: 2025-12-03
complexity: medium
execution_time: ~5 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_global_diabetes_prevalence

## Purpose

Fetches authoritative global diabetes prevalence data from two complementary sources:

1. **WHO (World Health Organization)**: Provides prevalence rates (% of adult population)
2. **Data Commons**: Provides absolute counts (total people with diabetes globally)

This skill is designed to replace uncited claims (like "537M adults globally (IDF 2021)") with
authoritative, properly sourced data suitable for academic and business use.

## Usage

### Direct Execution
```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/global-diabetes-prevalence/scripts/get_global_diabetes_prevalence.py
```

### Import and Use
```python
from .claude.skills.global_diabetes_prevalence.scripts.get_global_diabetes_prevalence import get_global_diabetes_prevalence

result = get_global_diabetes_prevalence()
print(result['summary_text'])

# Access structured data
who_data = result['summary']['who']
dc_data = result['summary']['datacommons']
```

## Output Format

Returns a dictionary with:
```python
{
    'who_data': {
        'indicator_code': { ... },
        # Multiple indicators with full data
    },
    'datacommons_data': {
        'stat_var_id': { ... },
        # Multiple stat vars with full data
    },
    'summary': {
        'who': {
            'indicator_code': 'NCD_GLUC_04',
            'indicator_name': 'Diabetes prevalence',
            'value': 8.5,
            'year': 2014,
            'unit': '%'
        },
        'datacommons': {
            'stat_var_id': 'Count_Person_Diabetes',
            'stat_var_name': 'People with diabetes',
            'value': 537000000,
            'value_millions': 537.0,
            'date': '2021'
        }
    },
    'summary_text': "Formatted summary for display"
}
```

## Implementation Details

### Multi-Server Strategy
This skill demonstrates the multi-server query pattern:
1. Search for relevant indicators/variables in each server
2. Try multiple options to find best available data
3. Extract latest values from each source
4. Combine into unified summary

### Data Source Selection
- **WHO**: Searches for "diabetes prevalence adults" indicators
  - Tries top 3 most relevant indicators
  - Extracts latest year with valid data
- **Data Commons**: Searches for "diabetes count adults global" variables
  - Tries top 5 most relevant stat vars
  - Converts large numbers to millions for readability

### Error Handling
- Gracefully handles missing data from either source
- Continues execution even if one source fails
- Reports which sources succeeded/failed
- Provides detailed error messages for debugging

## Data Quality

Both sources provide:
- ✅ Official statistics from recognized global health authorities
- ✅ Suitable for citation in research and reports
- ✅ Regularly updated (typically 1-2 year lag from collection)
- ✅ Peer-reviewed methodologies
- ✅ Transparent data collection processes

## Example Use Cases

1. **Market Sizing**: "How many people globally have diabetes?"
   → Returns absolute count for TAM calculation

2. **Prevalence Research**: "What is the global diabetes prevalence rate?"
   → Returns WHO percentage of adult population

3. **Competitive Analysis**: Replace uncited claims with authoritative data
   → Provides both rate and count with sources

4. **Regional Context**: Foundation for regional breakdown queries
   → Can extend pattern to country-level data

## Related Skills

- `get_us_diabetes_prevalence` - US-specific diabetes data
- `get_diabetes_treatment_market` - Market size and growth
- `get_glp1_trials` - GLP-1 clinical trials (diabetes treatment)

## Citation Format

When using this data in reports:

**WHO Data:**
"According to WHO [indicator_code], global diabetes prevalence was [value]% in [year]."

**Data Commons:**
"Data Commons reports [value_millions]M people worldwide with diabetes as of [date]."

## Notes

- Execution time: ~5 seconds (queries two servers)
- Both sources required for complete picture (rate + absolute count)
- Latest data typically 1-2 years behind current year
- WHO provides prevalence rates, Data Commons provides counts
- Combined data enables both epidemiological and market analysis
