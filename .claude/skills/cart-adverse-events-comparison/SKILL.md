---
name: get_cart_adverse_events_comparison
description: >
  Compare adverse event profiles for all 6 approved CAR-T cell therapies (Kymriah,
  Yescarta, Tecartus, Breyanzi, Abecma, Carvykti). Analyzes cytokine release syndrome
  (CRS) rates, neurotoxicity/ICANS frequencies, and serious adverse events to identify
  safety differentiation opportunities. Uses FDA FAERS database for real-world safety data.
category: regulatory
mcp_servers:
  - fda_mcp
patterns:
  - json_parsing
  - multi_product_comparison
  - adverse_event_analysis
data_scope:
  total_results: 6 CAR-T products analyzed
  geographical: Global (FDA FAERS)
  temporal: All reported adverse events
created: 2025-11-22
complexity: medium
execution_time: ~15 seconds
---
# get_cart_adverse_events_comparison


## Sample Queries

Examples of user queries that would trigger reuse of this skill:

1. `@agent-pharma-search-specialist Compare adverse event profiles for all approved CAR-T cell therapies`
2. `@agent-pharma-search-specialist What are the CRS and neurotoxicity rates across Kymriah, Yescarta, Tecartus, Breyanzi, Abecma, and Carvykti?`
3. `@agent-pharma-search-specialist Show me safety differentiation between approved CAR-T products based on FAERS data`
4. `@agent-pharma-search-specialist Which CAR-T therapy has the lowest cytokine release syndrome rates?`
5. `@agent-pharma-search-specialist Analyze real-world adverse events for all 6 FDA-approved CAR-T cell therapies`


Provides comprehensive comparative analysis of adverse event profiles for all 6 FDA-approved CAR-T cell therapies.

## CAR-T Products Analyzed

1. Kymriah (tisagenlecleucel) - Novartis
2. Yescarta (axicabtagene ciloleucel) - Kite/Gilead
3. Tecartus (brexucabtagene autoleucel) - Kite/Gilead
4. Breyanzi (lisocabtagene maraleucel) - BMS
5. Abecma (idecabtagene vicleucel) - BMS/bluebird bio
6. Carvykti (ciltacabtagene autoleucel) - J&J/Legend

## Key Metrics

- CRS rates by product
- Neurotoxicity/ICANS frequencies
- Serious adverse event counts
- Safety differentiation opportunities