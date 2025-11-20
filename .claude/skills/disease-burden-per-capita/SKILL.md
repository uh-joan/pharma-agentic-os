---
name: get_disease_burden_per_capita
description: >
  Compare WHO disease burden data with Data Commons population statistics for per-capita analysis.
  Combines absolute disease counts from WHO with population data from Data Commons to calculate
  normalized rates (per 100K, per 1M population). Enables cross-country comparisons by standardizing
  for population size. Supports multiple disease indicators (tuberculosis, malaria, etc.) and countries.
  Use when comparing disease burden across countries, analyzing public health metrics, normalizing
  health statistics, cross-country epidemiological analysis.
category: regulatory
mcp_servers:
  - who_mcp
  - datacommons_mcp
patterns:
  - multi_server_query
  - data_normalization
  - cross_source_integration
data_scope:
  total_results: 2 data sources integrated
  geographical: Configurable by country (ISO3 codes)
  temporal: Latest available data from both sources
created: 2025-11-20
last_updated: 2025-11-20
complexity: medium
execution_time: ~2 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_disease_burden_per_capita

## Purpose
Integrate WHO disease burden statistics with Data Commons population data to calculate per-capita disease rates for meaningful cross-country comparisons.

## Usage
Execute when you need:
- Cross-country disease burden comparisons
- Population-normalized health metrics
- Epidemiological analysis with standardized rates
- Public health policy benchmarking

## Multi-Server Integration
Demonstrates multi-server query pattern:
1. WHO MCP: Disease burden data (JSON)
2. Data Commons MCP: Population data (JSON)
3. Integration: Per-capita normalization

## Per-Capita Calculation
```python
per_100k = (disease_count / population) * 100000
per_million = (disease_count / population) * 1000000
```

## Example Output
```
ABSOLUTE NUMBERS:
  Total Cases: 12,500
  Population: 331,000,000

PER-CAPITA METRICS:
  Per 100,000 population: 3.78
  Per 1,000,000 population: 37.76
```

## Token Efficiency
- Raw data: ~4,000 tokens
- Summary: ~500 tokens
- **Reduction**: 87.5%
