---
name: get_crispr_2024_papers
description: >
  Retrieves CRISPR research papers published in 2024 from PubMed with comprehensive metadata.
  Extracts titles, authors, journals, publication dates, DOIs, and abstracts.
category: literature
mcp_servers:
  - pubmed_mcp
patterns:
  - json_parsing
  - date_filtering
data_scope:
  total_results: 487
  geographical: Global
  temporal: 2024/01/01 to 2024/12/31
created: 2025-11-22
complexity: medium
execution_time: ~4 seconds
token_efficiency: 99%
---
# get_crispr_2024_papers


## Sample Queries

Examples of user queries that would trigger reuse of this skill:

1. `@agent-pharma-search-specialist What CRISPR research papers were published in 2024?`
2. `@agent-pharma-search-specialist Show me the latest 2024 CRISPR gene editing literature with journal distribution`
3. `@agent-pharma-search-specialist Get all CRISPR publications from 2024 with comprehensive metadata`
4. `@agent-pharma-search-specialist Which journals published the most CRISPR research in 2024?`
5. `@agent-pharma-search-specialist Find recent CRISPR papers published this year with DOIs and abstracts`


CRISPR research papers from 2024 with journal distribution analysis.