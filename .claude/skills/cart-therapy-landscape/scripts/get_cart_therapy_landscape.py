import sys
sys.path.insert(0, ".claude")
from mcp.servers.ct_gov_mcp import search as ct_search
from mcp.servers.pubmed_mcp import search as pubmed_search
import re

def get_cart_therapy_landscape():
    """Get CAR-T therapy clinical trials and recent publications.

    Combines data from ClinicalTrials.gov (markdown) and PubMed (JSON)
    to provide comprehensive landscape view.

    Returns:
        dict: Contains trials, publications, and integrated summary
    """
    # 1. Get clinical trials from CT.gov (returns markdown)
    print("Fetching CAR-T clinical trials from ClinicalTrials.gov...")
    trials_result = ct_search(term="CAR-T therapy", pageSize=100)

    # Parse markdown trials
    trial_sections = re.split(r'###\s+\d+\.\s+(NCT\d{8})', trials_result)[1:]
    trials = []

    for i in range(0, len(trial_sections), 2):
        if i + 1 < len(trial_sections):
            nct_id = trial_sections[i]
            section = trial_sections[i + 1]

            trial = {'nct_id': nct_id}

            # Extract fields using regex
            title_match = re.search(r'\*\*Title:\*\*\s*(.+)', section)
            if title_match:
                trial['title'] = title_match.group(1).strip()

            status_match = re.search(r'\*\*Status:\*\*\s*(.+)', section)
            if status_match:
                trial['status'] = status_match.group(1).strip()

            phase_match = re.search(r'\*\*Phase:\*\*\s*(.+)', section)
            if phase_match:
                trial['phase'] = phase_match.group(1).strip()

            conditions_match = re.search(r'\*\*Conditions:\*\*\s*(.+)', section)
            if conditions_match:
                trial['conditions'] = conditions_match.group(1).strip()

            trials.append(trial)

    # 2. Get recent publications from PubMed (returns JSON)
    print("Fetching recent CAR-T publications from PubMed...")
    pub_result = pubmed_search(
        query="CAR-T therapy AND 2023:2024[PDAT]",
        max_results=100
    )

    publications = []
    for article in pub_result.get('results', []):
        publications.append({
            'pmid': article.get('pmid'),
            'title': article.get('title'),
            'authors': article.get('authors', []),
            'journal': article.get('journal'),
            'pub_date': article.get('pub_date'),
            'year': article.get('pub_date', '').split('-')[0] if article.get('pub_date') else None
        })

    # 3. Aggregate insights across both sources
    # Trial statistics
    trial_phases = {}
    trial_statuses = {}

    for trial in trials:
        phase = trial.get('phase', 'Unknown')
        status = trial.get('status', 'Unknown')

        trial_phases[phase] = trial_phases.get(phase, 0) + 1
        trial_statuses[status] = trial_statuses.get(status, 0) + 1

    # Publication statistics
    pub_years = {}
    pub_journals = {}

    for pub in publications:
        year = pub.get('year', 'Unknown')
        journal = pub.get('journal', 'Unknown')

        pub_years[year] = pub_years.get(year, 0) + 1
        pub_journals[journal] = pub_journals.get(journal, 0) + 1

    # Top journals
    top_journals = sorted(pub_journals.items(), key=lambda x: x[1], reverse=True)[:5]

    # 4. Create integrated summary
    summary = {
        'trials': {
            'total': len(trials),
            'by_phase': dict(sorted(trial_phases.items())),
            'by_status': dict(sorted(trial_statuses.items(), key=lambda x: x[1], reverse=True))
        },
        'publications': {
            'total': len(publications),
            'by_year': dict(sorted(pub_years.items())),
            'top_journals': top_journals
        }
    }

    return {
        'trials': trials,
        'publications': publications,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_cart_therapy_landscape()

    print("\n" + "="*60)
    print("CAR-T THERAPY LANDSCAPE")
    print("="*60)

    print(f"\n📊 CLINICAL TRIALS: {result['summary']['trials']['total']}")
    print("\nBy Phase:")
    for phase, count in result['summary']['trials']['by_phase'].items():
        print(f"  {phase}: {count}")

    print("\nBy Status:")
    for status, count in list(result['summary']['trials']['by_status'].items())[:5]:
        print(f"  {status}: {count}")

    print(f"\n📚 RECENT PUBLICATIONS (2023-2024): {result['summary']['publications']['total']}")
    print("\nBy Year:")
    for year, count in result['summary']['publications']['by_year'].items():
        print(f"  {year}: {count}")

    print("\nTop Journals:")
    for journal, count in result['summary']['publications']['top_journals']:
        print(f"  {journal}: {count}")

    print("\n" + "="*60)
    print("✓ Multi-server integration complete")
    print("✓ Data sources: ClinicalTrials.gov (markdown) + PubMed (JSON)")
    print("="*60)
