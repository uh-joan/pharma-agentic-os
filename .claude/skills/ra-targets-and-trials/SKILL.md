---
name: get_ra_targets_and_trials
description: >
  Multi-server integration combining Open Targets drug target validation
  with ClinicalTrials.gov clinical trials data for rheumatoid arthritis.
  Provides comprehensive view of validated drug targets with association scores,
  complete clinical trial landscape (all phases, statuses), and integrated
  analysis matching targets to trial activity. Use when analyzing drug target
  validation, competitive landscape for RA, target prioritization, clinical
  development opportunities, mechanism of action, validated targets,
  target-trial correlation.
category: target-validation
mcp_servers:
  - opentargets_mcp
  - ct_gov_mcp
patterns:
  - multi_server_integration
  - pagination
  - markdown_parsing
  - json_parsing
  - target_trial_matching
data_scope:
  total_results: 3745
  targets: 20
  trials: 3725
  geographical: Global
  temporal: All time
created: 2025-11-20
last_updated: 2025-11-20
complexity: complex
execution_time: ~12 seconds
token_efficiency: ~99% reduction vs raw data
---

# get_ra_targets_and_trials

## Purpose
Multi-server integration skill combining Open Targets Platform drug target validation with ClinicalTrials.gov to provide comprehensive rheumatoid arthritis drug development intelligence.

## Data Sources

**Open Targets Platform**
- Validated drug targets for rheumatoid arthritis
- Association scores based on genetics, literature, pathways
- Target-disease relationships with evidence strength

**ClinicalTrials.gov**
- Complete clinical trials database (all phases, statuses)
- Full pagination to retrieve all records

## Integration Analysis
Intelligent matching between validated targets (gene symbols) and clinical trials (titles, conditions), identifying which high-confidence targets have active clinical programs for target prioritization.

## Usage
Execute when you need:
- Target validation for RA drug discovery
- Competitive landscape analysis
- Target prioritization (validation + clinical activity)
- Partnership opportunity identification
- Clinical development strategy

## Output Example
```
Targets Identified: 20 validated targets (score ≥ 0.5)
Clinical Trials: 3,725 total trials
Integration: 8 targets with clinical trial activity

Top Targets with Clinical Activity:
  1. TNF (Score: 0.984) - 89 trials
  2. IL6 (Score: 0.964) - 45 trials
```

## Performance
- Execution Time: ~12 seconds
- Data Volume: 3,745 records
- Token Efficiency: ~99% reduction
- Pagination: Complete (4 pages, all trials)
