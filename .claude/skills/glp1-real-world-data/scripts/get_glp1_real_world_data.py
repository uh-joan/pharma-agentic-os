import sys
sys.path.insert(0, ".claude")
from mcp.servers.pubmed_mcp import search_keywords
import re

def get_glp1_real_world_data():
    """Get real-world evidence data for GLP-1 drugs from PubMed.

    Searches PubMed for observational studies, real-world evidence,
    and persistence/discontinuation data for major GLP-1 drugs.

    Returns:
        dict: Contains total_count, studies_by_drug, and summary
    """

    # GLP-1 drugs to search
    drugs = {
        'semaglutide': ['Ozempic', 'Wegovy', 'Rybelsus'],
        'tirzepatide': ['Mounjaro', 'Zepbound'],
        'dulaglutide': ['Trulicity'],
        'liraglutide': ['Victoza', 'Saxenda']
    }

    # RWE-specific search terms
    rwe_terms = [
        'real-world',
        'real world',
        'observational',
        'persistence',
        'discontinuation',
        'adherence',
        'retrospective cohort'
    ]

    all_studies = {}
    total_studies = 0

    for drug_generic, brand_names in drugs.items():
        drug_studies = []

        # Search for each RWE term combined with drug names
        for rwe_term in rwe_terms:
            # Combine drug names with OR
            drug_query = ' OR '.join([drug_generic] + brand_names)

            # Construct search query
            search_query = f'({drug_query}) AND ("{rwe_term}")'

            try:
                result = search_keywords(
                    keywords=search_query,
                    num_results=20
                )

                # Handle both list and dict response formats
                if isinstance(result, list):
                    articles = result
                elif isinstance(result, dict):
                    articles = result.get('articles', [])
                else:
                    articles = []

                for article in articles:
                    pmid = article.get('pmid', 'N/A')

                    # Skip duplicates
                    if any(s.get('pmid') == pmid for s in drug_studies):
                        continue

                    title = article.get('title', 'N/A')
                    abstract = article.get('abstract', '')
                    pub_date = article.get('pub_date', 'N/A')

                    # Extract metrics from abstract (pattern matching)
                    metrics = extract_rwe_metrics(abstract)

                    # Only include if relevant to RWE
                    if is_rwe_relevant(title, abstract):
                        study_info = {
                            'pmid': pmid,
                            'title': title,
                            'pub_date': pub_date,
                            'rwe_term': rwe_term,
                            'discontinuation_rate': metrics.get('discontinuation'),
                            'persistence_6mo': metrics.get('persistence_6mo'),
                            'persistence_12mo': metrics.get('persistence_12mo'),
                            'study_size': metrics.get('study_size'),
                            'abstract_snippet': abstract[:200] + '...' if len(abstract) > 200 else abstract
                        }
                        drug_studies.append(study_info)

            except Exception as e:
                print(f"Warning: Search failed for {drug_generic} + {rwe_term}: {str(e)}")
                continue

        # Remove duplicates and limit to top 10 most relevant
        unique_studies = []
        seen_pmids = set()
        for study in drug_studies:
            if study['pmid'] not in seen_pmids:
                unique_studies.append(study)
                seen_pmids.add(study['pmid'])

        all_studies[drug_generic] = unique_studies[:10]
        total_studies += len(all_studies[drug_generic])

    # Generate summary
    summary = generate_summary(all_studies, total_studies)

    return {
        'total_count': total_studies,
        'studies_by_drug': all_studies,
        'summary': summary
    }

