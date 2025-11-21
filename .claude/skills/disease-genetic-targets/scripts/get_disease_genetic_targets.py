import sys
sys.path.insert(0, ".claude")
from mcp.servers.opentargets_mcp import search_diseases, get_disease_targets_summary, get_target_disease_associations

def get_disease_genetic_targets(disease_query, min_genetic_score=0.3, min_overall_score=0.2, top_n=20, max_fetch=5000):
    """Get therapeutic targets for a disease with strong genetic evidence.

    Args:
        disease_query: Disease name to search for (e.g., "Alzheimer's disease")
        min_genetic_score: Minimum genetic association score threshold (0.0-1.0)
        min_overall_score: Minimum overall association score threshold (0.0-1.0)
        top_n: Maximum number of top targets to return
        max_fetch: Maximum associations to fetch (default: 5000, supports up to 50,000 with pagination)

    Returns:
        dict: Contains disease info, targets with genetic evidence, and summary statistics
    """

    # Step 1: Search for disease to get EFO ID
    print(f"Searching for disease: {disease_query}...")
    disease_search = search_diseases(query=disease_query, size=5)

    # Extract disease hits
    search_data = disease_search.get('data', {}).get('search', {})
    disease_hits = search_data.get('hits', [])

    if not disease_hits:
        return {
            'error': 'Disease not found',
            'query': disease_query
        }

    # Get the first (best) match
    disease = disease_hits[0]
    disease_id = disease['id']
    disease_name = disease['name']

    print(f"Found disease: {disease_name} ({disease_id})")

    # Step 2: Get target-disease associations (with pagination support)
    print(f"Fetching associations for {disease_name} (up to {max_fetch} targets)...")
    associations = get_target_disease_associations(
        diseaseId=disease_id,
        minScore=min_overall_score,
        size=max_fetch  # Now supports automatic pagination up to 50,000
    )

    # Extract pagination metadata
    pagination = associations.get('pagination', {})

    # Extract association rows from nested structure
    disease_data = associations.get('data', {}).get('disease', {})
    assoc_data = disease_data.get('associatedTargets', {})
    assoc_rows = assoc_data.get('rows', [])

    # Step 3: Collect targets above score threshold
    # Note: Current MCP implementation doesn't provide detailed datatype scores
    # We use overall association score as proxy
    all_targets = []

    for assoc in assoc_rows:
        # Extract scores
        overall_score = assoc.get('score', 0)

        # Filter by overall score (using as proxy for genetic evidence)
        if overall_score >= min_genetic_score:
            # Extract target info
            target = assoc.get('target', {})

            target_info = {
                'symbol': target.get('approvedSymbol', 'Unknown'),
                'name': target.get('approvedName', 'Unknown'),
                'id': target.get('id', 'Unknown'),
                'overall_score': round(overall_score, 3),
                'genetic_score': round(overall_score, 3),  # Using overall as proxy
                'evidence_scores': {
                    'overall': round(overall_score, 3)
                    # Note: Detailed evidence breakdown not available in current MCP implementation
                },
                'tractability': assoc.get('tractability', {})
            }

            all_targets.append(target_info)

    # Sort by overall score (descending)
    all_targets.sort(key=lambda x: x['overall_score'], reverse=True)

    # Limit to top N
    top_targets = all_targets[:top_n]

    print(f"Found {len(all_targets)} targets above threshold, returning top {len(top_targets)}...")
    if pagination:
        print(f"Pagination: Fetched {pagination.get('returned', 'N/A')} from {pagination.get('total', 'N/A')} total associations")

    # Note: Detailed drug information would require additional API calls
    for target in top_targets:
        target['has_known_drugs'] = False  # Would need separate API call to determine
        target['known_drugs'] = []

    # Step 4: Generate summary statistics
    summary = {
        'disease_name': disease_name,
        'disease_id': disease_id,
        'total_associations': len(assoc_rows),
        'targets_above_threshold': len(all_targets),
        'top_targets_returned': len(top_targets),
        'pagination': {
            'requested': pagination.get('requested', max_fetch),
            'returned': pagination.get('returned', len(assoc_rows)),
            'total_available': pagination.get('total', len(assoc_rows)),
            'filtered': pagination.get('filtered', len(assoc_rows))
        },
        'filters_applied': {
            'min_score_threshold': min_genetic_score,
            'note': 'Using overall association score (detailed evidence breakdown not available in current MCP version)'
        },
        'top_10_targets': [
            {
                'symbol': t['symbol'],
                'score': t['overall_score']
            }
            for t in top_targets[:10]
        ]
    }

    return {
        'disease': {
            'name': disease_name,
            'id': disease_id
        },
        'targets': top_targets,
        'summary': summary
    }

if __name__ == "__main__":
    # Get Alzheimer's disease genetic targets (fetch up to 5000 for comprehensive analysis)
    result = get_disease_genetic_targets(
        disease_query="Alzheimer's disease",
        min_genetic_score=0.3,
        min_overall_score=0.2,
        top_n=20,
        max_fetch=5000  # Leverage pagination to fetch comprehensive dataset
    )

    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        summary = result['summary']
        pagination = summary.get('pagination', {})

        print("\n" + "="*80)
        print(f"THERAPEUTIC TARGETS FOR {summary['disease_name'].upper()}")
        print("="*80)

        print(f"\nDisease ID: {summary['disease_id']}")
        print(f"\nPagination Info:")
        print(f"  Total associations in database: {pagination.get('total_available', 'N/A')}")
        print(f"  Associations fetched: {pagination.get('returned', 'N/A')}")
        print(f"  Requested fetch size: {pagination.get('requested', 'N/A')}")
        print(f"\nFiltering Results:")
        print(f"  Targets above threshold (score ≥ {summary['filters_applied']['min_score_threshold']}): {summary['targets_above_threshold']}")
        print(f"  Top targets returned: {summary['top_targets_returned']}")
        print(f"\nNote: {summary['filters_applied']['note']}")

        print("\n" + "-"*80)
        print("TOP 10 TARGETS BY ASSOCIATION SCORE")
        print("-"*80)

        for i, target in enumerate(summary['top_10_targets'], 1):
            print(f"{i:2d}. {target['symbol']:10s} | Score: {target['score']:.3f}")

        print("\n" + "-"*80)
        print("DETAILED TARGET INFORMATION")
        print("-"*80)

        for i, target in enumerate(result['targets'][:10], 1):  # Show top 10
            print(f"\n{i:2d}. {target['symbol']:10s} - {target['name']}")
            print(f"     Ensembl ID: {target['id']}")
            print(f"     Association Score: {target['overall_score']:.3f}")

        print("\n" + "="*80)
