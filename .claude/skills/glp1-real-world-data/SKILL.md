---
name: get_glp1_real_world_data
description: >
  Retrieves real-world evidence (RWE) data for GLP-1 drugs from PubMed, focusing on
  discontinuation rates, persistence, and adherence metrics. Searches for observational
  studies and real-world data on major GLP-1 drugs (semaglutide, tirzepatide, dulaglutide,
  liraglutide) and extracts key metrics like discontinuation rates at 6/12 months,
  persistence rates, and study populations. Useful for understanding real-world treatment
  patterns, patient adherence challenges, and comparative effectiveness outside clinical trials.

  Trigger keywords: "real-world data", "RWE", "persistence", "discontinuation", "adherence",
  "observational study", "GLP-1 real world", "treatment patterns".
category: drug-discovery
mcp_servers:
  - pubmed_mcp
patterns:
  - json_parsing
  - multi_drug_query
  - metric_extraction
  - deduplication
data_scope:
  total_results: 40 studies
  geographical: Global
  temporal: Recent publications (last 3-5 years prioritized)
created: 2025-12-03
last_updated: 2025-12-03
complexity: medium
execution_time: ~15 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_glp1_real_world_data

## Purpose

This skill retrieves and analyzes real-world evidence (RWE) publications from PubMed for major GLP-1 receptor agonist drugs. It focuses on extracting practical metrics about treatment persistence, discontinuation rates, and adherence patterns that are critical for understanding real-world treatment outcomes beyond controlled clinical trials.

## Key Features

- **Multi-drug coverage**: Searches for semaglutide (Ozempic, Wegovy, Rybelsus), tirzepatide (Mounjaro, Zepbound), dulaglutide (Trulicity), and liraglutide (Victoza, Saxenda)
- **RWE-specific search**: Uses targeted keywords like "real-world", "observational", "persistence", "discontinuation", "adherence"
- **Metric extraction**: Automatically extracts discontinuation rates, 6-month/12-month persistence, and study sizes from abstracts
- **Deduplication**: Removes duplicate PMIDs across multiple search terms
- **Relevance filtering**: Only includes studies with RWE-relevant content

## Usage

**When to use this skill**:
- Analyzing real-world treatment patterns for GLP-1 drugs
- Comparing persistence and discontinuation rates across different GLP-1 agents
- Understanding adherence challenges in clinical practice
- Evaluating post-market surveillance data
- Supporting market access or health economics research

**Example queries**:
- "What are the real-world discontinuation rates for GLP-1 drugs?"
- "How does persistence compare between semaglutide and tirzepatide in real-world settings?"
- "What RWE studies exist for GLP-1 adherence?"

## Implementation Details

### Search Strategy

The skill uses a comprehensive multi-term search approach:

1. **Drug coverage**: Both generic and brand names for each GLP-1 drug
2. **RWE keywords**: "real-world", "real world", "observational", "persistence", "discontinuation", "adherence", "retrospective cohort"
3. **Combined queries**: Each drug × each RWE term = comprehensive coverage
4. **Deduplication**: PMIDs tracked to avoid duplicates across searches

### Metric Extraction

Uses regex patterns to extract from abstracts:
- **Discontinuation rates**: Patterns like "discontinuation...X%", "X%...discontinued"
- **Persistence at 6 months**: "persistence...6...month...X%"
- **Persistence at 12 months**: "persistence...12...month...X%"
- **Study size**: Patterns like "N=X,XXX", "X,XXX patients", "cohort...X,XXX"

### Data Structure

Returns a dictionary with:
```python
{
    'total_count': int,
    'studies_by_drug': {
        'semaglutide': [study1, study2, ...],
        'tirzepatide': [...],
        'dulaglutide': [...],
        'liraglutide': [...]
    },
    'summary': str
}
```

Each study includes:
- PMID
- Title
- Publication date
- Extracted metrics (discontinuation, persistence, study size)
- Abstract snippet

## Output Format

**Summary output**:
```
======================================================================
GLP-1 Real-World Evidence Data Summary
======================================================================

Total RWE studies found: 40

Studies by drug:

  SEMAGLUTIDE: 10 studies
    1. PMID: 38123456
       Real-world persistence with semaglutide in type 2 diabetes...
       Discontinuation: 25%
       6-month persistence: 68%
       Study size: n=5000

  TIRZEPATIDE: 10 studies
    ...
```

## Limitations

- Metric extraction depends on abstract text patterns (may miss data in tables/figures)
- Limited to PubMed indexed publications
- Abstracts may not contain all relevant metrics
- Regex patterns may not capture all variations in metric reporting

## Future Enhancements

- Add filters for study design (cohort vs. claims analysis)
- Include reasons for discontinuation extraction
- Add time-based filtering (last 1 year, 2 years, etc.)
- Extract comparative effectiveness data
- Add cost-effectiveness metrics if available

## Related Skills

- `get_glp1_trials` - Clinical trial data (controlled settings)
- `get_glp1_fda_drugs` - FDA approval data and labeling
- `get_glp1_adverse_events` - FDA adverse event reporting

## References

- PubMed MCP Server: `.claude/mcp/servers/pubmed_mcp/`
- PubMed Tool Guide: `.claude/.context/mcp-tool-guides/pubmed.md`
