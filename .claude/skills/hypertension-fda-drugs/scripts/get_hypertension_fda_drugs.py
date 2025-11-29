import sys
sys.path.insert(0, ".claude")
from mcp.servers.fda_mcp import lookup_drug

def get_hypertension_fda_drugs():
    """Get FDA-approved drugs for hypertension using count-first pattern.

    NOTE: Direct indication search (e.g., 'hypertension') doesn't work with FDA API
    count-first pattern. The FDA database doesn't index by indication in a way that's
    accessible via the public API. This skill demonstrates the limitation.

    Alternative approaches would require:
    - Searching for specific drug classes (ACE inhibitors, ARBs, etc.)
    - Using drug ingredient names (lisinopril, amlodipine, etc.)
    - Querying label data (which is broken due to token overflow)
    """
    # Use count-first pattern (MANDATORY per FDA documentation)
    # FDA API has hard limit of 100 results
    result = lookup_drug(
        search_term='hypertension',
        search_type='general',
        count='openfda.brand_name.exact',
        limit=100  # Maximum allowed by FDA API
    )

    # FDA response is nested: result['data']['results']
    # Check for error response first
    if 'error' in result:
        error_msg = result.get('error', 'Unknown error')
        print(f"FDA API Error: {error_msg}")
        return {'total_count': 0, 'unique_drugs': 0, 'drugs': [], 'summary': f'FDA API error: {error_msg}'}

    data = result.get('data', {})
    if not data or 'results' not in data:
        return {'total_count': 0, 'unique_drugs': 0, 'drugs': [], 'summary': 'No drugs found for hypertension'}

    # Parse count results (format: [{'term': 'BRAND_NAME', 'count': N}, ...])
    brand_counts = []
    for item in data['results']:
        brand_name = item.get('term', 'Unknown')
        count = item.get('count', 0)
        brand_counts.append({
            'brand_name': brand_name,
            'occurrence_count': count
        })

    # Sort alphabetically
    sorted_drugs = sorted(brand_counts, key=lambda x: x['brand_name'])

    return {
        'total_count': len(sorted_drugs),
        'unique_drugs': len(sorted_drugs),
        'drugs': sorted_drugs,
        'summary': f"{len(sorted_drugs)} unique brand names found for hypertension"
    }

if __name__ == "__main__":
    result = get_hypertension_fda_drugs()
    print(f"\nHypertension FDA Drugs: {result['unique_drugs']} unique brand names")
    print(f"Top 10 most common:")
    sorted_by_count = sorted(result['drugs'], key=lambda x: x['occurrence_count'], reverse=True)
    for i, drug in enumerate(sorted_by_count[:10], 1):
        print(f"  {i}. {drug['brand_name']} (appears {drug['occurrence_count']} times)")
