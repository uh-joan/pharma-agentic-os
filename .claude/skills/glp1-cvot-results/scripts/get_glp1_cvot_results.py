import sys
sys.path.insert(0, ".claude")
from mcp.servers.pubmed_mcp import search_keywords

def get_glp1_cvot_results():
    """Fetch cardiovascular outcome trial (CVOT) results for GLP-1 drugs from PubMed.

    Queries 3 major CVOTs:
    1. SELECT - Semaglutide in obesity without diabetes
    2. LEADER - Liraglutide in T2D with CVD
    3. REWIND - Dulaglutide in T2D

    Returns:
        dict: Contains total_trials and cvot_results with structured data
    """

    # Define CVOT trials with targeted queries
    cvot_trials = [
        {
            'name': 'SELECT',
            'drug': 'Semaglutide',
            'query': 'Lincoff SELECT semaglutide cardiovascular NEJM',
            'expected_outcome': '20% MACE reduction in obesity without T2D'
        },
        {
            'name': 'LEADER',
            'drug': 'Liraglutide',
            'query': 'Marso LEADER liraglutide cardiovascular NEJM',
            'expected_outcome': '13% MACE reduction in T2D with CVD'
        },
        {
            'name': 'REWIND',
            'drug': 'Dulaglutide',
            'query': 'dulaglutide REWIND cardiovascular outcomes diabetes',
            'expected_outcome': '12% MACE reduction in T2D'
        }
    ]

    cvot_results = {}
    total_articles = 0

    for trial in cvot_trials:
        print(f"\nQuerying {trial['name']} trial ({trial['drug']})...")

        # Query PubMed with targeted search
        articles = search_keywords(
            keywords=trial['query'],
            num_results=5
        )

        if articles and len(articles) > 0:
            # Get primary article (first result should be main CVOT publication)
            primary = articles[0]

            cvot_results[trial['name']] = {
                'trial_name': trial['name'],
                'drug_name': trial['drug'],
                'expected_outcome': trial['expected_outcome'],
                'publication': {
                    'title': primary.get('title', 'N/A'),
                    'authors': primary.get('authors', 'N/A'),
                    'journal': primary.get('journal', 'N/A'),
                    'year': primary.get('year', 'N/A'),
                    'pmid': primary.get('pmid', 'N/A')
                },
                'abstract_snippet': primary.get('abstract', 'N/A')[:500] + '...' if primary.get('abstract') else 'N/A',
                'total_related_articles': len(articles)
            }
            total_articles += len(articles)
            print(f"✓ Found {len(articles)} articles for {trial['name']}")
        else:
            print(f"✗ No articles found for {trial['name']}")
            cvot_results[trial['name']] = {
                'trial_name': trial['name'],
                'drug_name': trial['drug'],
                'error': 'No articles found'
            }

    # Generate summary
    summary = f"""
GLP-1 CVOT Results Summary
=========================

Total trials queried: {len(cvot_trials)}
Total articles retrieved: {total_articles}

Trials with results:
"""

    for trial_name, data in cvot_results.items():
        if 'error' not in data:
            summary += f"\n{trial_name} ({data['drug_name']}):"
            summary += f"\n  Publication: {data['publication']['journal']} ({data['publication']['year']})"
            summary += f"\n  PMID: {data['publication']['pmid']}"
            summary += f"\n  Expected outcome: {data['expected_outcome']}"
            summary += f"\n  Related articles found: {data['total_related_articles']}"
        else:
            summary += f"\n{trial_name} ({data['drug_name']}): {data['error']}"

    return {
        'total_trials': len(cvot_trials),
        'total_articles': total_articles,
        'cvot_results': cvot_results,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_glp1_cvot_results()
    print(result['summary'])

    # Show detailed results
    print("\n\nDetailed CVOT Data:")
    print("=" * 80)
    for trial_name, data in result['cvot_results'].items():
        if 'error' not in data:
            print(f"\n{trial_name} - {data['drug_name']}")
            print("-" * 80)
            print(f"Title: {data['publication']['title']}")
            print(f"Authors: {data['publication']['authors']}")
            print(f"Journal: {data['publication']['journal']} ({data['publication']['year']})")
            print(f"PMID: {data['publication']['pmid']}")
            print(f"\nAbstract snippet:")
            print(data['abstract_snippet'])
