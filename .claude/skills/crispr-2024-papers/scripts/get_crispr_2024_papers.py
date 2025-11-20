import sys
sys.path.insert(0, ".claude")
from mcp.servers.pubmed_mcp import search_advanced

def get_crispr_2024_papers():
    """Search PubMed for CRISPR gene editing papers published in 2024.

    Returns:
        dict: Contains total_count, papers list, and summary
    """
    # Search with date filter for 2024
    result = search_advanced(
        term="CRISPR gene editing",
        start_date="2024/01/01",
        end_date="2024/12/31",
        num_results=100
    )

    if not result or 'articles' not in result:
        return {
            'total_count': 0,
            'papers': [],
            'summary': "No papers found in PubMed for CRISPR gene editing in 2024."
        }

    articles = result['articles']
    papers = []

    for article in articles:
        try:
            pmid = article.get('pmid', 'N/A')
            title = article.get('title', 'No title')

            # Extract authors
            authors_list = article.get('authors', [])
            if isinstance(authors_list, list) and authors_list:
                author_names = authors_list[:3]  # First 3 authors
                if len(authors_list) > 3:
                    author_names.append("et al.")
                authors = ', '.join(author_names)
            else:
                authors = 'No authors listed'

            journal = article.get('journal', 'Unknown Journal')
            pub_date = article.get('pub_date', '2024')

            papers.append({
                'pmid': str(pmid),
                'title': title,
                'authors': authors,
                'journal': journal,
                'publication_date': pub_date
            })

        except Exception as e:
            continue

    # Generate summary
    total = len(papers)

    if total == 0:
        return {
            'total_count': 0,
            'papers': [],
            'summary': "No CRISPR gene editing papers found for 2024."
        }

    # Count by journal
    journal_counts = {}
    for paper in papers:
        journal = paper['journal']
        journal_counts[journal] = journal_counts.get(journal, 0) + 1

    top_journals = sorted(journal_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    summary = f"""CRISPR Gene Editing Papers - 2024

Total Papers Found: {total}

Top Journals:
"""
    for journal, count in top_journals:
        summary += f"  • {journal}: {count} paper{'s' if count > 1 else ''}\n"

    summary += f"\nSample Papers:\n"
    for i, paper in enumerate(papers[:5], 1):
        summary += f"\n{i}. {paper['title']}\n"
        summary += f"   Authors: {paper['authors']}\n"
        summary += f"   Journal: {paper['journal']}\n"
        summary += f"   PMID: {paper['pmid']}\n"
        summary += f"   Date: {paper['publication_date']}\n"

    return {
        'total_count': total,
        'papers': papers,
        'summary': summary
    }

if __name__ == "__main__":
    result = get_crispr_2024_papers()
    print(result['summary'])
    print(f"\nTotal papers collected: {result['total_count']}")
