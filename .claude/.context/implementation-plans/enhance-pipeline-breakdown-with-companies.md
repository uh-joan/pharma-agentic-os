# Enhancement Plan: Add Company/Sponsor Info to indication-drug-pipeline-breakdown

## Executive Summary

**Goal**: Enhance existing `indication-drug-pipeline-breakdown` skill to include company/sponsor information

**Effort**: 2-3 days

**Value**: Everyone using the pipeline skill automatically gets "who's working on what" insights

**Risk**: Low (contained change to proven skill)

---

## Current State

### What the Skill Currently Returns

```python
{
    'indication': 'KRAS inhibitor',
    'total_trials': 363,
    'total_unique_drugs': 31,
    'approved_drugs': ['Sotorasib', 'Adagrasib'],
    'phase_breakdown': {
        'Phase 1': {'trials': 6, 'unique_drugs': 3, 'drugs': [...]},
        'Phase 2': {'trials': 12, 'unique_drugs': 7, 'drugs': [...]},
        'Phase 3': {'trials': 5, 'unique_drugs': 5, 'drugs': [...]},
        'Phase 4': {...},
        'Not Applicable': {...}
    },
    'visualization': '...'
}
```

### What's Missing

- ❌ No company/sponsor information
- ❌ Can't answer "Who's working on this?"
- ❌ Can't see competitive landscape by company

---

## Proposed Enhancement

### New Output Structure

```python
{
    'indication': 'KRAS inhibitor',
    'total_trials': 363,
    'total_unique_drugs': 31,
    'approved_drugs': ['Sotorasib', 'Adagrasib'],
    'phase_breakdown': {...},  # Unchanged
    'visualization': '...',     # Unchanged

    # NEW FIELDS
    'companies': {
        'Amgen': {
            'total_trials': 5,
            'phases': ['Phase 1', 'Phase 2', 'Phase 3'],
            'drugs': ['Sotorasib', 'AMG 510', ...],
            'approved': 1
        },
        'Mirati Therapeutics': {
            'total_trials': 3,
            'phases': ['Phase 2', 'Phase 3'],
            'drugs': ['Adagrasib', ...],
            'approved': 1
        },
        'Revolution Medicines': {
            'total_trials': 4,
            'phases': ['Phase 1', 'Phase 2'],
            'drugs': ['RMC-6236', 'RMC-6291', ...],
            'approved': 0
        }
    },
    'total_companies': 6,
    'company_summary': 'Top sponsors: Amgen (5 trials), Mirati (3 trials), Revolution Medicines (4 trials)'
}
```

---

## Implementation Plan

### Day 1: Sponsor Extraction Logic

**Task 1.1**: Extract sponsor from existing trial data

The skill already fetches detailed trial data via `get_study()`. We just need to parse the sponsor field.

**Location**: Line ~80 in `get_indication_drug_pipeline_breakdown.py` (after trial details fetched)

**Code Addition**:

```python
# Around line 80-90 (after get_study() call)
def extract_sponsor_from_trial(trial_markdown: str) -> str:
    """Extract lead sponsor from trial markdown."""
    # Pattern: **Sponsor:** Amgen
    sponsor_match = re.search(r'\*\*Sponsor:\*\*\s+(.+?)(?:\n|$)', trial_markdown)

    if sponsor_match:
        sponsor = sponsor_match.group(1).strip()
        # Clean up common patterns
        sponsor = re.sub(r'\s+\(.*?\)', '', sponsor)  # Remove parentheticals
        return sponsor

    return "Unknown"
```

**Test Cases**:
```python
# Test extraction
assert extract_sponsor_from_trial("**Sponsor:** Amgen\n") == "Amgen"
assert extract_sponsor_from_trial("**Sponsor:** Pfizer Inc\n") == "Pfizer Inc"
assert extract_sponsor_from_trial("No sponsor field") == "Unknown"
```

---

**Task 1.2**: M&A Attribution Module

Create helper for company hierarchy (acquired companies → parent)

**Location**: New function before main function

**Code Addition**:

