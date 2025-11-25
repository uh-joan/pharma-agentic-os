# Implementation Plan: get_companies_by_moa Skill

## Executive Summary

**Goal**: Create focused query skill to answer "Who's working on [mechanism]?"

**Effort**: 1 week (after Part 1 complete)

**Value**: Fast competitive query tool (10 seconds) for specific mechanisms

**Dependency**: Requires Part 1 (enhanced pipeline-breakdown) for testing patterns

---

## Use Cases

### Primary Questions Answered

1. **"Who's developing KRAS G12C inhibitors?"**
   → Returns: Amgen, Mirati, Roche, Eli Lilly (with trial counts)

2. **"Which companies are working on GLP-1 receptor agonists in obesity?"**
   → Returns: Novo Nordisk, Eli Lilly, Amgen, Pfizer (filtered by disease)

3. **"How many companies are targeting BTK?"**
   → Returns: Count + list with phase distribution

### Why This is Different from Part 1

| Feature | Part 1 (Enhanced Pipeline) | Part 2 (This Skill) |
|---------|---------------------------|---------------------|
| **Query type** | By indication (disease) | By mechanism of action |
| **Scope** | All mechanisms in disease | Single mechanism across diseases |
| **Speed** | 15-30 sec (comprehensive) | 5-10 sec (focused) |
| **Example** | "NSCLC pipeline" → All drugs | "KRAS inhibitors" → All companies |

---

## Skill Specification

### Function Signature

```python
def get_companies_by_moa(
    moa: str,
    disease: str = None,
    phase_filter: str = "Phase 1",
    include_academic: bool = False
) -> dict:
    """
    Get companies working on a specific mechanism of action.

    Args:
        moa: Mechanism of action (e.g., "KRAS inhibitor", "PD-1 antibody")
        disease: Optional disease filter (e.g., "NSCLC", "melanoma")
        phase_filter: Minimum phase ("Phase 1", "Phase 2", "Phase 3")
        include_academic: Include academic/non-pharma sponsors (default: False)

    Returns:
        dict: Company breakdown with trials, phases, drugs
    """
```

### Output Structure

```python
{
    'moa': 'KRAS G12C inhibitor',
    'disease': 'Non-Small Cell Lung Cancer',  # If filtered
    'total_trials': 23,
    'total_companies': 6,

    'companies': {
        'Amgen': {
            'trials': 5,
            'phases': ['Phase 1', 'Phase 2', 'Phase 3'],
            'drugs': ['Sotorasib', 'AMG 510'],
            'approved': 1,
            'lead_phase': 'Phase 3'  # Most advanced phase
        },
        'Mirati Therapeutics': {
            'trials': 3,
            'phases': ['Phase 2', 'Phase 3'],
            'drugs': ['Adagrasib'],
            'approved': 1,
            'lead_phase': 'Phase 3'
        },
        'Revolution Medicines': {
            'trials': 4,
            'phases': ['Phase 1', 'Phase 2'],
            'drugs': ['RMC-6236', 'RMC-6291'],
            'approved': 0,
            'lead_phase': 'Phase 2'
        }
    },

    'competitive_summary': {
        'leaders': ['Amgen', 'Mirati Therapeutics'],  # Companies with approved drugs
        'late_stage': ['Amgen', 'Mirati', 'Eli Lilly'],  # Phase 3
        'early_stage': ['Revolution Medicines', 'Johnson & Johnson'],  # Phase 1/2 only
        'assessment': 'Established market with 2 approved drugs and active late-stage competition'
    }
}
```

---

## Implementation Plan

### Day 1-2: Core Query Logic

**File**: `.claude/skills/companies-by-moa/scripts/get_companies_by_moa.py`

#### Step 1: Basic skeleton

```python
import sys
import re
from collections import defaultdict
sys.path.insert(0, ".claude")

from mcp.servers.ct_gov_mcp import search as ct_search

def get_companies_by_moa(
    moa: str,
    disease: str = None,
    phase_filter: str = "Phase 1",
    include_academic: bool = False
) -> dict:
    """Get companies working on specific mechanism of action."""

    print(f"\n🔍 Finding companies working on: {moa}")
    if disease:
        print(f"   Filtered by disease: {disease}")
    print("=" * 80)

    # Step 1: Query CT.gov for trials matching MoA
    trials = query_trials_by_moa(moa, disease)

    # Step 2: Extract sponsor info
    companies = extract_company_data(trials, phase_filter)

    # Step 3: Filter academic (optional)
    if not include_academic:
        companies = filter_pharma_only(companies)

    # Step 4: Generate competitive summary
    summary = generate_competitive_summary(companies, moa)

    return {
        'moa': moa,
        'disease': disease,
        'total_trials': sum(c['trials'] for c in companies.values()),
        'total_companies': len(companies),
        'companies': companies,
        'competitive_summary': summary
    }
```

