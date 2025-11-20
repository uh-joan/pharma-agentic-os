import sys
sys.path.insert(0, ".claude")

from mcp.servers.ct_gov_mcp import search as ct_search
from mcp.servers.fda_mcp import search as fda_search
from mcp.servers.pubmed_mcp import search as pubmed_search
import re
from collections import Counter

def get_kras_comprehensive_analysis():
    """Comprehensive KRAS inhibitor analysis integrating trials, FDA approvals, and publications.

    Integrates data from three sources:
    1. ClinicalTrials.gov - All KRAS inhibitor trials
    2. FDA - All approved KRAS inhibitor drugs
    3. PubMed - Recent KRAS inhibitor publications (2024)

    Returns:
        dict: Contains:
            - total_trials: int
            - trials_by_phase: dict
            - total_approved_drugs: int
            - approved_drugs: list
            - total_publications: int
            - publications_summary: str
            - strategic_insights: dict
            - summary: str (formatted overview)
    """

    # ===== 1. Clinical Trials (CT.gov - returns markdown) =====
    print("Collecting KRAS inhibitor clinical trials...")
    trials_data = []
    page_token = None

    while True:
        if page_token:
            result = ct_search(term="KRAS inhibitor", pageSize=1000, pageToken=page_token)
        else:
            result = ct_search(term="KRAS inhibitor", pageSize=1000)

        if not result:
            break

        # Parse markdown response
        trials = re.split(r'###\s+\d+\.\s+NCT\d{8}', result)
        trials_data.extend([t for t in trials if t.strip()])

        # Check for next page token
        token_match = re.search(r'pageToken:\s*"([^"]+)"', result)
        if token_match:
            page_token = token_match.group(1)
        else:
            break

    # Parse phases from trials
    phases = []
    statuses = []
    for trial in trials_data:
        phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', trial)
        if phase_match:
            phases.append(phase_match.group(1).strip())

        status_match = re.search(r'\*\*Status:\*\*\s*(.+?)(?:\n|$)', trial)
        if status_match:
            statuses.append(status_match.group(1).strip())

    phase_counts = Counter(phases)
    status_counts = Counter(statuses)

    # ===== 2. FDA Approved Drugs (FDA - returns JSON) =====
    print("Collecting FDA approved KRAS inhibitor drugs...")
    fda_result = fda_search(term="KRAS inhibitor", limit=100)

    approved_drugs = []
    if isinstance(fda_result, dict) and fda_result.get('results'):
        for drug in fda_result['results']:
            drug_name = drug.get('openfda', {}).get('brand_name', ['Unknown'])[0]
            generic_name = drug.get('openfda', {}).get('generic_name', ['Unknown'])[0]
            approved_drugs.append({
                'brand_name': drug_name,
                'generic_name': generic_name
            })

    # Deduplicate drugs
    unique_drugs = {d['brand_name']: d for d in approved_drugs}.values()

    # ===== 3. Recent Publications (PubMed - returns JSON) =====
    print("Collecting recent KRAS inhibitor publications (2024)...")
    pubmed_result = pubmed_search(
        query="KRAS inhibitor",
        max_results=100,
        date_from="2024/01/01",
        date_to="2024/12/31"
    )

    publications = []
    if isinstance(pubmed_result, dict) and pubmed_result.get('articles'):
        publications = pubmed_result['articles']

    # ===== Cross-Reference Analysis =====
    # Extract drug names from trials
    trial_drugs = []
    for trial in trials_data:
        intervention_match = re.search(r'\*\*Intervention:\*\*\s*(.+?)(?:\n|$)', trial)
        if intervention_match:
            trial_drugs.append(intervention_match.group(1).strip())

    # Find approved drugs mentioned in trials
    approved_drug_names = {d['brand_name'].lower() for d in unique_drugs}
    trial_drug_names = {d.lower() for d in trial_drugs}

    approved_in_trials = approved_drug_names.intersection(trial_drug_names)

    # ===== Strategic Insights =====
    total_trials = len(trials_data)
    recruiting_count = sum(1 for s in statuses if 'recruiting' in s.lower())

    strategic_insights = {
        'pipeline_maturity': {
            'early_phase': phase_counts.get('Phase 1', 0) + phase_counts.get('Early Phase 1', 0),
            'mid_phase': phase_counts.get('Phase 2', 0) + phase_counts.get('Phase 1/Phase 2', 0),
            'late_phase': phase_counts.get('Phase 3', 0) + phase_counts.get('Phase 2/Phase 3', 0),
            'post_approval': phase_counts.get('Phase 4', 0)
        },
        'market_activity': {
            'active_trials': recruiting_count,
            'approved_drugs': len(unique_drugs),
            'research_momentum': len(publications)
        },
        'drug_validation': {
            'approved_drugs_in_trials': len(approved_in_trials),
            'trial_only_drugs': len(trial_drug_names - approved_drug_names)
        }
    }

    # ===== Generate Summary =====
    summary = f"""
=== KRAS Inhibitor Comprehensive Analysis ===

CLINICAL TRIALS (ClinicalTrials.gov):
  Total trials: {total_trials}
  By Phase:
    - Phase 1/Early: {strategic_insights['pipeline_maturity']['early_phase']}
    - Phase 2/Mid: {strategic_insights['pipeline_maturity']['mid_phase']}
    - Phase 3/Late: {strategic_insights['pipeline_maturity']['late_phase']}
    - Phase 4/Post-approval: {strategic_insights['pipeline_maturity']['post_approval']}

  By Status:
    - Recruiting: {recruiting_count}
    - Other: {total_trials - recruiting_count}

FDA APPROVED DRUGS:
  Total approved: {len(unique_drugs)}
  Drugs:"""

    for drug in unique_drugs:
        summary += f"\n    - {drug['brand_name']} ({drug['generic_name']})"

    summary += f"""

RECENT PUBLICATIONS (2024):
  Total papers: {len(publications)}
  Research focus: KRAS inhibitor development and clinical application

STRATEGIC INSIGHTS:
  Pipeline Maturity:
    - Strong early-phase pipeline ({strategic_insights['pipeline_maturity']['early_phase']} trials)
    - Robust late-phase development ({strategic_insights['pipeline_maturity']['late_phase']} trials)
    - Active recruitment: {recruiting_count} trials

  Market Position:
    - {len(unique_drugs)} FDA approved drugs in market
    - {len(approved_in_trials)} approved drugs still in active trials
    - High research momentum ({len(publications)} papers in 2024)

  Cross-Reference:
    - Approved drugs validated in trials: {len(approved_in_trials)}
    - Novel drugs in pipeline: {len(trial_drug_names - approved_drug_names)}

=== End Analysis ===
"""

    return {
        'total_trials': total_trials,
        'trials_by_phase': dict(phase_counts),
        'trials_by_status': dict(status_counts),
        'total_approved_drugs': len(unique_drugs),
        'approved_drugs': list(unique_drugs),
        'total_publications': len(publications),
        'publications': publications[:10] if publications else [],  # Top 10 for brevity
        'strategic_insights': strategic_insights,
        'cross_references': {
            'approved_in_trials': list(approved_in_trials),
            'trial_only_drugs': list(trial_drug_names - approved_drug_names)
        },
        'summary': summary
    }

if __name__ == "__main__":
    result = get_kras_comprehensive_analysis()
    print(result['summary'])
