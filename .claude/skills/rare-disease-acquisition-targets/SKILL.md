---
name: get_rare_disease_acquisition_targets
description: >
  Identifies potential biotech acquisition targets with rare disease clinical programs in Phase 2 or Phase 3.
  Enhanced with optional SEC EDGAR financial intelligence for cash runway analysis and distress signal detection.

  Uses pattern-based filtering to detect rare disease indicators (orphan designation, ultra-rare, lysosomal storage,
  metabolic disorders) and adaptive phase strategy to capture early-stage companies before late-stage development.

  Optional financial enrichment provides:
  - Cash runway calculation (cash / monthly R&D burn rate)
  - Distress signal detection (low cash runway <12 months, negative earnings)
  - Fuzzy company name matching (CT.gov sponsor → SEC company lookup)
  - Public vs private company detection (graceful handling of private companies)

  Acquisition scoring ranks targets based on:
  - Clinical validation: Phase (earlier = more acquirable), orphan designation, ultra-rare indication
  - Financial distress: Low cash runway and negative earnings increase acquisition likelihood
  - Portfolio depth: Multiple programs suggest platform potential

  Use this skill when:
  - Evaluating M&A opportunities in rare disease biotech
  - Identifying financially distressed companies (cash runway <12-18 months)
  - Screening for orphan drug developers with active programs
  - Analyzing competitive landscape in ultra-rare diseases
  - Assessing acquisition targets by financial health (public companies only)

  Performance: Fast clinical-only mode (~10 sec) or comprehensive financial enrichment (~30-60 sec)
category: strategic-analysis
mcp_servers:
  - ct_gov_mcp
  - sec_edgar_mcp
patterns:
  - pagination
  - markdown_parsing
  - sponsor_aggregation
  - phase_distribution
  - fuzzy_matching
  - financial_enrichment
  - pattern_based_filtering
  - adaptive_phase_strategy
  - acquisition_scoring
data_scope:
  total_results: varies
  geographical: Global
  temporal: Active programs only
created: 2025-11-26
last_updated: 2025-11-26
complexity: complex
execution_time: ~10 seconds (clinical only) | ~30-60 seconds (with financials)
token_efficiency: ~99% reduction vs raw trial data
---

# get_rare_disease_acquisition_targets

## Purpose

Identifies rare disease companies that are potential acquisition targets using clinical trial data with optional SEC EDGAR financial enrichment.

This skill combines two intelligence layers:
1. **Clinical Intelligence**: Pattern-based rare disease detection in ClinicalTrials.gov data
2. **Financial Intelligence** (optional): SEC EDGAR metrics (cash, R&D expense, runway, distress signals)

## Enhancement Summary (v2.0)

**New in this version**:
- ✅ SEC EDGAR financial data integration
- ✅ Fuzzy company name matching (handles "Inc.", "Corp.", "Therapeutics" variations)
- ✅ Cash runway calculation: `months_of_cash = cash / (R&D_expense / 12)`
- ✅ Distress signal detection (low cash <12 months, negative earnings)
- ✅ Cash runway filtering (`max_cash_runway_months` parameter)
- ✅ Graceful handling of private companies (clinical scoring only)
- ✅ Optional enrichment (default: False for performance)
- ✅ Enhanced acquisition scoring with financial factors

## Usage

### Basic Usage (Clinical Data Only - Fast)
```python
from .claude.skills.rare_disease_acquisition_targets.scripts.get_rare_disease_acquisition_targets import get_rare_disease_acquisition_targets

# Fast screening without financial data (~10 seconds)
result = get_rare_disease_acquisition_targets(
    therapeutic_focus='ultra_rare_metabolic',
    max_results=30
)
```

### With Financial Enrichment (Comprehensive)
```python
# Include SEC EDGAR financial metrics (~30-60 seconds)
result = get_rare_disease_acquisition_targets(
    therapeutic_focus='ultra_rare_metabolic',
    enrich_financials=True,
    max_results=30
)
```

### Distress Signal Filtering
```python
# Filter for financially distressed companies only
result = get_rare_disease_acquisition_targets(
    therapeutic_focus='any',
    enrich_financials=True,
    max_cash_runway_months=18,  # Companies with <18 months cash
    max_results=50
)
```

