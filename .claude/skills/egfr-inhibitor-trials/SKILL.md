---
name: get_egfr_inhibitor_trials
description: Get comprehensive EGFR inhibitor clinical trials data across all phases
category: clinical-trials
tags:
  - clinical-trials
  - egfr
  - inhibitor
  - oncology
  - targeted-therapy
data_type: trials
mcp_servers:
  - ct_gov_mcp
patterns_demonstrated:
  - pagination
  - markdown_parsing
  - status_aggregation
complexity: medium
created_date: 2025-11-19
last_updated: 2025-11-19
version: 1.0.0
health_status: healthy
health_last_checked: 2025-11-19
---

# get_egfr_inhibitor_trials

## Description

Retrieves comprehensive clinical trials data for EGFR (Epidermal Growth Factor Receptor) inhibitors across all phases. EGFR inhibitors are a class of targeted cancer therapies commonly used in non-small cell lung cancer (NSCLC), colorectal cancer, and other malignancies.

## Data Source

- **Server**: ClinicalTrials.gov (ct_gov_mcp)
- **Search Method**: Intervention-based query
- **Search Term**: "EGFR inhibitor"
- **Response Format**: Markdown (parsed with regex)

## Features

- **Full Pagination**: Automatically retrieves all trials across multiple pages
- **Comprehensive Parsing**: Extracts NCT ID, title, and status from markdown responses
- **Status Aggregation**: Provides breakdown of trial statuses (Recruiting, Completed, Terminated, etc.)
- **Standalone Executable**: Can be run directly or imported as a module

## Patterns Demonstrated

### 1. Pagination
- Uses `pageToken` parameter for multi-page retrieval
- Detects page token in markdown response: `` `pageToken: "TOKEN_STRING"` ``
- Continues until no more page tokens found
- Handles datasets larger than single-page limit (1000 records)

### 2. Markdown Parsing
- Parses ClinicalTrials.gov markdown response format
- Extracts trial sections using regex: `r'###\s+\d+\.\s+NCT\d{8}'`
- Captures NCT IDs with pattern: `r'###\s+\d+\.\s+(NCT\d{8})'`
- Extracts structured fields (Title, Status) using field-specific regex

### 3. Status Aggregation
- Counts trials by recruitment status
- Sorts status breakdown by frequency (descending)
- Provides comprehensive trial portfolio overview

## Return Format

```python
{
    'total_count': int,           # Total trials in database
    'trials_parsed': [            # List of trial dictionaries
        {
            'nct_id': str,        # NCT identifier (e.g., 'NCT04675008')
            'title': str,         # Trial title
            'status': str         # Recruitment status
        },
        ...
    ],
    'summary': {
        'total_trials': int,      # Same as total_count
        'trials_retrieved': int,  # Number retrieved (may equal total)
        'pages_fetched': int,     # Number of pages processed
        'retrieval_note': str,    # Human-readable retrieval summary
        'status_breakdown': {     # Trial counts by status
            'Completed': int,
            'Recruiting': int,
            'Terminated': int,
            ...
        }
    }
}
```

## Usage

### As Standalone Script

```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/egfr-inhibitor-trials/scripts/get_egfr_inhibitor_trials.py
```

### As Imported Module

```python
import sys
sys.path.insert(0, ".claude")
from skills.egfr_inhibitor_trials.scripts.get_egfr_inhibitor_trials import get_egfr_inhibitor_trials

result = get_egfr_inhibitor_trials()
print(f"Found {result['total_count']} EGFR inhibitor trials")
```

## Output Example

```
================================================================================
EGFR INHIBITOR CLINICAL TRIALS ANALYSIS
================================================================================

Total trials found: 630
Retrieved 630 trials
Note: Retrieved 630 of 630 total trials across 1 page(s)

STATUS BREAKDOWN:
----------------------------------------
  Completed                     :  248
  Recruiting                    :  113
  Terminated                    :   83
  Unknown                       :   79
  Active Not Recruiting         :   56
  Not Yet Recruiting            :   30
  Withdrawn                     :   19
  Enrolling By Invitation       :    2

Sample Trial IDs (first 5):
----------------------------------------
  NCT ID: NCT04675008 - Central Nervous System(CNS) Efficacy of Dacomitinib
  NCT ID: NCT00402896 - Malignant Pleural Effusion With ZD6474
  NCT ID: NCT00054691 - ZD1839 (Iressa) for Recurrent or Metastatic Squamous Cell Ca
  NCT ID: NCT05256290 - Phase 1/2 Study of Silevertinib (BDTX-1535) in Patients With
  NCT ID: NCT05017025 - Aurora Kinase Inhibitor LY3295668 in Combination With Osimer

================================================================================
```

## Therapeutic Context

**EGFR Inhibitors** are a major class of targeted cancer therapies that include:

- **First Generation**: Gefitinib (Iressa), Erlotinib (Tarceva)
- **Second Generation**: Afatinib (Gilotrif), Dacomitinib (Vizimpro)
- **Third Generation**: Osimertinib (Tagrisso) - targets T790M resistance mutation

**Primary Indications**:
- Non-small cell lung cancer (NSCLC) with EGFR mutations
- Colorectal cancer
- Head and neck cancers
- Pancreatic cancer

**Common EGFR Mutations Targeted**:
- Exon 19 deletions
- L858R point mutation
- T790M resistance mutation (third-generation inhibitors)

## Related Skills

- `get_glp1_trials` - Original reference skill (similar pagination pattern)
- `get_kras_inhibitor_trials` - Sibling skill for KRAS inhibitors
- `get_braf_inhibitor_trials` - Sibling skill for BRAF inhibitors

## Technical Notes

- **Pagination Method**: Token-based (ClinicalTrials.gov API v2)
- **Page Size**: 1000 records per page (API maximum)
- **Regex Pattern for NCT IDs**: `r'###\s+\d+\.\s+(NCT\d{8})'`
- **Regex Pattern for Titles**: `r'\*\*Title:\*\*\s*(.+?)(?:\n|\*\*)'`
- **Regex Pattern for Status**: `r'\*\*Status:\*\*\s*(.+?)(?:\n|\*\*)'`

## Verification

This skill has passed all verification checks:
- Execution: Code runs without errors
- Data Retrieved: 630 trials collected
- Pagination: Complete (no truncation)
- Executable: Standalone execution confirmed
- Schema: Valid CT.gov format (NCT IDs present)

**Verified**: 2025-11-19
**Strategy**: ADAPT from `get_glp1_trials`
