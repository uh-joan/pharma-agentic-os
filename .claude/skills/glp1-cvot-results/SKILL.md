---
name: get_glp1_cvot_results
description: >
  Fetches cardiovascular outcome trial (CVOT) results for GLP-1 drugs from PubMed.
  Queries 3 major CVOTs: SELECT (semaglutide in obesity), LEADER (liraglutide in T2D),
  and REWIND (dulaglutide in T2D). Returns structured data including MACE reduction outcomes,
  publication details, and abstracts. Use when analyzing cardiovascular safety and efficacy
  of GLP-1 receptor agonists, comparing CVOT results across drugs, or researching
  cardiovascular benefits in different patient populations (obesity vs T2D).

  Trigger keywords: CVOT, cardiovascular outcomes, MACE, SELECT trial, LEADER trial,
  REWIND trial, GLP-1 cardiovascular safety, semaglutide cardiovascular, liraglutide
  cardiovascular, dulaglutide cardiovascular.
category: clinical-trials
mcp_servers:
  - pubmed_mcp
patterns:
  - targeted_literature_search
  - trial_specific_queries
  - structured_results_aggregation
data_scope:
  total_results: 15 articles (5 per CVOT)
  geographical: Global
  temporal: 2016-2023 (LEADER 2016, REWIND 2019, SELECT 2023)
created: 2025-12-03
last_updated: 2025-12-03
complexity: medium
execution_time: ~4 seconds
token_efficiency: ~99% reduction vs raw abstracts
---

# get_glp1_cvot_results

## Purpose
Retrieves cardiovascular outcome trial (CVOT) results for major GLP-1 receptor agonist drugs from PubMed. Focuses on three landmark trials that established cardiovascular safety and efficacy.

## CVOT Trials Queried

### 1. SELECT (2023)
- **Drug**: Semaglutide
- **Population**: Obesity without diabetes
- **Expected Outcome**: MACE reduction in non-diabetic obesity patients
- **Query**: "Lincoff SELECT semaglutide cardiovascular NEJM 2023"

### 2. LEADER (2016)
- **Drug**: Liraglutide
- **Population**: T2D with cardiovascular disease
- **Expected Outcome**: 13% MACE reduction
- **Query**: "Marso LEADER liraglutide cardiovascular NEJM 2016"

### 3. REWIND (2019)
- **Drug**: Dulaglutide
- **Population**: Type 2 diabetes
- **Expected Outcome**: 12% MACE reduction
- **Query**: "Gerstein REWIND dulaglutide cardiovascular Lancet 2019"

## Usage

```python
from .claude.skills.glp1_cvot_results.scripts.get_glp1_cvot_results import get_glp1_cvot_results

# Get CVOT results for all 3 trials
result = get_glp1_cvot_results()

# Access structured data
for trial_name, data in result['cvot_results'].items():
    print(f"{trial_name}: {data['drug_name']}")
    print(f"PMID: {data['publication']['pmid']}")
    print(f"Outcome: {data['expected_outcome']}")
```

Or execute standalone:
```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/glp1-cvot-results/scripts/get_glp1_cvot_results.py
```

## Output Format

Returns dictionary with:
- `total_trials`: Number of CVOTs queried (3)
- `total_articles`: Total PubMed articles retrieved
- `cvot_results`: Dict keyed by trial name containing:
  - `trial_name`: CVOT acronym (SELECT, LEADER, REWIND)
  - `drug_name`: GLP-1 drug tested
  - `expected_outcome`: Primary cardiovascular endpoint
  - `publication`: Title, authors, journal, year, PMID
  - `abstract_snippet`: First 500 characters of abstract
  - `total_related_articles`: Number of related publications found
- `summary`: Human-readable text summary

## Implementation Details

### PubMed Query Strategy
Uses targeted queries with:
- Lead author name (Lincoff, Marso, Gerstein)
- Trial acronym (SELECT, LEADER, REWIND)
- Drug name (semaglutide, liraglutide, dulaglutide)
- Journal + year for precision

### Data Extraction
- Retrieves top 5 articles per CVOT
- Primary article (first result) used for main data
- Extracts publication metadata and abstract snippet
- Handles missing data gracefully with 'N/A' defaults

### Error Handling
- Returns error message if no articles found for a trial
- Continues processing remaining trials on individual failures
- Summary indicates which trials succeeded/failed

## When to Use This Skill

**Use this skill when you need to**:
- Compare cardiovascular outcomes across GLP-1 drugs
- Analyze MACE reduction data for different patient populations
- Research cardiovascular safety profiles of GLP-1 agonists
- Find publication details for major CVOT trials
- Gather evidence for cardiovascular benefits in obesity vs T2D

**Example queries that should trigger this skill**:
- "What are the CVOT results for GLP-1 drugs?"
- "Compare cardiovascular outcomes of semaglutide vs liraglutide"
- "Get SELECT trial cardiovascular data"
- "Show MACE reduction for GLP-1 receptor agonists"
- "Find cardiovascular safety data for obesity GLP-1 drugs"

## Related Skills
- `get_glp1_clinical_trial_results` - Broader clinical trial results (not CVOT-specific)
- `get_glp1_trials` - All GLP-1 trials from ClinicalTrials.gov
- `get_glp1_fda_drugs` - FDA-approved GLP-1 drugs

## Data Quality Notes
- **Verification status**: ✓ All checks passed
  - Execution: Success (exit code 0)
  - Data retrieved: 15 articles (5 per trial)
  - Pagination: N/A (limited to 5 results per query)
  - Executable: Standalone execution confirmed
  - Schema: Valid structure with all required fields

- **Known limitations**:
  - Limited to 3 specific CVOTs (not exhaustive)
  - Abstract snippets truncated to 500 characters
  - Relies on author + trial name for query precision
  - May miss secondary publications if query too specific

## Token Efficiency
- **Input**: 3 targeted PubMed queries
- **Raw data**: ~15 full abstracts (~15,000 tokens)
- **Processed output**: Trial summaries + metadata (~500 tokens)
- **Reduction**: ~97% (15,000 → 500 tokens)

## Execution Results (2025-12-03)

Successfully retrieved all 3 CVOTs:
- **SELECT**: Found 5 articles (NEJM 2023, PMID: 37952131)
- **LEADER**: Found 5 articles (NEJM 2016, PMID: 27295427)
- **REWIND**: Found 5 articles (Lancet 2019, PMID: 31189511)

All trials returned expected primary publications with complete metadata.
