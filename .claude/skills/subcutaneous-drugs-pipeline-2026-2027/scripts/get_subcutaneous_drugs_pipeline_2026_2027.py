import sys
import re
from datetime import datetime
from collections import defaultdict
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search, get_study


def parse_trial_detail(nct_id, trial_detail):
    """Parse detailed trial information from get_study() markdown response."""

    def extract_field(pattern, text, default="Not specified"):
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        return match.group(1).strip() if match else default

    # Extract completion date (use Study Completion, not Primary Completion Date)
    completion_date = extract_field(r'\*\*Study Completion:\*\*\s*(.+?)(?=\n|$)', trial_detail)

    # Extract other key fields
    title = extract_field(r'\*\*Study Title:\*\*\s*(.+?)(?=\n|$)', trial_detail)
    status = extract_field(r'\*\*Status:\*\*\s*(.+?)(?=\n|$)', trial_detail)
    phase = extract_field(r'\*\*Phase:\*\*\s*(.+?)(?=\n|$)', trial_detail)
    sponsor = extract_field(r'\*\*Lead Sponsor:\*\*\s*(.+?)(?=\(|$)', trial_detail)

    # Conditions section
    condition_match = re.search(r'## Conditions\s+[-\s]+(.*?)(?=\n##|\Z)', trial_detail, re.DOTALL)
    condition = condition_match.group(1).strip() if condition_match else "Not specified"

    # Interventions section
    intervention_match = re.search(r'## Interventions\s+###\s+([^:]+):\s+(.+?)(?=\n##|\Z)', trial_detail, re.DOTALL)
    if intervention_match:
        intervention_type = intervention_match.group(1).strip()
        intervention = intervention_match.group(2).strip().split('\n')[0]  # First line
    else:
        intervention_type = "Not specified"
        intervention = "Not specified"

    enrollment = extract_field(r'\*\*Enrollment:\*\*\s*(\d+)', trial_detail, "0")

    return {
        'nct_id': nct_id,
        'title': title,
        'status': status,
        'phase': phase,
        'completion_date': completion_date,
        'sponsor': sponsor,
        'condition': condition,
        'intervention': intervention,
        'intervention_type': intervention_type,
        'enrollment': int(enrollment) if enrollment.isdigit() else 0
    }