#### Step 2: Trial querying

```python
def query_trials_by_moa(moa: str, disease: str = None) -> list:
    """
    Query CT.gov for trials matching mechanism of action.

    Strategy:
    - Use MoA as search term (e.g., "KRAS inhibitor")
    - Filter for interventional drug trials
    - Filter for active status only
    - Optional disease filter
    """

    print(f"\n📊 Step 1: Querying ClinicalTrials.gov...")

    # Build query
    query_parts = [moa]
    if disease:
        query_parts.append(disease)

    term = " ".join(query_parts)

    # Search CT.gov
    result = ct_search(
        term=term,
        studyType="interventional",
        interventionType="drug",
        status="recruiting OR active_not_recruiting",
        pageSize=1000
    )

    # Extract NCT IDs
    nct_ids = re.findall(r'NCT\d{8}', result)

    # Extract total count
    total_match = re.search(r'(\d+)\s+of\s+([\d,]+)\s+studies', result)
    total_trials = int(total_match.group(2).replace(',', '')) if total_match else len(nct_ids)

    print(f"   Found {total_trials} trials matching '{term}'")
    print(f"   Analyzing first {len(nct_ids)} trials")

    return nct_ids
```

#### Step 3: Company extraction (reuse from Part 1)

```python
# Import M&A attribution from Part 1
COMPANY_HIERARCHY = {
    # Same as Part 1 - keep in sync or import from shared module
    'Celgene': 'Bristol Myers Squibb',
    'Array BioPharma': 'Pfizer',
    'Five Prime Therapeutics': 'Amgen',
    'Mirati Therapeutics': 'Bristol Myers Squibb',
    # ... etc
}

def attribute_company(sponsor_name: str) -> str:
    """Map sponsor to parent company (same as Part 1)."""
    if sponsor_name in COMPANY_HIERARCHY:
        return COMPANY_HIERARCHY[sponsor_name]

    for acquired, parent in COMPANY_HIERARCHY.items():
        if acquired.lower() in sponsor_name.lower():
            return parent

    return sponsor_name


def extract_company_data(nct_ids: list, phase_filter: str) -> dict:
    """Extract sponsor and drug info from trials."""

    from mcp.servers.ct_gov_mcp import get_study

    print(f"\n🏢 Step 2: Extracting company information...")

    # Track by company
    company_data = defaultdict(lambda: {
        'trials': 0,
        'phases': set(),
        'drugs': set(),
        'approved': 0,
        'nct_ids': []
    })

    phase_order = ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4']
    phase_filter_idx = phase_order.index(phase_filter) if phase_filter in phase_order else 0

    for nct_id in nct_ids[:100]:  # Sample first 100 for speed
        trial_data = get_study(nct_id)

        # Extract sponsor
        sponsor_match = re.search(r'\*\*Sponsor:\*\*\s+(.+?)(?:\n|$)', trial_data)
        if not sponsor_match:
            continue

        sponsor = sponsor_match.group(1).strip()
        sponsor = attribute_company(sponsor)

        # Extract phase
        phase_match = re.search(r'\*\*Phase:\*\*\s+(.+?)(?:\n|$)', trial_data)
        phase = phase_match.group(1).strip() if phase_match else 'Phase 1'

        # Normalize phase (handle "Phase2/Phase3" → "Phase 3")
        phase = normalize_phase(phase)

        # Apply phase filter
        if phase in phase_order:
            phase_idx = phase_order.index(phase)
            if phase_idx < phase_filter_idx:
                continue  # Skip trials below filter

        # Extract drugs
        drugs = extract_drugs_from_trial(trial_data)

        # Track
        company_data[sponsor]['trials'] += 1
        company_data[sponsor]['phases'].add(phase)
        for drug in drugs:
            company_data[sponsor]['drugs'].add(drug)
        company_data[sponsor]['nct_ids'].append(nct_id)

    print(f"   Found {len(company_data)} companies")

    # Format output
    return format_company_output(company_data, phase_order)


def normalize_phase(phase_str: str) -> str:
    """Normalize phase string (same as Part 1)."""
    if 'Phase 4' in phase_str or 'Phase4' in phase_str:
        return 'Phase 4'
    elif 'Phase 3' in phase_str or 'Phase3' in phase_str:
        return 'Phase 3'
    elif 'Phase 2' in phase_str or 'Phase2' in phase_str:
        return 'Phase 2'
    elif 'Phase 1' in phase_str or 'Phase1' in phase_str:
        return 'Phase 1'
    else:
        return 'Not Applicable'


def extract_drugs_from_trial(trial_markdown: str) -> set:
    """Extract drug names (same as Part 1)."""
    drugs = set()
    drug_matches = re.findall(r'###\s+Drug:\s*(.+?)(?:\n|$)', trial_markdown)

    for drug in drug_matches:
        drug = drug.strip()
        # Filter placebo
        if 'placebo' in drug.lower():
            continue
        if drug.lower() in ['drug', 'other', 'unknown']:
            continue
        drugs.add(drug)

    return drugs


def format_company_output(company_data: dict, phase_order: list) -> dict:
    """Format company data into output structure."""

    formatted = {}

    for company, data in company_data.items():
        # Determine lead phase (most advanced)
        phases = [p for p in phase_order if p in data['phases']]
        lead_phase = phases[-1] if phases else 'Phase 1'

        formatted[company] = {
            'trials': data['trials'],
            'phases': sorted(list(data['phases'])),
            'drugs': sorted(list(data['drugs'])),
            'approved': 0,  # Will be updated in Step 4
            'lead_phase': lead_phase
        }

    # Sort by lead phase (most advanced first), then by trial count
    def sort_key(item):
        company, data = item
        phase_idx = phase_order.index(data['lead_phase']) if data['lead_phase'] in phase_order else -1
        return (-phase_idx, -data['trials'])

    return dict(sorted(formatted.items(), key=sort_key))
```

