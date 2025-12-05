import sys
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search as ct_search
from mcp.servers.pubmed_mcp import search_keywords as pubmed_search
import re

def get_pipeline_drug_efficacy():
    """Get Phase 2/3 efficacy data for pipeline GLP-1 drugs.

    Queries ClinicalTrials.gov for trial status and PubMed for published
    efficacy outcomes (weight loss %, HbA1c reduction) for 5 pipeline drugs:
    - Retatrutide (Eli Lilly)
    - CagriSema (Novo Nordisk)
    - Orforglipron (Eli Lilly)
    - Survodutide (Boehringer Ingelheim)
    - AMG 133 (Amgen)

    Returns:
        dict: Contains drug profiles with trial counts, status, and efficacy data
    """

    # Pipeline drugs to analyze
    pipeline_drugs = [
        "retatrutide",
        "CagriSema",
        "orforglipron",
        "survodutide",
        "AMG 133"
    ]

    print("Analyzing pipeline GLP-1 drugs efficacy data...")
    print(f"{'='*70}\n")

    drug_profiles = []

    for drug_name in pipeline_drugs:
        print(f"Processing {drug_name}...")

        # Get Phase 2/3 trials from CT.gov
        trials_data = get_drug_trials(drug_name)

        # Get efficacy data from PubMed
        efficacy_data = get_drug_efficacy(drug_name)

        profile = {
            'drug_name': drug_name,
            'trials': trials_data,
            'efficacy': efficacy_data
        }

        drug_profiles.append(profile)
        print(f"  ✓ {drug_name} complete\n")

    # Generate summary
    summary = format_pipeline_summary(drug_profiles)

    return {
        'total_drugs': len(pipeline_drugs),
        'drug_profiles': drug_profiles,
        'summary': summary
    }

def get_drug_trials(drug_name):
    """Get Phase 2/3 trials for a drug from CT.gov.

    Args:
        drug_name: Drug name to search

    Returns:
        dict: Trial counts and latest status by phase
    """

    trials_by_phase = {}

    for phase in ['PHASE2', 'PHASE3']:
        result = ct_search(
            term=drug_name,
            phase=phase,
            pageSize=100
        )

        # Extract count
        count = extract_count(result)

        # Parse trials for status
        trials = parse_trials_markdown(result)

        # Get latest trial status
        latest_status = None
        if trials:
            # Sort by start date if available, otherwise take first
            latest_trial = trials[0]
            latest_status = latest_trial.get('status', 'UNKNOWN')

        trials_by_phase[phase] = {
            'count': count,
            'latest_status': latest_status,
            'trials': trials
        }

    return {
        'phase2_count': trials_by_phase['PHASE2']['count'],
        'phase3_count': trials_by_phase['PHASE3']['count'],
        'phase2_status': trials_by_phase['PHASE2']['latest_status'],
        'phase3_status': trials_by_phase['PHASE3']['latest_status'],
        'total_count': trials_by_phase['PHASE2']['count'] + trials_by_phase['PHASE3']['count']
    }

def get_drug_efficacy(drug_name):
    """Get published efficacy data from PubMed.

    Args:
        drug_name: Drug name to search

    Returns:
        dict: Efficacy metrics extracted from publications
    """

    # Search for clinical trial publications
    result = pubmed_search(
        keywords=f"{drug_name} AND (weight loss OR HbA1c OR efficacy) AND Clinical Trial[Publication Type]",
        num_results=10
    )

    # Handle both dict and list response formats
    if isinstance(result, list):
        articles = result
        publications_found = len(result)
    else:
        articles = result.get('articles', [])
        publications_found = result.get('count', 0)

    efficacy_data = {
        'publications_found': publications_found,
        'weight_loss': [],
        'hba1c_reduction': [],
        'key_studies': []
    }

    # Extract efficacy from abstracts
    for article in articles:
        abstract = article.get('abstract', '')

        if not abstract:
            continue

        # Extract weight loss percentage
        weight_loss = extract_weight_loss(abstract)
        if weight_loss:
            efficacy_data['weight_loss'].append({
                'value': weight_loss,
                'study': article.get('title', 'Unknown'),
                'pmid': article.get('pmid', 'Unknown')
            })

        # Extract HbA1c reduction
        hba1c = extract_hba1c(abstract)
        if hba1c:
            efficacy_data['hba1c_reduction'].append({
                'value': hba1c,
                'study': article.get('title', 'Unknown'),
                'pmid': article.get('pmid', 'Unknown')
            })

        # Track key studies
        if weight_loss or hba1c:
            efficacy_data['key_studies'].append({
                'title': article.get('title', 'Unknown'),
                'pmid': article.get('pmid', 'Unknown'),
                'pub_date': article.get('pub_date', 'Unknown')
            })

    return efficacy_data