```python
# Add at top of file (after imports)
COMPANY_HIERARCHY = {
    # Acquisitions (acquired → parent)
    'Celgene': 'Bristol Myers Squibb',
    'Celgene Corporation': 'Bristol Myers Squibb',
    'Array BioPharma': 'Pfizer',
    'Array BioPharma Inc.': 'Pfizer',
    'Five Prime Therapeutics': 'Amgen',
    'Mirati Therapeutics': 'Bristol Myers Squibb',  # Acquired Dec 2024
    'ChemoCentryx': 'Amgen',  # Acquired 2022
    'Immunomedics': 'Gilead Sciences',  # Acquired 2020
    'Kite Pharma': 'Gilead Sciences',  # Acquired 2017
    'Tesaro': 'GlaxoSmithKline',  # Acquired 2019
    'Loxo Oncology': 'Eli Lilly',  # Acquired 2019

    # Normalize variations
    'Pfizer Inc': 'Pfizer',
    'Pfizer Inc.': 'Pfizer',
    'Amgen Inc': 'Amgen',
    'Amgen Inc.': 'Amgen',
    'Bristol-Myers Squibb': 'Bristol Myers Squibb',
    'Bristol-Myers Squibb Company': 'Bristol Myers Squibb',
}

def attribute_company(sponsor_name: str) -> str:
    """
    Map sponsor to parent company (handles M&A and name variations).

    Args:
        sponsor_name: Sponsor name from trial (e.g., "Celgene")

    Returns:
        Parent company name (e.g., "Bristol Myers Squibb")
    """
    # Check hierarchy first (M&A)
    if sponsor_name in COMPANY_HIERARCHY:
        return COMPANY_HIERARCHY[sponsor_name]

    # Check for partial matches (handle "Inc", "Inc.", "Corporation", etc.)
    for acquired, parent in COMPANY_HIERARCHY.items():
        if acquired.lower() in sponsor_name.lower():
            return parent

    return sponsor_name
```

**Test Cases**:
```python
assert attribute_company("Celgene") == "Bristol Myers Squibb"
assert attribute_company("Celgene Corporation") == "Bristol Myers Squibb"
assert attribute_company("Pfizer Inc") == "Pfizer"
assert attribute_company("Unknown Company") == "Unknown Company"
```

---

**Task 1.3**: Integrate into existing loop

**Location**: Inside the trial processing loop (~line 120)

**Code Modification**:

```python
# BEFORE (existing code around line 120):
for nct_id in trials_to_analyze:
    trial_data = get_study(nct_id)

    # Extract phase
    phase_match = re.search(r'\*\*Phase:\*\*\s+(.+?)(?:\n|$)', trial_data)
    phase = normalize_phase(phase_match.group(1)) if phase_match else 'Not Applicable'

    # Extract drugs
    drugs = extract_drugs(trial_data)

    # Count trials and drugs
    phase_data[phase]['trials'] += 1
    for drug in drugs:
        phase_data[phase]['drugs'].add(drug)

# AFTER (add sponsor extraction):
# Initialize company tracking at top of function
company_data = defaultdict(lambda: {
    'trials': 0,
    'phases': set(),
    'drugs': set(),
    'approved': 0
})

for nct_id in trials_to_analyze:
    trial_data = get_study(nct_id)

    # Extract phase
    phase_match = re.search(r'\*\*Phase:\*\*\s+(.+?)(?:\n|$)', trial_data)
    phase = normalize_phase(phase_match.group(1)) if phase_match else 'Not Applicable'

    # Extract drugs
    drugs = extract_drugs(trial_data)

    # NEW: Extract and attribute sponsor
    sponsor = extract_sponsor_from_trial(trial_data)
    sponsor = attribute_company(sponsor)

    # Count trials and drugs
    phase_data[phase]['trials'] += 1
    for drug in drugs:
        phase_data[phase]['drugs'].add(drug)

    # NEW: Track by company
    company_data[sponsor]['trials'] += 1
    company_data[sponsor]['phases'].add(phase)
    for drug in drugs:
        company_data[sponsor]['drugs'].add(drug)
```

---

### Day 2: Company Summary & Output

**Task 2.1**: Add approved drug attribution

After FDA cross-check (existing code around line 200), attribute approvals to companies

**Code Addition**:

```python
# After FDA cross-check
print(f"✓ Found {len(approved_drugs)} FDA approved drugs")

# NEW: Attribute approved drugs to companies
for company in company_data:
    # Count how many of this company's drugs are approved
    company_approved_count = sum(
        1 for drug in company_data[company]['drugs']
        if drug in approved_drugs
    )
    company_data[company]['approved'] = company_approved_count
```

---

**Task 2.2**: Format company output

**Code Addition**:

```python
# NEW: Format company data for output
def format_company_data(company_data: dict) -> dict:
    """Convert company tracking data to clean output format."""

    formatted = {}
    for company, data in company_data.items():
        if company == "Unknown":
            continue  # Skip unknown sponsors

        formatted[company] = {
            'total_trials': data['trials'],
            'phases': sorted(list(data['phases'])),
            'drugs': sorted(list(data['drugs'])),
            'approved': data['approved']
        }

    # Sort by trial count (descending)
    return dict(sorted(
        formatted.items(),
        key=lambda x: x[1]['total_trials'],
        reverse=True
    ))

# Format companies
companies = format_company_data(company_data)
total_companies = len(companies)

# Create summary
top_3 = list(companies.items())[:3]
company_summary = "Top sponsors: " + ", ".join(
    f"{name} ({data['total_trials']} trials)"
    for name, data in top_3
)
```

---

**Task 2.3**: Update return statement

**Location**: End of function (around line 250)

**Code Modification**:

```python
# BEFORE:
return {
    'indication': indication,
    'total_trials': total_trials,
    'total_unique_drugs': total_unique_drugs,
    'approved_drugs': approved_drugs,
    'phase_breakdown': phase_breakdown,
    'visualization': visualization
}

# AFTER:
return {
    'indication': indication,
    'total_trials': total_trials,
    'total_unique_drugs': total_unique_drugs,
    'approved_drugs': approved_drugs,
    'phase_breakdown': phase_breakdown,
    'visualization': visualization,

    # NEW
    'companies': companies,
    'total_companies': total_companies,
    'company_summary': company_summary
}
```

---

**Task 2.4**: Update output display (if __name__ == "__main__")

**Location**: After existing output (around line 280)

**Code Addition**:

```python
# Existing output (unchanged)
print(result['visualization'])
print(f"\nTotal trials: {result['total_trials']}")
print(f"Unique drugs: {result['total_unique_drugs']}")
print(f"FDA approved: {len(result['approved_drugs'])}")

# NEW: Display company information
print("\n" + "=" * 80)
print("COMPANY LANDSCAPE")
print("=" * 80)
print(f"\nTotal Companies: {result['total_companies']}")
print(f"\n{result['company_summary']}")

print("\nTop 10 Companies by Trial Count:")
print("-" * 80)
for i, (company, data) in enumerate(list(result['companies'].items())[:10], 1):
    phases_str = ", ".join(data['phases'])
    approved_marker = f" ✓ {data['approved']} approved" if data['approved'] > 0 else ""
    print(f"{i:2}. {company:40} {data['total_trials']:2} trials ({phases_str}){approved_marker}")
```

---

### Day 3: Testing & Documentation

**Task 3.1**: Test with diverse examples

```bash
# Test case 1: Crowded space (many companies)
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/indication-drug-pipeline-breakdown/scripts/get_indication_drug_pipeline_breakdown.py "KRAS inhibitor"

# Expected: 6-8 companies, including Amgen, Mirati, Revolution Medicines

# Test case 2: Sparse space (few companies)
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/indication-drug-pipeline-breakdown/scripts/get_indication_drug_pipeline_breakdown.py "Duchenne muscular dystrophy"

# Expected: 3-5 companies, specialty pharma focus

# Test case 3: M&A attribution test
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/indication-drug-pipeline-breakdown/scripts/get_indication_drug_pipeline_breakdown.py "multiple myeloma"

# Expected: Celgene trials should be attributed to Bristol Myers Squibb
```

**Validation Checklist**:
- [ ] Sponsor extraction works (no "Unknown" for major trials)
- [ ] M&A attribution correct (Celgene → Bristol Myers Squibb)
- [ ] Company counts accurate
- [ ] Approved drug attribution works
- [ ] Output formatting clean
- [ ] No errors on edge cases (trials without sponsors)

---

