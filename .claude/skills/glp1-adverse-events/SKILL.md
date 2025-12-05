---
name: get_glp1_adverse_events
description: >
  Extracts adverse event rates from FDA drug labels for GLP-1 drugs.
  Queries FDA labels for semaglutide, tirzepatide, liraglutide, dulaglutide,
  exenatide, and oral semaglutide. Extracts rates for common adverse events:
  nausea, vomiting, diarrhea, constipation, and discontinuation.

  Use cases:
  - Safety profile comparison across GLP-1 drugs
  - Adverse event rate analysis for competitive intelligence
  - Clinical trial design reference data
  - Regulatory documentation review

  Trigger keywords: adverse events, side effects, safety profile, GLP-1 safety,
  nausea rates, discontinuation rates, tolerability
category: regulatory
mcp_servers:
  - fda_mcp
patterns:
  - json_parsing
  - regex_extraction
  - multi_drug_query
data_scope:
  total_results: 6 drugs analyzed
  geographical: US (FDA approved)
  temporal: Current approved labels
created: 2025-12-03
last_updated: 2025-12-03
complexity: medium
execution_time: ~8 seconds
token_efficiency: ~99% reduction vs raw label text
---

# get_glp1_adverse_events

## Purpose

Extracts adverse event rates from FDA drug labels for major GLP-1 receptor agonist drugs. Provides structured data on common adverse events (nausea, vomiting, diarrhea, constipation, discontinuation) across six GLP-1 drugs.

## Usage

**When to use this skill**:
- Comparing safety profiles across GLP-1 drugs
- Analyzing adverse event patterns for competitive intelligence
- Supporting clinical trial design with reference safety data
- Reviewing regulatory documentation for adverse events
- Assessing drug tolerability for market positioning

**Drugs analyzed**:
- Semaglutide (Ozempic, Wegovy)
- Tirzepatide (Mounjaro, Zepbound)
- Liraglutide (Victoza, Saxenda)
- Dulaglutide (Trulicity)
- Exenatide (Byetta, Bydureon)
- Oral semaglutide (Rybelsus)

## Implementation Details

**Data Source**: FDA drug labels via `fda_mcp` server
- Uses `lookup_drug` method with `search_type='label'`
- Queries multiple brand names per drug for comprehensive coverage
- Extracts adverse_reactions sections from label data

**Extraction Method**:
- Regex patterns for common adverse events
- Percentage rate extraction from label text
- Handles variable label text formats
- Safe parsing with error handling

**Adverse Events Tracked**:
1. Nausea
2. Vomiting
3. Diarrhea
4. Constipation
5. Discontinuation due to adverse events

**Return Format**:
```python
{
    'total_drugs_analyzed': 6,
    'adverse_events': {
        'drug_name': {
            'nausea': 44.0,
            'vomiting': 24.0,
            'diarrhea': 31.0,
            'constipation': 24.0,
            'discontinued': 6.9
        }
    },
    'summary': "Text summary with rates by drug"
}
```

## Notes

**Label Text Variability**:
- FDA labels use varying formats for adverse event reporting
- Regex patterns extract common formats but may miss variations
- Some labels may require manual review for complete extraction

**Data Interpretation**:
- Rates represent clinical trial data reported in FDA labels
- Adverse event frequencies may vary by indication and dose
- Compare across drugs considering study design differences

**Future Enhancements**:
- Add indication-specific adverse event extraction
- Include dose-dependent rate analysis
- Expand adverse event types tracked
- Add severity classification extraction

## Example Output

```
FDA Drug Label Adverse Events Analysis - GLP-1 Drugs
============================================================
Total drugs analyzed: 6/6

Adverse Event Rates by Drug:

SEMAGLUTIDE:
  - Constipation: 24.0%
  - Diarrhea: 31.0%
  - Nausea: 44.0%
  - Vomiting: 24.0%
  - Discontinued: 6.9%

TIRZEPATIDE:
  - Nausea: 28.0%
  - Vomiting: 13.0%
  - Diarrhea: 23.0%

[... other drugs ...]

Note: Rates extracted via regex patterns from FDA labels.
Label text formats vary - some rates may require manual extraction.
Data represents most common adverse events reported in clinical trials.
```

## Integration

**Standalone execution**:
```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/glp1-adverse-events/scripts/get_glp1_adverse_events.py
```

**Import in Python**:
```python
from skills.glp1_adverse_events.scripts.get_glp1_adverse_events import get_glp1_adverse_events

result = get_glp1_adverse_events()
print(f"Analyzed {result['total_drugs_analyzed']} drugs")
for drug, events in result['adverse_events'].items():
    print(f"{drug}: {events}")
```

**Use in strategic analysis**:
- Competitive landscape: Compare safety profiles across drugs
- Market positioning: Identify differentiation opportunities
- Clinical strategy: Inform trial design and endpoints
- Regulatory intelligence: Track label changes over time