### Standalone Execution
```bash
# Default execution with financial enrichment
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/rare-disease-acquisition-targets/scripts/get_rare_disease_acquisition_targets.py

# Fast clinical-only mode (modify __main__ block)
# Set enrich_financials=False in the script
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `therapeutic_focus` | str | 'any' | Therapeutic area: 'ultra_rare_metabolic', 'neuromuscular', 'gene_therapy', 'oncology_rare', 'any' |
| `min_programs` | int | 1 | Minimum trials per company (filter out single-program companies) |
| `max_programs` | int | 8 | Maximum trials per company (filter out large pharma) |
| `exclude_academic` | bool | True | Exclude universities and medical centers (pattern-based detection) |
| `exclude_government` | bool | True | Exclude NIH, NCI, and other government agencies |
| `exclude_cro` | bool | True | Exclude contract research organizations |
| `prefer_phase3` | bool | True | Adaptive phase strategy: Try Phase 3 first, expand to Phase 2 if <20 companies |
| `max_results` | int | 50 | Maximum number of ranked targets to return |
| `enrich_financials` | bool | False | **Enable SEC EDGAR financial data lookup** (slower but adds cash runway, distress signals) |
| `max_cash_runway_months` | float | None | Filter for distressed companies (requires `enrich_financials=True`) |

## Returns

```python
{
    'query_strategy': {
        'therapeutic_focus': str,
        'phases_included': str,  # 'PHASE3 only' or 'PHASE2+PHASE3'
        'phase_expansion_reason': str,
        'financial_enrichment': bool
    },
    'filtering_summary': {
        'total_trials': int,
        'companies_before_filtering': int,
        'excluded_academic': int,
        'excluded_government': int,
        'excluded_large_pharma': int,
        'excluded_cro': int,
        'excluded_small_portfolio': int,
        'companies_after_filtering': int
    },
    'top_targets': [
        {
            'rank': int,
            'sponsor': str,
            'acquisition_score': int,  # 0-100+
            'total_programs': int,
            'phase2_count': int,
            'phase3_count': int,
            'recruiting_count': int,
            'lead_asset': {
                'nct_id': str,
                'intervention': str,
                'condition': str,
                'phase': str,
                'status': str
            },
            'financial_metrics': {  # Only if enrich_financials=True
                'company_name': str,
                'cik': str,
                'ticker': str,
                'cash_millions': float,
                'rd_expense_millions': float,
                'cash_runway_months': float,
                'distress_signals': List[str]  # e.g., ['Low cash runway (8.3 months)', 'Negative earnings ($45M loss)']
            } | None,
            'all_programs': List[dict]
        }
    ],
    'summary': str  # Markdown-formatted summary
}
```

## Implementation Details

### Pattern-Based Rare Disease Detection

**No hardcoded company names** - uses keywords only:

```python
THERAPEUTIC_QUERIES = {
    'ultra_rare_metabolic': 'lysosomal storage OR mitochondrial disease OR organic acidemia OR urea cycle OR peroxisomal',
    'neuromuscular': 'muscular dystrophy OR spinal muscular atrophy OR myasthenia gravis OR neuropathy',
    'gene_therapy': 'gene therapy OR AAV OR lentiviral OR adenoviral OR CRISPR',
    'oncology_rare': 'rare cancer OR orphan cancer OR sarcoma OR mesothelioma',
    'any': 'orphan OR "rare disease"'
}
```

### Adaptive Phase Strategy

**Intelligent expansion** to ensure sufficient results:

1. **Try Phase 3 first** (most de-risked programs)
2. **Check result count**: If <20 companies found
3. **Expand to Phase 2**: Combine Phase 2 + Phase 3 trials
4. **Report strategy**: Transparent reporting of expansion decision

### Financial Enrichment Process

**Step 1: Fuzzy Company Name Matching**
```python
# Handles variations:
# CT.gov: "Ultragenyx Pharmaceutical Inc."
# SEC: "Ultragenyx Pharmaceutical Inc"
# Match: 95% similarity → Success

# Normalization:
# - Remove suffixes: Inc., Corp., Ltd., LLC, Therapeutics, Pharma, Bio
# - Lowercase and strip whitespace
# - Calculate similarity ratio (threshold: 60%)
```

**Step 2: SEC EDGAR Data Extraction**
- Search company by name (`search_companies`)
- Get CIK (Central Index Key)
- Retrieve company facts (`get_company_facts`)
- Extract metrics from 10-K filings:
  - `CashAndCashEquivalentsAtCarryingValue` → Cash on hand
  - `ResearchAndDevelopmentExpense` (annual) → R&D burn rate
  - `NetIncomeLoss` → Profitability
  - `CommonStockSharesOutstanding` → Shares

**Step 3: Cash Runway Calculation**
```python
monthly_burn = rd_expense_millions / 12
cash_runway_months = cash_millions / monthly_burn