**Task 3.2**: Update SKILL.md documentation

**Location**: `.claude/skills/indication-drug-pipeline-breakdown/SKILL.md`

**Updates Needed**:

1. **Update description** (line 3):
```yaml
description: >
  Active drug pipeline analysis for any indication showing phase breakdown,
  unique drug counts, FDA approval status, **company/sponsor landscape**, and
  elegant ASCII visualization.
```

2. **Add to "When to Use This Skill"** (line 71):
```markdown
- **Competitive landscape**: Understanding which companies are active
- **M&A analysis**: Tracking sponsor changes (acquisitions handled automatically)
```

3. **Update "Output Structure"** (line 79):
```markdown
Returns dict with:
- `indication`: Disease/condition analyzed
- `total_trials`: Total clinical trials found
- `total_unique_drugs`: Total unique drug interventions
- `approved_drugs`: List of FDA approved drugs (cross-checked)
- `phase_breakdown`: Dict with trials/drugs per phase
- `visualization`: ASCII bar chart showing distribution
- **`companies`**: Dict with company/sponsor breakdown (NEW)
- **`total_companies`**: Total unique companies/sponsors (NEW)
- **`company_summary`**: Text summary of top sponsors (NEW)
```

4. **Add to "Example Output"** (after visualization):
```markdown
Company Landscape
--------------------------------------------------------------------------------
Total Companies: 8

Top sponsors: Amgen (5 trials), Mirati Therapeutics (3 trials), Revolution Medicines (4 trials)

Top 10 Companies by Trial Count:
 1. Amgen                                   5 trials (Phase 1, Phase 2, Phase 3) ✓ 1 approved
 2. Revolution Medicines                    4 trials (Phase 1, Phase 2)
 3. Mirati Therapeutics                     3 trials (Phase 2, Phase 3) ✓ 1 approved
 4. Eli Lilly                              2 trials (Phase 1)
 5. Roche                                  2 trials (Phase 1, Phase 2)
```

5. **Update "Implementation Details"** (line 117):
Add new section:
```markdown
6. **Company Attribution**: Handles M&A and name variations
   - Extracts lead sponsor from trial metadata
   - Applies M&A mapping (e.g., Celgene → Bristol Myers Squibb)
   - Normalizes company name variations (Inc., Inc, Corporation)
   - Tracks trials, phases, drugs per company
   - Cross-references with approved drugs
```

6. **Add to "Limitations"** (line 167):
```markdown
5. **M&A mapping**: Only tracks known major acquisitions (updated manually)
6. **Sponsor attribution**: Uses lead sponsor only (doesn't track collaborators)
```

7. **Add to "Future Enhancements"** (line 174):
```markdown
- Collaborator tracking (beyond lead sponsor)
- Automatic M&A database updates
- Company financial data integration
- Geographic presence by company
```

---

**Task 3.3**: Update index.json

**Location**: `.claude/skills/index.json`

Find the `indication-drug-pipeline-breakdown` entry and update:

```json
{
  "name": "get_indication_drug_pipeline_breakdown",
  "folder": "indication-drug-pipeline-breakdown",
  "category": "drug-discovery",
  "description": "Active drug pipeline analysis with phase breakdown, company landscape, and FDA approval status",
  "patterns_demonstrated": [
    "pagination",
    "markdown_parsing",
    "intervention_extraction",
    "data_aggregation",
    "ascii_visualization",
    "multi_server_query",
    "company_attribution"  // NEW
  ],
  "complexity": "complex",
  "health": "healthy",
  "servers": ["ct_gov_mcp", "fda_mcp"],
  "last_verified": "2025-11-25"  // Update date
}
```

---

## Testing Script

Create quick validation script:

**File**: `.claude/skills/indication-drug-pipeline-breakdown/test_company_enhancement.py`

