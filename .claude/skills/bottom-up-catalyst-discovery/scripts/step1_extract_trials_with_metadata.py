#!/usr/bin/env python3
"""
Step 1 Enhanced: Extract Trials with Full Metadata

Instead of just extracting sponsor names, this extracts complete trial details:
- NCT ID
- Trial title
- Lead sponsor
- Primary completion date
- Intervention (drug name)
- Condition (indication)
- Phase
- Status
- Enrollment

This allows us to carry trial details through the pipeline and enrich
the final list of public companies with their associated trials.
"""

import sys
import re
from typing import List, Dict, Optional

sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search


def get_quarter_date_range(quarter: str, year: int) -> str:
    """Convert quarter to CT.gov date range format.

    Args:
        quarter: "Q1", "Q2", "Q3", or "Q4"
        year: Year (e.g., 2025)

    Returns:
        str: Date range in CT.gov format "YYYY-MM-DD_YYYY-MM-DD"
    """
    quarter_dates = {
        'Q1': (f"{year}-01-01", f"{year}-03-31"),
        'Q2': (f"{year}-04-01", f"{year}-06-30"),
        'Q3': (f"{year}-07-01", f"{year}-09-30"),
        'Q4': (f"{year}-10-01", f"{year}-12-31")
    }
    start_date, end_date = quarter_dates.get(quarter.upper(), (f"{year}-10-01", f"{year}-12-31"))
    return f"{start_date}_{end_date}"


def extract_trial_details_from_markdown(markdown_text: str) -> List[Dict[str, str]]:
    """Extract complete trial details from CT.gov markdown response.

    Args:
        markdown_text: Markdown string from CT.gov search() function

    Returns:
        list: Trial dictionaries with all metadata
              [{
                  'nct_id': 'NCT12345678',
                  'title': 'Study of Drug X in Cancer',
                  'sponsor': 'AbbVie Inc.',
                  'phase': 'Phase3',
                  'status': 'Recruiting',
                  'completion_date': '2025-12-31',
                  'intervention': 'Drug X',
                  'condition': 'Non-Small Cell Lung Cancer',
                  'enrollment': '300'
              }, ...]
    """
    trials = []

    # Split markdown into individual trial sections
    # Each trial starts with "### N. NCT#########"
    trial_sections = re.split(r'(?=###\s+\d+\.\s+NCT)', markdown_text)

    for section in trial_sections:
        if not section.strip():
            continue

        trial = {}

        # Extract NCT ID from header line: "### 1. NCT05768997"
        nct_match = re.search(r'###\s+\d+\.\s+(NCT\d+)', section)
        if nct_match:
            trial['nct_id'] = nct_match.group(1).strip()
        else:
            continue  # Skip if no NCT ID

        # Extract Trial Title
        title_match = re.search(r'\*\*Title:\*\*\s*([^\n]+)', section)
        if title_match:
            trial['title'] = title_match.group(1).strip()

        # Extract Lead Sponsor
        sponsor_match = re.search(r'\*\*Lead Sponsor:\*\*\s*([^\n]+)', section)
        if sponsor_match:
            trial['sponsor'] = sponsor_match.group(1).strip()

        # Extract Phase
        phase_match = re.search(r'\*\*Phase:\*\*\s*([^\n]+)', section)
        if phase_match:
            trial['phase'] = phase_match.group(1).strip()

        # Extract Status
        status_match = re.search(r'\*\*Status:\*\*\s*([^\n]+)', section)
        if status_match:
            trial['status'] = status_match.group(1).strip()

        # Extract Primary Completion Date - may not be in response
        completion_match = re.search(r'\*\*Primary Completion Date:\*\*\s*([^\n]+)', section)
        if completion_match:
            trial['completion_date'] = completion_match.group(1).strip()
        else:
            trial['completion_date'] = 'Unknown'

        # Extract Conditions
        condition_match = re.search(r'\*\*Conditions:\*\*\s*([^\n]+)', section)
        if condition_match:
            trial['condition'] = condition_match.group(1).strip()

        # Extract Interventions - may not be in response
        intervention_match = re.search(r'\*\*Interventions:\*\*\s*([^\n]+)', section)
        if intervention_match:
            trial['intervention'] = intervention_match.group(1).strip()
        else:
            trial['intervention'] = 'Not specified'

        # Extract Enrollment
        enrollment_match = re.search(r'\*\*Enrollment:\*\*\s*(\d+)', section)
        if enrollment_match:
            trial['enrollment'] = enrollment_match.group(1).strip()
        else:
            trial['enrollment'] = 'Unknown'

        trials.append(trial)

    return trials