# Example:
# Cash: $50M
# Annual R&D: $48M → Monthly burn: $4M
# Runway: 50 / 4 = 12.5 months
```

**Step 4: Distress Signal Detection**
- **Low cash runway**: < 12 months
- **Negative earnings**: Annual net income < 0

### Acquisition Scoring System

**Base Clinical Scores**:
- Portfolio sweet spot (2-5 programs): +30 points
- Has Phase 3 (de-risked): +25 points
- Multiple programs (platform): +20 points
- Active recruiting (momentum): +15 points
- Balanced Phase 2+3: +10 points

**Financial Modifiers** (if `enrich_financials=True`):
- **Each distress signal**: +5 points
  - Low cash runway (<12 months): +5
  - Negative earnings: +5
  - Both signals: +10 total

**Interpretation**:
- **Score 80+**: Exceptional target (sweet spot portfolio + Phase 3 + recruiting + distressed)
- **Score 60-79**: High priority target (strong clinical + some distress)
- **Score 40-59**: Medium priority target
- **Score <40**: Lower priority target

## Use Cases

### 1. Fast Clinical Screening (No Financial Data)
**Scenario**: Quick landscape scan of rare disease companies
```python
result = get_rare_disease_acquisition_targets()
# Returns: All rare disease sponsors, ranked by clinical score only
# Time: ~10 seconds
```

### 2. Distressed Company Identification
**Scenario**: Find companies likely to need funding/exit soon
```python
result = get_rare_disease_acquisition_targets(
    enrich_financials=True,
    max_cash_runway_months=12  # <12 months cash
)
# Returns: Companies with low cash runway, ranked by acquisition score
# Time: ~30-60 seconds
```

### 3. Therapeutic Area Focus with Financials
**Scenario**: Evaluate acquisition targets in neuromuscular diseases
```python
result = get_rare_disease_acquisition_targets(
    therapeutic_focus='neuromuscular',
    enrich_financials=True,
    max_results=20
)
# Returns: Top 20 neuromuscular rare disease companies with financial metrics
```

### 4. Platform Company Identification
**Scenario**: Find companies with multiple programs (platform potential)
```python
result = get_rare_disease_acquisition_targets(
    min_programs=3,  # At least 3 programs
    enrich_financials=True
)
# Returns: Multi-program rare disease platforms with financial health data
```

## Performance Characteristics

| Configuration | Execution Time | Targets Scanned | Financial Lookups | Use Case |
|---------------|----------------|-----------------|-------------------|----------|
| Clinical only | ~10 seconds | 50-100 sponsors | 0 | Fast screening |
| With financials (all) | ~60 seconds | 50-100 sponsors | 50-100 API calls | Comprehensive analysis |
| With financials (filtered) | ~30-45 seconds | 50-100 sponsors | 20-40 API calls | Distress signal focus |

**Token Efficiency**:
- **Clinical only**: ~99.5% reduction (only summary + top targets)
- **With financials**: ~99.2% reduction (adds financial metrics to summary)
- **Raw data never enters context**: All processing in execution environment

## Data Quality

**Verification Results** (v2.0):
- ✅ Execution: No errors, clean exit
- ✅ Data Retrieved: Successfully queries CT.gov and SEC EDGAR
- ✅ Pagination: Complete dataset retrieved
- ✅ Fuzzy Matching: Handles company name variations
- ✅ Financial Calculation: Cash runway formula verified
- ✅ Distress Detection: Correctly identifies low cash and negative earnings
- ✅ Executable: Standalone execution verified
- ✅ Importable: Can be imported as Python module

**Known Limitations**:
1. **Private companies**: No SEC data available (clinical scoring only)
2. **Market cap**: Requires stock price (not available in SEC facts alone)
3. **Fuzzy matching**: May miss alternative company names (e.g., subsidiaries)
4. **Recent funding**: Not detected (would need additional data source like Crunchbase)

## Error Handling

**Graceful Degradation**:
- **Private companies**: Included in results, no financial metrics
- **API failures**: Continue processing, log error, return partial results
- **Missing financial fields**: Calculate what's available, mark others as N/A
- **Fuzzy match failures**: Fallback to first search result

**Example Output**:
```
  Enriching: Ultragenyx Pharmaceutical Inc... ✓ (2 distress signals)
  Enriching: BioMarin Pharmaceutical... ✓ (0 distress signals)
  Enriching: Private Biotech Corp... ✗ (not found)
```

## Future Enhancements

**Planned Features** (v3.0):
1. Stock price integration (Yahoo Finance MCP) for accurate market cap
2. Crunchbase/PitchBook integration for private company valuations
3. Patent portfolio analysis (USPTO MCP) for IP value assessment
4. Publication analysis (PubMed MCP) for scientific credibility
5. Recent funding detection (SEC Form D filings, press releases)
6. Geographic filtering (US vs EU rare disease companies)
7. Collaboration/partnership history (strategic fit assessment)

## Related Skills

- `get_orphan_drug_designations` - FDA orphan drug analysis
- `get_company_segment_geographic_financials` - SEC financial data (deep dive)
- `get_clinical_trial_timeline_analysis` - Program timeline assessment
- `get_kras_inhibitor_trials` - Reference for pagination and markdown parsing patterns

## Metadata

- **Category**: Strategic Analysis / M&A Intelligence
- **Servers**: ct_gov_mcp, sec_edgar_mcp
- **Complexity**: Complex (multi-server integration, fuzzy matching, financial calculations)
- **Token Efficiency**: 99% reduction (clinical-only) | 99.2% reduction (with financials)
- **Execution Time**: ~10 seconds (clinical-only) | ~30-60 seconds (with financials)
- **Version**: 2.0 (enhanced with SEC EDGAR financial intelligence)
