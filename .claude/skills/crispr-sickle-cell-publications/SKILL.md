---
name: get_crispr_sickle_cell_publications
description: >
  Search PubMed for latest publications on CRISPR gene editing for sickle cell disease.
  Analyzes publication trends over time, clinical outcomes data, off-target effects,
  and safety profiles. Context: Covers research leading to and following Casgevy
  (first CRISPR therapy) FDA approval in December 2023.
category: scientific-literature
mcp_servers:
  - pubmed_mcp
patterns:
  - pubmed_search
  - json_parsing
  - trend_analysis
  - keyword_extraction
data_scope:
  total_results: 200
  geographical: Global
  temporal: All time (sorted by date)
created: 2025-11-22
complexity: medium
execution_time: ~3 seconds
---
# get_crispr_sickle_cell_publications


## Sample Queries

Examples of user queries that would trigger reuse of this skill:

1. `@agent-pharma-search-specialist What are the latest publications on CRISPR gene editing for sickle cell disease?`
2. `@agent-pharma-search-specialist Show me publication trends and clinical outcomes for CRISPR sickle cell therapy research`
3. `@agent-pharma-search-specialist Find research papers on Casgevy and CRISPR treatment for sickle cell disease`
4. `@agent-pharma-search-specialist Analyze the scientific literature on safety and off-target effects of CRISPR in sickle cell patients`
5. `@agent-pharma-search-specialist Track publication growth in CRISPR sickle cell research following Casgevy FDA approval`


Search and analyze PubMed publications on CRISPR gene editing for sickle cell disease.

## Key Features

- 200 most recent publications on CRISPR + SCD
- Year-over-year publication growth tracking
- Topic coverage analysis (clinical trials, efficacy, safety, off-target effects)
- Recent highlights with clinical/safety tags
- Context: Casgevy FDA approval milestone (Dec 2023)