def get_trials_by_quarter_with_metadata(
    quarter: str = "Q4",
    year: int = 2025,
    phases: Optional[List[str]] = None,
    max_trials: int = 10000
) -> Dict[str, any]:
    """Extract all trials with full metadata for trials completing in quarter.

    Args:
        quarter: "Q1", "Q2", "Q3", or "Q4"
        year: Year (e.g., 2025)
        phases: List of phases (default: ["PHASE2", "PHASE3"])
        max_trials: Maximum trials to retrieve per phase (default: 10000)

    Returns:
        dict: {
            'quarter': 'Q4 2025',
            'total_trials': 234,
            'trials': [
                {
                    'nct_id': 'NCT12345678',
                    'title': 'Study of Drug X',
                    'sponsor': 'AbbVie Inc.',
                    'phase': 'PHASE3',
                    'status': 'RECRUITING',
                    'completion_date': '2025-12-31',
                    'intervention': 'Drug X',
                    'condition': 'Cancer',
                    'enrollment': '300'
                },
                ...
            ],
            'by_sponsor': {
                'AbbVie Inc.': [trial1, trial2, ...],
                'Amgen Inc.': [trial3, ...],
                ...
            }
        }
    """
    if phases is None:
        phases = ["PHASE2", "PHASE3"]

    all_trials = []

    # Get date range for quarter
    date_range = get_quarter_date_range(quarter, year)

    print(f"\n{'='*60}")
    print(f"Extracting Trials with Metadata from {quarter} {year}")
    print(f"Completion Date Range: {date_range}")
    print(f"{'='*60}\n")

    # Query each phase separately with pagination
    for phase in phases:
        print(f"Querying {phase} trials completing in {quarter} {year}...")

        try:
            start_date, end_date = date_range.split('_')
            complex_query = f"AREA[Phase]{phase} AND AREA[PrimaryCompletionDate]RANGE[{start_date},{end_date}]"

            phase_trials = []
            seen_nct_ids = set()  # Track duplicates
            page_token = None
            page_count = 0
            max_pages = max_trials // 1000 + 1

            # Paginate through all results
            while page_count < max_pages:
                if page_token:
                    result = search(complexQuery=complex_query, pageSize=1000, pageToken=page_token)
                else:
                    result = search(complexQuery=complex_query, pageSize=1000)

                # Extract trial details from markdown
                trials = extract_trial_details_from_markdown(result)
                page_count += 1

                # Track new trials (by NCT ID)
                new_trials = [t for t in trials if t['nct_id'] not in seen_nct_ids]
                seen_nct_ids.update(t['nct_id'] for t in trials)

                phase_trials.extend(trials)

                # Stop on partial page
                if len(trials) < 1000:
                    print(f"  ✓ Found {len(seen_nct_ids)} unique {phase} trials (across {page_count} pages, partial page)")
                    break

                # Safety: Stop if < 5% new trials (heavy duplicates)
                duplicate_ratio = len(new_trials) / len(trials) if trials else 0
                if duplicate_ratio < 0.05 and page_count > 1:
                    print(f"  ✓ Found {len(seen_nct_ids)} unique {phase} trials (across {page_count} pages)")
                    break

                # Try to get next page token
                # Note: CT.gov API bug - may return same token repeatedly
                next_token_match = re.search(r'nextPageToken["\s:]+([^"\s,}]+)', result)
                if next_token_match:
                    page_token = next_token_match.group(1).strip()
                else:
                    break

            all_trials.extend(phase_trials)

        except Exception as e:
            print(f"  ✗ Error querying {phase} trials: {str(e)}")
            continue

    # Group trials by sponsor
    trials_by_sponsor = {}
    for trial in all_trials:
        sponsor = trial.get('sponsor', 'Unknown')
        if sponsor not in trials_by_sponsor:
            trials_by_sponsor[sponsor] = []
        trials_by_sponsor[sponsor].append(trial)

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total trials: {len(all_trials)}")
    print(f"  Unique sponsors: {len(trials_by_sponsor)}")
    print(f"{'='*60}\n")

    return {
        'quarter': f'{quarter} {year}',
        'total_trials': len(all_trials),
        'trials': all_trials,
        'by_sponsor': trials_by_sponsor,
        'unique_sponsors': list(trials_by_sponsor.keys())
    }


# Make script executable
if __name__ == "__main__":
    # Test with Q4 2025
    result = get_trials_by_quarter_with_metadata(
        quarter="Q4",
        year=2025,
        phases=["PHASE3"],  # Test with Phase 3 only
        max_trials=1000  # Limit for testing
    )

    print(f"\n\nSample Trial Details:")
    print("="*60)

    # Show first 3 trials
    for trial in result['trials'][:3]:
        print(f"\nNCT ID: {trial.get('nct_id')}")
        print(f"  Sponsor: {trial.get('sponsor')}")
        print(f"  Drug: {trial.get('intervention')}")
        print(f"  Indication: {trial.get('condition')}")
        print(f"  Completion: {trial.get('completion_date')}")
        print(f"  Phase: {trial.get('phase')}")
        print(f"  Enrollment: {trial.get('enrollment')}")

    # Show sponsor with most trials
    sponsor_counts = [(s, len(trials)) for s, trials in result['by_sponsor'].items()]
    sponsor_counts.sort(key=lambda x: x[1], reverse=True)

    print(f"\n\nTop 10 Sponsors by Trial Count:")
    print("="*60)
    for sponsor, count in sponsor_counts[:10]:
        print(f"  {sponsor}: {count} trials")