def extract_count(markdown):
    """Extract total count from CT.gov markdown."""
    match = re.search(r'Total studies found:\s*(\d+)', markdown)
    return int(match.group(1)) if match else 0

def parse_trials_markdown(markdown):
    """Parse CT.gov markdown into trial dicts."""
    trial_blocks = re.split(r'###\s+\d+\.\s+(NCT\d{8})', markdown)

    trials = []
    for i in range(1, len(trial_blocks), 2):
        if i + 1 < len(trial_blocks):
            nct_id = trial_blocks[i]
            content = trial_blocks[i + 1]

            trials.append({
                'nct_id': nct_id,
                'title': extract_field(content, r'\*\*Title:\*\*\s*(.+)'),
                'status': extract_field(content, r'\*\*Status:\*\*\s*(.+)'),
                'phase': extract_field(content, r'\*\*Phase:\*\*\s*(.+)'),
                'start_date': extract_field(content, r'\*\*Start Date:\*\*\s*(.+)')
            })

    return trials

def extract_field(text, pattern):
    """Extract field from markdown using regex."""
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None

def extract_weight_loss(abstract):
    """Extract weight loss percentage from abstract.

    Looks for patterns like:
    - "15% weight loss"
    - "weight reduction of 12.4%"
    - "lost 18.2% body weight"
    """
    patterns = [
        r'(\d+\.?\d*)\s*%\s*(?:body\s*)?weight\s*(?:loss|reduction)',
        r'(?:weight\s*loss|reduction)\s*of\s*(\d+\.?\d*)\s*%',
        r'lost\s*(\d+\.?\d*)\s*%\s*(?:body\s*)?weight'
    ]

    for pattern in patterns:
        match = re.search(pattern, abstract, re.IGNORECASE)
        if match:
            return float(match.group(1))

    return None

def extract_hba1c(abstract):
    """Extract HbA1c reduction from abstract.

    Looks for patterns like:
    - "HbA1c reduction of 2.1%"
    - "reduced HbA1c by 1.8%"
    - "HbA1c decreased 1.5%"
    """
    patterns = [
        r'HbA1c\s*(?:reduction|decrease)\s*of\s*(\d+\.?\d*)\s*%',
        r'reduced?\s*HbA1c\s*by\s*(\d+\.?\d*)\s*%',
        r'HbA1c\s*(?:decreased|reduced)\s*(\d+\.?\d*)\s*%'
    ]

    for pattern in patterns:
        match = re.search(pattern, abstract, re.IGNORECASE)
        if match:
            return float(match.group(1))

    return None

def format_pipeline_summary(profiles):
    """Format comprehensive summary of pipeline drugs."""

    lines = [
        f"\n{'='*70}",
        f"PIPELINE GLP-1 DRUGS EFFICACY ANALYSIS",
        f"{'='*70}\n"
    ]

    for profile in profiles:
        drug = profile['drug_name']
        trials = profile['trials']
        efficacy = profile['efficacy']

        lines.extend([
            f"{drug.upper()}",
            f"{'-'*len(drug)}",
            f"Phase 2 Trials: {trials['phase2_count']} (Latest: {trials['phase2_status'] or 'N/A'})",
            f"Phase 3 Trials: {trials['phase3_count']} (Latest: {trials['phase3_status'] or 'N/A'})",
            f"Total Trials: {trials['total_count']}",
            f"\nPublished Efficacy Data:",
            f"  Publications Found: {efficacy['publications_found']}"
        ])

        # Weight loss data
        if efficacy['weight_loss']:
            lines.append(f"  Weight Loss Reported:")
            for wl in efficacy['weight_loss'][:3]:  # Top 3
                lines.append(f"    - {wl['value']}% (PMID: {wl['pmid']})")
        else:
            lines.append(f"  Weight Loss: No published data found")

        # HbA1c data
        if efficacy['hba1c_reduction']:
            lines.append(f"  HbA1c Reduction Reported:")
            for hba1c in efficacy['hba1c_reduction'][:3]:  # Top 3
                lines.append(f"    - {hba1c['value']}% (PMID: {hba1c['pmid']})")
        else:
            lines.append(f"  HbA1c Reduction: No published data found")

        lines.append("")  # Blank line between drugs

    lines.append(f"{'='*70}\n")

    return "\n".join(lines)

if __name__ == "__main__":
    result = get_pipeline_drug_efficacy()
    print(result['summary'])
