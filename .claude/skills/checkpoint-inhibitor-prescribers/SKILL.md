---
name: get_checkpoint_inhibitor_prescribers
description: >
  Identifies top checkpoint inhibitor prescribers from CMS Medicare Part D data.
  Provides institutional analysis, KOL identification, and geographic insights.
category: regulatory
mcp_servers:
  - healthcare_mcp
patterns:
  - json_parsing
  - data_aggregation
  - institutional_analysis
data_scope:
  total_results: 2162
  geographical: United States
  temporal: 2022 Medicare Part D data
created: 2025-11-22
complexity: medium
execution_time: ~15 seconds
---
# get_checkpoint_inhibitor_prescribers


## Sample Queries

Examples of user queries that would trigger reuse of this skill:

1. `@agent-pharma-search-specialist Who are the top checkpoint inhibitor prescribers from CMS Medicare data?`
2. `@agent-pharma-search-specialist Identify KOLs and major cancer centers prescribing PD-1/PD-L1 inhibitors`
3. `@agent-pharma-search-specialist Show me geographic distribution of checkpoint inhibitor prescribers in the US`
4. `@agent-pharma-search-specialist Which medical oncologists have the highest checkpoint inhibitor prescription volumes?`
5. `@agent-pharma-search-specialist Analyze institutional prescribing patterns for pembrolizumab, nivolumab, and atezolizumab`


Identifies KOLs and major cancer centers for checkpoint inhibitor targeting.

## Key Findings
- 2,162 prescribers, 258,349 claims, $3.45B spend
- Top centers: Houston, NYC, Tampa, Nashville, LA
- Top KOL: Dr. David Waterhouse (Omaha) - 7,851 claims
- Medical Oncology: 85% of prescribers