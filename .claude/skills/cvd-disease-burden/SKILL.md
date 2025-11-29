---
name: get_cvd_disease_burden
description: >
  Retrieves WHO cardiovascular disease burden data globally including mortality rates,
  morbidity indicators, and disease statistics across countries and regions. Searches
  for cardiovascular disease mortality, heart disease, stroke, and ischemic heart disease
  indicators. Returns comprehensive disease burden metrics with country-level data,
  temporal trends, and age-standardized death rates.
category: regulatory
mcp_servers:
  - who_mcp
patterns:
  - json_parsing
  - multi_term_search
  - data_aggregation
data_scope:
  total_results: varies
  geographical: Global (all countries)
  temporal: Historical WHO data
created: 2025-11-22
last_updated: 2025-11-22
complexity: medium
execution_time: ~5-8 seconds
token_efficiency: ~99% reduction vs raw data
---
# get_cvd_disease_burden


## Sample Queries

Examples of user queries that would trigger reuse of this skill:

1. `@agent-pharma-search-specialist Get comprehensive WHO cardiovascular disease burden data globally`
2. `@agent-pharma-search-specialist Show me age-standardized CVD mortality rates across countries from WHO`
3. `@agent-pharma-search-specialist What are the heart disease, stroke, and ischemic heart disease statistics by region?`
4. `@agent-pharma-search-specialist Analyze temporal trends in cardiovascular disease mortality using WHO data`
5. `@agent-pharma-search-specialist Retrieve country-level CVD morbidity and mortality indicators from WHO health statistics`


Retrieves comprehensive cardiovascular disease burden data from WHO health statistics.