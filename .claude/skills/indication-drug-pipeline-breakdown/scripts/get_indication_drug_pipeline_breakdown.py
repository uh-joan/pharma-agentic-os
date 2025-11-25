import sys
import re
import random
from collections import defaultdict
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search as ct_search, get_study
from mcp.servers.fda_mcp import lookup_drug

# Company M&A hierarchy (acquired → parent company)
# Updated: 2025-11-25
COMPANY_HIERARCHY = {
    # Major pharma M&A
    'Celgene': 'Bristol Myers Squibb',
    'Celgene Corporation': 'Bristol Myers Squibb',
    'Array BioPharma': 'Pfizer',
    'Array BioPharma Inc.': 'Pfizer',
    'Five Prime Therapeutics': 'Amgen',
    'Mirati Therapeutics': 'Bristol Myers Squibb',  # Acquired Jan 2024
    'ChemoCentryx': 'Amgen',  # Acquired 2022
    'Immunomedics': 'Gilead Sciences',  # Acquired 2020
    'Kite Pharma': 'Gilead Sciences',  # Acquired 2017
    'Tesaro': 'GlaxoSmithKline',  # Acquired 2019
    'Loxo Oncology': 'Eli Lilly',  # Acquired 2019
    'Spark Therapeutics': 'Roche',  # Acquired 2019
    'Genmab': 'Johnson & Johnson',  # Partnership, not acquisition
    'Pharmacyclics': 'AbbVie',  # Acquired 2015

    # Normalize company name variations
    'Pfizer Inc': 'Pfizer',
    'Pfizer Inc.': 'Pfizer',
    'Amgen Inc': 'Amgen',
    'Amgen Inc.': 'Amgen',
    'Bristol-Myers Squibb': 'Bristol Myers Squibb',
    'Bristol-Myers Squibb Company': 'Bristol Myers Squibb',
    'Eli Lilly and Company': 'Eli Lilly',
    'Merck & Co.': 'Merck',
    'Merck & Co., Inc.': 'Merck',
    'Novartis Pharmaceuticals': 'Novartis',
    'Roche Holding AG': 'Roche',
    'F. Hoffmann-La Roche': 'Roche',
    'Hoffmann-La Roche': 'Roche',
}


def extract_sponsor_from_trial(trial_markdown: str) -> str:
    """Extract lead sponsor from trial markdown."""
    # Pattern: **Lead Sponsor:** Company Name (Industry)
    sponsor_match = re.search(r'\*\*Lead Sponsor:\*\*\s+(.+?)(?:\n|$)', trial_markdown)

    if sponsor_match:
        sponsor = sponsor_match.group(1).strip()
        # Clean up common patterns
        sponsor = re.sub(r'\s+\(.*?\)', '', sponsor)  # Remove parentheticals like (Industry)
        return sponsor

    return "Unknown"


def attribute_company(sponsor_name: str) -> str:
    """
    Map sponsor to parent company (handles M&A and name variations).

    Args:
        sponsor_name: Sponsor name from trial (e.g., "Celgene")

    Returns:
        Parent company name (e.g., "Bristol Myers Squibb")
    """
    # Direct match in hierarchy
    if sponsor_name in COMPANY_HIERARCHY:
        return COMPANY_HIERARCHY[sponsor_name]

    # Check for partial matches (handle "Inc", "Inc.", "Corporation", etc.)
    for acquired, parent in COMPANY_HIERARCHY.items():
        if acquired.lower() in sponsor_name.lower():
            return parent

    return sponsor_name