```python
#!/usr/bin/env python3
"""Quick test for company enhancement."""
import sys
sys.path.insert(0, ".claude")

from skills.indication_drug_pipeline_breakdown.scripts.get_indication_drug_pipeline_breakdown import (
    get_indication_drug_pipeline_breakdown
)

def test_company_enhancement():
    """Test that company fields are present and populated."""

    print("Testing company enhancement...")

    # Test with KRAS inhibitor (known crowded space)
    result = get_indication_drug_pipeline_breakdown("KRAS inhibitor")

    # Verify new fields exist
    assert 'companies' in result, "Missing 'companies' field"
    assert 'total_companies' in result, "Missing 'total_companies' field"
    assert 'company_summary' in result, "Missing 'company_summary' field"

    # Verify data populated
    assert result['total_companies'] > 0, "No companies found"
    assert len(result['companies']) == result['total_companies'], "Company count mismatch"

    # Verify structure
    for company, data in result['companies'].items():
        assert 'total_trials' in data, f"Missing trial count for {company}"
        assert 'phases' in data, f"Missing phases for {company}"
        assert 'drugs' in data, f"Missing drugs for {company}"
        assert 'approved' in data, f"Missing approved count for {company}"

    # Verify M&A attribution (if Celgene trials exist, should be Bristol Myers Squibb)
    if 'Celgene' in result['companies']:
        raise AssertionError("Celgene should be attributed to Bristol Myers Squibb")

    print("✓ All tests passed!")
    print(f"✓ Found {result['total_companies']} companies")
    print(f"✓ Top company: {list(result['companies'].keys())[0]}")

    return True

if __name__ == "__main__":
    test_company_enhancement()
```

Run test:
```bash
PYTHONPATH=.claude:$PYTHONPATH python3 .claude/skills/indication-drug-pipeline-breakdown/test_company_enhancement.py
```

---

## Code Diff Summary

**Lines changed**: ~80 lines added, 5 lines modified
**Files modified**: 2 files

1. **`get_indication_drug_pipeline_breakdown.py`**:
   - Add: `COMPANY_HIERARCHY` dict (~40 lines)
   - Add: `extract_sponsor_from_trial()` function (~10 lines)
   - Add: `attribute_company()` function (~15 lines)
   - Add: Company tracking in main loop (~10 lines)
   - Add: `format_company_data()` function (~15 lines)
   - Modify: Return statement (add 3 fields)
   - Add: Company output display (~20 lines)

2. **`SKILL.md`**:
   - Update: Description, output structure, example output
   - Add: Company attribution to implementation details
   - Update: Limitations, future enhancements

---

## Rollout Plan

### Phase 1: Internal Testing (Day 3 morning)
- Test on 5 diverse indications
- Verify M&A attribution
- Check edge cases

### Phase 2: Documentation (Day 3 afternoon)
- Update SKILL.md
- Update index.json
- Add inline code comments

### Phase 3: Validation (End of Day 3)
- Run test script
- Verify output format
- Check backward compatibility (existing code still works)

---

## Success Metrics

✅ **Functionality**:
- [ ] Company extraction works (>90% trials have sponsor)
- [ ] M&A attribution correct (test with known acquisitions)
- [ ] Approved drug attribution accurate

✅ **Quality**:
- [ ] No errors on existing test cases
- [ ] Clean output formatting
- [ ] Informative company summary

✅ **Documentation**:
- [ ] SKILL.md updated
- [ ] index.json updated
- [ ] Code comments added

---

## Risk Mitigation

**Risk 1**: Sponsor field missing from some trials
- **Mitigation**: Use "Unknown" category, skip in company list

**Risk 2**: M&A data outdated
- **Mitigation**: Comment in code about last update date, easy to update dict

**Risk 3**: Breaking existing consumers
- **Mitigation**: Only adding fields, not changing existing ones (backward compatible)

---

## Timeline

**Day 1** (6-8 hours):
- Morning: Sponsor extraction + M&A attribution
- Afternoon: Integration into existing loop + testing

**Day 2** (6-8 hours):
- Morning: Approved drug attribution + company formatting
- Afternoon: Update return statement + output display

**Day 3** (4-6 hours):
- Morning: Testing with diverse examples
- Afternoon: Documentation updates + final validation

**Total**: 16-22 hours over 3 days

---

## Next Steps After Completion

Once this enhancement is done:
1. ✅ All users of `indication-drug-pipeline-breakdown` get company info
2. ✅ Builds foundation for Part 2 (`get_companies_by_moa`)
3. ✅ Enables competitive landscape analysis without new skills

Part 2 can then focus on querying by company or MoA specifically, building on this foundation.
