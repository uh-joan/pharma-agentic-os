import sys
import re
import random
from collections import Counter
sys.path.insert(0, ".claude")

from mcp.servers.ct_gov_mcp import search

def get_indication_pipeline_attrition(indication: str, sample_size: int = None) -> dict:
    """Track terminated and withdrawn clinical trials for therapeutic area.

    Args:
        indication: Therapeutic area, drug class, or mechanism (e.g., "KRAS inhibitor", "obesity")
        sample_size: Number of trials to analyze in detail (default: None = analyze all)

    Returns:
        dict: Contains attrition metrics, phase breakdown, sponsor patterns, and interventions
    """
    all_trials = []

    print(f"Searching for terminated/withdrawn trials for: {indication}")

    # Query for TERMINATED and WITHDRAWN trials separately, then combine
    for status_filter in ["terminated", "withdrawn"]:
        page_token = None
        print(f"  Fetching {status_filter} trials...")

        while True:
            if page_token:
                result = search(
                    term=indication,
                    status=status_filter,
                    pageSize=1000,
                    pageToken=page_token
                )
            else:
                result = search(
                    term=indication,
                    status=status_filter,
                    pageSize=1000
                )

            # Parse markdown response
            trials_text = result

            # Extract individual trials using NCT ID headers
            trial_blocks = re.split(r'###\s+\d+\.\s+(NCT\d{8})', trials_text)

            # Process trial blocks (skip first empty element)
            for i in range(1, len(trial_blocks), 2):
                if i + 1 < len(trial_blocks):
                    nct_id = trial_blocks[i]
                    trial_content = trial_blocks[i + 1]
                    all_trials.append({
                        'nct_id': nct_id,
                        'content': trial_content,
                        'status': status_filter
                    })

            # Check for next page
            next_token_match = re.search(r'pageToken:\s*"([^"]+)"', trials_text)
            if next_token_match and next_token_match.group(1) != page_token:
                page_token = next_token_match.group(1)
            else:
                break

        print(f"    Found {len([t for t in all_trials if t['status'] == status_filter])} {status_filter} trials")

    print(f"Total trials retrieved: {len(all_trials)}")

    # Parse trial details from markdown
    phase_counts = Counter()
    status_counts = Counter()
    titles = []

    # Count status from our tracking
    for trial in all_trials:
        content = trial['content']
        status = trial['status']

        # Count by status we already tracked
        if status == 'terminated':
            status_counts['TERMINATED'] += 1
        elif status == 'withdrawn':
            status_counts['WITHDRAWN'] += 1

        # Extract title for intervention tracking
        title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', content)
        if title_match:
            title = title_match.group(1).strip()
            titles.append(title)

    # Calculate totals
    total_terminated = status_counts.get('TERMINATED', 0)
    total_withdrawn = status_counts.get('WITHDRAWN', 0)
    total_attrition = len(all_trials)

    # Apply sampling if specified
    if sample_size is None:
        # Default: analyze all trials
        sample_trials = all_trials
        print(f"\nFetching detailed information for all {len(sample_trials)} trials (full analysis)...")
    else:
        # User specified sample size
        if sample_size >= len(all_trials):
            sample_trials = all_trials
            print(f"\nFetching detailed information for all {len(sample_trials)} trials (sample_size >= total)...")
        else:
            sample_trials = random.sample(all_trials, sample_size)
            coverage_pct = int(100 * sample_size / len(all_trials))
            print(f"\nFetching detailed information for {len(sample_trials)} trials ({coverage_pct}% sample)...")

    from mcp.servers.ct_gov_mcp import get_study

    sponsor_counts = Counter()
    for i, trial in enumerate(sample_trials):
        try:
            detailed = get_study(nctId=trial['nct_id'])

            # Extract phase from detailed response
            phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', detailed)
            if phase_match:
                phase = phase_match.group(1).strip()
                # Parse comma-separated phases (e.g., "Phase1, Phase2")
                # Count each phase mentioned
                if 'Phase1' in phase or 'Phase 1' in phase:
                    phase_counts['PHASE1'] += 1
                elif 'Phase2' in phase or 'Phase 2' in phase:
                    phase_counts['PHASE2'] += 1
                elif 'Phase3' in phase or 'Phase 3' in phase:
                    phase_counts['PHASE3'] += 1
                elif 'Phase4' in phase or 'Phase 4' in phase:
                    phase_counts['PHASE4'] += 1
                else:
                    phase_counts['OTHER'] += 1

            # Extract sponsor (format: "Company Name (Industry)")
            sponsor_match = re.search(r'\*\*Lead Sponsor:\*\*\s*(.+?)(?:\s*\(|$)', detailed)
            if sponsor_match:
                sponsor = sponsor_match.group(1).strip()
                sponsor_counts[sponsor] += 1

        except Exception as e:
            # Skip trials that fail to fetch
            continue

    print(f"  Analyzed {len([t for t in phase_counts.elements()])} trials for phase distribution")
    print(f"  Identified {len(sponsor_counts)} unique sponsors")

    # Top 10 sponsors
    top_sponsors = [
        {'sponsor': sponsor, 'count': count}
        for sponsor, count in sponsor_counts.most_common(10)
    ]

    # Generate summary
    summary = f"""
Pipeline Attrition Analysis for {indication}
{'=' * 60}

Total Attrition: {total_attrition} trials
  - Terminated: {total_terminated}
  - Withdrawn: {total_withdrawn}

Phase Breakdown:
  - Phase 1: {phase_counts.get('PHASE1', 0)}
  - Phase 2: {phase_counts.get('PHASE2', 0)}
  - Phase 3: {phase_counts.get('PHASE3', 0)}
  - Phase 4: {phase_counts.get('PHASE4', 0)}
  - Other/Not Applicable: {phase_counts.get('OTHER', 0)}

Top 5 Sponsors with Failed Trials:
"""

    for i, sponsor_data in enumerate(top_sponsors[:5], 1):
        summary += f"  {i}. {sponsor_data['sponsor']}: {sponsor_data['count']} trials\n"

    return {
        'indication': indication,
        'total_terminated': total_terminated,
        'total_withdrawn': total_withdrawn,
        'total_attrition': total_attrition,
        'sample_size': len(sample_trials),
        'analyzed_trials': len(sample_trials),  # Trials analyzed in detail
        'phase_breakdown': {
            'PHASE1': phase_counts.get('PHASE1', 0),
            'PHASE2': phase_counts.get('PHASE2', 0),
            'PHASE3': phase_counts.get('PHASE3', 0),
            'PHASE4': phase_counts.get('PHASE4', 0),
            'OTHER': phase_counts.get('OTHER', 0)
        },
        'top_sponsors': top_sponsors,
        'trial_titles': titles[:20],  # Sample of trial titles
        'summary': summary.strip()
    }

if __name__ == "__main__":
    import sys

    # Accept indication as command line argument or use default
    indication = sys.argv[1] if len(sys.argv) > 1 else "KRAS inhibitor"

    result = get_indication_pipeline_attrition(indication)
    print(result['summary'])
    print(f"\nTotal unique sponsors tracked: {len(result['top_sponsors'])}")
    print(f"Trial titles captured: {len(result['trial_titles'])}")
