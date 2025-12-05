import sys
sys.path.insert(0, ".claude")
from mcp.servers.pubmed_mcp import search_keywords
import json

def get_glp1_clinical_trial_results():
    """Fetch published efficacy results from landmark GLP-1 clinical trials.

    Returns:
        dict: Contains summary and trial results with efficacy data
    """

    # Define landmark trials to query
    # Use simple, targeted queries - rely on PubMed relevance ranking
    trials = [
        {
            'name': 'SURMOUNT-1',
            'drug': 'Tirzepatide',
            'indication': 'obesity',
            'query': 'Jastreboff SURMOUNT-1 tirzepatide obesity NEJM 2022'
        },
        {
            'name': 'STEP-1',
            'drug': 'Semaglutide',
            'indication': 'obesity',
            'query': 'Wilding STEP 1 semaglutide obesity NEJM 2021'
        },
        {
            'name': 'SURPASS-6',
            'drug': 'Tirzepatide',
            'indication': 'T2D',
            'query': 'Ludvik SURPASS-6 tirzepatide insulin Lancet 2023'
        },
        {
            'name': 'SUSTAIN-6',
            'drug': 'Semaglutide',
            'indication': 'T2D',
            'query': 'Marso SUSTAIN-6 semaglutide cardiovascular NEJM 2016'
        },
        {
            'name': 'PIONEER-1',
            'drug': 'Oral Semaglutide',
            'indication': 'T2D',
            'query': 'Aroda PIONEER 1 oral semaglutide diabetes 2019'
        },
        {
            'name': 'AWARD-6',
            'drug': 'Dulaglutide',
            'indication': 'T2D',
            'query': 'Dungan AWARD-6 dulaglutide liraglutide Lancet 2014'
        },
        {
            'name': 'LEADER',
            'drug': 'Liraglutide',
            'indication': 'T2D',
            'query': 'Marso LEADER liraglutide cardiovascular NEJM 2016'
        }
    ]

    results = {}
    successful_queries = 0

    for trial in trials:
        try:
            # Search PubMed for trial publication
            articles = search_keywords(
                keywords=trial['query'],
                num_results=5  # Get top 5 most relevant
            )

            # PubMed MCP returns list of articles directly (not dict with 'articles' key)
            if articles and isinstance(articles, list) and len(articles) > 0:
                # Take the first (most relevant) article
                article = articles[0]

                results[trial['name']] = {
                    'drug': trial['drug'],
                    'indication': trial['indication'],
                    'title': article.get('title', 'N/A'),
                    'authors': article.get('authors', 'N/A'),
                    'journal': article.get('journal', 'N/A'),
                    'pub_date': article.get('pub_date', 'N/A'),
                    'pmid': article.get('pmid', 'N/A'),
                    'abstract': article.get('abstract', 'N/A')[:500] + '...' if article.get('abstract') else 'N/A',
                    'query_used': trial['query']
                }
                successful_queries += 1
            else:
                results[trial['name']] = {
                    'drug': trial['drug'],
                    'indication': trial['indication'],
                    'status': 'No publications found',
                    'query_used': trial['query']
                }

        except Exception as e:
            results[trial['name']] = {
                'drug': trial['drug'],
                'indication': trial['indication'],
                'status': f'Error: {str(e)}',
                'query_used': trial['query']
            }

    # Generate summary
    summary = {
        'total_trials_queried': len(trials),
        'successful_queries': successful_queries,
        'failed_queries': len(trials) - successful_queries,
        'trials_by_indication': {
            'obesity': sum(1 for t in trials if t['indication'] == 'obesity'),
            'T2D': sum(1 for t in trials if t['indication'] == 'T2D')
        }
    }

    return {
        'summary': summary,
        'results': results
    }

if __name__ == "__main__":
    result = get_glp1_clinical_trial_results()

    print("=" * 80)
    print("GLP-1 Clinical Trial Results from PubMed")
    print("=" * 80)
    print(f"\nTotal trials queried: {result['summary']['total_trials_queried']}")
    print(f"Successful queries: {result['summary']['successful_queries']}")
    print(f"Failed queries: {result['summary']['failed_queries']}")
    print(f"\nTrials by indication:")
    print(f"  - Obesity trials: {result['summary']['trials_by_indication']['obesity']}")
    print(f"  - T2D trials: {result['summary']['trials_by_indication']['T2D']}")

    print("\n" + "=" * 80)
    print("Trial Details")
    print("=" * 80)

    for trial_name, data in result['results'].items():
        print(f"\n{trial_name} ({data['drug']} - {data['indication']})")
        print("-" * 80)

        if 'status' in data:
            print(f"Status: {data['status']}")
        else:
            print(f"Title: {data.get('title', 'N/A')}")
            print(f"Authors: {data.get('authors', 'N/A')}")
            print(f"Journal: {data.get('journal', 'N/A')}")
            print(f"Publication Date: {data.get('pub_date', 'N/A')}")
            print(f"PMID: {data.get('pmid', 'N/A')}")
            print(f"\nAbstract (truncated):\n{data.get('abstract', 'N/A')}")