---

### Day 3: Academic Filtering

```python
def filter_pharma_only(companies: dict) -> dict:
    """Remove academic and non-pharma sponsors."""

    # Patterns for academic/non-profit
    ACADEMIC_PATTERNS = [
        'university', 'hospital', 'medical center', 'institute',
        'foundation', 'cancer center', 'national', 'veterans',
        'mayo clinic', 'md anderson', 'memorial sloan',
        'government', 'NIH', 'NCI'
    ]

    filtered = {}

    for company, data in companies.items():
        # Check if academic
        is_academic = any(
            pattern.lower() in company.lower()
            for pattern in ACADEMIC_PATTERNS
        )

        if not is_academic:
            filtered[company] = data

    return filtered
```

---

### Day 4: FDA Cross-Check & Competitive Summary

```python
def check_fda_approvals(companies: dict, moa: str) -> dict:
    """Check which companies have FDA approved drugs."""

    from mcp.servers.fda_mcp import lookup_drug

    print(f"\n💊 Step 3: Checking FDA approvals...")

    # Get all unique drugs
    all_drugs = set()
    for company_data in companies.values():
        all_drugs.update(company_data['drugs'])

    # Check FDA (sample to avoid too many calls)
    approved_drugs = set()
    for drug in list(all_drugs)[:30]:  # Sample first 30
        result = lookup_drug(
            search_term=drug,
            search_type='label',
            limit=1
        )

        # Check if approved (has results)
        if 'results' in result and result.get('results'):
            approved_drugs.add(drug)

    print(f"   Found {len(approved_drugs)} approved drugs")

    # Update company approved counts
    for company, data in companies.items():
        approved_count = sum(
            1 for drug in data['drugs']
            if drug in approved_drugs
        )
        data['approved'] = approved_count

    return companies


def generate_competitive_summary(companies: dict, moa: str) -> dict:
    """Generate strategic summary of competitive landscape."""

    # Identify leaders (approved drugs)
    leaders = [
        company for company, data in companies.items()
        if data['approved'] > 0
    ]

    # Identify late-stage (Phase 3+)
    late_stage = [
        company for company, data in companies.items()
        if 'Phase 3' in data['phases'] or 'Phase 4' in data['phases']
    ]

    # Identify early-stage only
    early_stage = [
        company for company, data in companies.items()
        if data['lead_phase'] in ['Phase 1', 'Phase 2']
        and company not in late_stage
    ]

    # Generate assessment
    if len(leaders) >= 2:
        assessment = f"Established market with {len(leaders)} approved drugs and active late-stage competition"
    elif len(leaders) == 1:
        assessment = f"Emerging market with 1 approved drug. {len(late_stage) - 1} late-stage competitors"
    elif len(late_stage) >= 3:
        assessment = f"Pre-commercial space with {len(late_stage)} late-stage programs (no approvals yet)"
    else:
        assessment = f"Early-stage space. {len(companies)} companies exploring {moa}"

    return {
        'leaders': leaders,
        'late_stage': late_stage,
        'early_stage': early_stage,
        'assessment': assessment
    }
```

