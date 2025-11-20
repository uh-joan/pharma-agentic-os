---
name: get_diabetes_recruiting_trials
description: >
  Retrieves all recruiting diabetes clinical trials from ClinicalTrials.gov.
  Uses pagination to collect complete dataset (10,000+ trials).
  Includes phase distribution analysis and intervention type breakdown.

  Use this skill when querying for:
  - Diabetes clinical trials
  - Recruiting diabetes studies
  - Current diabetes research landscape
  - Diabetes intervention types (drugs, behavioral, devices)
  - Phase distribution of diabetes trials

  Keywords: diabetes, recruiting, clinical trials, active studies
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
patterns:
  - pagination
  - markdown_parsing
  - status_aggregation
  - phase_analysis
data_scope:
  total_results: 10865
  geographical: Global
  temporal: Currently recruiting
  status: RECRUITING only
created: 2025-11-19
last_updated: 2025-11-19
complexity: medium
execution_time: ~15 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_diabetes_recruiting_trials

## Purpose
Collects comprehensive data on all currently recruiting diabetes clinical trials worldwide from ClinicalTrials.gov.

## Usage
Use this skill when you need to:
- Understand the current diabetes clinical trials landscape
- Analyze phase distribution of active diabetes research
- Identify intervention types being studied for diabetes
- Track recruiting opportunities in diabetes research
- Compare diabetes trial activity across phases

## Data Collected
- **Total trials**: 10,865 recruiting diabetes studies
- **Phase distribution**: Breakdown by trial phase (Phase 1-4, N/A)
- **Intervention types**: Categorization by intervention (Drug, Behavioral, Device, etc.)
- **Complete pagination**: All trials retrieved, not just first 1000

## Implementation Details

### Pagination Strategy
Uses token-based pagination to retrieve all results:
1. Initial query with pageSize=1000
2. Extract nextPageToken from markdown response using regex
3. Continue until no more tokens returned
4. Aggregates results from all pages

### Markdown Parsing
CT.gov returns markdown format - uses regex patterns:
- Split trials: `r'###\s+\d+\.\s+NCT\d{8}'`
- Extract phase: `r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)'`
- Extract intervention: `r'\*\*Intervention Type:\*\*\s*(.+?)(?:\n|$)'`

### Analysis Features
- Phase aggregation with frequency counts
- Intervention type categorization
- Top 10 most common intervention types
- Summary statistics for quick insights

## Return Format
```python
{
    'total_count': 10865,
    'data': [trial_markdown_strings],
    'summary': {
        'total_recruiting_trials': 10865,
        'pages_fetched': 11,
        'phase_distribution': {
            'PHASE2': 2314,
            'PHASE3': 1847,
            ...
        },
        'intervention_types': {
            'DRUG': 7784,
            'BEHAVIORAL': 1385,
            ...
        }
    }
}
```

## Example Output
```
Total recruiting diabetes trials: 10,865
Pages fetched: 11

Phase Distribution:
  PHASE2: 2,314
  PHASE3: 1,847
  PHASE4: 1,608
  NOT_APPLICABLE: 1,442
  PHASE1: 998

Top Intervention Types:
  DRUG: 7,784
  BEHAVIORAL: 1,385
  DEVICE: 838
  DIETARY_SUPPLEMENT: 436
  OTHER: 259
```

## Quality Assurance
- ✅ Complete pagination (all 10,865 trials collected)
- ✅ Markdown parsing validated
- ✅ Both importable and executable
- ✅ Verification checks passed
