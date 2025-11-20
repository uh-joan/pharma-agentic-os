---
name: get_cart_therapy_landscape
description: >
  Retrieves comprehensive CAR-T therapy landscape combining clinical trials
  from ClinicalTrials.gov with recent scientific publications from PubMed.
  Multi-server integration demonstrating handling of both markdown (CT.gov)
  and JSON (PubMed) response formats. Provides aggregated statistics including
  trial phase distribution, recruitment status, publication trends, and top
  journals. Use for: CAR-T research overview, competitive landscape analysis,
  publication trend analysis, clinical development tracking.
  Keywords: CAR-T, chimeric antigen receptor, immunotherapy, cell therapy,
  multi-server, clinical trials, publications.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
  - pubmed_mcp
patterns:
  - multi_server_query
  - markdown_parsing
  - json_parsing
  - data_aggregation
data_scope:
  total_results: 200 (100 trials + 100 publications)
  geographical: Global
  temporal: All time trials, 2023-2024 publications
created: 2025-11-20
last_updated: 2025-11-20
complexity: medium
execution_time: ~4 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_cart_therapy_landscape

## Purpose
Provides comprehensive CAR-T therapy landscape by integrating clinical trial data with recent scientific publications. Demonstrates multi-server MCP pattern handling different response formats.

## Usage
Execute this skill when you need:
- Complete CAR-T therapy research overview
- Clinical trial pipeline analysis
- Publication trend analysis
- Competitive landscape assessment
- Integration of trial and literature data

**Trigger keywords**: CAR-T, chimeric antigen receptor, immunotherapy, landscape, trials + publications

## Implementation Details

### Multi-Server Integration
This skill demonstrates the multi-server query pattern:

1. **ClinicalTrials.gov** (markdown response):
   - Returns trial summaries in markdown format
   - Requires regex parsing for field extraction
   - Provides trial phase, status, conditions

2. **PubMed** (JSON response):
   - Returns publications in structured JSON
   - Standard dictionary access methods
   - Filtered for recent publications (2023-2024)

### Data Processing

**Trial Parsing** (Markdown):
- Split trials using NCT ID headers
- Extract fields via regex patterns
- Aggregate by phase and status

**Publication Parsing** (JSON):
- Access results via dictionary methods
- Extract metadata (PMID, title, journal, date)
- Aggregate by year and journal

**Cross-Source Analysis**:
- Trial phase distribution
- Recruitment status breakdown
- Publication trends over time
- Top contributing journals

### Key Features
- ✅ Handles both markdown and JSON responses
- ✅ Comprehensive data aggregation
- ✅ Publication date filtering (2023-2024)
- ✅ Top journal identification
- ✅ Trial status breakdown

## Example Output

```
CAR-T THERAPY LANDSCAPE

📊 CLINICAL TRIALS: 100
By Phase:
  Phase 1: 33
  Phase 2: 30
  Phase 3: 7

By Status:
  Recruiting: 50
  Completed: 13

📚 RECENT PUBLICATIONS (2023-2024): 100
By Year:
  2023: 55
  2024: 45

Top Journals:
  Blood: 8
  Journal of Clinical Oncology: 6
```

## Dependencies
- `mcp.servers.ct_gov_mcp`: Clinical trial data
- `mcp.servers.pubmed_mcp`: Publication data
- `re`: Markdown parsing

## Data Sources
- ClinicalTrials.gov API (via CT.gov MCP)
- PubMed/NCBI API (via PubMed MCP)

## Related Skills
- `get_cart_trials`: CT.gov trials only
- `get_cart_publications`: PubMed publications only
- Multi-server integration pattern

## Notes
- CT.gov returns markdown (only MCP server to do so)
- PubMed returns JSON (standard format)
- Publication query filtered to 2023-2024 for recency
- Trial query retrieves first 100 results
- Can be extended with pagination for complete datasets