---

### Day 5: Output Formatting & Main Function

```python
# Make skill executable
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python get_companies_by_moa.py 'mechanism' ['disease']")
        print("Example: python get_companies_by_moa.py 'KRAS inhibitor'")
        print("Example: python get_companies_by_moa.py 'PD-1 antibody' 'melanoma'")
        sys.exit(1)

    moa = sys.argv[1]
    disease = sys.argv[2] if len(sys.argv) > 2 else None

    result = get_companies_by_moa(moa, disease)

    # Display results
    print("\n" + "=" * 80)
    print("COMPANY LANDSCAPE BY MECHANISM")
    print("=" * 80)

    print(f"\n📋 Mechanism: {result['moa']}")
    if result['disease']:
        print(f"   Disease: {result['disease']}")

    print(f"\n📊 Overview:")
    print(f"   Total Companies: {result['total_companies']}")
    print(f"   Total Trials: {result['total_trials']}")

    print("\n🏢 Companies (sorted by development stage):")
    print("-" * 80)

    for i, (company, data) in enumerate(result['companies'].items(), 1):
        phases_str = ", ".join(data['phases'])
        drug_count = len(data['drugs'])
        approved_marker = f" ✓ {data['approved']} approved" if data['approved'] > 0 else ""

        print(f"{i:2}. {company:40} {data['trials']} trials | {drug_count} drugs")
        print(f"    Phases: {phases_str} (Lead: {data['lead_phase']}){approved_marker}")

        # Show sample drugs
        sample_drugs = list(data['drugs'])[:3]
        if sample_drugs:
            drugs_str = ", ".join(sample_drugs)
            if len(data['drugs']) > 3:
                drugs_str += f" (+{len(data['drugs']) - 3} more)"
            print(f"    Drugs: {drugs_str}")

        print()

    # Competitive summary
    summary = result['competitive_summary']

    print("=" * 80)
    print("COMPETITIVE ASSESSMENT")
    print("=" * 80)

    print(f"\n{summary['assessment']}")

    if summary['leaders']:
        print(f"\n✓ Market Leaders ({len(summary['leaders'])}):")
        for company in summary['leaders']:
            print(f"  - {company}")

    if summary['late_stage']:
        print(f"\n⚡ Late-Stage Competitors ({len(summary['late_stage'])}):")
        for company in summary['late_stage']:
            print(f"  - {company}")

    if summary['early_stage']:
        print(f"\n🔬 Early-Stage Explorers ({len(summary['early_stage'])}):")
        for company in summary['early_stage'][:5]:  # Show top 5
            print(f"  - {company}")
        if len(summary['early_stage']) > 5:
            print(f"  ... and {len(summary['early_stage']) - 5} more")
```

---

### Day 6-7: Documentation & Testing

#### SKILL.md

**File**: `.claude/skills/companies-by-moa/SKILL.md`

```yaml
---
name: get_companies_by_moa
description: >
  Fast competitive query tool to identify companies working on specific mechanisms
  of action. Answers "Who's developing KRAS inhibitors?" in 5-10 seconds.

  Provides company breakdown with trial counts, development phases, drug names,
  and FDA approval status. Includes competitive assessment (leaders, late-stage,
  early-stage).

  Use when you need:
  - Quick competitive intelligence by mechanism
  - Company identification for partnerships/acquisitions
  - Development stage assessment (who's leading, who's early)
  - Competitive intensity check before starting program

category: competitive-intelligence
mcp_servers:
  - ct_gov_mcp
  - fda_mcp
patterns:
  - focused_query
  - company_attribution
  - competitive_assessment
data_scope:
  total_results: Samples first 100 trials
  geographical: Global
  temporal: Active trials only
created: 2025-11-25
complexity: simple
execution_time: ~5-10 seconds
token_efficiency: ~99% reduction
---

# get_companies_by_moa

## Purpose

Fast competitive query tool to answer "Who's working on [mechanism]?"

Focuses on:
- Company identification by mechanism
- Development stage assessment
- Competitive positioning (leaders vs followers)

## Usage

**Direct execution**:
```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/companies-by-moa/scripts/get_companies_by_moa.py "KRAS inhibitor"