def extract_rwe_metrics(text):
    """Extract RWE metrics from abstract text using pattern matching.

    Args:
        text: Abstract text

    Returns:
        dict: Extracted metrics
    """
    metrics = {}

    if not text:
        return metrics

    text_lower = text.lower()

    # Discontinuation rate patterns
    disc_patterns = [
        r'discontinuation.*?(\d+(?:\.\d+)?)\s*%',
        r'(\d+(?:\.\d+)?)\s*%.*?discontinu',
        r'discontinued.*?(\d+(?:\.\d+)?)\s*%'
    ]

    for pattern in disc_patterns:
        match = re.search(pattern, text_lower)
        if match:
            metrics['discontinuation'] = f"{match.group(1)}%"
            break

    # Persistence patterns
    persist_patterns = [
        r'persistence.*?6.*?month.*?(\d+(?:\.\d+)?)\s*%',
        r'(\d+(?:\.\d+)?)\s*%.*?persisten.*?6.*?month',
        r'6.*?month.*?persistence.*?(\d+(?:\.\d+)?)\s*%'
    ]

    for pattern in persist_patterns:
        match = re.search(pattern, text_lower)
        if match:
            metrics['persistence_6mo'] = f"{match.group(1)}%"
            break

    persist_12mo_patterns = [
        r'persistence.*?12.*?month.*?(\d+(?:\.\d+)?)\s*%',
        r'(\d+(?:\.\d+)?)\s*%.*?persisten.*?12.*?month',
        r'12.*?month.*?persistence.*?(\d+(?:\.\d+)?)\s*%'
    ]

    for pattern in persist_12mo_patterns:
        match = re.search(pattern, text_lower)
        if match:
            metrics['persistence_12mo'] = f"{match.group(1)}%"
            break

    # Study size patterns
    size_patterns = [
        r'(\d{1,3}(?:,\d{3})+|\d{4,})\s+patient',
        r'n\s*=\s*(\d{1,3}(?:,\d{3})+|\d{4,})',
        r'cohort.*?(\d{1,3}(?:,\d{3})+|\d{4,})'
    ]

    for pattern in size_patterns:
        match = re.search(pattern, text_lower)
        if match:
            size_str = match.group(1).replace(',', '')
            metrics['study_size'] = f"n={size_str}"
            break

    return metrics

def is_rwe_relevant(title, abstract):
    """Check if study is relevant to real-world evidence.

    Args:
        title: Study title
        abstract: Study abstract

    Returns:
        bool: True if relevant
    """
    text = (title + ' ' + abstract).lower()

    # Required keywords
    rwe_keywords = [
        'real-world', 'real world', 'observational',
        'persistence', 'discontinuation', 'adherence',
        'retrospective', 'cohort', 'claims data',
        'electronic health record', 'ehr'
    ]

    # Must contain at least one RWE keyword
    return any(keyword in text for keyword in rwe_keywords)

def generate_summary(studies_by_drug, total_count):
    """Generate summary of RWE data collection.

    Args:
        studies_by_drug: Dictionary of studies by drug
        total_count: Total number of studies

    Returns:
        str: Formatted summary
    """
    summary_lines = [
        f"\n{'='*70}",
        f"GLP-1 Real-World Evidence Data Summary",
        f"{'='*70}\n",
        f"Total RWE studies found: {total_count}\n",
        f"Studies by drug:"
    ]

    for drug, studies in studies_by_drug.items():
        summary_lines.append(f"\n  {drug.upper()}: {len(studies)} studies")

        if studies:
            # Show top 3 most relevant studies
            for i, study in enumerate(studies[:3], 1):
                summary_lines.append(f"    {i}. PMID: {study['pmid']}")
                summary_lines.append(f"       {study['title'][:80]}...")

                if study['discontinuation_rate']:
                    summary_lines.append(f"       Discontinuation: {study['discontinuation_rate']}")
                if study['persistence_6mo']:
                    summary_lines.append(f"       6-month persistence: {study['persistence_6mo']}")
                if study['persistence_12mo']:
                    summary_lines.append(f"       12-month persistence: {study['persistence_12mo']}")
                if study['study_size']:
                    summary_lines.append(f"       Study size: {study['study_size']}")
                summary_lines.append("")

    summary_lines.extend([
        f"\n{'='*70}",
        f"Data Source: PubMed via pubmed_mcp",
        f"Search Strategy: RWE-specific keywords + drug names",
        f"{'='*70}\n"
    ])

    return '\n'.join(summary_lines)

if __name__ == "__main__":
    result = get_glp1_real_world_data()
    print(result['summary'])

    # Print detailed results for each drug
    print("\n\nDetailed Results by Drug:")
    print("="*70)
    for drug, studies in result['studies_by_drug'].items():
        print(f"\n{drug.upper()} ({len(studies)} studies):")
        for study in studies:
            print(f"\n  PMID: {study['pmid']}")
            print(f"  Title: {study['title']}")
            print(f"  Date: {study['pub_date']}")
            if study['discontinuation_rate']:
                print(f"  Discontinuation: {study['discontinuation_rate']}")
            if study['persistence_6mo']:
                print(f"  6-month persistence: {study['persistence_6mo']}")
            if study['persistence_12mo']:
                print(f"  12-month persistence: {study['persistence_12mo']}")
            if study['study_size']:
                print(f"  Study size: {study['study_size']}")
