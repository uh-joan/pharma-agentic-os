---
name: get_pipeline_drug_efficacy
description: >
  Extract Phase 2/3 clinical trial status and published efficacy data for 5 pipeline GLP-1 drugs:
  retatrutide (Eli Lilly), CagriSema (Novo Nordisk), orforglipron (Eli Lilly),
  survodutide (Boehringer Ingelheim), and AMG 133 (Amgen).

  Multi-server query combining ClinicalTrials.gov trial metadata with PubMed published
  efficacy outcomes (weight loss %, HbA1c reduction). Uses intelligent parsing to extract
  efficacy metrics from publication abstracts.

  Trigger keywords: pipeline drugs, GLP-1 efficacy, retatrutide, CagriSema, orforglipron,
  survodutide, AMG 133, weight loss data, HbA1c reduction, Phase 2/3 trials.
category: clinical-trials
mcp_servers:
  - ct_gov_mcp
  - pubmed_mcp
patterns:
  - multi_server_query
  - markdown_parsing
  - efficacy_extraction
  - regex_parsing
data_scope:
  total_results: 43 trials across 5 drugs
  geographical: Global
  temporal: All time
created: 2025-12-03
last_updated: 2025-12-03
complexity: complex
execution_time: ~15 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_pipeline_drug_efficacy

## Purpose
Extract comprehensive Phase 2/3 clinical development status and published efficacy data for 5 key pipeline GLP-1 drugs in obesity/diabetes: retatrutide, CagriSema, orforglipron, survodutide, and AMG 133.

## Usage
Use this skill when analyzing competitive landscape for next-generation GLP-1 therapies, comparing pipeline drug efficacy, or tracking clinical development progress for specific pipeline candidates.

**Trigger scenarios**:
- "Get efficacy data for pipeline GLP-1 drugs"
- "Compare retatrutide vs survodutide clinical outcomes"
- "What's the weight loss data for orforglipron?"
- "Phase 3 status for AMG 133 and CagriSema"

## Data Sources

### ClinicalTrials.gov (ct_gov_mcp)
- Phase 2 and Phase 3 trial counts
- Latest trial status (RECRUITING, ACTIVE_NOT_RECRUITING, etc.)
- Returns markdown format (parsed with regex)

### PubMed (pubmed_mcp)
- Clinical trial publications with efficacy outcomes
- Weight loss percentages extracted from abstracts
- HbA1c reduction metrics extracted from abstracts
- Returns JSON format

## Implementation Details

### Multi-Server Integration
Combines two MCP servers with different response formats:
1. **CT.gov**: Markdown parsing for trial metadata
2. **PubMed**: JSON parsing for efficacy extraction

### Efficacy Extraction Patterns
Uses regex patterns to extract metrics from publication abstracts:

**Weight Loss**:
- "X% weight loss"
- "weight reduction of X%"
- "lost X% body weight"

**HbA1c Reduction**:
- "HbA1c reduction of X%"
- "reduced HbA1c by X%"
- "HbA1c decreased X%"

### Data Structure
```python
{
    'drug_name': str,
    'trials': {
        'phase2_count': int,
        'phase3_count': int,
        'phase2_status': str,
        'phase3_status': str,
        'total_count': int
    },
    'efficacy': {
        'publications_found': int,
        'weight_loss': [
            {'value': float, 'study': str, 'pmid': str}
        ],
        'hba1c_reduction': [
            {'value': float, 'study': str, 'pmid': str}
        ],
        'key_studies': [
            {'title': str, 'pmid': str, 'pub_date': str}
        ]
    }
}
```

## Pipeline Drugs Covered

| Drug | Company | Mechanism |
|------|---------|-----------|
| Retatrutide | Eli Lilly | GLP-1/GIP/glucagon triple agonist |
| CagriSema | Novo Nordisk | GLP-1/amylin dual agonist |
| Orforglipron | Eli Lilly | Oral GLP-1 receptor agonist |
| Survodutide | Boehringer Ingelheim | GLP-1/glucagon dual agonist |
| AMG 133 | Amgen | GLP-1/GIP dual agonist |

## Example Output

```
RETATRUTIDE
-----------
Phase 2 Trials: 14 (Latest: RECRUITING)
Phase 3 Trials: 5 (Latest: RECRUITING)
Total Trials: 19

Published Efficacy Data:
  Publications Found: 9
  Weight Loss Reported:
    - 24.2% (PMID: 37478600)
    - 17.5% (PMID: 37478600)
  HbA1c Reduction Reported:
    - 2.16% (PMID: 37478600)
```

## Key Insights from Current Data

**Retatrutide** (Eli Lilly):
- Most advanced pipeline: 5 Phase 3 trials recruiting
- Highest weight loss: Up to 24.2% reported
- Strong HbA1c reduction: Up to 2.16%

**CagriSema** (Novo Nordisk):
- No registered Phase 2/3 trials found (may use different naming)
- Published efficacy: 15.1% weight loss

**Orforglipron** (Eli Lilly):
- 2 Phase 2 trials (active but not recruiting)
- Weight loss: Up to 14.7%
- HbA1c reduction: Up to 2.1%

**Survodutide** (Boehringer Ingelheim):
- 1 Phase 3 trial recruiting
- Weight loss: Up to 12.2%
- HbA1c reduction: Up to 1.5%

**AMG 133** (Amgen):
- 6 Phase 2 trials recruiting
- Weight loss: Up to 14.5%
- HbA1c reduction: Up to 1.8%

## Limitations

1. **Abstract Parsing**: Efficacy extraction relies on abstract text patterns - full papers may have additional data
2. **Trial Naming**: Some trials may use proprietary drug codes not captured by generic names
3. **Publication Lag**: Most recent trial results may not yet be published
4. **Metric Variability**: Weight loss reported at different timepoints (12, 24, 48 weeks)

## Future Enhancements

- Add trial phase-specific filters (e.g., only Phase 3 data)
- Extract dosing information from publications
- Add safety/adverse event extraction
- Include patent expiration dates
- Track FDA submission timelines