# With disease filter
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/companies-by-moa/scripts/get_companies_by_moa.py "PD-1 antibody" "melanoma"
```

**Import and use**:
```python
from skills.companies_by_moa.scripts.get_companies_by_moa import get_companies_by_moa

result = get_companies_by_moa("BTK inhibitor")
print(f"Total companies: {result['total_companies']}")
print(f"Leaders: {result['competitive_summary']['leaders']}")
```

## Parameters

- `moa` (required): Mechanism of action (e.g., "KRAS inhibitor", "GLP-1 agonist")
- `disease` (optional): Disease filter (e.g., "NSCLC", "diabetes")
- `phase_filter`: Minimum phase (default: "Phase 1")
- `include_academic`: Include academic sponsors (default: False)

## Output

Returns dict with:
- `moa`: Mechanism queried
- `disease`: Disease filter (if applied)
- `total_companies`: Count of unique companies
- `total_trials`: Total trials found
- `companies`: Dict with company details (trials, phases, drugs, approval status)
- `competitive_summary`: Assessment (leaders, late-stage, early-stage, narrative)

## Related Skills

- `indication-drug-pipeline-breakdown`: Comprehensive pipeline analysis by indication
- Complementary: Use this for MoA-specific queries, pipeline-breakdown for disease-wide analysis
```

#### Test Script

**File**: `.claude/skills/companies-by-moa/test_companies_by_moa.py`

```python
#!/usr/bin/env python3
"""Test get_companies_by_moa skill."""
import sys
sys.path.insert(0, ".claude")

from skills.companies_by_moa.scripts.get_companies_by_moa import get_companies_by_moa

def test_basic_query():
    """Test basic MoA query."""
    result = get_companies_by_moa("KRAS inhibitor")

    assert result['total_companies'] > 0, "No companies found"
    assert result['total_trials'] > 0, "No trials found"
    assert 'companies' in result
    assert 'competitive_summary' in result

    print("✓ Basic query test passed")
    return True

def test_disease_filter():
    """Test with disease filter."""
    result = get_companies_by_moa("PD-1 antibody", "melanoma")

    assert result['disease'] == "melanoma"
    assert result['total_companies'] > 0

    print("✓ Disease filter test passed")
    return True

def test_moa_attribution():
    """Test M&A attribution."""
    result = get_companies_by_moa("multiple myeloma drug")

    # Celgene should be attributed to Bristol Myers Squibb
    assert 'Celgene' not in result['companies'], "M&A attribution failed"

    print("✓ M&A attribution test passed")
    return True

if __name__ == "__main__":
    test_basic_query()
    test_disease_filter()
    test_moa_attribution()

    print("\n✓ All tests passed!")
```

---

## Integration Testing

Test interaction with Part 1:

```python
# Test that both skills work together
from skills.indication_drug_pipeline_breakdown.scripts.get_indication_drug_pipeline_breakdown import (
    get_indication_drug_pipeline_breakdown
)
from skills.companies_by_moa.scripts.get_companies_by_moa import get_companies_by_moa

# Part 1: Disease-wide analysis
pipeline = get_indication_drug_pipeline_breakdown("NSCLC")
print(f"NSCLC: {pipeline['total_companies']} companies")

# Part 2: Mechanism-specific analysis
kras_companies = get_companies_by_moa("KRAS inhibitor", "NSCLC")
print(f"KRAS in NSCLC: {kras_companies['total_companies']} companies")

# Verify subset relationship
assert kras_companies['total_companies'] <= pipeline['total_companies']
```

---

## Success Criteria

✅ **Speed**: < 10 seconds for typical query
✅ **Accuracy**: >90% sponsor extraction
✅ **Completeness**: Samples 100 trials (representative)
✅ **Utility**: Answers "who's working on X?" clearly

---

## Limitations

1. **Sampling**: Analyzes first 100 trials (not exhaustive)
2. **MoA matching**: Relies on text search (may miss synonyms)
3. **Academic filter**: Pattern-based (may miss some non-pharma)
4. **FDA check**: Samples first 30 drugs (performance trade-off)

---

## Future Enhancements

- Synonym expansion for MoA (KRAS → "Kirsten rat sarcoma")
- Patent integration (IP landscape by company)
- Financial data (R&D spend by company/MoA)
- Geographic analysis (where companies are running trials)
- Combination therapy tracking

---

## Timeline

**Day 1-2**: Core query + company extraction
**Day 3**: Academic filtering
**Day 4**: FDA cross-check + competitive summary
**Day 5**: Output formatting + main function
**Day 6-7**: Documentation + testing

**Total**: 1 week (~40 hours)
