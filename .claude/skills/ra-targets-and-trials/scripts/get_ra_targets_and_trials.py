import sys
import re
sys.path.insert(0, ".claude")

from mcp.servers.opentargets_mcp import search_targets
from mcp.servers.ct_gov_mcp import search

def get_ra_targets_and_trials():
    """Get drug targets for rheumatoid arthritis and their clinical trials.

    This multi-server integration combines:
    1. Open Targets: Target validation data for rheumatoid arthritis
    2. ClinicalTrials.gov: Clinical trials for identified targets

    Returns:
        dict: Contains targets summary, trials summary, and integrated data
    """
    print("\n=== Rheumatoid Arthritis Target & Trial Analysis ===\n")

    # Step 1: Get targets from Open Targets
    print("Step 1: Querying Open Targets for rheumatoid arthritis targets...")
    targets_result = search_targets(
        disease="rheumatoid arthritis",
        min_score=0.5,
        limit=20
    )

    # Parse targets from JSON response
    targets = []
    if isinstance(targets_result, dict) and 'data' in targets_result:
        target_data = targets_result['data']
        if isinstance(target_data, dict) and 'disease' in target_data:
            disease_data = target_data['disease']
            if isinstance(disease_data, dict) and 'associatedTargets' in disease_data:
                associated = disease_data['associatedTargets']
                if isinstance(associated, dict) and 'rows' in associated:
                    for row in associated['rows']:
                        if isinstance(row, dict):
                            target_info = {
                                'gene_symbol': row.get('target', {}).get('approvedSymbol', 'Unknown'),
                                'gene_name': row.get('target', {}).get('approvedName', 'Unknown'),
                                'score': row.get('score', 0.0),
                                'id': row.get('target', {}).get('id', 'Unknown')
                            }
                            targets.append(target_info)

    print(f"✓ Found {len(targets)} targets with validation score ≥ 0.5\n")

    # Display top targets
    print("Top 10 Validated Targets:")
    print("-" * 80)
    for i, target in enumerate(targets[:10], 1):
        print(f"{i:2d}. {target['gene_symbol']:10s} | Score: {target['score']:.3f} | {target['gene_name']}")
    print()

    # Step 2: Get clinical trials for rheumatoid arthritis
    print("Step 2: Querying ClinicalTrials.gov for rheumatoid arthritis trials...")

    all_trials = []
    page_token = None
    page_count = 0

    while True:
        page_count += 1
        print(f"  Fetching page {page_count}...")

        result = search(
            query="rheumatoid arthritis",
            pageSize=1000,
            pageToken=page_token
        )

        if not result or not isinstance(result, str):
            break

        # Extract trials from markdown
        trial_sections = re.split(r'###\s+\d+\.\s+NCT\d{8}', result)

        for section in trial_sections[1:]:  # Skip first empty section
            trial = {}

            # Extract NCT ID
            nct_match = re.search(r'NCT\d{8}', result[result.find(section)-20:result.find(section)])
            if nct_match:
                trial['nct_id'] = nct_match.group()

            # Extract fields
            title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?=\n\*\*|$)', section, re.DOTALL)
            if title_match:
                trial['title'] = title_match.group(1).strip()

            status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?=\n|$)', section)
            if status_match:
                trial['status'] = status_match.group(1).strip()

            phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?=\n|$)', section)
            if phase_match:
                trial['phase'] = phase_match.group(1).strip()

            conditions_match = re.search(r'\*\*Conditions:\*\*\s*(.+?)(?=\n\*\*|$)', section, re.DOTALL)
            if conditions_match:
                trial['conditions'] = conditions_match.group(1).strip()

            if 'nct_id' in trial:
                all_trials.append(trial)

        # Check for next page
        next_token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        if next_token_match:
            page_token = next_token_match.group(1)
        else:
            break

    print(f"✓ Total trials retrieved: {len(all_trials)}\n")

    # Step 3: Aggregate trial statistics
    phase_counts = {}
    status_counts = {}

    for trial in all_trials:
        phase = trial.get('phase', 'Not Specified')
        status = trial.get('status', 'Unknown')

        phase_counts[phase] = phase_counts.get(phase, 0) + 1
        status_counts[status] = status_counts.get(status, 0) + 1

    # Step 4: Integration analysis
    print("Step 3: Analyzing target-trial integration...")
    target_trial_matches = []

    for target in targets[:10]:
        gene_symbol = target['gene_symbol']
        matching_trials = [
            trial for trial in all_trials
            if gene_symbol.lower() in trial.get('title', '').lower() or
               gene_symbol.lower() in trial.get('conditions', '').lower()
        ]

        if matching_trials:
            target_trial_matches.append({
                'target': gene_symbol,
                'score': target['score'],
                'trial_count': len(matching_trials),
                'trials': matching_trials[:3]
            })

    print(f"✓ Found {len(target_trial_matches)} targets with matching clinical trials\n")

    # Generate summary
    summary = {
        'targets': {
            'total_count': len(targets),
            'top_targets': targets[:10],
            'score_range': f"{min(t['score'] for t in targets):.3f} - {max(t['score'] for t in targets):.3f}"
        },
        'trials': {
            'total_count': len(all_trials),
            'by_phase': dict(sorted(phase_counts.items(), key=lambda x: x[1], reverse=True)),
            'by_status': dict(sorted(status_counts.items(), key=lambda x: x[1], reverse=True))
        },
        'integration': {
            'targets_with_trials': len(target_trial_matches),
            'matches': target_trial_matches
        }
    }

    return summary

if __name__ == "__main__":
    result = get_ra_targets_and_trials()
    print("\nExecution complete.")
