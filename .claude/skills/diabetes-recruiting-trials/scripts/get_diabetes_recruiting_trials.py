import sys
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search
import re

def get_diabetes_recruiting_trials():
    """Get all recruiting diabetes clinical trials.

    Returns:
        dict: Contains total_count, trials data, and summary with:
            - total_recruiting_trials: Total number of trials found
            - pages_fetched: Number of pages retrieved
            - phase_distribution: Breakdown by trial phase
            - intervention_types: Breakdown by intervention type
    """
    all_trials = []
    page_token = None
    page_count = 0

    print("Collecting diabetes recruiting trials...")

    while True:
        page_count += 1
        print(f"Fetching page {page_count}...")

        # Query CT.gov for diabetes recruiting trials
        if page_token:
            result = search(
                query="diabetes",
                filter_overallStatus="RECRUITING",
                pageSize=1000,
                pageToken=page_token
            )
        else:
            result = search(
                query="diabetes",
                filter_overallStatus="RECRUITING",
                pageSize=1000
            )

        # CT.gov returns markdown - parse trials
        trials = re.split(r'###\s+\d+\.\s+NCT\d{8}', result)
        trials = [t.strip() for t in trials if t.strip()]

        all_trials.extend(trials)

        # Check for next page token
        token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        if token_match:
            page_token = token_match.group(1)
            print(f"Found page token, continuing...")
        else:
            break

    total_count = len(all_trials)

    # Extract phases and interventions for summary
    phases = {}
    interventions = {}

    for trial in all_trials:
        # Extract phase
        phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', trial)
        if phase_match:
            phase = phase_match.group(1).strip()
            phases[phase] = phases.get(phase, 0) + 1

        # Extract intervention type
        intervention_match = re.search(r'\*\*Intervention Type:\*\*\s*(.+?)(?:\n|$)', trial)
        if intervention_match:
            intervention = intervention_match.group(1).strip()
            interventions[intervention] = interventions.get(intervention, 0) + 1

    # Sort by count
    phases_sorted = sorted(phases.items(), key=lambda x: x[1], reverse=True)
    interventions_sorted = sorted(interventions.items(), key=lambda x: x[1], reverse=True)

    summary = {
        'total_recruiting_trials': total_count,
        'pages_fetched': page_count,
        'phase_distribution': dict(phases_sorted),
        'intervention_types': dict(interventions_sorted[:10])  # Top 10
    }

    return {
        'total_count': total_count,
        'data': all_trials,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_diabetes_recruiting_trials()
    print(f"\n{'='*60}")
    print(f"Total recruiting diabetes trials: {result['total_count']}")
    print(f"Pages fetched: {result['summary']['pages_fetched']}")
    print(f"\nPhase Distribution:")
    for phase, count in result['summary']['phase_distribution'].items():
        print(f"  {phase}: {count}")
    print(f"\nTop Intervention Types:")
    for intervention, count in list(result['summary']['intervention_types'].items())[:5]:
        print(f"  {intervention}: {count}")
    print(f"{'='*60}\n")
