---
name: get_biotech_ma_filings
description: >
  Analyzes biotech M&A activity from SEC EDGAR Form 8-K filings. Searches for current reports
  containing M&A keywords from biotech companies. Provides trend analysis by company and year.
category: financial
mcp_servers:
  - sec_edgar_mcp
patterns:
  - multi_keyword_search
  - deduplication
  - trend_analysis
data_scope:
  total_results: 83
  geographical: US
  temporal: 2020-2024
created: 2025-11-22
complexity: medium
execution_time: ~5 seconds
---
# get_biotech_ma_filings


## Sample Queries

Examples of user queries that would trigger reuse of this skill:

1. `@agent-pharma-search-specialist What biotech M&A deals were announced via SEC 8-K filings in 2023-2024?`
2. `@agent-pharma-search-specialist Analyze biotech merger and acquisition activity from SEC EDGAR filings`
3. `@agent-pharma-search-specialist Which biotech companies filed 8-Ks announcing acquisitions or mergers?`
4. `@agent-pharma-search-specialist Show me trends in biotech M&A announcements from SEC current reports`
5. `@agent-pharma-search-specialist Track biotech acquisition activity by company using SEC filings`


Biotech merger and acquisition SEC filings analysis.