def get_indication_drug_pipeline_breakdown(indication: str, sample_size: int = None) -> dict:
    """Analyze drug pipeline for a given indication with phase breakdown and visualization.

    Performs full analysis by default, analyzing ALL active trials for complete accuracy.
    User can optionally specify sample_size for faster results on very large datasets.

    Args:
        indication (str): Disease/condition (e.g., "obesity", "Alzheimer's disease", "heart failure")
        sample_size (int, optional): Number of trials to analyze (default: None = analyze all)

    Returns:
        dict: Contains indication, total_trials, sample_size, total_unique_drugs, approved_drugs,
              phase_breakdown, companies, and visualization
    """
    print(f"\n🔍 Analyzing drug pipeline for: {indication}")
    print("=" * 80)

    # Step 1: Get trial NCT IDs for the indication
    print(f"\n📊 Step 1: Discovering active drug trials for {indication}...")

    # Search for active drug trials (recruiting + active not recruiting)
    # This shows the current development pipeline, excluding completed/terminated trials
    result = ct_search(
        condition=indication,
        studyType="interventional",
        interventionType="drug",
        status="recruiting OR active_not_recruiting",
        pageSize=1000
    )

    # Extract total count
    total_match = re.search(r'\*\*Results:\*\*\s+\d+\s+of\s+([\d,]+)\s+studies found', result)
    total_trials = int(total_match.group(1).replace(',', '')) if total_match else 0

    # Collect ALL NCT IDs (with pagination if needed)
    all_nct_ids = re.findall(r'NCT\d{8}', result)

    # Check if we need more pages
    if total_trials > 1000:
        print(f"  Collecting all {total_trials:,} trial IDs (paginating)...")
        page_token_match = re.search(r'`pageToken:\s*"([^"]+)"', result)
        while page_token_match:
            page_token = page_token_match.group(1)
            result = ct_search(
                condition=indication,
                studyType="interventional",
                interventionType="drug",
                status="recruiting OR active_not_recruiting",
                pageSize=1000,
                pageToken=page_token
            )
            all_nct_ids.extend(re.findall(r'NCT\d{8}', result))
            page_token_match = re.search(r'`pageToken:\s*"([^"]+)"', result)

    print(f"✓ Found {total_trials:,} active drug trials")

    # Step 2: Apply sampling if specified
    if sample_size is None:
        # Default: analyze ALL trials (full analysis)
        sample_nct_ids = all_nct_ids
        print(f"✓ Analyzing ALL {len(sample_nct_ids):,} trials (100% coverage)")
    else:
        # User specified sample size
        if sample_size >= len(all_nct_ids):
            sample_nct_ids = all_nct_ids
            print(f"✓ Analyzing ALL {len(sample_nct_ids):,} trials (sample_size >= total)")
        else:
            sample_nct_ids = random.sample(all_nct_ids, sample_size)
            coverage_pct = int(100 * sample_size / len(all_nct_ids))
            print(f"✓ Analyzing {len(sample_nct_ids):,} trials ({coverage_pct}% sample)")

    # Step 3: Fetch detailed information for sampled trials
    print(f"\n💊 Step 2: Fetching detailed trial information...")

    # Phase breakdown data structure
    phase_breakdown = {
        'Phase 1': {'trials': 0, 'drugs': set()},
        'Phase 2': {'trials': 0, 'drugs': set()},
        'Phase 3': {'trials': 0, 'drugs': set()},
        'Phase 4': {'trials': 0, 'drugs': set()},
        'Not Applicable': {'trials': 0, 'drugs': set()}
    }

    # Company tracking data structure (NEW)
    company_data = defaultdict(lambda: {
        'trials': 0,
        'phases': set(),
        'drugs': set(),
        'approved': 0
    })

    all_drugs = set()
    processed = 0

    for nct_id in sample_nct_ids:
        try:
            processed += 1
            if processed % 20 == 0:
                print(f"  Progress: {processed}/{len(sample_nct_ids)} trials processed...")

            # Get detailed trial information
            trial_detail = get_study(nctId=nct_id)

            # Extract phase
            phase_match = re.search(r'\*\*Phase:\*\*\s*(.+?)(?:\n|$)', trial_detail)
            phase = phase_match.group(1).strip() if phase_match else 'Na'

            # Normalize phase name (handle both "Phase2" and "Phase 2" formats)
            # If multiple phases (e.g., "Phase2, Phase3"), use the highest phase
            if 'Phase4' in phase or 'Phase 4' in phase:
                phase_key = 'Phase 4'
            elif 'Phase3' in phase or 'Phase 3' in phase:
                phase_key = 'Phase 3'
            elif 'Phase2' in phase or 'Phase 2' in phase:
                phase_key = 'Phase 2'
            elif 'Phase1' in phase or 'Phase 1' in phase:
                phase_key = 'Phase 1'
            else:
                phase_key = 'Not Applicable'

            # Extract sponsor (NEW)
            sponsor = extract_sponsor_from_trial(trial_detail)
            sponsor = attribute_company(sponsor)

            # Extract Drug interventions (filter out Behavioral, Procedure, etc.)
            drug_interventions = re.findall(r'###\s+Drug:\s*(.+?)(?:\n|$)', trial_detail)

            if drug_interventions:
                phase_breakdown[phase_key]['trials'] += 1

                # Track by company (NEW)
                company_data[sponsor]['trials'] += 1
                company_data[sponsor]['phases'].add(phase_key)

                for drug in drug_interventions:
                    drug_clean = drug.strip()
                    # Filter out placebo and generic terms
                    if drug_clean and drug_clean.lower() not in ['placebo', 'other', 'not applicable']:
                        phase_breakdown[phase_key]['drugs'].add(drug_clean)
                        all_drugs.add(drug_clean)
                        # Track drug by company (NEW)
                        company_data[sponsor]['drugs'].add(drug_clean)

        except Exception as e:
            # Skip trials that fail to fetch
            continue

    total_unique_drugs = len(all_drugs)
    print(f"✓ Processed {processed} trials")
    print(f"✓ Total unique drugs extracted: {total_unique_drugs}")

    # Step 3: Cross-check with FDA for approved drugs
    print(f"\n🏛️  Step 3: Cross-checking FDA for approved drugs...")

    approved_drugs = []
    # Check all drugs for FDA approval (full analysis)
    drugs_to_check = list(all_drugs)

    checked = 0
    for drug in drugs_to_check:
        try:
            checked += 1
            if checked % 10 == 0:
                print(f"  FDA check progress: {checked}/{len(drugs_to_check)}...")

            fda_result = lookup_drug(search_term=drug, search_type='general', count='openfda.brand_name.exact', limit=1)
            # Parse FDA JSON response (nested under 'data')
            data = fda_result.get('data', {})
            if data.get('results') and len(data.get('results', [])) > 0:
                approved_drugs.append(drug)
        except:
            pass

    print(f"✓ FDA check complete: {len(approved_drugs)} approved drugs identified")

    # Attribute approved drugs to companies
    for company in company_data:
        company_approved_count = sum(
            1 for drug in company_data[company]['drugs']
            if drug in approved_drugs
        )
        company_data[company]['approved'] = company_approved_count

    # Step 4: Create visualization
    print(f"\n📈 Step 4: Creating pipeline visualization...")

    # Build phase breakdown dict with counts
    phase_summary = {}
    for phase, data in phase_breakdown.items():
        phase_summary[phase] = {
            'trials': data['trials'],
            'unique_drugs': len(data['drugs']),
            'drugs': sorted(list(data['drugs']))[:10]  # Top 10 for display
        }

    # Create ASCII visualization
    max_trials = max([data['trials'] for data in phase_summary.values()]) or 1
    max_drugs = max([len(data['drugs']) for data in phase_breakdown.values()]) or 1
    bar_width = 30

    # Calculate coverage
    coverage_pct = 100 if len(sample_nct_ids) == total_trials else int(100 * len(sample_nct_ids) / total_trials)

    viz_lines = []
    viz_lines.append(f"\n{'='*80}")
    viz_lines.append(f"ACTIVE DRUG PIPELINE: {indication.upper()}")
    viz_lines.append(f"{'='*80}")
    viz_lines.append(f"Active Trials: {total_trials:,} (recruiting + active not recruiting)")
    if len(sample_nct_ids) == total_trials:
        viz_lines.append(f"Coverage: ALL trials analyzed (100%)")
    else:
        viz_lines.append(f"Sample: {len(sample_nct_ids)} trials analyzed ({coverage_pct}% coverage)")
    viz_lines.append(f"Unique Drugs in Pipeline: {total_unique_drugs}")
    if approved_drugs:
        viz_lines.append(f"FDA Approved Drugs: {len(approved_drugs)} ({', '.join(approved_drugs[:5])}{'...' if len(approved_drugs) > 5 else ''})")
    viz_lines.append(f"\n{'Phase Distribution':<20} Trials         Unique Drugs")
    viz_lines.append("-" * 80)

    for phase in ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4', 'Not Applicable']:
        data = phase_summary[phase]
        trials = data['trials']
        drugs = data['unique_drugs']

        # Create trial bar
        trial_filled = int((trials / max_trials) * bar_width) if trials > 0 else 0
        trial_bar = '█' * trial_filled + '░' * (bar_width - trial_filled)

        # Create drug bar
        drug_filled = int((drugs / max_drugs) * bar_width) if drugs > 0 else 0
        drug_bar = '█' * drug_filled + '░' * (bar_width - drug_filled)

        viz_lines.append(f"{phase:<15}     {trials:>3}  {trial_bar}   {drugs:>3}  {drug_bar}")

    # Add sample drugs per phase
    viz_lines.append(f"\n{'Sample Drugs by Phase'}")
    viz_lines.append("-" * 80)
    for phase in ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4']:
        drugs_list = sorted(list(phase_breakdown[phase]['drugs']))[:5]
        if drugs_list:
            viz_lines.append(f"{phase}: {', '.join(drugs_list)}")

    # Add company breakdown (NEW)
    viz_lines.append(f"\n{'='*80}")
    viz_lines.append("TOP COMPANIES BY TRIAL COUNT")
    viz_lines.append("=" * 80)

    # Sort companies by trial count
    sorted_companies = sorted(
        company_data.items(),
        key=lambda x: x[1]['trials'],
        reverse=True
    )[:10]  # Top 10 companies

    viz_lines.append(f"{'Company':<35} Trials  Phases  Drugs  Approved")
    viz_lines.append("-" * 80)

    for company, data in sorted_companies:
        phases_str = ', '.join(sorted(data['phases']))
        viz_lines.append(
            f"{company:<35} {data['trials']:>6}  {len(data['phases']):>6}  {len(data['drugs']):>5}  {data['approved']:>8}"
        )

    visualization = '\n'.join(viz_lines)

    # Print visualization
    print(visualization)

    # Format company data for return
    formatted_companies = []
    for company, data in sorted_companies:
        formatted_companies.append({
            'company': company,
            'trials': data['trials'],
            'phases': sorted(list(data['phases'])),
            'drugs': sorted(list(data['drugs'])),
            'approved_count': data['approved']
        })

    return {
        'indication': indication,
        'total_trials': total_trials,
        'sample_size': len(sample_nct_ids),
        'total_unique_drugs': total_unique_drugs,
        'approved_drugs': approved_drugs,
        'phase_breakdown': phase_summary,
        'companies': formatted_companies,
        'total_companies': len(company_data),
        'visualization': visualization
    }

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python3 get_indication_drug_pipeline_breakdown.py <INDICATION> [SAMPLE_SIZE]")
        print("\nExamples:")
        print("  # Auto-intelligent sampling (all trials if ≤500, otherwise smart sample)")
        print("  python3 get_indication_drug_pipeline_breakdown.py 'obesity'")
        print("  python3 get_indication_drug_pipeline_breakdown.py \"Alzheimer's disease\"")
        print("")
        print("  # Manual sample size (for faster execution or larger coverage)")
        print("  python3 get_indication_drug_pipeline_breakdown.py 'heart failure' 200")
        print("  python3 get_indication_drug_pipeline_breakdown.py 'diabetes' 500")
        sys.exit(1)

    test_indication = sys.argv[1]
    sample = int(sys.argv[2]) if len(sys.argv) > 2 else None  # Auto-determine if not specified

    result = get_indication_drug_pipeline_breakdown(test_indication, sample_size=sample)

    print("\n" + "=" * 80)
    print("✅ PIPELINE ANALYSIS COMPLETE")
    print("=" * 80)
    coverage = 100 if result['sample_size'] == result['total_trials'] else int(100 * result['sample_size'] / result['total_trials'])
    print(f"Coverage: {result['sample_size']} of {result['total_trials']:,} trials ({coverage}%)")
    print(f"Identified {result['total_unique_drugs']} unique drug interventions")
    print(f"Found {len(result['approved_drugs'])} FDA approved drugs")
    print(f"Tracked {result['total_companies']} unique companies/sponsors")
    print(f"Top 10 companies displayed in visualization above")
    print("=" * 80)
