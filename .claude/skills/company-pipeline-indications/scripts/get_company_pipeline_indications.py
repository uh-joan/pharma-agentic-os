import sys
import re
from collections import defaultdict
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search

def get_company_pipeline_indications(company: str):
    """Get active drug development indications for any pharmaceutical company.

    Identifies therapeutic areas and indications where a company is actively
    developing drugs by analyzing their clinical trial pipeline. Filters for
    active development statuses and aggregates conditions with phase/status breakdown.

    Args:
        company: Company name (e.g., "Novo Nordisk", "Pfizer", "Merck", "Eli Lilly")

    Returns:
        dict: Contains total_trials, unique_indications, indication_details, and summary
              - total_trials: Total number of active trials
              - unique_indications: Number of unique therapeutic areas
              - indication_details: List of dicts with per-indication breakdown
              - summary: Formatted text summary
    """

    # Active development statuses (OR-separated for CT.gov API)
    active_status_filter = "recruiting OR active_not_recruiting OR enrolling_by_invitation"

    all_trials = []
    page_token = None

    print(f"Fetching {company} trials (active statuses only)...")

    # Fetch all active trials with pagination
    while True:
        # Search for company sponsored/collaborated trials with active statuses
        # FIXED: Using 'lead' for sponsor filter and 'status' for recruitment status
        # (was using invalid 'query' and 'filter_overallStatus' parameters)
        result = search(
            lead=company,
            status=active_status_filter,
            pageSize=1000,
            pageToken=page_token
        )

        if not result or not isinstance(result, str):
            break

        # Parse trials from markdown
        trial_blocks = re.split(r'###\s+\d+\.\s+NCT\d{8}', result)

        for block in trial_blocks[1:]:  # Skip first empty split
            trial_data = {}

            # Extract NCT ID from block context
            nct_match = re.search(r'NCT\d{8}', block)
            if nct_match:
                trial_data['nct_id'] = nct_match.group()

            # Extract conditions
            conditions_match = re.search(r'\*\*Conditions:\*\*\s*(.+?)(?=\n\*\*|\n###|\Z)', block, re.DOTALL)
            if conditions_match:
                trial_data['conditions'] = conditions_match.group(1).strip()

            # Extract status
            status_match = re.search(r'\*\*Overall Status:\*\*\s*(.+?)(?=\n|\Z)', block)
            if status_match:
                trial_data['status'] = status_match.group(1).strip()

            # Extract phase
            phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?=\n|\Z)', block)
            if phase_match:
                trial_data['phase'] = phase_match.group(1).strip()

            # Extract title for context
            title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?=\n\*\*|\Z)', block, re.DOTALL)
            if title_match:
                trial_data['title'] = title_match.group(1).strip()

            if trial_data.get('conditions'):
                all_trials.append(trial_data)

        # Check for next page
        next_page_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        if next_page_match:
            page_token = next_page_match.group(1)
            print(f"  Fetched {len(all_trials)} trials so far, getting next page...")
        else:
            break

    print(f"Total trials fetched: {len(all_trials)}")

    # Aggregate by indication
    indication_stats = defaultdict(lambda: {
        'trial_count': 0,
        'phases': defaultdict(int),
        'statuses': defaultdict(int),
        'nct_ids': []
    })

    for trial in all_trials:
        conditions = trial.get('conditions', '')

        # Split conditions (often comma or semicolon separated)
        condition_list = re.split(r'[,;]\s*', conditions)

        for condition in condition_list:
            condition = condition.strip()
            if condition and condition.lower() != 'n/a':
                indication_stats[condition]['trial_count'] += 1
                indication_stats[condition]['nct_ids'].append(trial.get('nct_id', 'Unknown'))

                phase = trial.get('phase', 'Not Specified')
                indication_stats[condition]['phases'][phase] += 1

                status = trial.get('status', 'Unknown')
                indication_stats[condition]['statuses'][status] += 1

    # Sort indications by trial count
    sorted_indications = sorted(
        indication_stats.items(),
        key=lambda x: x[1]['trial_count'],
        reverse=True
    )

    # Format indication details
    indication_details = []
    for indication, stats in sorted_indications:
        # Format phase distribution
        phase_dist = ', '.join([f"{phase}: {count}" for phase, count in
                                sorted(stats['phases'].items(),
                                      key=lambda x: x[1], reverse=True)])

        # Format status distribution
        status_dist = ', '.join([f"{status}: {count}" for status, count in
                                 sorted(stats['statuses'].items(),
                                       key=lambda x: x[1], reverse=True)])

        indication_details.append({
            'indication': indication,
            'trial_count': stats['trial_count'],
            'phase_distribution': phase_dist,
            'status_distribution': status_dist,
            'sample_nct_ids': stats['nct_ids'][:3]  # First 3 for reference
        })

    # Generate summary
    summary = f"""
=== {company} Active Drug Development Pipeline ===

Total Active Trials: {len(all_trials)}
Unique Indications: {len(indication_stats)}

Top 20 Indications by Trial Count:
"""

    for i, detail in enumerate(indication_details[:20], 1):
        summary += f"\n{i}. {detail['indication']} ({detail['trial_count']} trials)"
        summary += f"\n   Phases: {detail['phase_distribution']}"
        summary += f"\n   Status: {detail['status_distribution']}"
        summary += f"\n   Sample NCT IDs: {', '.join(detail['sample_nct_ids'])}\n"

    if len(indication_details) > 20:
        summary += f"\n... and {len(indication_details) - 20} more indications"

    return {
        'total_trials': len(all_trials),
        'unique_indications': len(indication_stats),
        'indication_details': indication_details,
        'summary': summary
    }

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Get company pipeline indications')
    parser.add_argument('company', help='Company name (e.g., "Novo Nordisk", "Pfizer")')

    args = parser.parse_args()

    result = get_company_pipeline_indications(args.company)
    print(result['summary'])
