import sys
import re
import random
from collections import defaultdict
sys.path.insert(0, ".claude")

from mcp.servers.ct_gov_mcp import search as ct_search, get_study
from mcp.servers.fda_mcp import lookup_drug

# Company M&A hierarchy (shared with indication-drug-pipeline-breakdown)
# Updated: 2025-11-25
COMPANY_HIERARCHY = {
    # Major pharma M&A
    'Celgene': 'Bristol Myers Squibb',
    'Celgene Corporation': 'Bristol Myers Squibb',
    'Array BioPharma': 'Pfizer',
    'Array BioPharma Inc.': 'Pfizer',
    'Five Prime Therapeutics': 'Amgen',
    'Mirati Therapeutics': 'Bristol Myers Squibb',
    'ChemoCentryx': 'Amgen',
    'Immunomedics': 'Gilead Sciences',
    'Kite Pharma': 'Gilead Sciences',
    'Tesaro': 'GlaxoSmithKline',
    'Loxo Oncology': 'Eli Lilly',
    'Spark Therapeutics': 'Roche',
    'Pharmacyclics': 'AbbVie',

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

# Academic/non-pharma patterns for filtering
ACADEMIC_PATTERNS = [
    'university', 'hospital', 'medical center', 'institute',
    'foundation', 'cancer center', 'national', 'veterans',
    'mayo clinic', 'md anderson', 'memorial sloan',
    'government', 'NIH', 'NCI', 'college', 'academic',
    'health sciences', 'health system', 'healthcare system'
]


def attribute_company(sponsor_name: str) -> str:
    """
    Map sponsor to parent company (handles M&A and name variations).

    Args:
        sponsor_name: Sponsor name from trial

    Returns:
        Parent company name (M&A attributed)
    """
    # Direct match in hierarchy
    if sponsor_name in COMPANY_HIERARCHY:
        return COMPANY_HIERARCHY[sponsor_name]

    # Check for partial matches
    for acquired, parent in COMPANY_HIERARCHY.items():
        if acquired.lower() in sponsor_name.lower():
            return parent

    return sponsor_name


def normalize_phase(phase_str: str) -> str:
    """Normalize phase string to standard format."""
    if 'Phase4' in phase_str or 'Phase 4' in phase_str:
        return 'Phase 4'
    elif 'Phase3' in phase_str or 'Phase 3' in phase_str:
        return 'Phase 3'
    elif 'Phase2' in phase_str or 'Phase 2' in phase_str:
        return 'Phase 2'
    elif 'Phase1' in phase_str or 'Phase 1' in phase_str:
        return 'Phase 1'
    else:
        return 'Not Applicable'


def extract_drugs_from_trial(trial_markdown: str) -> set:
    """Extract drug names from trial markdown."""
    drugs = set()
    drug_matches = re.findall(r'###\s+Drug:\s*(.+?)(?:\n|$)', trial_markdown)

    for drug in drug_matches:
        drug = drug.strip()
        # Filter placebo and generic terms
        if 'placebo' in drug.lower():
            continue
        if drug.lower() in ['drug', 'other', 'unknown', 'not applicable']:
            continue
        drugs.add(drug)

    return drugs


def filter_pharma_only(companies: dict) -> dict:
    """Remove academic and non-pharma sponsors."""
    filtered = {}

    for company, data in companies.items():
        # Check if academic
        is_academic = any(
            pattern.lower() in company.lower()
            for pattern in ACADEMIC_PATTERNS
        )

        if not is_academic:
            filtered[company] = data

    return filtered


def query_trials_by_moa(moa: str, disease: str = None) -> list:
    """
    Query CT.gov for trials matching mechanism of action.

    Args:
        moa: Mechanism of action (e.g., "KRAS inhibitor")
        disease: Optional disease filter

    Returns:
        List of NCT IDs
    """
    print(f"\n📊 Step 1: Querying ClinicalTrials.gov...")

    # Build query
    query_parts = [moa]
    if disease:
        query_parts.append(disease)

    term = " ".join(query_parts)

    # Search CT.gov
    result = ct_search(
        term=term,
        studyType="interventional",
        interventionType="drug",
        status="recruiting OR active_not_recruiting",
        pageSize=1000
    )

    # Extract NCT IDs
    nct_ids = re.findall(r'NCT\d{8}', result)

    # Extract total count
    total_match = re.search(r'\*\*Results:\*\*\s+\d+\s+of\s+([\d,]+)\s+studies', result)
    total_trials = int(total_match.group(1).replace(',', '')) if total_match else len(nct_ids)

    print(f"   Found {total_trials:,} trials matching '{term}'")

    return nct_ids, total_trials  # Return both for sampling decision


def extract_company_data(nct_ids: list, phase_filter: str) -> dict:
    """
    Extract sponsor and drug info from trials.

    Args:
        nct_ids: List of NCT IDs to analyze
        phase_filter: Minimum phase to include

    Returns:
        Dict of company data
    """
    print(f"\n🏢 Step 2: Extracting company information...")

    # Track by company
    company_data = defaultdict(lambda: {
        'trials': 0,
        'phases': set(),
        'drugs': set(),
        'approved': 0,
        'nct_ids': []
    })

    phase_order = ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4']
    phase_filter_idx = phase_order.index(phase_filter) if phase_filter in phase_order else 0

    processed = 0
    for nct_id in nct_ids:
        try:
            processed += 1
            if processed % 20 == 0:
                print(f"   Progress: {processed}/{len(nct_ids)} trials processed...")

            trial_data = get_study(nctId=nct_id)

            # Extract sponsor
            sponsor_match = re.search(r'\*\*Lead Sponsor:\*\*\s+(.+?)(?:\n|$)', trial_data)
            if not sponsor_match:
                continue

            sponsor = sponsor_match.group(1).strip()
            sponsor = re.sub(r'\s+\(.*?\)', '', sponsor)  # Remove parentheticals
            sponsor = attribute_company(sponsor)

            # Extract phase
            phase_match = re.search(r'\*\*Phase:\*\*\s+(.+?)(?:\n|$)', trial_data)
            phase = phase_match.group(1).strip() if phase_match else 'Phase 1'
            phase = normalize_phase(phase)

            # Apply phase filter
            if phase in phase_order:
                phase_idx = phase_order.index(phase)
                if phase_idx < phase_filter_idx:
                    continue  # Skip trials below filter

            # Extract drugs
            drugs = extract_drugs_from_trial(trial_data)

            # Track
            company_data[sponsor]['trials'] += 1
            company_data[sponsor]['phases'].add(phase)
            for drug in drugs:
                company_data[sponsor]['drugs'].add(drug)
            company_data[sponsor]['nct_ids'].append(nct_id)

        except Exception as e:
            continue

    print(f"   Found {len(company_data)} unique companies/sponsors")

    # Format output
    return format_company_output(company_data, phase_order)


def format_company_output(company_data: dict, phase_order: list) -> dict:
    """Format company data into output structure."""
    formatted = {}

    for company, data in company_data.items():
        # Determine lead phase (most advanced)
        phases = [p for p in phase_order if p in data['phases']]
        lead_phase = phases[-1] if phases else 'Phase 1'

        formatted[company] = {
            'trials': data['trials'],
            'phases': sorted(list(data['phases'])),
            'drugs': sorted(list(data['drugs'])),
            'approved': 0,  # Will be updated in FDA check
            'lead_phase': lead_phase
        }

    # Sort by lead phase (most advanced first), then by trial count
    def sort_key(item):
        company, data = item
        phase_idx = phase_order.index(data['lead_phase']) if data['lead_phase'] in phase_order else -1
        return (-phase_idx, -data['trials'])

    return dict(sorted(formatted.items(), key=sort_key))


def check_fda_approvals(companies: dict, moa: str) -> dict:
    """Check which companies have FDA approved drugs."""
    print(f"\n💊 Step 3: Checking FDA approvals...")

    # Get all unique drugs
    all_drugs = set()
    for company_data in companies.values():
        all_drugs.update(company_data['drugs'])

    # Check FDA for all drugs (full analysis)
    approved_drugs = set()
    checked = 0
    for drug in list(all_drugs):  # Check all drugs
        try:
            checked += 1
            if checked % 10 == 0:
                print(f"   FDA check progress: {checked}/{len(all_drugs)}...")

            result = lookup_drug(
                search_term=drug,
                search_type='general',
                count='openfda.brand_name.exact',
                limit=1
            )

            # Check if approved
            data = result.get('data', {})
            if data.get('results') and len(data.get('results', [])) > 0:
                approved_drugs.add(drug)
        except:
            pass

    print(f"   Found {len(approved_drugs)} approved drugs")

    # Update company approved counts
    for company, data in companies.items():
        approved_count = sum(
            1 for drug in data['drugs']
            if drug in approved_drugs
        )
        data['approved'] = approved_count

    return companies


def generate_competitive_summary(companies: dict, moa: str) -> dict:
    """Generate strategic summary of competitive landscape."""

    # Identify leaders (approved drugs)
    leaders = [
        company for company, data in companies.items()
        if data['approved'] > 0
    ]

    # Identify late-stage (Phase 3+)
    late_stage = [
        company for company, data in companies.items()
        if 'Phase 3' in data['phases'] or 'Phase 4' in data['phases']
    ]

    # Identify early-stage only
    early_stage = [
        company for company, data in companies.items()
        if data['lead_phase'] in ['Phase 1', 'Phase 2']
        and company not in late_stage
    ]

    # Generate assessment
    if len(leaders) >= 2:
        assessment = f"Established market with {len(leaders)} approved drugs and active late-stage competition"
    elif len(leaders) == 1:
        assessment = f"Emerging market with 1 approved drug. {len(late_stage) - 1} late-stage competitors"
    elif len(late_stage) >= 3:
        assessment = f"Pre-commercial space with {len(late_stage)} late-stage programs (no approvals yet)"
    else:
        assessment = f"Early-stage space. {len(companies)} companies exploring {moa}"

    return {
        'leaders': leaders,
        'late_stage': late_stage,
        'early_stage': early_stage,
        'assessment': assessment
    }


def get_companies_by_moa(
    moa: str,
    disease: str = None,
    phase_filter: str = "Phase 1",
    include_academic: bool = False,
    sample_size: int = None
) -> dict:
    """
    Get companies working on a specific mechanism of action.

    Args:
        moa: Mechanism of action (e.g., "KRAS inhibitor", "PD-1 antibody")
        disease: Optional disease filter (e.g., "NSCLC", "melanoma")
        phase_filter: Minimum phase ("Phase 1", "Phase 2", "Phase 3")
        include_academic: Include academic/non-pharma sponsors (default: False)
        sample_size: Number of trials to analyze (default: None = analyze all)

    Returns:
        dict: Company breakdown with trials, phases, drugs, competitive summary
    """
    print(f"\n🔍 Finding companies working on: {moa}")
    if disease:
        print(f"   Filtered by disease: {disease}")
    print("=" * 80)

    # Step 1: Query CT.gov for trials matching MoA
    all_nct_ids, total_trials = query_trials_by_moa(moa, disease)

    # Step 1.5: Apply sampling if specified
    if sample_size is None:
        # Default: analyze all trials
        sample_nct_ids = all_nct_ids
        print(f"   Analyzing all {len(sample_nct_ids):,} trials (full coverage)")
    else:
        # User specified sample size
        if sample_size >= len(all_nct_ids):
            sample_nct_ids = all_nct_ids
            print(f"   Analyzing all {len(sample_nct_ids):,} trials (sample_size >= total)")
        else:
            sample_nct_ids = random.sample(all_nct_ids, sample_size)
            coverage_pct = int(100 * sample_size / len(all_nct_ids))
            print(f"   Analyzing {len(sample_nct_ids):,} trials ({coverage_pct}% sample)")

    # Step 2: Extract sponsor info
    companies = extract_company_data(sample_nct_ids, phase_filter)

    # Step 3: Filter academic (optional)
    if not include_academic:
        companies = filter_pharma_only(companies)
        print(f"   Filtered to {len(companies)} pharma/biotech companies")

    # Step 4: Check FDA approvals
    companies = check_fda_approvals(companies, moa)

    # Step 5: Generate competitive summary
    summary = generate_competitive_summary(companies, moa)

    return {
        'moa': moa,
        'disease': disease,
        'total_trials': total_trials,
        'sample_size': len(sample_nct_ids),
        'analyzed_trials': sum(c['trials'] for c in companies.values()),
        'total_companies': len(companies),
        'companies': companies,
        'competitive_summary': summary
    }


# Make skill executable
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_companies_by_moa.py 'mechanism' ['disease']")
        print("\nExamples:")
        print("  python get_companies_by_moa.py 'KRAS inhibitor'")
        print("  python get_companies_by_moa.py 'PD-1 antibody' 'melanoma'")
        print("  python get_companies_by_moa.py 'GLP-1 agonist' 'obesity'")
        sys.exit(1)

    moa = sys.argv[1]
    disease = sys.argv[2] if len(sys.argv) > 2 else None

    result = get_companies_by_moa(moa, disease)

    # Display results
    print("\n" + "=" * 80)
    print("COMPANY LANDSCAPE BY MECHANISM")
    print("=" * 80)

    print(f"\n📋 Mechanism: {result['moa']}")
    if result['disease']:
        print(f"   Disease: {result['disease']}")

    print(f"\n📊 Overview:")
    print(f"   Total Companies: {result['total_companies']}")
    print(f"   Total Trials: {result['total_trials']}")

    print("\n🏢 Companies (sorted by development stage):")
    print("-" * 80)

    for i, (company, data) in enumerate(result['companies'].items(), 1):
        phases_str = ", ".join(data['phases'])
        drug_count = len(data['drugs'])
        approved_marker = f" ✓ {data['approved']} approved" if data['approved'] > 0 else ""

        print(f"{i:2}. {company:40} {data['trials']} trials | {drug_count} drugs")
        print(f"    Phases: {phases_str} (Lead: {data['lead_phase']}){approved_marker}")

        # Show sample drugs
        sample_drugs = list(data['drugs'])[:3]
        if sample_drugs:
            drugs_str = ", ".join(sample_drugs)
            if len(data['drugs']) > 3:
                drugs_str += f" (+{len(data['drugs']) - 3} more)"
            print(f"    Drugs: {drugs_str}")

        print()

    # Competitive summary
    summary = result['competitive_summary']

    print("=" * 80)
    print("COMPETITIVE ASSESSMENT")
    print("=" * 80)

    print(f"\n{summary['assessment']}")

    if summary['leaders']:
        print(f"\n✓ Market Leaders ({len(summary['leaders'])}):")
        for company in summary['leaders']:
            print(f"  - {company}")

    if summary['late_stage']:
        print(f"\n⚡ Late-Stage Competitors ({len(summary['late_stage'])}):")
        for company in summary['late_stage']:
            print(f"  - {company}")

    if summary['early_stage']:
        print(f"\n🔬 Early-Stage Explorers ({len(summary['early_stage'])}):")
        for company in summary['early_stage'][:5]:  # Show top 5
            print(f"  - {company}")
        if len(summary['early_stage']) > 5:
            print(f"  ... and {len(summary['early_stage']) - 5} more")

    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
