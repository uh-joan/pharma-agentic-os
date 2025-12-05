---
name: cdc-obesity-prevalence
description: Get CDC obesity prevalence data for the United States from Data Commons
category: epidemiology
servers:
  - datacommons_mcp
patterns:
  - indicator_search
  - geographic_aggregation
complexity: medium
health_status: healthy
trigger_keywords:
  - obesity prevalence
  - CDC obesity
  - adult obesity rate
created: 2025-12-03
---

# CDC Obesity Prevalence

## Overview
Retrieves CDC obesity prevalence data from Data Commons Knowledge Graph for US adults and young adults (18-24), including state-level breakdowns and time series trends.

## Data Sources
- **Primary**: Data Commons (datacommons_mcp)
- **Indicators**:
  - `Percent_Person_Obesity` (Adult obesity prevalence)
  - `Percent_Person_18To24_Obesity` (Young adult obesity)

## Usage

### Python Import
```python
from .claude.skills.cdc_obesity_prevalence.scripts.get_cdc_obesity_prevalence import get_cdc_obesity_prevalence

result = get_cdc_obesity_prevalence()
print(f"Adult obesity: {result['adult_obesity']['latest_value']}%")
```

### Direct Execution
```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/cdc-obesity-prevalence/scripts/get_cdc_obesity_prevalence.py
```

## Output Format
```python
{
    'adult_obesity': {
        'latest_value': float,
        'latest_year': str,
        'time_series': List[dict]
    },
    'young_adult_obesity': {
        'latest_value': float,
        'latest_year': str
    },
    'state_level': List[dict],
    'summary': str
}
```

## Example Output
```
Adult obesity prevalence: 32.0% (2021)
Young adult (18-24) obesity: 26.4% (2021)

State-level data (2021):
- California: 27.6%
- Texas: 34.8%
- Florida: 28.4%
- New York: 27.1%
- Pennsylvania: 32.0%
```