def get_subcutaneous_drugs_pipeline_2026_2027():
    """Find subcutaneous drugs in Phase 3 expected to be approved in 2026-2027.

    Strategy:
    1. Search Phase 3 trials mentioning "subcutaneous"
    2. Filter for completed or active (not recruiting) trials
    3. Fetch detailed trial information for each
    4. Parse completion dates and filter for 2024-2025 (→ 2026-2027 approval)
    5. Analyze therapeutic areas, sponsors, and timelines

    Returns:
        dict: Contains total_count, trials_data, and summary
    """

    print("Step 1: Searching Phase 3 trials with subcutaneous administration...")

    # Step 1a: Quick query to get total count (orphan drugs pattern)
    result_preview = search(
        term="subcutaneous",
        phase="PHASE3",
        pageSize=1
    )

    # Extract total available (handle comma-separated numbers like "3,028")
    total_match = re.search(r'\*\*Results:\*\*\s*[\d,]+\s*of\s*([\d,]+)', result_preview)
    if not total_match:
        print("Could not determine total trial count")
        return {
            'total_count': 0,
            'target_count': 0,
            'trials': [],
            'summary': {}
        }

    total_available = int(total_match.group(1).replace(',', ''))
    print(f"  Found {total_available} total trials available")

    # Step 1b: Calculate optimal pageSize to fetch all trials in 2 pages
    from math import ceil
    optimal_page_size = ceil(total_available / 2)
    print(f"  Using optimal pageSize={optimal_page_size} (fetches all trials in 2 pages)")

    # Step 1c: Collect NCT IDs from all pages (using set for deduplication)
    all_nct_ids = set()
    page_num = 1
    next_token = None

    while True:
        result = search(
            term="subcutaneous",
            phase="PHASE3",
            pageSize=optimal_page_size,
            pageToken=next_token
        ) if next_token else search(
            term="subcutaneous",
            phase="PHASE3",
            pageSize=optimal_page_size
        )

        if not result:
            break

        # Extract NCT IDs (set automatically deduplicates)
        page_nct_ids = set(re.findall(r'NCT\d{8}', result))
        all_nct_ids.update(page_nct_ids)

        print(f"  Page {page_num}: collected {len(page_nct_ids)} trials (total: {len(all_nct_ids)})")

        # Check for next page token
        next_token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        if next_token_match:
            next_token = next_token_match.group(1)
            page_num += 1
        else:
            print(f"  Completed: {page_num} page(s), {len(all_nct_ids)} unique trials")
            break

    nct_ids = list(all_nct_ids)
    total_count = len(nct_ids)

    print(f"\nStep 2: Fetching detailed information for all {total_count} trials...")
    print(f"  (This may take several minutes for {total_count} trials)")

    # Step 2: Fetch detailed trial data for each NCT ID
    all_trials = []
    error_count = 0

    for i, nct_id in enumerate(nct_ids, 1):
        # Progress indicator every 100 trials
        if i % 100 == 0 or i == total_count:
            print(f"  Progress: {i}/{total_count} ({len(all_trials)} successful, {error_count} errors)")

        try:
            # Get full trial details (much more reliable than parsing search markdown)
            trial_detail = get_study(nctId=nct_id)

            if not trial_detail:
                error_count += 1
                continue

            # Parse detailed information
            trial_data = parse_trial_detail(nct_id, trial_detail)
            if trial_data:
                all_trials.append(trial_data)
            else:
                error_count += 1

        except Exception as e:
            error_count += 1
            if error_count <= 3:  # Show first 3 errors
                print(f"    Error on {nct_id}: {str(e)[:60]}")
            continue

    print(f"\nCompleted: {len(all_trials)} trials retrieved ({error_count} errors)")

    print("\nStep 3: Filtering for trials likely to lead to 2026-2027 approval...")

    # Step 3: Filter for 2024-2025 completion dates
    target_trials = []

    for trial in all_trials:
        completion_date = trial.get('completion_date', '')

        if not completion_date or completion_date == "Not specified":
            continue

        # Strip "(Estimated)" or "(Actual)" suffix
        completion_date = re.sub(r'\s*\((Estimated|Actual)\)\s*$', '', completion_date).strip()

        # Try to parse the date robustly (multiple formats)
        parsed_date = None
        for fmt in ['%B %d, %Y', '%B %Y', '%Y-%m-%d', '%m/%Y', '%Y']:
            try:
                parsed_date = datetime.strptime(completion_date, fmt)
                break
            except:
                continue

        if parsed_date:
            year = parsed_date.year

            # Include trials completing in 2024-2025
            if year in [2024, 2025]:
                target_trials.append(trial)

    print(f"  Found {len(target_trials)} trials completing in 2024-2025")
    
    # Analyze therapeutic areas
    therapeutic_areas = {}
    sponsors = {}
    status_counts = {}
    
    for trial in target_trials:
        # Count therapeutic areas
        condition = trial.get('condition', 'Unknown')
        therapeutic_areas[condition] = therapeutic_areas.get(condition, 0) + 1
        
        # Count sponsors
        sponsor = trial.get('sponsor', 'Unknown')
        sponsors[sponsor] = sponsors.get(sponsor, 0) + 1
        
        # Count statuses
        status = trial.get('status', 'Unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Sort by frequency
    top_areas = sorted(therapeutic_areas.items(), key=lambda x: x[1], reverse=True)[:10]
    top_sponsors = sorted(sponsors.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Create summary
    summary = {
        'total_phase3_subcutaneous': len(all_trials),
        'likely_2026_2027_approval': len(target_trials),
        'top_therapeutic_areas': top_areas,
        'top_sponsors': top_sponsors,
        'status_distribution': status_counts,
        'completion_years': {
            '2024': sum(1 for t in target_trials if '2024' in t.get('completion_date', '')),
            '2025': sum(1 for t in target_trials if '2025' in t.get('completion_date', ''))
        }
    }
    
    return {
        'total_count': len(all_trials),
        'target_count': len(target_trials),
        'trials': target_trials,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_subcutaneous_drugs_pipeline_2026_2027()
    
    print("\n" + "="*80)
    print("SUBCUTANEOUS DRUGS PIPELINE: 2026-2027 APPROVAL FORECAST")
    print("="*80)
    
    print(f"\nTotal Phase 3 trials with subcutaneous administration: {result['total_count']}")
    print(f"Trials likely for 2026-2027 approval (completing 2024-2025): {result['target_count']}")
    
    summary = result['summary']
    
    print(f"\nCompletion Timeline:")
    print(f"  • Completing in 2024: {summary['completion_years']['2024']} trials")
    print(f"  • Completing in 2025: {summary['completion_years']['2025']} trials")
    
    print(f"\nTrial Status Distribution:")
    for status, count in sorted(summary['status_distribution'].items(), key=lambda x: x[1], reverse=True):
        print(f"  • {status}: {count} trials")
    
    print(f"\nTop Therapeutic Areas:")
    for i, (area, count) in enumerate(summary['top_therapeutic_areas'], 1):
        print(f"  {i}. {area}: {count} trials")
    
    print(f"\nTop Sponsors:")
    for i, (sponsor, count) in enumerate(summary['top_sponsors'], 1):
        print(f"  {i}. {sponsor}: {count} trials")
    
    print(f"\n" + "="*80)
    print("ANALYSIS")
    print("="*80)
    print("\nApproval Timeline Rationale:")
    print("• Phase 3 trials completing in 2024-2025")
    print("• Typical FDA review: 1-2 years")
    print("• Expected approval window: 2026-2027")
    print("\nNote: This is a probabilistic forecast based on completion dates.")
    print("Actual approval depends on trial results, FDA review speed, and regulatory factors.")
