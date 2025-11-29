import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import lookup_drug
from mcp.servers.ct_gov_mcp import search
import re

def get_obesity_drugs_early_development():
    """Get FDA-approved obesity drugs with early-stage development pipeline.

    Uses known obesity drug names (FDA best practice) to avoid false positives
    from broad term searches. For each approved drug, checks CT.gov for Phase 1/2 trials.

    Returns:
        dict: Contains approved_drugs list and summary statistics
    """

    # Known FDA-approved obesity drugs (generic names)
    # Source: FDA guidance - query specific drug names, not indication term
    known_obesity_drugs = [
        "semaglutide",      # Wegovy
        "liraglutide",      # Saxenda
        "orlistat",         # Xenical, Alli
        "phentermine",      # Adipex-P, Lomaira
        "setmelanotide",    # Imcivree
        "tirzepatide"       # Zepbound
    ]

    approved_drugs = []

    print("Querying FDA for known obesity drugs...")

    # Query each drug specifically (parallel queries as documented)
    for drug_name in known_obesity_drugs:
        try:
            result = lookup_drug(
                search_term=drug_name,
                search_type="general",
                count="openfda.brand_name.exact",
                limit=10
            )

            if result and result.get('data', {}).get('results'):
                # Get unique brand names for this drug
                brands = {}
                for item in result['data']['results']:
                    brand = item.get('term', 'Unknown')
                    if brand != 'Unknown':
                        brands[brand] = item.get('count', 0)

                if brands:
                    # Take the top brand name
                    top_brand = sorted(brands.items(), key=lambda x: x[1], reverse=True)[0][0]
                    approved_drugs.append({
                        'brand_name': top_brand,
                        'generic_name': drug_name,
                        'search_term': drug_name
                    })
                    print(f"  ✓ Found: {drug_name} ({top_brand})")

        except Exception as e:
            print(f"  ✗ Error querying {drug_name}: {e}")
            continue

    print(f"\nFound {len(approved_drugs)} approved obesity drugs")
    print("\nQuerying CT.gov for early-stage trials (Phase 1/2)...")

    # For each approved drug, check for Phase 1/2 trials
    drugs_with_pipeline = []

    for drug in approved_drugs:
        drug_name = drug['generic_name']

        print(f"\nChecking {drug_name}...")

        # Query CT.gov for Phase 1 OR Phase 2 trials
        try:
            ct_result = search(
                intervention=drug_name,
                phase="PHASE1 OR PHASE2",
                pageSize=5000  # High limit to get all results without pagination
            )

            # Parse markdown response to count trials
            def count_trials_by_phase(markdown_response):
                if not markdown_response:
                    return 0, 0

                # Split by trial blocks
                trial_blocks = re.split(r'###\s+\d+\.\s+NCT\d{8}', markdown_response)

                phase1_count = 0
                phase2_count = 0

                for block in trial_blocks[1:]:  # Skip first empty block
                    phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', block)
                    if phase_match:
                        phase_text = phase_match.group(1).upper()
                        if 'PHASE1' in phase_text or 'PHASE 1' in phase_text:
                            phase1_count += 1
                        elif 'PHASE2' in phase_text or 'PHASE 2' in phase_text:
                            phase2_count += 1

                return phase1_count, phase2_count

            phase1_count, phase2_count = count_trials_by_phase(ct_result)
            total_early_trials = phase1_count + phase2_count

            if total_early_trials > 0:
                drugs_with_pipeline.append({
                    'brand_name': drug['brand_name'],
                    'generic_name': drug_name,
                    'phase1_trials': phase1_count,
                    'phase2_trials': phase2_count,
                    'total_early_trials': total_early_trials
                })

                print(f"  ✓ {total_early_trials} early trials (Phase 1: {phase1_count}, Phase 2: {phase2_count})")
            else:
                print(f"  ✗ No early-stage trials found")

        except Exception as e:
            print(f"  ✗ Error querying CT.gov for {drug_name}: {e}")
            continue

    # Generate summary
    total_phase1 = sum(d['phase1_trials'] for d in drugs_with_pipeline)
    total_phase2 = sum(d['phase2_trials'] for d in drugs_with_pipeline)

    summary_text = f"""
{'='*60}
FDA-APPROVED OBESITY DRUGS WITH EARLY-STAGE DEVELOPMENT
{'='*60}

Total approved obesity drugs: {len(approved_drugs)}
Drugs with Phase 1/2 pipeline: {len(drugs_with_pipeline)}

Early-Stage Trial Activity:
- Phase 1 trials: {total_phase1}
- Phase 2 trials: {total_phase2}
- Total early trials: {total_phase1 + total_phase2}

Drugs with Active Early Development:
{'-'*60}
"""

    for drug in sorted(drugs_with_pipeline, key=lambda x: x['total_early_trials'], reverse=True):
        summary_text += f"\n{drug['brand_name']} ({drug['generic_name']})"
        summary_text += f"\n  Phase 1: {drug['phase1_trials']} trials"
        summary_text += f"\n  Phase 2: {drug['phase2_trials']} trials"
        summary_text += f"\n  Total: {drug['total_early_trials']} trials\n"

    return {
        'approved_drugs': drugs_with_pipeline,
        'total_approved': len(approved_drugs),
        'total_with_pipeline': len(drugs_with_pipeline),
        'summary': summary_text
    }

if __name__ == "__main__":
    result = get_obesity_drugs_early_development()
    print(result['summary'])
    print(f"\n✓ Analysis complete: {result['total_with_pipeline']} of {result['total_approved']} approved obesity drugs have active early-stage development programs")
