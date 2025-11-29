import sys
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search
import re
from datetime import datetime

def get_company_clinical_trials_portfolio(
    sponsor_name,
    status=None,
    condition=None,
    phase=None,
    start_year=2020
):
    """Get comprehensive clinical trial portfolio for any company sponsor.

    Args:
        sponsor_name (str): Company/sponsor name (e.g., "Boston Scientific", "Pfizer")
        status (str, optional): Trial status filter (e.g., "recruiting", "completed")
        condition (str, optional): Condition/disease filter
        phase (str, optional): Trial phase (e.g., "PHASE1", "PHASE2", "PHASE3")
        start_year (int, optional): Filter trials posted after this year (default: 2020)

    Returns:
        dict: Contains sponsor, total_trials, trials_by_status, trials_by_phase, trials list, and summary
    """

    # Build query parameters
    query_params = {
        'leadSponsorName': sponsor_name,
        'pageSize': 5000
    }

    if status:
        query_params['status'] = status
    if condition:
        query_params['condition'] = condition
    if phase:
        query_params['phase'] = phase

    # Execute search with pagination
    all_trials = []
    page_token = None
    page_count = 0

    while True:
        page_count += 1

        if page_token:
            query_params['pageToken'] = page_token

        result = search(**query_params)

        if not result or not isinstance(result, str):
            break

        # Parse trials from markdown response
        trial_sections = re.split(r'###\s+\d+\.\s+(NCT\d{8})', result)

        # Process pairs of (NCT ID, content)
        for i in range(1, len(trial_sections), 2):
            if i + 1 < len(trial_sections):
                nct_id = trial_sections[i]
                content = trial_sections[i + 1]

                trial = parse_trial_content(nct_id, content, start_year)
                if trial:
                    all_trials.append(trial)

        # Check for next page token
        next_token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        if next_token_match and page_count < 10:
            page_token = next_token_match.group(1)
        else:
            break

    # Generate statistics
    trials_by_status = {}
    trials_by_phase = {}

    for trial in all_trials:
        status_val = trial.get('status', 'Unknown')
        trials_by_status[status_val] = trials_by_status.get(status_val, 0) + 1

        phase_val = trial.get('phase', 'Unknown')
        trials_by_phase[phase_val] = trials_by_phase.get(phase_val, 0) + 1

    trials_by_status = dict(sorted(trials_by_status.items(), key=lambda x: x[1], reverse=True))
    trials_by_phase = dict(sorted(trials_by_phase.items(), key=lambda x: x[1], reverse=True))

    filters = {
        'sponsor': sponsor_name,
        'start_year': start_year
    }
    if status:
        filters['status'] = status
    if condition:
        filters['condition'] = condition
    if phase:
        filters['phase'] = phase

    summary = generate_summary(sponsor_name, len(all_trials), trials_by_status, trials_by_phase, filters)

    return {
        'sponsor': sponsor_name,
        'total_trials': len(all_trials),
        'filters_applied': filters,
        'trials_by_status': trials_by_status,
        'trials_by_phase': trials_by_phase,
        'trials': all_trials,
        'summary': summary
    }

def parse_trial_content(nct_id, content, start_year):
    """Parse individual trial content from markdown."""

    posted_match = re.search(r'\*\*First Posted:\*\*\s*(.+?)(?:\n|$)', content)
    if posted_match:
        posted_date = posted_match.group(1).strip()
        try:
            posted_year = int(posted_date.split()[-1])
            if posted_year < start_year:
                return None
        except:
            pass
    else:
        posted_date = 'Unknown'

    title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', content)
    title = title_match.group(1).strip() if title_match else 'Unknown'

    status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', content)
    status = status_match.group(1).strip() if status_match else 'Unknown'

    phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', content)
    phase = phase_match.group(1).strip() if phase_match else 'Unknown'

    conditions_match = re.search(r'\*\*Conditions:\*\*\s*(.+?)(?:\n\*\*|\n\n|$)', content, re.DOTALL)
    conditions = []
    if conditions_match:
        cond_text = conditions_match.group(1).strip()
        conditions = [c.strip() for c in cond_text.split('|') if c.strip()]

    interventions_match = re.search(r'\*\*Interventions:\*\*\s*(.+?)(?:\n\*\*|\n\n|$)', content, re.DOTALL)
    interventions = []
    if interventions_match:
        int_text = interventions_match.group(1).strip()
        interventions = [i.strip() for i in int_text.split('|') if i.strip()]

    enrollment_match = re.search(r'\*\*Enrollment:\*\*\s*(\d+)', content)
    enrollment = int(enrollment_match.group(1)) if enrollment_match else 0

    return {
        'nct_id': nct_id,
        'title': title,
        'status': status,
        'phase': phase,
        'posted_date': posted_date,
        'conditions': conditions,
        'interventions': interventions,
        'enrollment': enrollment
    }

def generate_summary(sponsor, total, by_status, by_phase, filters):
    """Generate human-readable summary."""

    lines = [
        f"Clinical Trials Portfolio: {sponsor}",
        f"Total Trials: {total}",
        ""
    ]

    if len(filters) > 2:
        lines.append("Filters Applied:")
        for key, value in filters.items():
            if key not in ['sponsor']:
                lines.append(f"  - {key}: {value}")
        lines.append("")

    if by_status:
        lines.append("Trials by Status:")
        for status, count in list(by_status.items())[:5]:
            percentage = (count / total * 100) if total > 0 else 0
            lines.append(f"  - {status}: {count} ({percentage:.1f}%)")
        lines.append("")

    if by_phase:
        lines.append("Trials by Phase:")
        for phase, count in list(by_phase.items())[:5]:
            percentage = (count / total * 100) if total > 0 else 0
            lines.append(f"  - {phase}: {count} ({percentage:.1f}%)")

    return "\n".join(lines)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Get comprehensive clinical trial portfolio for any company sponsor'
    )
    parser.add_argument('sponsor', help='Company/sponsor name (e.g., "Boston Scientific", "Pfizer")')
    parser.add_argument('--status', help='Trial status filter (e.g., "recruiting", "completed")')
    parser.add_argument('--condition', help='Condition/disease filter (e.g., "atrial fibrillation")')
    parser.add_argument('--phase', help='Trial phase (e.g., "PHASE1", "PHASE2", "PHASE3")')
    parser.add_argument('--start-year', type=int, default=2020, help='Filter trials posted after this year (default: 2020)')

    args = parser.parse_args()

    result = get_company_clinical_trials_portfolio(
        sponsor_name=args.sponsor,
        status=args.status,
        condition=args.condition,
        phase=args.phase,
        start_year=args.start_year
    )

    print(result['summary'])
    print(f"\nTotal trials retrieved: {result['total_trials']}")

    if result['trials']:
        print("\nSample Trials:")
        for trial in result['trials'][:3]:
            print(f"\n  {trial['nct_id']}: {trial['title']}")
            print(f"  Status: {trial['status']} | Phase: {trial['phase']}")
            print(f"  Conditions: {', '.join(trial['conditions'][:2])}")
